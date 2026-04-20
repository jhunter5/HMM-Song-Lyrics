"""
Music processing pipeline:
  audio file → Spleeter vocal extraction → MFCC per frame
"""

import os
import tempfile
from pathlib import Path

import librosa
from spleeter.separator import Separator

SAMPLE_RATE = 22050
FRAME_DURATION_MS = 100
HOP_DURATION_MS = 50
N_MFCC = 13

# Loaded on first request; None until then so the container starts up
# even on memory-constrained hosts.
_separator: Separator | None = None


def _get_separator() -> Separator:
    global _separator
    if _separator is None:
        _separator = Separator("spleeter:2stems")
    return _separator


def process_audio(audio_bytes: bytes, filename: str) -> dict:
    suffix = Path(filename).suffix or ".mp3"

    with tempfile.TemporaryDirectory() as tmpdir:
        # --- Write uploaded audio to a temp file ---
        input_path = os.path.join(tmpdir, f"input{suffix}")
        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        # --- Vocal extraction with Spleeter (2stems: vocals + accompaniment) ---
        _get_separator().separate_to_file(input_path, tmpdir)

        # Spleeter writes to: <tmpdir>/<stem>/vocals.wav
        stem_name = Path(input_path).stem          # "input"
        vocals_path = os.path.join(tmpdir, stem_name, "vocals.wav")

        # --- Load vocals at target sample rate ---
        y, sr = librosa.load(vocals_path, sr=SAMPLE_RATE, mono=True)

        # --- Compute MFCCs ---
        frame_length = int(sr * FRAME_DURATION_MS / 1000)   # 2205 samples @ 22050 Hz
        hop_length   = int(sr * HOP_DURATION_MS   / 1000)   # 1102 samples @ 22050 Hz

        mfccs = librosa.feature.mfcc(
            y=y, sr=sr, n_mfcc=N_MFCC,
            n_fft=frame_length, hop_length=hop_length,
        )
        # shape: (N_MFCC, total_frames)

        total_frames    = mfccs.shape[1]
        total_duration  = round(len(y) / sr, 1)

        frames = [
            {
                "frame_index": i,
                "time_seconds": round(i * hop_length / sr, 3),
                "mfcc": [round(float(v), 1) for v in mfccs[:, i]],
            }
            for i in range(total_frames)
        ]

        return {
            "sample_rate": sr,
            "frame_duration_ms": FRAME_DURATION_MS,
            "hop_duration_ms": HOP_DURATION_MS,
            "total_frames": total_frames,
            "total_duration_seconds": total_duration,
            "frames": frames,
        }
