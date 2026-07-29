from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from urllib.parse import urlparse


TRUSTED_SUFFIXES = (".gov", ".gov.vn", ".edu", ".edu.vn")
TRUSTED_DOMAINS = {
    "arxiv.org",
    "nature.com",
    "science.org",
    "who.int",
    "oecd.org",
    "openai.com",
    "anthropic.com",
    "ai.google.dev",
}


def _host(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def _age_score(value: Any) -> float:
    if not value:
        return 0.0
    try:
        published = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        days = max(0, (datetime.now(timezone.utc) - published).days)
        if days <= 7:
            return 20.0
        if days <= 30:
            return 15.0
        if days <= 365:
            return 8.0
    except (TypeError, ValueError):
        try:
            parsed_date = date.fromisoformat(str(value))
            days = max(0, (date.today() - parsed_date).days)
            return 20.0 if days <= 7 else 15.0 if days <= 30 else 8.0 if days <= 365 else 0.0
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def rank_sources(
    sources: list[dict[str, Any]] | None = None,
    prefer_recent: bool = True,
) -> dict[str, Any]:
    ranked: list[dict[str, Any]] = []
    for source in sources or []:
        item = dict(source)
        url = str(item.get("url") or "")
        host = _host(url)
        score = 20.0
        reasons: list[str] = []

        if url.startswith("https://"):
            score += 10
            reasons.append("HTTPS")
        if host in TRUSTED_DOMAINS or host.endswith(TRUSTED_SUFFIXES):
            score += 30
            reasons.append("miền nguồn uy tín/ưu tiên")

        relevance = item.get("relevance_score", item.get("relevance"))
        if isinstance(relevance, (int, float)):
            normalized = max(0.0, min(1.0, float(relevance)))
            score += normalized * 30
            reasons.append("có tín hiệu liên quan")

        if prefer_recent:
            recency = _age_score(item.get("published_at") or item.get("date"))
            score += recency
            if recency:
                reasons.append("nguồn tương đối mới")

        item["domain"] = host
        item["score"] = round(min(100.0, score), 1)
        item["ranking_reasons"] = reasons or ["chưa có đủ metadata để cộng điểm"]
        ranked.append(item)

    ranked.sort(key=lambda value: (-value["score"], str(value.get("title") or "")))
    return {
        "tool": "source_ranker",
        "ranked_sources": ranked,
        "item_count": len(ranked),
        "disclaimer": "Điểm là heuristic hỗ trợ, không thay thế việc kiểm chứng nội dung.",
        "error": None,
    }
