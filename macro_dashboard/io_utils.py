from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def stable_id(*parts: str) -> str:
    joined = "|".join(part or "" for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def ensure_dirs(data_dir: Path) -> None:
    folders = [
        "config",
        "raw/api",
        "raw/downloads",
        "raw/scraped",
        "raw/news",
        "raw/user_uploads",
        "bronze/normalized_raw_json",
        "silver/validated_time_series",
        "silver/validated_events",
        "silver/validated_text_extracts",
        "gold/indicators",
        "gold/derived_series",
        "gold/sentiment_indexes",
        "gold/regime_scores",
        "gold/chart_specs",
        "logs",
    ]
    for folder in folders:
        (data_dir / folder).mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def append_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, sort_keys=True) + "\n")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if text in {"", ".", "NA", "N/A", "null", "None"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_date(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%Y-%m",
        "%Y",
        "%YQ%q",
    ]
    if len(text) == 7 and text[4] == "-":
        return f"{text}-01"
    if len(text) == 4 and text.isdigit():
        return f"{text}-01-01"
    for fmt in formats[:-1]:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    if "Q" in text.upper():
        year, quarter = text.upper().replace(" ", "").split("Q", 1)
        if year.isdigit() and quarter[:1].isdigit():
            month = {"1": "01", "2": "04", "3": "07", "4": "10"}.get(quarter[:1])
            if month:
                return f"{year}-{month}-01"
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None

