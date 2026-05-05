from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .io_utils import read_json, write_json


@dataclass
class SourceEntry:
    source: str
    type: str
    auth: str
    format: str
    update_frequency: str
    reliability_tier: str
    dashboard_use: str
    base_url: str | None = None
    notes: str | None = None


DEFAULT_SOURCES: list[SourceEntry] = [
    SourceEntry("FRED", "API", "API key", "JSON/CSV/XLSX/XML", "Varies", "Primary", "Macro, rates, spreads", "https://api.stlouisfed.org/fred"),
    SourceEntry("BEA", "API/download", "API key", "JSON/CSV/XLSX", "Monthly/quarterly", "Primary", "GDP, PCE, profits", "https://apps.bea.gov/api/data"),
    SourceEntry("BLS", "API/download", "Optional API key", "JSON/CSV", "Monthly/quarterly", "Primary", "CPI, labor, wages", "https://api.bls.gov/publicAPI/v2/timeseries/data"),
    SourceEntry("Treasury FiscalData", "API", "No key", "JSON/CSV/XML", "Daily/monthly", "Primary", "Fiscal, debt, Treasury data", "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"),
    SourceEntry("Fed DDP", "Download/API-style", "No key", "CSV/XML/SDMX", "Varies", "Primary", "Fed releases", "https://www.federalreserve.gov/datadownload"),
    SourceEntry("Census", "API", "Key recommended", "JSON", "Monthly/quarterly", "Primary", "Retail, housing, trade", "https://api.census.gov/data/timeseries"),
    SourceEntry("SEC EDGAR", "API/bulk", "No key; user-agent required", "JSON/ZIP", "Real time/nightly", "Primary", "Filings/fundamentals", "https://data.sec.gov"),
    SourceEntry("IMF", "SDMX API", "No key/account may be needed for explorer", "JSON/CSV/SDMX", "Varies", "Primary", "Global macro", "https://data.imf.org"),
    SourceEntry("World Bank", "API", "No key", "JSON/XML", "Annual/varies", "Primary", "Structural indicators", "https://api.worldbank.org/v2"),
    SourceEntry("OECD", "SDMX API", "No key", "JSON/CSV/XML", "Varies", "Primary", "Global DM comparison", "https://sdmx.oecd.org/public/rest"),
    SourceEntry("ECB", "SDMX API", "No key", "JSON/CSV/XML", "Varies", "Primary", "Eurozone expansion", "https://data-api.ecb.europa.eu/service"),
    SourceEntry("GDELT", "API/bulk", "No key", "JSON/CSV/RSS", "Near real time", "Secondary", "News volume/tone", "https://api.gdeltproject.org/api/v2"),
    SourceEntry("NewsAPI", "API", "API key", "JSON", "Near real time", "Secondary", "Article discovery", "https://newsapi.org/v2"),
    SourceEntry("Alpha Vantage", "API", "API key", "JSON/CSV", "Daily/intraday", "Market", "Prototype market/economic data", "https://www.alphavantage.co/query"),
    SourceEntry("Nasdaq Data Link", "API", "API key/subscription", "JSON/CSV/XML", "Varies", "Market", "Prices/alt data", "https://data.nasdaq.com/api/v3"),
    SourceEntry("Polygon", "API/WebSocket", "API key/subscription", "JSON/CSV", "Real time/historical", "Market", "Prices/events", "https://api.polygon.io"),
]


def registry_path(data_dir: Path) -> Path:
    return data_dir / "config" / "source_registry.json"


def init_source_registry(data_dir: Path) -> list[dict[str, Any]]:
    records = [asdict(source) for source in DEFAULT_SOURCES]
    write_json(registry_path(data_dir), records)
    return records


def load_source_registry(data_dir: Path) -> list[dict[str, Any]]:
    return read_json(registry_path(data_dir), default=[]) or []

