# Macro Analysis Dashboard Plan: United States Multi-Asset, 3-6 Month Horizon

## Summary
Build the macro dashboard as a point-in-time regime classifier for a U.S. multi-asset portfolio. The primary tactical horizon is 3-6 months, so the dashboard should emphasize timely momentum, surprises, financial conditions, policy repricing, liquidity, credit stress, and market-implied expectations. Add 12-month and 5-year extensions as optional overlays, not as the core read.

Core output:
- Dominant macro regime
- Conviction level
- Evidence by bucket
- Conflicting indicators
- Indicator extraction table
- Chart pack with latest observation callouts
- Regime implications for equities, duration, credit, USD, commodities, and real assets

## 0. Architecture & Tech Stack
To build a robust, deterministic visual dashboard using a modern web application stack, the following architecture is recommended:
- **Frontend Framework:** Next.js (React) for a highly scalable, modern web application.
- **Styling:** Vanilla CSS (or CSS Modules) focusing on a premium, highly responsive dark-mode financial aesthetic.
- **Charting:** Recharts or Lightweight Charts (TradingView) for performant, interactive React-based time-series visualizations.
- **Backend/Data Pipeline:** Python (FastAPI) combined with Pandas for robust data processing, calculating z-scores, and evaluating deterministic rules before serving structured JSON to the frontend.
- **Data Storage:** PostgreSQL or a lightweight DuckDB/SQLite database to store historical series and calculated indicators.
- **Automation:** Scheduled cron jobs (e.g., via GitHub Actions or Airflow) to fetch daily/weekly data automatically from APIs like FRED and BLS.

## 1. Workflow Substeps

### Step 1: Ingest Data
Prioritize automated API ingestion over manual uploads. For automated sources (FRED API, BLS, Yahoo Finance, etc.):
- Schedule daily/weekly data pulls for each required series.
- Store raw data in the database with standard schemas (`date`, `series_id`, `value`).

For any remaining uploaded Excel/CSV (fallback for proprietary or un-API-able data):
- Detect date column using names like `date`, `observation_date`, `period`, `month`, `quarter`.
- Detect numeric columns, excluding IDs, labels, notes, and empty columns.
- Convert date column to proper date format.
- Convert numeric columns to floats.
- Preserve source filename and sheet name.
- Treat each numeric column as one candidate time series.

Validation checks:
- Latest observation date.
- Frequency: daily, weekly, monthly, quarterly.
- Missing values in last 12 observations.
- Staleness relative to session date, May 3, 2026.
- Duplicate dates.
- Non-numeric values in numeric fields.
- Truncated history, defined as fewer than 24 monthly observations, 8 quarterly observations, or 252 daily observations.

If stale or missing, supplement only from primary sources: FRED, BLS, BEA, Treasury, Federal Reserve, IMF, or official central bank releases.

### Step 2: Normalize and Transform
For every series:
- Latest level.
- 3-month change.
- 12-month change.
- Rolling z-score, preferably 5-year if enough history exists.
- Percentile rank over available history.
- Acceleration tag:
  - `Accelerating`: recent 3-month change is stronger than prior 3-month change.
  - `Decelerating`: recent 3-month change is weaker than prior 3-month change.
  - `Stable`: absolute change is small or direction is flat.
  - `Mixed`: noisy or contradictory across related indicators.

For quarterly data:
- Use latest quarter and compare to one quarter ago and four quarters ago.
- Do not force quarterly data into monthly precision.

### Step 3: Create Derived Indicators
Compute these explicitly when source series are available:
- `10Y - 2Y yield curve = DGS10 - DGS2`
- `10Y - 3M yield curve = DGS10 - TB3MS`
- `Real policy rate proxy = Effective Fed Funds - Core PCE YoY`
- `Real 10Y yield = 10Y nominal Treasury - 10Y breakeven inflation`, or use TIPS 10Y if available
- `Headline-core inflation gap = CPI YoY - Core CPI YoY`
- `Growth-inflation momentum = growth z-score - inflation z-score`
- `Credit stress gap = HY OAS - IG OAS`
- `Financial conditions impulse = current FCI - 3M ago FCI`
- `Dollar-pressure read = DXY 3M change + real-yield 3M change`
- `Commodity inflation pressure = oil 3M change + gasoline 3M change + food/energy inflation spread`
- `Stock-bond correlation proxy = rolling 60-day correlation of equity returns and Treasury returns`

### Step 4: Bucket Indicators
Use seven buckets:
- Growth
- Inflation
- Labor
- Financial conditions
- Liquidity
- External / FX
- Credit

Each bucket receives:
- Direction tag
- Conviction tag
- Key drivers
- Plain-English explanation
- Supports/challenges dominant regime

### Step 5: Classify Regime (Deterministic Logic)
Use a rigid deterministic scorecard to eliminate the need for an LLM or analyst override in the core view. Map z-scores and momentum directly to categorical scores:
- Growth score: based on GDP/PMI z-scores (e.g., >0.5 accelerating, <-0.5 slowing, else stable).
- Inflation score: based on CPI/PCE momentum (accelerating, stable, or disinflating).
- Policy score: based on Fed Funds vs core inflation (easing, restrictive, or tightening).
- Financial conditions score: based on FCI/VIX changes (loosening or tightening).
- Liquidity score: based on Bank Reserves/RRP (abundant, normal, or stressed).
- Credit score: based on OAS spreads (benign, deteriorating, or stressed).
- External score: USD pressure, commodity shock, or calm

Primary regime labels:
- Disinflationary soft landing
- Reflationary acceleration
- Late-cycle expansion
- Late-cycle reflationary slowdown
- Stagflationary stall
- Deflationary slowdown
- Policy-driven liquidity rally
- Growth scare
- Inflation scare

## 2. Main Indicator Library

### Growth Indicators
Use these to determine whether real activity is accelerating, slowing, or diverging across hard and soft data.

Priority series:
- Real GDP growth: BEA / FRED `GDPC1`
- GDPNow or nowcast: Atlanta Fed
- Industrial production: FRED `INDPRO`
- Retail sales: FRED `RSAFS`
- Real personal consumption expenditures: FRED `PCEC96`
- ISM manufacturing PMI: ISM
- ISM services PMI: ISM
- New orders PMI
- Durable goods orders: Census / FRED
- Housing starts: FRED `HOUST`
- Building permits: FRED `PERMIT`
- Existing home sales: NAR
- Consumer sentiment: University of Michigan `UMCSENT`
- Conference Board consumer confidence
- Small business optimism: NFIB

How to use:
- Strong hard data plus weak sentiment supports the Lecture 1 “resilient but fragile” read.
- Weak PMIs, weak housing, and falling retail sales support growth scare or deflationary slowdown.
- Strong retail sales, production, and PMIs support reflationary acceleration or late-cycle expansion.

Main visuals:
- Real GDP / nowcast line chart
- Industrial production line chart
- Retail sales line chart
- ISM manufacturing and services dual-line chart
- Consumer sentiment line chart

Appendix visuals:
- Housing starts
- Durable goods
- NFIB
- Building permits

### Inflation Indicators
Use these to distinguish disinflation, sticky inflation, and renewed inflation pressure.

Priority series:
- CPI YoY: BLS / FRED `CPIAUCSL`
- Core CPI YoY: BLS / FRED `CPILFESL`
- PCE inflation: BEA / FRED `PCEPI`
- Core PCE: BEA / FRED `PCEPILFE`
- PPI final demand: BLS / FRED `PPIFIS`
- Import prices
- Average hourly earnings YoY: BLS / FRED `CES0500000003`
- Employment cost index
- 5Y breakeven inflation: FRED `T5YIE`
- 10Y breakeven inflation: FRED `T10YIE`
- 5Y5Y forward inflation expectation: FRED `T5YIFR`
- Michigan 1Y and 5Y inflation expectations
- Oil price: FRED `DCOILWTICO`
- Gasoline price: EIA / FRED
- Food CPI and energy CPI

How to use:
- Headline rising faster than core implies commodity/supply shock.
- Core sticky above target implies Fed restriction remains relevant.
- Breakevens rising with oil supports inflation scare or stagflation risk.
- Inflation falling while growth remains stable supports disinflationary soft landing.

Main visuals:
- CPI vs core CPI
- PCE vs core PCE
- 5Y and 10Y breakevens
- Oil price
- Michigan inflation expectations

Appendix visuals:
- PPI
- Import prices
- ECI
- Food/energy CPI

### Labor Indicators
Use these to test whether growth is translating into jobs, and whether wage pressure remains inflationary.

Priority series:
- Nonfarm payrolls: BLS / FRED `PAYEMS`
- Unemployment rate: BLS / FRED `UNRATE`
- Initial claims: FRED `ICSA`
- Continuing claims: FRED `CCSA`
- Labor force participation: FRED `CIVPART`
- Prime-age participation: FRED `LNS11300060`
- Job openings: FRED `JTSJOL`
- Quits rate: FRED `JTSQUR`
- Wage growth: average hourly earnings
- Employment cost index
- Productivity growth: BLS / FRED `OPHNFB`

Derived labor reads:
- Payroll growth vs breakeven job growth.
- Job openings per unemployed worker.
- Wage growth minus inflation.
- Claims acceleration over 4, 13, and 26 weeks.

How to use:
- Slowing payrolls but stable unemployment supports late-cycle slowdown.
- Rising claims and falling openings support growth scare.
- Strong wages and tight labor support inflation pressure.
- Stable GDP with weak labor confirms Lecture 1 labor-output decoupling.

Main visuals:
- Payroll growth
- Unemployment rate
- Initial claims
- Job openings
- Wage growth

### Financial Conditions Indicators
Use these to measure whether markets are easing or tightening before macro data confirms it.

Priority series:
- Effective Fed Funds Rate: FRED `EFFR`
- Fed policy target range
- 2Y Treasury: FRED `DGS2`
- 10Y Treasury: FRED `DGS10`
- 10Y-2Y curve
- 10Y-3M curve
- 10Y real yield: FRED `DFII10`
- Term premium: New York Fed ACM
- Chicago Fed NFCI
- Goldman Sachs FCI, if licensed/available
- VIX: CBOE / FRED `VIXCLS`
- MOVE index, if available
- S&P 500 drawdown
- Stock-bond correlation

How to use:
- Falling real yields, rising equities, and easing FCI support policy-driven liquidity rally.
- Rising real yields and tighter FCI challenge equity valuation.
- Bear flattening supports hawkish policy shock.
- Bull steepening supports growth scare or easing expectations.

Main visuals:
- Fed funds and 2Y Treasury
- 10Y Treasury and real 10Y yield
- Yield curve slopes
- Financial conditions index
- VIX

### Liquidity Indicators
Use these to detect funding stress, market plumbing risk, and liquidity-driven rallies.

Priority series:
- Fed balance sheet assets: FRED `WALCL`
- Bank reserves: FRED `WRESBAL`
- Reverse repo facility: FRED `RRPONTSYD`
- Treasury General Account: FRED `WTREGEN`
- SOFR: FRED `SOFR`
- SOFR-Fed funds spread
- Treasury market liquidity index, if available
- Bid-ask proxy for Treasury ETFs, if market data available
- Money market fund assets
- Bank deposits
- Commercial bank credit: FRED `TOTBKCR`
- Senior Loan Officer Survey standards

How to use:
- Rising reserves and falling RRP can support liquidity rally.
- Rising funding spreads or falling reserves can flag liquidity squeeze.
- Tight lending standards challenge growth and credit risk appetite.

Main visuals:
- Fed balance sheet
- Bank reserves
- RRP and TGA
- SOFR-Fed funds spread
- Bank credit

### External / FX Indicators
Use these to capture dollar, commodity, and global spillover risk.

Priority series:
- DXY or broad trade-weighted dollar: FRED `DTWEXBGS`
- EUR/USD, USD/JPY, USD/CNY
- Real broad dollar index
- Current account balance
- Trade balance: BEA / Census
- Import/export growth
- WTI crude
- Copper
- Gold
- Commodity index
- Global PMI
- Foreign central bank policy rates, if relevant

How to use:
- Strong USD plus rising real yields tightens global financial conditions.
- Weak USD plus rising commodities supports reflation.
- Gold rising with yields or dollar stress can indicate institutional-confidence risk.
- Oil spike supports inflation scare or stagflationary stall.

Main visuals:
- Broad dollar
- WTI crude
- Copper
- Gold
- Trade balance

### Credit Indicators
Use these to judge whether macro stress is becoming balance-sheet stress.

Priority series:
- Investment grade OAS: FRED `BAMLC0A0CM`
- High yield OAS: FRED `BAMLH0A0HYM2`
- CCC OAS: FRED `BAMLH0A3HYC`
- Leveraged loan index spreads, if available
- Delinquency rates: credit card, auto, commercial real estate
- Bank charge-offs
- Bank lending standards
- Corporate bankruptcies
- Commercial paper spread
- Mortgage spreads
- CMBS spreads, if available

How to use:
- Tight credit spreads with weak macro can signal complacency.
- Widening HY/CCC spreads supports growth scare or credit stress.
- CRE/mortgage stress matters for real estate and bank-risk reads.
- Credit resilience with tight labor supports soft landing.

Main visuals:
- IG OAS
- HY OAS
- CCC OAS
- Lending standards
- Delinquency rates

## 3. Main Chart Pack

Prioritize 15 charts for the main dashboard:

1. Real GDP / GDPNow  
Caption: Shows current growth momentum relative to recent trend.  
Regime implication: Strong growth supports expansion/reflation; weakening growth supports growth scare.

2. ISM manufacturing and services  
Caption: Separates goods-cycle weakness from services resilience.  
Regime implication: Broad PMI deterioration supports slowdown.

3. Retail sales or real consumption  
Caption: Measures household demand, especially relevant for K-shaped consumption.  
Regime implication: Strong consumption supports soft landing or reflation.

4. Consumer sentiment  
Caption: Captures soft-data stress versus hard-data resilience.  
Regime implication: Weak sentiment challenges confidence in the expansion.

5. CPI vs core CPI  
Caption: Separates headline commodity pressure from sticky underlying inflation.  
Regime implication: Rising core supports inflation scare.

6. Core PCE  
Caption: Fed’s preferred underlying inflation gauge.  
Regime implication: Falling core PCE supports disinflationary soft landing.

7. 5Y/10Y breakevens  
Caption: Market-implied inflation compensation.  
Regime implication: Rising breakevens support reflation or inflation scare.

8. Nonfarm payroll growth  
Caption: Measures job creation versus labor-market trend.  
Regime implication: Slowing payrolls support late-cycle slowdown.

9. Unemployment and claims  
Caption: Tracks labor-market deterioration before recession confirmation.  
Regime implication: Rising claims support growth scare.

10. Fed funds, 2Y yield, and implied policy path  
Caption: Shows market repricing of Fed expectations.  
Regime implication: Higher front-end yields tighten conditions.

11. 10Y yield and 10Y real yield  
Caption: Tracks discount-rate pressure on assets.  
Regime implication: Rising real yields pressure equities, credit, and real estate.

12. 10Y-2Y and 10Y-3M curves  
Caption: Measures recession risk and policy-cycle expectations.  
Regime implication: Deep inversion or rapid bull steepening warns of slowdown.

13. Financial conditions index and VIX  
Caption: Shows market stress and risk appetite.  
Regime implication: Loosening supports liquidity rally; tightening challenges risk assets.

14. High yield and investment grade spreads  
Caption: Tracks credit-market stress.  
Regime implication: Widening spreads challenge soft landing.

15. Broad dollar, oil, gold  
Caption: Captures external, inflation, and confidence shocks.  
Regime implication: Oil/gold spikes with dollar stress support stagflation or confidence risk.

## 4. Data Ingestion and Validation Table

Use this table for every uploaded file and supplemented source:

| File / Source | Sheet | Series Name | Date Column | Value Column(s) | Latest Observation | Latest Value | Frequency | Status | Issue Flag |
|---|---:|---|---|---|---:|---:|---|---|---|
| Uploaded workbook | Sheet name | Detected series | Detected date field | Numeric fields | Date | Value | Daily/monthly/etc. | Usable / stale / unusable | Missing, stale, truncated, duplicate, nonnumeric |

Rules:
- If a file contains multiple numeric columns, each becomes a separate series.
- If no valid date column exists, mark unusable.
- If no valid numeric value exists, mark unusable.
- If stale, supplement only from primary sources.
- If unavailable, state unavailable and do not invent a value.

## 5. Indicator Extraction Table

Use this table for every series:

| Series | Latest Observation Date | Level | 3-Month Direction | 12-Month Direction | Acceleration | Bucket | Signal Interpretation | Source |
|---|---:|---:|---|---|---|---|---|---|
| Core CPI YoY | Date | Value | Up/down by X pp | Up/down by X pp | Accelerating/decelerating/stable | Inflation | Sticky inflation / disinflation / inflation scare | BLS/FRED |
| 10Y-2Y curve | Date | Value | Steepened/flattened by X bp | Steepened/flattened by X bp | Accelerating/decelerating/stable | Financial conditions | Recession risk / policy easing expectation | Treasury/FRED |
| HY OAS | Date | Value | Wider/tighter by X bp | Wider/tighter by X bp | Accelerating/decelerating/stable | Credit | Credit stress / benign risk appetite | ICE/FRED |

Derived reads must be reported as their own rows:
- 10Y minus 2Y yield curve
- 10Y minus 3M yield curve
- Headline CPI minus core CPI
- Real policy rate proxy
- Real 10Y yield
- Growth-inflation momentum
- HY minus IG credit stress gap
- Dollar-pressure read
- Commodity inflation pressure
- Stock-bond correlation proxy

## 6. Bucket Characterization

Start with a summary table:

| Bucket | Direction | Conviction | Key Indicators | What It Says | Supports or Challenges Regime |
|---|---|---|---|---|---|
| Growth | Accelerating / decelerating / mixed | High/Medium/Low | GDP, PMI, retail sales | One-sentence read | Supports/challenges |
| Inflation | Accelerating / decelerating / mixed | High/Medium/Low | CPI, core PCE, breakevens | One-sentence read | Supports/challenges |
| Labor | Accelerating / decelerating / mixed | High/Medium/Low | payrolls, claims, unemployment | One-sentence read | Supports/challenges |
| Financial conditions | Loosening / tightening / mixed | High/Medium/Low | rates, FCI, VIX | One-sentence read | Supports/challenges |
| Liquidity | Ample / tightening / stressed | High/Medium/Low | reserves, RRP, SOFR spreads | One-sentence read | Supports/challenges |
| External / FX | Calm / reflationary / stress | High/Medium/Low | dollar, oil, gold | One-sentence read | Supports/challenges |
| Credit | Benign / deteriorating / stressed | High/Medium/Low | IG, HY, CCC, lending standards | One-sentence read | Supports/challenges |

Then write one short explanation per bucket:
- Growth: explain whether hard data confirms or contradicts soft data.
- Inflation: explain whether inflation is demand-driven, supply-driven, or sticky.
- Labor: explain whether labor is tight, cooling, or breaking.
- Financial conditions: explain whether markets are easing despite Fed policy.
- Liquidity: explain whether funding conditions support risk-taking.
- External / FX: explain dollar, oil, gold, and global pressure.
- Credit: explain whether balance-sheet stress is contained or spreading.

## 7. Dominant Regime Classification

Since this is a deterministic visual dashboard, the UI will display a distinct Regime Banner based on the scoring matrix.

UI Output format:

**Regime Name:** Displayed prominently (e.g., "Reflationary Acceleration").  
**Conviction:** High / Medium / Low (calculated mathematically based on the % of indicators aligning with the regime).  
**Plain-English Explanation:** Replaced with a hardcoded, deterministic string template for each regime (e.g., "Growth is >0.5z and inflation momentum is positive, signaling a reflationary acceleration...").  
**Why It Fits:** A dynamic list auto-populated with indicators that meet the regime's threshold conditions.  
**Supporting Indicators:** Visual column showing indicators flashing green for this regime.  
**Challenging Indicators:** Visual column showing conflicting indicators.  
**What Would Change the Label:** A deterministic "Distance to next regime" metric (e.g., "If Growth Z-score drops by 0.2, regime shifts to Stagflationary Stall").  

Example trigger rules:
- Shift to `Inflation scare` if core inflation, breakevens, oil, and wages accelerate while growth remains stable.
- Shift to `Growth scare` if claims rise, PMIs fall below 50, curve bull-steepens, credit spreads widen, and equities weaken.
- Shift to `Stagflationary stall` if growth weakens while oil/headline inflation and inflation expectations rise.
- Shift to `Policy-driven liquidity rally` if growth is mediocre but real yields fall, financial conditions ease, credit spreads tighten, and risk assets rally.
- Shift to `Disinflationary soft landing` if core inflation decelerates, labor cools without breaking, growth remains positive, and credit stays benign.

## 8. Multi-Asset Interpretation Layer

For each regime, add portfolio implications:

| Regime | Equities | Duration | Credit | USD | Commodities | Real Assets |
|---|---|---|---|---|---|---|
| Disinflationary soft landing | Positive, quality/growth | Modestly positive | Positive | Neutral/weak | Mixed | Neutral |
| Reflationary acceleration | Cyclicals/value positive | Negative | Positive until overheating | Often weaker | Positive | Positive |
| Late-cycle expansion | Selective, quality bias | Neutral/negative | Carry positive but watch spreads | Neutral | Positive | Positive |
| Late-cycle reflationary slowdown | Narrow leadership, fragile | Mixed | Caution | Stronger | Energy/gold positive | Positive |
| Stagflationary stall | Negative broad equities | Negative nominal duration | Negative HY | Mixed | Positive energy/gold | Positive |
| Deflationary slowdown | Negative equities | Positive duration | Negative credit | Stronger | Negative cyclicals, gold mixed | Mixed |
| Policy-driven liquidity rally | Positive risk assets | Positive if yields fall | Positive | Weaker | Positive beta assets | Positive |
| Growth scare | Defensive equities | Positive duration | Negative lower quality | Stronger | Oil/copper negative, gold positive | Mixed |
| Inflation scare | Duration-sensitive equities negative | Negative duration | Mixed/negative | Stronger if Fed reprices | Positive commodities | Positive |

## 9. Horizon Extensions

### Quarterly Expansion
Add:
- Earnings revisions
- Capex intentions
- Fiscal impulse
- Term premium trend
- Credit cycle deterioration
- Housing cycle
- Bank lending standards
- Profit margins
- Productivity trend
- Global growth divergence

Use for:
- Asset allocation tilts
- Sector rotation
- Duration exposure
- Credit quality decisions

### 5-Year Expansion
Add:
- Demographics and labor-force growth
- Productivity and AI capex/productivity conversion
- Debt/GDP and fiscal sustainability
- Dollar reserve status
- Deglobalization/tariff exposure
- Energy security
- Commodity supply constraints
- Climate/insurance/housing affordability
- Structural inflation volatility
- Equity concentration and intangible-capital valuation

Use for:
- Strategic allocation
- Real asset policy
- Long-run dollar and duration assumptions
- Equity risk premium and valuation regime analysis

## 10. Dashboard UI/UX Layout
To make this a highly effective visual tool, the interface should be divided into:
1. **Top Banner (The "Bottom Line"):** Current Macro Regime, Conviction Gauge, and automated Asset Class Implications (Green/Red highlights for Equities, Duration, etc.).
2. **The "Speedometer" Row:** High-level gauges for the 7 buckets (Growth, Inflation, Labor, FCI, Liquidity, External, Credit).
3. **Main Chart Grid:** The 15 priority charts, interactively synced to the same timeline. Tooltips should display the current z-score and momentum.
4. **Indicator Table View:** A searchable, sortable data table replacing the manual "Indicator Extraction Table."
5. **FOMC & Narrative Integration Panel:** A side panel or tab dedicated to text-based analysis.

## 11. Integrating LLM/Text Analyses (FOMC)
While the core dashboard is strictly deterministic, the `FOMC Narrative Shift Analysis` and `Macroeconomic Regime Classification` prompts can be incorporated into the data ingestion pipeline:
- **FOMC Ingestion:** A background script runs the FOMC prompt on new meeting statements and outputs structured JSON (e.g., `{"Stance": "Hawkish", "Shift": "More cautious"}`).
- **Dashboard Display:** The dashboard fetches this JSON and displays it deterministically (e.g., moving a "Fed Policy Gauge" visually based on the JSON output, rather than generating free-text on the fly).
- This bridges the gap between the qualitative LLM text analysis and the quantitative, deterministic visual dashboard.
