from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .contracts import ChartSpec, Observation, TimeSeriesContract, TransformSummary, ValidationStatus
from .io_utils import ensure_dirs, read_json, write_json
from .registry import init_source_registry


SERIES_STALENESS_DAYS = {
    "daily": 10,
    "weekly": 21,
    "monthly": 75,
    "quarterly": 150,
    "annual": 550,
    "unknown": 180,
}


def initialize_project(data_dir: Path) -> None:
    ensure_dirs(data_dir)
    init_source_registry(data_dir)
    write_json(data_dir / "config" / "indicator_manifest.json", default_indicator_manifest())


def save_time_series(data_dir: Path, contract: TimeSeriesContract, layer: str = "silver/validated_time_series") -> Path:
    prepared = prepare_time_series(contract)
    safe = prepared.series_id.replace(":", "_").replace("/", "_")
    path = data_dir / layer / f"{safe}.json"
    write_json(path, prepared.to_dict())
    return path


def load_time_series_dir(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [read_json(file) for file in sorted(path.glob("*.json"))]


def prepare_time_series(contract: TimeSeriesContract, as_of: date | None = None) -> TimeSeriesContract:
    as_of = as_of or date.today()
    observations = sorted(contract.observations, key=lambda obs: obs.date)
    for obs in observations:
        obs.is_latest = False
    non_null = [obs for obs in observations if obs.value is not None]
    if non_null:
        non_null[-1].is_latest = True
    frequency = infer_frequency([obs.date for obs in non_null])
    contract.frequency = frequency
    contract.observations = observations
    contract.validation = validate_observations(observations, frequency, as_of)
    contract.transforms = compute_transforms(non_null, frequency)
    return contract


def infer_frequency(dates: list[str]) -> str:
    if len(dates) < 3:
        return "unknown"
    parsed = [_to_date(item) for item in dates[-10:]]
    parsed = [item for item in parsed if item]
    if len(parsed) < 3:
        return "unknown"
    gaps = [(parsed[i] - parsed[i - 1]).days for i in range(1, len(parsed))]
    avg_gap = mean(gaps)
    if avg_gap <= 3:
        return "daily"
    if avg_gap <= 10:
        return "weekly"
    if avg_gap <= 45:
        return "monthly"
    if avg_gap <= 120:
        return "quarterly"
    return "annual"


def validate_observations(observations: list[Observation], frequency: str, as_of: date) -> ValidationStatus:
    issues = []
    if not observations:
        return ValidationStatus(status="unusable", latest_observation_date=None, issues=["No observations"])
    non_null = [obs for obs in observations if obs.value is not None]
    if not non_null:
        return ValidationStatus(status="unusable", latest_observation_date=None, issues=["No numeric observations"])
    latest = non_null[-1]
    latest_date = _to_date(latest.date)
    missing_recent = sum(1 for obs in observations[-12:] if obs.value is None)
    if missing_recent:
        issues.append(f"{missing_recent} missing values in latest 12 observations")
    if len(non_null) < _minimum_history(frequency):
        issues.append("Truncated history")
    stale = False
    if latest_date:
        allowed_lag = SERIES_STALENESS_DAYS.get(frequency, SERIES_STALENESS_DAYS["unknown"])
        stale = (as_of - latest_date).days > allowed_lag
        if stale:
            issues.append(f"Latest observation is older than expected for {frequency} data")
    status = "usable"
    if stale:
        status = "stale"
    if any(issue == "Truncated history" for issue in issues):
        status = "truncated" if status == "usable" else status
    return ValidationStatus(
        status=status,
        latest_observation_date=latest.date,
        missing_recent_values=missing_recent,
        stale=stale,
        issues=issues,
    )


def compute_transforms(observations: list[Observation], frequency: str) -> TransformSummary:
    values = [(obs.date, obs.value) for obs in observations if obs.value is not None]
    if not values:
        return TransformSummary()
    step_3m = {"daily": 63, "weekly": 13, "monthly": 3, "quarterly": 1, "annual": 1}.get(frequency, 3)
    step_12m = {"daily": 252, "weekly": 52, "monthly": 12, "quarterly": 4, "annual": 1}.get(frequency, 12)
    latest = values[-1][1]
    three = _change(values, step_3m)
    twelve = _change(values, step_12m)
    history_5y = [v for _, v in values[-_window_count(frequency, 5) :]]
    history_10y = [v for _, v in values[-_window_count(frequency, 10) :]]
    z = None
    if len(history_5y) >= 6:
        sd = pstdev(history_5y)
        z = (latest - mean(history_5y)) / sd if sd else 0.0
    pct = None
    if len(history_10y) >= 6:
        pct = sum(1 for item in history_10y if item <= latest) / len(history_10y)
    acceleration = _acceleration(values, step_3m)
    return TransformSummary(
        three_month_change=three,
        twelve_month_change=twelve,
        z_score_5y=z,
        percentile_10y=pct,
        acceleration=acceleration,
    )


def build_gold_outputs(data_dir: Path) -> dict[str, Any]:
    ensure_dirs(data_dir)
    series_records = load_time_series_dir(data_dir / "silver" / "validated_time_series")
    for record in series_records:
        write_json(data_dir / "gold" / "indicators" / f"{_safe_id(record['series_id'])}.json", record)
    derived = compute_derived_series(series_records)
    for record in derived:
        write_json(data_dir / "gold" / "derived_series" / f"{_safe_id(record['series_id'])}.json", record)
    all_records = series_records + derived
    chart_specs = generate_chart_specs(all_records)
    for spec in chart_specs:
        write_json(data_dir / "gold" / "chart_specs" / f"{spec['chart_id']}.json", spec)
    report = classify_regime(all_records)
    
    # Calculate transition probabilities
    from .probabilities import calculate_regime_probabilities
    report["transition_probabilities"] = calculate_regime_probabilities(all_records, report.get("bucket_reads", {}))
    
    write_json(data_dir / "gold" / "regime_scores" / "regime_report.json", report)
    return {"series": len(series_records), "derived": len(derived), "chart_specs": len(chart_specs), "regime": report}


def compute_derived_series(series_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {record["series_id"]: record for record in series_records}
    derived_specs = [
        ("DERIVED:10Y_MINUS_2Y", "10Y minus 2Y yield curve", "Financial conditions", "FRED:DGS10", "FRED:DGS2", "subtract"),
        ("DERIVED:10Y_MINUS_3M", "10Y minus 3M yield curve", "Financial conditions", "FRED:DGS10", "FRED:TB3MS", "subtract"),
        ("DERIVED:HEADLINE_MINUS_CORE_CPI", "Headline CPI minus Core CPI", "Inflation", "FRED:CPIAUCSL", "FRED:CPILFESL", "subtract_yoy"),
        ("DERIVED:REAL_POLICY_RATE_PROXY", "Real policy rate proxy", "Financial conditions", "FRED:EFFR", "FRED:PCEPILFE", "subtract_yoy"),
        ("DERIVED:HY_MINUS_IG_OAS", "High yield minus investment grade OAS", "Credit", "FRED:BAMLH0A0HYM2", "FRED:BAMLC0A0CM", "subtract"),
        ("DERIVED:GROWTH_MINUS_INFLATION_MOMENTUM", "Growth minus inflation momentum", "Growth", "FRED:INDPRO", "FRED:CPILFESL", "zscore_gap"),
        ("DERIVED:BBD_MINUS_VIX", "VIX vs BBD (Uncertainty Gap)", "Financial conditions", "FRED:USEPUINDXD", "FRED:VIXCLS", "zscore_gap"),
    ]
    out = []
    for series_id, name, bucket, left, right, operation in derived_specs:
        if left not in by_id or right not in by_id:
            continue
        contract = _derive_pair(series_id, name, bucket, by_id[left], by_id[right], operation)
        if contract:
            out.append(contract)
    return out


def generate_chart_specs(series_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = [
        "FRED:GDPC1",
        "FRED:INDPRO",
        "FRED:RSAFS",
        "FRED:UMCSENT",
        "FRED:CPIAUCSL",
        "FRED:CPILFESL",
        "FRED:PCEPILFE",
        "FRED:T10YIE",
        "FRED:PAYEMS",
        "FRED:UNRATE",
        "FRED:ICSA",
        "FRED:EFFR",
        "FRED:DGS2",
        "FRED:DGS10",
        "DERIVED:10Y_MINUS_2Y",
        "FRED:VIXCLS",
        "FRED:BAMLH0A0HYM2",
        "FRED:DTWEXBGS",
        "FRED:DCOILWTICO",
    ]
    by_id = {record["series_id"]: record for record in series_records}
    chosen = [by_id[item] for item in priority if item in by_id]
    if len(chosen) < 15:
        for record in series_records:
            if record not in chosen:
                chosen.append(record)
            if len(chosen) >= 15:
                break
    specs = []
    for record in chosen[:15]:
        transforms = record.get("transforms", {})
        consistency = _trend_consistency(transforms)
        spec = ChartSpec(
            chart_id=_safe_id(record["series_id"]).lower(),
            title=record.get("series_name") or record["series_id"],
            bucket=record.get("bucket", "Unknown"),
            x_axis="date",
            y_axis="indicator value",
            series=[record["series_id"]],
            latest_callout=True,
            caption=_caption_for_bucket(record.get("bucket", ""), record.get("series_name", record["series_id"])),
            regime_implication=_regime_implication(record.get("bucket", ""), transforms),
            trend_consistency=consistency,
        )
        specs.append(spec.to_dict())
    return specs


def classify_regime(series_records: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in series_records:
        buckets[record.get("bucket", "Unknown")].append(record)
    bucket_reads = {}
    for bucket, records in buckets.items():
        bucket_reads[bucket] = _bucket_read(bucket, records)
    growth = bucket_reads.get("Growth", {}).get("direction", "Mixed")
    inflation = bucket_reads.get("Inflation", {}).get("direction", "Mixed")
    financial = bucket_reads.get("Financial conditions", {}).get("direction", "Mixed")
    credit = bucket_reads.get("Credit", {}).get("direction", "Mixed")
    if growth in {"Accelerating", "Stable"} and inflation == "Decelerating" and credit != "Deteriorating":
        regime = "Disinflationary soft landing"
    elif growth == "Accelerating" and inflation == "Accelerating":
        regime = "Reflationary acceleration"
    elif growth == "Decelerating" and inflation == "Accelerating":
        regime = "Stagflationary stall"
    elif growth == "Decelerating" and inflation == "Decelerating":
        regime = "Growth scare"
    elif financial == "Loosening" and growth in {"Stable", "Mixed"}:
        regime = "Policy-driven liquidity rally"
    else:
        regime = "Late-cycle reflationary slowdown"
    convictions = [read.get("conviction_score", 0.0) for read in bucket_reads.values()]
    avg_conviction = mean(convictions) if convictions else 0.0
    conviction = "High" if avg_conviction >= 0.66 else "Medium" if avg_conviction >= 0.40 else "Low"
    return {
        "regime_name": regime,
        "conviction": conviction,
        "plain_english_explanation": _regime_explanation(regime),
        "bucket_reads": bucket_reads,
        "supporting_indicators": _top_indicators(series_records, supportive=True),
        "challenging_indicators": _top_indicators(series_records, supportive=False),
        "label_shift_triggers": [
            "Inflation scare if core inflation, breakevens, oil, and wages accelerate while growth remains stable.",
            "Growth scare if claims rise, PMIs fall, the curve bull-steepens, credit spreads widen, and equities weaken.",
            "Stagflationary stall if growth weakens while oil/headline inflation and inflation expectations rise.",
            "Policy-driven liquidity rally if real yields fall, financial conditions ease, credit spreads tighten, and risk assets rally.",
        ],
    }


def default_indicator_manifest() -> list[dict[str, str]]:
    return [
        {"series_id": "FRED:GDPC1", "series_name": "Real GDP", "bucket": "Growth", "source": "FRED/BEA"},
        {"series_id": "FRED:INDPRO", "series_name": "Industrial Production", "bucket": "Growth", "source": "FRED/Fed"},
        {"series_id": "FRED:RSAFS", "series_name": "Retail Sales", "bucket": "Growth", "source": "FRED/Census"},
        {"series_id": "FRED:UMCSENT", "series_name": "Consumer Sentiment", "bucket": "Growth", "source": "FRED/University of Michigan"},
        {"series_id": "FRED:CPIAUCSL", "series_name": "CPI", "bucket": "Inflation", "source": "FRED/BLS"},
        {"series_id": "FRED:CPILFESL", "series_name": "Core CPI", "bucket": "Inflation", "source": "FRED/BLS"},
        {"series_id": "FRED:PCEPILFE", "series_name": "Core PCE Price Index", "bucket": "Inflation", "source": "FRED/BEA"},
        {"series_id": "FRED:T10YIE", "series_name": "10Y Breakeven Inflation", "bucket": "Inflation", "source": "FRED"},
        {"series_id": "FRED:PAYEMS", "series_name": "Nonfarm Payrolls", "bucket": "Labor", "source": "FRED/BLS"},
        {"series_id": "FRED:UNRATE", "series_name": "Unemployment Rate", "bucket": "Labor", "source": "FRED/BLS"},
        {"series_id": "FRED:ICSA", "series_name": "Initial Claims", "bucket": "Labor", "source": "FRED/DOL"},
        {"series_id": "FRED:EFFR", "series_name": "Effective Fed Funds Rate", "bucket": "Financial conditions", "source": "FRED/Fed"},
        {"series_id": "FRED:DGS2", "series_name": "2Y Treasury Yield", "bucket": "Financial conditions", "source": "FRED/Treasury"},
        {"series_id": "FRED:DGS10", "series_name": "10Y Treasury Yield", "bucket": "Financial conditions", "source": "FRED/Treasury"},
        {"series_id": "FRED:WALCL", "series_name": "Fed Balance Sheet Assets", "bucket": "Liquidity", "source": "FRED/Fed"},
        {"series_id": "FRED:WRESBAL", "series_name": "Bank Reserves", "bucket": "Liquidity", "source": "FRED/Fed"},
        {"series_id": "FRED:DTWEXBGS", "series_name": "Broad Dollar Index", "bucket": "External / FX", "source": "FRED/Fed"},
        {"series_id": "FRED:DCOILWTICO", "series_name": "WTI Crude Oil", "bucket": "External / FX", "source": "FRED/EIA"},
        {"series_id": "FRED:BAMLC0A0CM", "series_name": "Investment Grade OAS", "bucket": "Credit", "source": "FRED/ICE"},
        {"series_id": "FRED:BAMLH0A0HYM2", "series_name": "High Yield OAS", "bucket": "Credit", "source": "FRED/ICE"},
    ]


def _derive_pair(series_id: str, name: str, bucket: str, left: dict[str, Any], right: dict[str, Any], operation: str) -> dict[str, Any] | None:
    left_obs = {obs["date"]: obs["value"] for obs in left.get("observations", []) if obs.get("value") is not None}
    right_obs = {obs["date"]: obs["value"] for obs in right.get("observations", []) if obs.get("value") is not None}
    all_dates = sorted(set(left_obs) & set(right_obs))
    dates = all_dates
    if operation in {"subtract_yoy", "zscore_gap"}:
        dates = all_dates[12:] if len(all_dates) > 12 else []
    observations = []
    for dt in dates:
        if operation == "subtract":
            value = left_obs[dt] - right_obs[dt]
        elif operation == "subtract_yoy":
            idx = all_dates.index(dt)
            prev = all_dates[idx - 12]
            left_yoy = left_obs[dt] - left_obs[prev]
            right_yoy = right_obs[dt] - right_obs[prev]
            value = left_yoy - right_yoy
        elif operation == "zscore_gap":
            value = _latest_z_gap(left_obs, right_obs, dt)
        else:
            value = None
        observations.append(Observation(date=dt, value=value))
    if not observations:
        return None
    contract = TimeSeriesContract(series_id=series_id, series_name=name, bucket=bucket, source="Derived", observations=observations)
    return prepare_time_series(contract).to_dict()


def _latest_z_gap(left: dict[str, float], right: dict[str, float], dt: str) -> float | None:
    l_dates = sorted([key for key in left if key <= dt])[-60:]
    r_dates = sorted([key for key in right if key <= dt])[-60:]
    if len(l_dates) < 12 or len(r_dates) < 12:
        return None
    l_vals = [left[key] for key in l_dates]
    r_vals = [right[key] for key in r_dates]
    l_sd = pstdev(l_vals)
    r_sd = pstdev(r_vals)
    l_z = (left[dt] - mean(l_vals)) / l_sd if l_sd else 0.0
    r_z = (right[dt] - mean(r_vals)) / r_sd if r_sd else 0.0
    return l_z - r_z


def _change(values: list[tuple[str, float]], periods: int) -> float | None:
    if len(values) <= periods:
        return None
    return values[-1][1] - values[-1 - periods][1]


def _acceleration(values: list[tuple[str, float]], periods: int) -> str:
    if len(values) <= periods * 2:
        return "unavailable"
    recent = values[-1][1] - values[-1 - periods][1]
    prior = values[-1 - periods][1] - values[-1 - periods * 2][1]
    if abs(recent - prior) < 1e-9:
        return "stable"
    if abs(recent) < 1e-9 and abs(prior) < 1e-9:
        return "stable"
    return "accelerating" if recent > prior else "decelerating"


def _window_count(frequency: str, years: int) -> int:
    return {"daily": 252, "weekly": 52, "monthly": 12, "quarterly": 4, "annual": 1}.get(frequency, 12) * years


def _minimum_history(frequency: str) -> int:
    return {"daily": 252, "weekly": 52, "monthly": 24, "quarterly": 8, "annual": 5}.get(frequency, 12)


def _to_date(value: str) -> date | None:
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _safe_id(series_id: str) -> str:
    return series_id.replace(":", "_").replace("/", "_")


def _trend_consistency(transforms: dict[str, Any]) -> str:
    three = transforms.get("three_month_change")
    twelve = transforms.get("twelve_month_change")
    if three is None or twelve is None:
        return "Insufficient history to compare latest trend with prior trend"
    if three == 0:
        return "Latest trend is stable relative to the prior trend"
    if (three > 0 and twelve > 0) or (three < 0 and twelve < 0):
        return "Latest trend is consistent with the prior trend"
    return "Latest trend diverges from the prior trend"


def _caption_for_bucket(bucket: str, series_name: str) -> str:
    captions = {
        "Growth": "Shows real-activity momentum and whether hard data confirms or challenges the expansion.",
        "Inflation": "Shows underlying price pressure and whether disinflation is durable.",
        "Labor": "Shows whether labor conditions are cooling gradually or deteriorating abruptly.",
        "Financial conditions": "Shows market-implied policy, rate, and risk-appetite pressure.",
        "Liquidity": "Shows whether funding and balance-sheet conditions support risk-taking.",
        "External / FX": "Shows dollar, commodity, and external shock pressure.",
        "Credit": "Shows whether macro stress is becoming balance-sheet stress.",
    }
    return captions.get(bucket, f"Tracks {series_name} as an input to regime classification.")


def _regime_implication(bucket: str, transforms: dict[str, Any]) -> str:
    acc = transforms.get("acceleration", "unavailable")
    if bucket == "Inflation":
        return "Accelerating inflation supports inflation scare or stagflation risk." if acc == "accelerating" else "Decelerating inflation supports disinflationary soft landing."
    if bucket == "Growth":
        return "Accelerating growth supports expansion or reflation." if acc == "accelerating" else "Decelerating growth supports slowdown or growth scare."
    if bucket == "Credit":
        return "Widening or accelerating credit stress challenges risk assets." if acc == "accelerating" else "Stable/tighter credit supports benign risk appetite."
    if bucket == "Financial conditions":
        return "Tighter financial conditions challenge valuations and credit." if acc == "accelerating" else "Easier financial conditions support liquidity-sensitive assets."
    return "Use with related bucket indicators to confirm or challenge the dominant regime."


def _bucket_read(bucket: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    accels = [record.get("transforms", {}).get("acceleration") for record in records]
    accels = [item for item in accels if item in {"accelerating", "decelerating", "stable"}]
    if not accels:
        direction = "Mixed"
        score = 0.0
    else:
        accelerating = accels.count("accelerating")
        decelerating = accels.count("decelerating")
        stable = accels.count("stable")
        score = max(accelerating, decelerating, stable) / len(accels)
        if score < 0.5:
            direction = "Mixed"
        elif accelerating >= decelerating and accelerating >= stable:
            direction = "Accelerating"
        elif decelerating >= accelerating and decelerating >= stable:
            direction = "Decelerating"
        else:
            direction = "Stable"
    if bucket == "Financial conditions":
        direction = {"Accelerating": "Tightening", "Decelerating": "Loosening"}.get(direction, direction)
    if bucket == "Credit":
        direction = {"Accelerating": "Deteriorating", "Decelerating": "Benign"}.get(direction, direction)
    conviction = "High" if score >= 0.66 else "Medium" if score >= 0.40 else "Low"
    return {
        "direction": direction,
        "conviction": conviction,
        "conviction_score": score,
        "key_indicators": [record.get("series_name") or record["series_id"] for record in records[:5]],
        "what_it_says": f"{bucket} indicators are {direction.lower()} with {conviction.lower()} conviction.",
        "supports_or_challenges_regime": "Used in aggregate regime score",
    }


def _top_indicators(records: list[dict[str, Any]], supportive: bool) -> list[str]:
    candidates = []
    for record in records:
        transforms = record.get("transforms", {})
        z = transforms.get("z_score_5y")
        if z is None:
            continue
        if supportive and abs(z) >= 0.75:
            candidates.append(f"{record.get('series_name', record['series_id'])}: z={z:.2f}")
        if not supportive and abs(z) < 0.25:
            candidates.append(f"{record.get('series_name', record['series_id'])}: muted/ambiguous z={z:.2f}")
    return candidates[:8]


def _regime_explanation(regime: str) -> str:
    explanations = {
        "Disinflationary soft landing": "Growth remains positive while inflation cools and credit stress stays contained.",
        "Reflationary acceleration": "Growth and inflation are both strengthening, usually favoring cyclicals and real assets while pressuring duration.",
        "Stagflationary stall": "Growth is weakening while inflation pressure rises, creating a difficult mix for equities, bonds, and policy.",
        "Growth scare": "Growth and inflation momentum are weakening, with markets likely focused on downside activity risk.",
        "Policy-driven liquidity rally": "Risk assets are supported more by easing financial conditions and liquidity than by strong macro fundamentals.",
        "Late-cycle reflationary slowdown": "The data are mixed: inflation or policy pressure remains relevant while growth momentum is no longer clearly accelerating.",
    }
    return explanations.get(regime, "The regime is inferred from bucket-level macro, liquidity, credit, and external indicators.")


def generate_dynamic_snapshot(data_dir: Path, as_of_str: str) -> dict[str, Any]:
    from datetime import date
    from .contracts import TimeSeriesContract
    from .probabilities import calculate_regime_probabilities

    as_of = date.fromisoformat(as_of_str)
    
    # 1. Load silver data
    raw_records = load_time_series_dir(data_dir / "silver" / "validated_time_series")
    
    processed_series = []
    for record in raw_records:
        # Filter observations up to as_of
        filtered_obs = [obs for obs in record.get("observations", []) if obs["date"] <= as_of_str]
        record["observations"] = filtered_obs
        
        # We need to re-run prepare_time_series which takes a TimeSeriesContract
        contract = TimeSeriesContract.from_dict(record)
        prepared = prepare_time_series(contract, as_of=as_of)
        processed_series.append(prepared.to_dict())
        
    # 2. Derived series
    derived = compute_derived_series(processed_series)
    
    # 3. All records
    all_records = processed_series + derived
    
    # 4. Chart specs & Regime
    chart_specs = generate_chart_specs(all_records)
    report = classify_regime(all_records)
    
    report["transition_probabilities"] = calculate_regime_probabilities(all_records, report.get("bucket_reads", {}))
    
    return {
        "series": all_records,
        "charts": chart_specs,
        "regime": report
    }

