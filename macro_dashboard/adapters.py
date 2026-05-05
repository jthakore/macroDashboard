from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from .contracts import DocumentContract, Observation, TimeSeriesContract, ValidationStatus
from .io_utils import parse_date, parse_float, read_csv_rows, stable_id, utc_now_iso, write_json


class AdapterError(RuntimeError):
    pass


def fetch_json(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def write_raw_api(data_dir: Path, source: str, name: str, payload: Any) -> Path:
    path = data_dir / "raw" / "api" / source.lower().replace(" ", "_") / f"{name}.json"
    write_json(path, {"fetched_at": utc_now_iso(), "source": source, "payload": payload})
    return path


def ingest_fred(
    data_dir: Path,
    series_id: str,
    bucket: str,
    series_name: str | None = None,
    api_key: str | None = None,
    observation_start: str | None = None,
) -> TimeSeriesContract:
    key = api_key or os.getenv("FRED_API_KEY")
    if not key:
        raise AdapterError("FRED_API_KEY is required for FRED ingestion.")
    params = {
        "series_id": series_id,
        "api_key": key,
        "file_type": "json",
    }
    if observation_start:
        params["observation_start"] = observation_start
    url = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(params)
    payload = fetch_json(url)
    write_raw_api(data_dir, "FRED", series_id, payload)
    observations = []
    for item in payload.get("observations", []):
        value = parse_float(item.get("value"))
        date = parse_date(item.get("date"))
        if date:
            observations.append(
                Observation(
                    date=date,
                    value=value,
                    realtime_start=item.get("realtime_start"),
                    realtime_end=item.get("realtime_end"),
                    vintage_date=item.get("realtime_end"),
                )
            )
    return TimeSeriesContract(
        series_id=f"FRED:{series_id}",
        series_name=series_name or series_id,
        bucket=bucket,
        source="FRED",
        observations=observations,
        metadata={"api_url": url, "raw_source": "FRED series observations"},
    )


def ingest_yfinance(
    data_dir: Path,
    ticker: str,
    bucket: str,
    series_name: str | None = None,
    period: str = "5y",
    interval: str = "1wk",
) -> TimeSeriesContract:
    series_id = f"YF:{ticker}"
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(period=period, interval=interval)
    
    raw_payload = df.reset_index().assign(Date=lambda x: x["Date"].astype(str)).to_dict(orient="records")
    write_raw_api(data_dir, "yfinance", ticker, raw_payload)
    
    observations = []
    for date_val, row in df.iterrows():
        date_str = date_val.strftime("%Y-%m-%d")
        parsed_date = parse_date(date_str)
        if parsed_date and not pd.isna(row["Close"]):
            observations.append(
                Observation(
                    date=parsed_date,
                    value=float(row["Close"])
                )
            )
            
    return TimeSeriesContract(
        series_id=series_id,
        series_name=series_name or ticker,
        bucket=bucket,
        source="yfinance",
        observations=observations,
        metadata={"ticker": ticker, "period": period, "interval": interval},
    )


def ingest_treasury(
    data_dir: Path,
    endpoint: str,
    fields: list[str],
    date_field: str,
    value_field: str,
    series_id: str,
    series_name: str,
    bucket: str,
    filters: str | None = None,
) -> TimeSeriesContract:
    base = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
    params = {"fields": ",".join(fields), "sort": date_field, "format": "json", "page[size]": "10000"}
    if filters:
        params["filter"] = filters
    url = base + endpoint + "?" + urllib.parse.urlencode(params)
    payload = fetch_json(url)
    write_raw_api(data_dir, "Treasury FiscalData", series_id.replace(":", "_"), payload)
    observations = []
    for item in payload.get("data", []):
        date = parse_date(item.get(date_field))
        if date:
            observations.append(Observation(date=date, value=parse_float(item.get(value_field))))
    return TimeSeriesContract(
        series_id=series_id,
        series_name=series_name,
        bucket=bucket,
        source="Treasury FiscalData",
        observations=observations,
        metadata={"endpoint": endpoint, "fields": fields, "date_field": date_field, "value_field": value_field},
    )


def ingest_user_csv(
    data_dir: Path,
    csv_path: Path,
    source: str,
    bucket: str,
    date_column: str | None = None,
    value_columns: list[str] | None = None,
) -> list[TimeSeriesContract]:
    rows = read_csv_rows(csv_path)
    raw_path = data_dir / "raw" / "user_uploads" / csv_path.name
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(csv_path.read_text(encoding="utf-8-sig"), encoding="utf-8")
    if not rows:
        return []
    headers = list(rows[0].keys())
    date_col = date_column or _guess_date_column(headers)
    if not date_col:
        raise AdapterError("No date column found. Provide --date-column.")
    numeric_cols = value_columns or _guess_numeric_columns(rows, headers, date_col)
    series_list = []
    for col in numeric_cols:
        observations = []
        for row in rows:
            parsed_date = parse_date(row.get(date_col))
            if parsed_date:
                observations.append(Observation(date=parsed_date, value=parse_float(row.get(col))))
        series_list.append(
            TimeSeriesContract(
                series_id=f"USER:{stable_id(str(csv_path), col)[:12]}",
                series_name=col,
                bucket=bucket,
                source=source,
                observations=observations,
                metadata={"file": str(csv_path), "date_column": date_col, "value_column": col},
            )
        )
    return series_list


def ingest_gdelt_doc(
    data_dir: Path,
    query: str,
    theme: str,
    max_records: int = 75,
    mode: str = "artlist",
) -> list[DocumentContract]:
    params = {
        "query": query,
        "mode": mode,
        "format": "json",
        "maxrecords": str(max_records),
        "sort": "datedesc",
    }
    url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(params)
    payload = fetch_json(url)
    write_raw_api(data_dir, "GDELT", stable_id(query, theme)[:16], payload)
    articles = payload.get("articles", [])
    docs = []
    for item in articles:
        url_value = item.get("url")
        published = item.get("seendate") or item.get("publishedAt")
        docs.append(
            DocumentContract(
                document_id=stable_id(url_value or "", item.get("title") or ""),
                source_name=item.get("sourceCountry") or item.get("domain") or "GDELT",
                source_type="news_article",
                url=url_value,
                published_at_utc=_gdelt_date_to_iso(published),
                region=item.get("sourceCountry") or "unknown",
                title=item.get("title"),
                text_excerpt=item.get("seendate"),
                metadata={"theme": theme, "domain": item.get("domain"), "language": item.get("language")},
            )
        )
    return docs


def build_placeholder_api_series(
    data_dir: Path,
    source: str,
    series_id: str,
    series_name: str,
    bucket: str,
    reason: str,
) -> TimeSeriesContract:
    contract = TimeSeriesContract(
        series_id=series_id,
        series_name=series_name,
        bucket=bucket,
        source=source,
        observations=[],
        validation=ValidationStatus(status="unusable", latest_observation_date=None, issues=[reason]),
        metadata={"status": "adapter_placeholder", "reason": reason},
    )
    return contract


def _guess_date_column(headers: list[str]) -> str | None:
    candidates = {"date", "observation_date", "period", "time", "month", "quarter", "year"}
    for header in headers:
        if header.strip().lower() in candidates:
            return header
    for header in headers:
        lower = header.strip().lower()
        if "date" in lower or "period" in lower:
            return header
    return None


def _guess_numeric_columns(rows: list[dict[str, str]], headers: list[str], date_col: str) -> list[str]:
    numeric = []
    for header in headers:
        if header == date_col:
            continue
        sample = [parse_float(row.get(header)) for row in rows[:20]]
        if any(value is not None for value in sample):
            numeric.append(header)
    return numeric


def _gdelt_date_to_iso(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value)
    if len(text) >= 14 and text[:14].isdigit():
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}T{text[8:10]}:{text[10:12]}:{text[12:14]}Z"
    parsed = parse_date(text)
    return f"{parsed}T00:00:00Z" if parsed else None

