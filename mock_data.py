import json
import random
from datetime import date, timedelta
from pathlib import Path
from macro_dashboard.contracts import TimeSeriesContract, Observation
from macro_dashboard.pipeline import save_time_series, build_gold_outputs

DATA_DIR = Path("data_demo")

# Base parameters for generating realistic-looking data
MOCK_PARAMS = {
    "FRED:GDPC1": {"start": 20000, "trend": 0.005, "volatility": 100, "freq": "monthly"},
    "FRED:INDPRO": {"start": 100, "trend": 0.001, "volatility": 1, "freq": "monthly"},
    "FRED:RSAFS": {"start": 500000, "trend": 0.003, "volatility": 2000, "freq": "monthly"},
    "FRED:UMCSENT": {"start": 70, "trend": 0, "volatility": 2, "freq": "monthly"},
    "FRED:CPIAUCSL": {"start": 280, "trend": 0.002, "volatility": 0.5, "freq": "monthly"},
    "FRED:CPILFESL": {"start": 290, "trend": 0.002, "volatility": 0.3, "freq": "monthly"},
    "FRED:PCEPILFE": {"start": 120, "trend": 0.002, "volatility": 0.2, "freq": "monthly"},
    "FRED:T10YIE": {"start": 2.2, "trend": 0, "volatility": 0.05, "freq": "daily"},
    "FRED:PAYEMS": {"start": 150000, "trend": 0.001, "volatility": 200, "freq": "monthly"},
    "FRED:UNRATE": {"start": 4.0, "trend": 0, "volatility": 0.1, "freq": "monthly"},
    "FRED:ICSA": {"start": 220000, "trend": 0, "volatility": 5000, "freq": "weekly"},
    "FRED:EFFR": {"start": 5.3, "trend": 0, "volatility": 0.01, "freq": "daily"},
    "FRED:DGS2": {"start": 4.5, "trend": 0, "volatility": 0.05, "freq": "daily"},
    "FRED:DGS10": {"start": 4.2, "trend": 0, "volatility": 0.04, "freq": "daily"},
    "FRED:WALCL": {"start": 8000000, "trend": -0.001, "volatility": 10000, "freq": "weekly"},
    "FRED:WRESBAL": {"start": 3000000, "trend": -0.002, "volatility": 20000, "freq": "weekly"},
    "FRED:DTWEXBGS": {"start": 120, "trend": 0, "volatility": 0.5, "freq": "daily"},
    "FRED:DCOILWTICO": {"start": 80, "trend": 0, "volatility": 1, "freq": "daily"},
    "FRED:BAMLC0A0CM": {"start": 1.2, "trend": 0, "volatility": 0.02, "freq": "daily"},
    "FRED:BAMLH0A0HYM2": {"start": 4.5, "trend": 0, "volatility": 0.08, "freq": "daily"},
    "FRED:TB3MS": {"start": 5.4, "trend": 0, "volatility": 0.01, "freq": "daily"},
    "FRED:VIXCLS": {"start": 15.0, "trend": 0, "volatility": 1.5, "freq": "daily"},
}

def generate_mock_series():
    manifest_path = DATA_DIR / "config" / "indicator_manifest.json"
    if not manifest_path.exists():
        print(f"Manifest not found at {manifest_path}")
        return
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    # Ensure missing dependencies are added (e.g. TB3MS, VIXCLS are used in derived/charts)
    extras = [
        {"series_id": "FRED:TB3MS", "series_name": "3-Month Treasury", "bucket": "Financial conditions", "source": "FRED"},
        {"series_id": "FRED:VIXCLS", "series_name": "VIX", "bucket": "Financial conditions", "source": "FRED"}
    ]
    manifest.extend(extras)
        
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * 6) # 6 years of data
    
    for item in manifest:
        series_id = item["series_id"]
        params = MOCK_PARAMS.get(series_id, {"start": 100, "trend": 0, "volatility": 1, "freq": "monthly"})
        
        observations = []
        current_date = start_date
        current_value = params["start"]
        
        while current_date <= end_date:
            observations.append(Observation(
                date=current_date.strftime("%Y-%m-%d"),
                value=current_value
            ))
            
            # Step forward
            if params["freq"] == "daily":
                current_date += timedelta(days=1)
                # skip weekends
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=2)
            elif params["freq"] == "weekly":
                current_date += timedelta(days=7)
            else: # monthly
                # Add a month
                month = current_date.month % 12 + 1
                year = current_date.year + (current_date.month // 12)
                current_date = date(year, month, 1)
                
            # Random walk with drift
            drift = current_value * params["trend"]
            shock = random.gauss(0, params["volatility"])
            current_value = max(0.1, current_value + drift + shock)
            
        contract = TimeSeriesContract(
            series_id=series_id,
            series_name=item["series_name"],
            bucket=item.get("bucket", "Unknown"),
            source=item.get("source", "FRED"),
            observations=observations
        )
        
        save_time_series(DATA_DIR, contract)
        print(f"Generated mock data for {series_id}")
        
    print("\nBuilding gold outputs...")
    result = build_gold_outputs(DATA_DIR)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    generate_mock_series()
