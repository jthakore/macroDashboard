from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .contracts import LLMExtractionContract
from .io_utils import read_json, stable_id, write_json


PROMPT_TEMPLATE = """You are extracting macro-financial event data for a regime dashboard.
Return strict JSON matching the supplied schema. Do not invent facts or numeric data.
Use neutral labels when evidence is insufficient.

Schema keys:
document_id, source_name, source_type, url, published_at_utc, region,
macro_bucket, event_type, event_importance, directional_signal,
sentiment_scores, causal_channels, assets_impacted, summary,
evidence_spans, confidence, model, prompt_version.

Text:
{text}
"""


REQUIRED_EXTRACTION_KEYS = {
    "document_id",
    "source_name",
    "source_type",
    "url",
    "published_at_utc",
    "region",
    "macro_bucket",
    "event_type",
    "event_importance",
    "directional_signal",
    "sentiment_scores",
    "causal_channels",
    "assets_impacted",
    "summary",
    "evidence_spans",
    "confidence",
    "model",
    "prompt_version",
}


def validate_llm_extraction(payload: dict[str, Any]) -> list[str]:
    issues = []
    missing = REQUIRED_EXTRACTION_KEYS - set(payload)
    if missing:
        issues.append(f"Missing keys: {', '.join(sorted(missing))}")
    if "event_importance" in payload and not _between_zero_one(payload["event_importance"]):
        issues.append("event_importance must be between 0 and 1")
    if "confidence" in payload and not _between_zero_one(payload["confidence"]):
        issues.append("confidence must be between 0 and 1")
    if "sentiment_scores" in payload and not isinstance(payload["sentiment_scores"], dict):
        issues.append("sentiment_scores must be an object")
    return issues


def save_llm_extraction(data_dir: Path, payload: dict[str, Any]) -> Path:
    issues = validate_llm_extraction(payload)
    if issues:
        payload = dict(payload)
        payload["validation_issues"] = issues
    document_id = payload.get("document_id") or stable_id(str(payload))
    path = data_dir / "silver" / "validated_text_extracts" / f"{document_id}.json"
    write_json(path, payload)
    return path


def aggregate_sentiment_indexes(data_dir: Path) -> list[dict[str, Any]]:
    folder = data_dir / "silver" / "validated_text_extracts"
    if not folder.exists():
        return []
    by_date_theme: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for file in folder.glob("*.json"):
        payload = read_json(file)
        if payload.get("validation_issues"):
            continue
        date = (payload.get("published_at_utc") or "")[:10] or "unknown"
        scores = payload.get("sentiment_scores", {})
        confidence = float(payload.get("confidence") or 0.0)
        for score_name, value in scores.items():
            if isinstance(value, (int, float)):
                by_date_theme[(date, score_name)].append({"value": float(value), "confidence": confidence, "document": payload})
    records = []
    for (date, score_name), items in sorted(by_date_theme.items()):
        confidence_sum = sum(item["confidence"] for item in items) or len(items)
        score = sum(item["value"] * (item["confidence"] or 1.0) for item in items) / confidence_sum
        top_docs = sorted(items, key=lambda item: item["confidence"], reverse=True)[:3]
        records.append(
            {
                "series_id": f"SENTIMENT:{score_name.upper()}",
                "date": date,
                "score_name": score_name,
                "confidence_weighted_score": score,
                "article_count": len(items),
                "top_contributing_documents": [
                    {
                        "document_id": item["document"].get("document_id"),
                        "source_name": item["document"].get("source_name"),
                        "url": item["document"].get("url"),
                        "summary": item["document"].get("summary"),
                    }
                    for item in top_docs
                ],
            }
        )
    write_json(data_dir / "gold" / "sentiment_indexes" / "daily_sentiment_indexes.json", records)
    return records


def extraction_template_from_document(document: dict[str, Any], model: str = "manual_or_llm", prompt_version: str = "macro_event_v1.0") -> dict[str, Any]:
    return LLMExtractionContract(
        document_id=document.get("document_id") or stable_id(str(document)),
        source_name=document.get("source_name", "unknown"),
        source_type=document.get("source_type", "unknown"),
        url=document.get("url"),
        published_at_utc=document.get("published_at_utc"),
        region=document.get("region", "unknown"),
        macro_bucket=[],
        event_type=None,
        event_importance=0.0,
        directional_signal={
            "growth": "neutral",
            "inflation": "neutral",
            "policy": "neutral",
            "liquidity": "neutral",
            "credit": "neutral",
            "usd": "neutral",
            "commodities": "neutral",
        },
        sentiment_scores={
            "growth_sentiment": 0.0,
            "inflation_pressure": 0.0,
            "policy_hawkishness": 0.0,
            "risk_appetite": 0.0,
            "uncertainty": 0.0,
        },
        causal_channels=[],
        assets_impacted=[],
        summary="",
        evidence_spans=[],
        confidence=0.0,
        model=model,
        prompt_version=prompt_version,
    ).to_dict()


def _between_zero_one(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0

