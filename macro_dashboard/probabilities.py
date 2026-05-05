from typing import Any, Dict, List

def calculate_regime_probabilities(series_records: List[Dict[str, Any]], current_bucket_reads: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Deterministically calculates the probability of shifting into each of the 9 regimes
    based on advanced, institutional-grade macro indicators (First Principles).
    """
    regimes = [
        "Disinflationary soft landing",
        "Reflationary acceleration",
        "Late-cycle expansion",
        "Late-cycle reflationary slowdown",
        "Stagflationary stall",
        "Deflationary slowdown",
        "Policy-driven liquidity rally",
        "Growth scare",
        "Inflation scare"
    ]
    
    scores = {r: 10.0 for r in regimes} # base score
    drivers = {r: [] for r in regimes}
    
    by_id = {r["series_id"]: r for r in series_records}
    
    def get_latest(series_id: str):
        series = by_id.get(series_id)
        if not series or not series.get("observations"): return None
        obs = [o for o in series["observations"] if o.get("value") is not None]
        return obs[-1]["value"] if obs else None

    def get_accel(series_id: str):
        series = by_id.get(series_id)
        if not series or not series.get("transforms"): return "stable"
        return series["transforms"].get("acceleration", "stable")

    # ---------------------------------------------------------
    # Rule 1: The Term Premium Factor
    # ---------------------------------------------------------
    acmtp10 = get_latest("FRED:ACMTP10")
    if acmtp10 is not None:
        acm_accel = get_accel("FRED:ACMTP10")
        if acmtp10 > 0 or acm_accel == "accelerating":
            scores["Stagflationary stall"] += 15.0
            scores["Inflation scare"] += 15.0
            scores["Policy-driven liquidity rally"] -= 5.0
            scores["Reflationary acceleration"] -= 5.0
            msg = "Term Premium: Investors are demanding higher compensation for holding long-term debt (fiscal dominance/supply fears)."
            drivers["Stagflationary stall"].append(msg)
            drivers["Inflation scare"].append(msg)

    # ---------------------------------------------------------
    # Rule 2: The True Credit Impulse (SLOOS)
    # ---------------------------------------------------------
    sloos = get_latest("FRED:DRTSCILM")
    if sloos is not None:
        if sloos > 0:
            scores["Deflationary slowdown"] += 20.0
            scores["Growth scare"] += 15.0
            scores["Disinflationary soft landing"] -= 10.0
            msg = f"Credit Impulse: Banks are actively tightening lending standards (Net {sloos:.1f}% tightening)."
            drivers["Deflationary slowdown"].append(msg)
            drivers["Growth scare"].append(msg)
        elif sloos < 0:
            scores["Reflationary acceleration"] += 15.0
            scores["Late-cycle expansion"] += 10.0
            msg = "Credit Impulse: Banks are easing lending standards, stimulating private credit creation."
            drivers["Reflationary acceleration"].append(msg)
            drivers["Late-cycle expansion"].append(msg)

    # ---------------------------------------------------------
    # Rule 3: The Sahm Rule Override
    # ---------------------------------------------------------
    sahm = get_latest("FRED:SAHMREALTIME")
    if sahm is not None and sahm >= 0.5:
        scores["Growth scare"] += 40.0
        scores["Deflationary slowdown"] += 30.0
        scores["Disinflationary soft landing"] -= 20.0
        scores["Late-cycle expansion"] -= 20.0
        msg = f"Sahm Rule Triggered: Real-time Sahm rule is {sahm:.2f} (>= 0.5 signals recession)."
        drivers["Growth scare"].append(msg)
        drivers["Deflationary slowdown"].append(msg)

    # ---------------------------------------------------------
    # Rule 4: True Policy Restrictiveness (R* Gap)
    # ---------------------------------------------------------
    real_rate = get_latest("DERIVED:REAL_POLICY_RATE_PROXY")
    r_star = get_latest("FRED:HLW158")
    if r_star is None:
        r_star = 1.0 # fallback natural rate
        
    if real_rate is not None:
        restrictive_gap = real_rate - r_star
        if restrictive_gap > 1.0:
            scores["Deflationary slowdown"] += 15.0
            scores["Disinflationary soft landing"] -= 10.0
            msg = f"Policy Restrictiveness: Real policy rate ({real_rate:.2f}%) is far above the neutral rate R* ({r_star:.2f}%), raising policy error risks."
            drivers["Deflationary slowdown"].append(msg)

    # ---------------------------------------------------------
    # Rule 5: Labor Margins Divergence
    # ---------------------------------------------------------
    temp_accel = get_accel("FRED:TEMPHELPS")
    hours_accel = get_accel("FRED:AWHNONPI")
    payems_accel = get_accel("FRED:PAYEMS")
    
    if (temp_accel == "decelerating" or hours_accel == "decelerating") and payems_accel != "decelerating":
        scores["Late-cycle reflationary slowdown"] += 15.0
        scores["Growth scare"] += 10.0
        msg = "Labor Divergence: Margin employment (Temp help / Hours worked) is contracting before aggregate payrolls."
        drivers["Late-cycle reflationary slowdown"].append(msg)
        drivers["Growth scare"].append(msg)

    # ---------------------------------------------------------
    # Rule 6: The Complacency Gap (BBD vs VIX)
    # ---------------------------------------------------------
    bbd_vix = get_latest("DERIVED:BBD_MINUS_VIX")
    if bbd_vix is not None and bbd_vix > 1.0:
        scores["Growth scare"] += 15.0
        scores["Inflation scare"] += 15.0
        msg = "Complacency Gap: High policy uncertainty (BBD) vs low market volatility (VIX)"
        drivers["Growth scare"].append(msg)
        drivers["Inflation scare"].append(msg)

    # ---------------------------------------------------------
    # Normalize probabilities to sum to 100%
    # ---------------------------------------------------------
    for r in scores:
        if scores[r] < 0.1:
            scores[r] = 0.1
            
    total_score = sum(scores.values())
    
    results = []
    for r in regimes:
        prob = (scores[r] / total_score) * 100
        results.append({
            "regime": r,
            "probability": prob,
            "drivers": drivers[r]
        })
        
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results
