from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .adapters import (
    AdapterError,
    build_placeholder_api_series,
    ingest_fred,
    ingest_gdelt_doc,
    ingest_treasury,
    ingest_user_csv,
)
from .io_utils import ensure_dirs, read_json, write_json
from .llm_text import aggregate_sentiment_indexes, extraction_template_from_document, save_llm_extraction
from .pipeline import build_gold_outputs, initialize_project, save_time_series
from .registry import load_source_registry


def main() -> None:
    data_dir_parent = argparse.ArgumentParser(add_help=False)
    data_dir_parent.add_argument("--data-dir", default="data", help="Data directory")
    parser = argparse.ArgumentParser(description="Macro dashboard mixed-source data pipeline")
    parser.add_argument("--data-dir", default="data", help="Data directory")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", parents=[data_dir_parent], help="Create data folders and source registry")

    fred = sub.add_parser("ingest-fred", parents=[data_dir_parent], help="Ingest FRED series observations")
    fred.add_argument("series_id")
    fred.add_argument("--bucket", required=True)
    fred.add_argument("--series-name")
    fred.add_argument("--start")
    fred.add_argument("--api-key")

    user = sub.add_parser("ingest-user-file", parents=[data_dir_parent], help="Ingest a CSV user file")
    user.add_argument("path")
    user.add_argument("--source", required=True)
    user.add_argument("--bucket", required=True)
    user.add_argument("--date-column")
    user.add_argument("--value-columns", nargs="*")

    treasury = sub.add_parser("ingest-treasury", parents=[data_dir_parent], help="Ingest Treasury FiscalData endpoint")
    treasury.add_argument("endpoint")
    treasury.add_argument("--fields", required=True, help="Comma-separated API fields")
    treasury.add_argument("--date-field", required=True)
    treasury.add_argument("--value-field", required=True)
    treasury.add_argument("--series-id", required=True)
    treasury.add_argument("--series-name", required=True)
    treasury.add_argument("--bucket", required=True)
    treasury.add_argument("--filter")

    gdelt = sub.add_parser("ingest-gdelt", parents=[data_dir_parent], help="Ingest GDELT DOC articles as document contracts")
    gdelt.add_argument("query")
    gdelt.add_argument("--theme", required=True)
    gdelt.add_argument("--max-records", type=int, default=75)

    placeholder = sub.add_parser("register-placeholder-series", parents=[data_dir_parent], help="Register an unavailable/auth-gated source explicitly")
    placeholder.add_argument("--source", required=True)
    placeholder.add_argument("--series-id", required=True)
    placeholder.add_argument("--series-name", required=True)
    placeholder.add_argument("--bucket", required=True)
    placeholder.add_argument("--reason", required=True)

    template = sub.add_parser("llm-template", parents=[data_dir_parent], help="Create an LLM extraction template from a document contract")
    template.add_argument("document_json")

    extraction = sub.add_parser("save-llm-extraction", parents=[data_dir_parent], help="Validate and save an LLM extraction JSON file")
    extraction.add_argument("extraction_json")

    sub.add_parser("aggregate-sentiment", parents=[data_dir_parent], help="Aggregate saved LLM extractions into sentiment indexes")
    sub.add_parser("build", parents=[data_dir_parent], help="Build gold indicators, derived series, chart specs, and regime report")
    sub.add_parser("report", parents=[data_dir_parent], help="Print the latest regime report")
    sub.add_parser("sources", parents=[data_dir_parent], help="Print source registry")

    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    ensure_dirs(data_dir)

    try:
        if args.command == "init":
            initialize_project(data_dir)
            print(f"Initialized macro dashboard data directory at {data_dir.resolve()}")

        elif args.command == "ingest-fred":
            contract = ingest_fred(
                data_dir=data_dir,
                series_id=args.series_id,
                bucket=args.bucket,
                series_name=args.series_name,
                api_key=args.api_key,
                observation_start=args.start,
            )
            path = save_time_series(data_dir, contract)
            print(f"Saved {contract.series_id} to {path}")

        elif args.command == "ingest-user-file":
            contracts = ingest_user_csv(
                data_dir=data_dir,
                csv_path=Path(args.path),
                source=args.source,
                bucket=args.bucket,
                date_column=args.date_column,
                value_columns=args.value_columns,
            )
            for contract in contracts:
                path = save_time_series(data_dir, contract)
                print(f"Saved {contract.series_id} to {path}")
            print(f"Ingested {len(contracts)} series")

        elif args.command == "ingest-treasury":
            contract = ingest_treasury(
                data_dir=data_dir,
                endpoint=args.endpoint,
                fields=[field.strip() for field in args.fields.split(",")],
                date_field=args.date_field,
                value_field=args.value_field,
                series_id=args.series_id,
                series_name=args.series_name,
                bucket=args.bucket,
                filters=args.filter,
            )
            path = save_time_series(data_dir, contract)
            print(f"Saved {contract.series_id} to {path}")

        elif args.command == "ingest-gdelt":
            documents = ingest_gdelt_doc(data_dir, args.query, args.theme, args.max_records)
            out_dir = data_dir / "silver" / "validated_text_extracts" / "documents"
            out_dir.mkdir(parents=True, exist_ok=True)
            for doc in documents:
                write_json(out_dir / f"{doc.document_id}.json", doc.to_dict())
            print(f"Saved {len(documents)} GDELT document contracts")

        elif args.command == "register-placeholder-series":
            contract = build_placeholder_api_series(data_dir, args.source, args.series_id, args.series_name, args.bucket, args.reason)
            path = save_time_series(data_dir, contract)
            print(f"Saved placeholder {contract.series_id} to {path}")

        elif args.command == "llm-template":
            document = read_json(Path(args.document_json))
            print(json.dumps(extraction_template_from_document(document), indent=2, sort_keys=True))

        elif args.command == "save-llm-extraction":
            payload = read_json(Path(args.extraction_json))
            path = save_llm_extraction(data_dir, payload)
            print(f"Saved LLM extraction to {path}")

        elif args.command == "aggregate-sentiment":
            records = aggregate_sentiment_indexes(data_dir)
            print(f"Aggregated {len(records)} sentiment index rows")

        elif args.command == "build":
            result = build_gold_outputs(data_dir)
            print(json.dumps(result, indent=2, sort_keys=True))

        elif args.command == "report":
            report = read_json(data_dir / "gold" / "regime_scores" / "regime_report.json", default={})
            print(json.dumps(report, indent=2, sort_keys=True))

        elif args.command == "sources":
            print(json.dumps(load_source_registry(data_dir), indent=2, sort_keys=True))

    except AdapterError as exc:
        print(f"Adapter error: {exc}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
