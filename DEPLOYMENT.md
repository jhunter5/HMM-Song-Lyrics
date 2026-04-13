# Deployment Guide

## Prerequisites

- **OS**: Ubuntu 24.04 LTS (WSL2 or native)
- **Docker Engine** 24+ and the **Compose plugin**

### Install Docker (Ubuntu / WSL2)

```bash
sudo bash install-docker.sh
```

After the script finishes, apply the new group membership:

```bash
newgrp docker
```

> On WSL2 the script relies on systemd being active as PID 1 (default on Ubuntu 22.04+).
> Verify with: `cat /proc/1/comm` — should print `systemd`.

---

## Project Structure

```
hmm-song-lyrics/
├── docker-compose.yml
├── frontend/            # nginx — static upload UI
├── reverse-proxy/       # C# ASP.NET Core + YARP
└── text-processing/     # Python FastAPI — lyrics → phonemes → HMM sequence
```

---

## Running the Stack

### Build and start

```bash
docker compose up --build
```

### Start (images already built)

```bash
docker compose up
```

### Run in the background

```bash
docker compose up --build -d
```

### Stop

```bash
docker compose down
```

---

## Services & Ports

| Service | Internal address | Exposed port |
|---|---|---|
| frontend | `frontend:80` | `localhost:3000` |
| reverse-proxy (YARP) | `reverse-proxy:8080` | `localhost:8080` |
| processing-service | `processing-service:5000` | *(internal only)* |

Open **http://localhost:3000** to use the UI.

---

## Request Flow

```
Browser
  └─ POST /api/upload  →  nginx (3000)
       └─ strips /api   →  YARP (8080) /upload
            └─ proxies  →  processing-service (5000) /upload
                 └─ returns JSON
```

The multipart body carries two fields:

| Field | Content |
|---|---|
| `audio` | `.mp3` music file |
| `lyrics` | `.txt` lyrics file |

---

## Processing Pipeline (text-processing service)

1. **Clean** — removes section markers (`[Verse 1]`, `[Chorus]`, …), lowercases, strips punctuation while preserving in-word apostrophes
2. **Tokenize** — splits on whitespace
3. **Phoneme lookup** — queries the bundled CMU Pronouncing Dictionary (`cmudict.dict`, 135k entries, no network call)
4. **Build HMM sequence** — produces:

```json
{
  "words": [
    { "word": "hello", "phonemes": ["HH", "AH0", "L", "OW1"], "word_index": 0 },
    { "word": "world", "phonemes": ["W", "ER1", "L", "D"],    "word_index": 1 }
  ],
  "flat_phoneme_sequence": ["HH", "AH0", "L", "OW1", "W", "ER1", "L", "D"]
```

Phonemes follow the [ARPAbet](https://en.wikipedia.org/wiki/ARPABET) scheme.
Stress markers on vowels: `0` = unstressed, `1` = primary, `2` = secondary.
Words not found in the dictionary return an empty `phonemes` list.

---

## Adding the Next Service

The reverse proxy is pre-configured to forward to `processing-service:5000`.
When the audio processing service is ready:

1. Add it to `docker-compose.yml` on the `pipeline` network.
2. Update `reverse-proxy/appsettings.json` with a new route and cluster pointing to it.
3. No changes needed to YARP's C# code.
