import json
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
from typing import Optional

app = FastAPI(title="Macro Analysis Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data_demo")

@lru_cache(maxsize=32)
def get_dynamic_snapshot(as_of: str):
    from macro_dashboard.pipeline import generate_dynamic_snapshot
    try:
        return generate_dynamic_snapshot(DATA_DIR, as_of)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format or data error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/regime")
def get_current_regime(as_of: Optional[str] = Query(None, description="YYYY-MM-DD")):
    if as_of:
        snapshot = get_dynamic_snapshot(as_of)
        return snapshot["regime"]

    regime_path = DATA_DIR / "gold" / "regime_scores" / "regime_report.json"
    if regime_path.exists():
        with open(regime_path, "r") as f:
            return json.load(f)
    return {
        "regime_name": "Pending",
        "conviction": "Low",
        "plain_english_explanation": "Awaiting data pipeline execution."
    }

@app.get("/api/charts")
def get_charts(as_of: Optional[str] = Query(None, description="YYYY-MM-DD")):
    if as_of:
        snapshot = get_dynamic_snapshot(as_of)
        return {"charts": snapshot["charts"]}

    charts_dir = DATA_DIR / "gold" / "chart_specs"
    charts = []
    if charts_dir.exists():
        for file in charts_dir.glob("*.json"):
            with open(file, "r") as f:
                charts.append(json.load(f))
    return {"charts": charts}

@app.get("/api/series")
def get_all_series(as_of: Optional[str] = Query(None, description="YYYY-MM-DD")):
    if as_of:
        snapshot = get_dynamic_snapshot(as_of)
        series_list = []
        for s in snapshot["series"]:
            data = s.copy()
            if "observations" in data:
                del data["observations"]
            series_list.append(data)
        return {"series": series_list}

    indicators_dir = DATA_DIR / "gold" / "indicators"
    derived_dir = DATA_DIR / "gold" / "derived_series"
    series_list = []
    
    for d in [indicators_dir, derived_dir]:
        if d.exists():
            for file in d.glob("*.json"):
                with open(file, "r") as f:
                    data = json.load(f)
                    if "observations" in data:
                        del data["observations"]
                    series_list.append(data)
    
    return {"series": series_list}

@app.get("/api/series/{series_id}")
def get_series(series_id: str, as_of: Optional[str] = Query(None, description="YYYY-MM-DD")):
    if as_of:
        snapshot = get_dynamic_snapshot(as_of)
        for s in snapshot["series"]:
            if s["series_id"] == series_id:
                return s
        raise HTTPException(status_code=404, detail="Series not found")

    safe_id = series_id.replace(":", "_").replace("/", "_")
    
    indicator_path = DATA_DIR / "gold" / "indicators" / f"{safe_id}.json"
    if indicator_path.exists():
        with open(indicator_path, "r") as f:
            return json.load(f)
            
    derived_path = DATA_DIR / "gold" / "derived_series" / f"{safe_id}.json"
    if derived_path.exists():
        with open(derived_path, "r") as f:
            return json.load(f)
            
    raise HTTPException(status_code=404, detail="Series not found")
