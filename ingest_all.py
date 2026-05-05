import json
import os
import argparse
from pathlib import Path
from macro_dashboard.adapters import ingest_fred
from macro_dashboard.pipeline import save_time_series, build_gold_outputs

DATA_DIR = Path("data_demo")

def load_env():
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip()

def main():
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="FRED API Key")
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("FRED_API_KEY")
    if not api_key:
        print("Error: FRED_API_KEY not provided. Pass --api-key or set FRED_API_KEY environment variable.")
        return
        
    manifest_path = DATA_DIR / "config" / "indicator_manifest.json"
    if not manifest_path.exists():
        print(f"Manifest not found at {manifest_path}")
        return
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    # Ensure missing dependencies are added
    extras = [
        {"series_id": "FRED:TB3MS", "series_name": "3-Month Treasury", "bucket": "Financial conditions", "source": "FRED"},
        {"series_id": "FRED:VIXCLS", "series_name": "VIX", "bucket": "Financial conditions", "source": "FRED"}
    ]
    manifest.extend(extras)
    
    success_count = 0
    for item in manifest:
        if not item["series_id"].startswith("FRED:"):
            continue
            
        fred_id = item["series_id"].replace("FRED:", "")
        try:
            print(f"Fetching {fred_id}...")
            # We fetch last 5-10 years to ensure rolling z-scores can be calculated
            contract = ingest_fred(
                data_dir=DATA_DIR,
                series_id=fred_id,
                bucket=item.get("bucket", "Unknown"),
                series_name=item.get("series_name"),
                api_key=api_key,
                observation_start="2015-01-01"
            )
            save_time_series(DATA_DIR, contract)
            success_count += 1
        except Exception as e:
            print(f"Failed to fetch {fred_id}: {e}")
            
    print(f"\nSuccessfully fetched {success_count} series from FRED.")
    
    print("\nBuilding gold outputs...")
    result = build_gold_outputs(DATA_DIR)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
