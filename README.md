# Macro Dashboard Mixed-Source Data Architecture

This project implements a runnable scaffold for a U.S. multi-asset macro dashboard data layer.

It supports:

- Source registry and lakehouse-style folders (`raw`, `bronze`, `silver`, `gold`)
- API adapters for FRED, Treasury FiscalData, BEA, BLS, Census, World Bank, SEC EDGAR, GDELT, NewsAPI, Alpha Vantage, Nasdaq Data Link, and Polygon
- User file ingestion for CSV and JSON
- Common machine-readable contracts for time series, events, chart specs, documents, and LLM extractions
- Validation, freshness checks, 3-month/12-month transformations, z-scores, percentiles, and acceleration tags
- Derived indicators such as `10Y - 2Y`, `10Y - 3M`, headline-core inflation gap, real policy rate proxy, HY-IG spread gap, and growth-inflation momentum
- Bucket scoring and dominant regime classification
- Chart spec generation for downstream dashboard rendering

## Quick Start

```bash
python3 -m macro_dashboard.cli init
python3 -m macro_dashboard.cli ingest-user-file path/to/file.csv --source "User Upload" --bucket Growth
python3 -m macro_dashboard.cli build
python3 -m macro_dashboard.cli report
```

The default data directory is `./data`. Override it with `--data-dir`.

## API Examples

FRED requires an API key:

```bash
export FRED_API_KEY="..."
python3 -m macro_dashboard.cli ingest-fred UNRATE --bucket Labor
```

Treasury FiscalData does not require a key:

```bash
python3 -m macro_dashboard.cli ingest-treasury \
  /v2/accounting/od/debt_to_penny \
  --fields record_date,tot_pub_debt_out_amt \
  --date-field record_date \
  --value-field tot_pub_debt_out_amt \
  --series-id TREASURY:DEBT_TO_PENNY \
  --series-name "Debt to the Penny" \
  --bucket "Financial conditions"
```

GDELT document timeline:

```bash
python3 -m macro_dashboard.cli ingest-gdelt "inflation OR recession" --theme macro_pressure
```

## How to Run the Dashboard

The project features a full-stack visual dashboard, consisting of a Python FastAPI backend and a Next.js React frontend.

**1. Start the Backend**
Open a terminal in the project root and activate the virtual environment:
```bash
source .venv/bin/activate
uvicorn macro_dashboard.main:app --reload --port 8000
```

**2. Start the Frontend**
Open a second terminal window, navigate to the frontend directory, and start the development server:
```bash
cd frontend
npm run dev
```

**3. View the UI**
Navigate to [http://localhost:3000](http://localhost:3000) in your web browser to view the live dashboard.

## Outputs

Important generated artifacts:

- `data/config/source_registry.json`
- `data/silver/validated_time_series/*.json`
- `data/gold/indicators/*.json`
- `data/gold/derived_series/*.json`
- `data/gold/chart_specs/*.json`
- `data/gold/regime_scores/regime_report.json`

## Design Notes

The implementation is intentionally conservative:

- Raw API responses are stored unchanged before normalization.
- Official data is preferred over aggregators.
- News and LLM-derived data are treated as soft indicators, not replacements for hard macro data.
- Missing API keys do not break the pipeline; adapters fail with explicit, machine-readable errors.
- No numeric data is invented.

