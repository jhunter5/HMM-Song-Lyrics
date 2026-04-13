"""
Text processing pipeline:
  raw text → clean → tokenize → CMU phonemes → HMM state sequence
"""

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# CMU dict loader  (local file, no NLTK)
# ---------------------------------------------------------------------------

# Entries like "word(2)" are alternate pronunciations; we keep only primary.
_ALT_RE = re.compile(r"\(\d+\)$")

def _load_cmudict(path: Path) -> dict[str, list[str]]:
    cmu: dict[str, list[str]] = {}
    with path.open(encoding="latin-1") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(";;;"):
                continue
            parts = line.split()
            word_token = parts[0]
            if _ALT_RE.search(word_token):   # skip alternate pronunciations
                continue
            cmu[word_token.lower()] = parts[1:]
    return cmu

_DICT_PATH = Path(__file__).parent / "cmudict.dict"
_CMU: dict[str, list[str]] = _load_cmudict(_DICT_PATH)


# ---------------------------------------------------------------------------
# Step 1 – clean
# ---------------------------------------------------------------------------

_SECTION_RE  = re.compile(r"\[.*?\]")             # [Verse 1], [Chorus] …
_STRIP_RE    = re.compile(r"[^a-z\s']")            # keep letters + apostrophes
_LONE_APOS   = re.compile(r"(?<![a-z])'|'(?![a-z])")  # apostrophes not in contractions

def clean(text: str) -> str:
    text = _SECTION_RE.sub(" ", text)
    text = text.lower()
    text = _STRIP_RE.sub(" ", text)
    text = _LONE_APOS.sub(" ", text)
    return " ".join(text.split())


# ---------------------------------------------------------------------------
# Step 2 – tokenize
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    return text.split()


# ---------------------------------------------------------------------------
# Step 3 – phoneme lookup
# ---------------------------------------------------------------------------

def phonemes_for(word: str) -> list[str]:
    """Primary CMU pronunciation for *word*, or [] if not in dictionary."""
    return list(_CMU.get(word, []))


# ---------------------------------------------------------------------------
# Step 4 – HMM state-sequence structure
# ---------------------------------------------------------------------------

def build_hmm_sequence(words: list[str]) -> dict:
    word_entries: list[dict] = []
    flat: list[str] = []

    for idx, word in enumerate(words):
        ph = phonemes_for(word)
        word_entries.append({"word": word, "phonemes": ph, "word_index": idx})
        flat.extend(ph)

    return {"words": word_entries, "flat_phoneme_sequence": flat}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def process(raw_text: str) -> dict:
    return build_hmm_sequence(tokenize(clean(raw_text)))
