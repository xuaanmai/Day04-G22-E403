from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def fallback_tweets(*, screenname: str = "", query: str = "", limit: int = 5) -> list[dict[str, Any]]:
    label = screenname or query or "sample"
    samples = [
        {
            "title": f"{label} sample post 1",
            "summary": f"Fallback content for {label} because the live Twitter API is unavailable.",
            "url": f"https://x.com/{label}/status/1",
            "source": f"@{label}" if screenname else "x.com",
            "date": "2026-01-01T00:00:00Z",
            "metrics": {"favorites": 0, "retweets": 0, "views": 0},
        },
        {
            "title": f"{label} sample post 2",
            "summary": f"This fallback item keeps the lab workflow running while the external API is blocked.",
            "url": f"https://x.com/{label}/status/2",
            "source": f"@{label}" if screenname else "x.com",
            "date": "2026-01-02T00:00:00Z",
            "metrics": {"favorites": 0, "retweets": 0, "views": 0},
        },
    ]
    return samples[: max(int(limit or 5), 1)]


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}

