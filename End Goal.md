
--- END GOAL --
The end goal is to build a testable macro econ-finance system, not just a trading model. Rising DCF pricing error may reflect behavioral forces, momentum, uncertainty, changing discount-rate premia, intangible accounting failures, or model misspecification. The research should therefore test whether behavioral/regime variables explain valuation gaps after controlling for standard fundamentals, factors, rates, and liquidity.

Use macro indicators : output, labor, inflation, Fed policy, K-shaped consumption, AI capex, and hard-vs-soft data divergence,  yield-curve decomposition, real rates, inflation expectations, and term premium. Lecture 3/4 add asset-class regime behavior, dollar/FX, commodities, home bias, diversification, and inflation hedges. Fed communication volatility, private credit stress, AI capex, K-shaped consumption, tariff/oil shocks, and diversified hedges.

## Literature Anchors
Use these as the theoretical scaffolding:
- Fundamentals and valuation limits: Campbell-Shiller present-value tests show stock prices are too volatile relative to simple dividend/earnings models; use this to justify valuation-gap analysis. Source: [NBER](https://www.nber.org/papers/w2511).
- Behavioral/social pricing: Shiller argues speculative prices are influenced by social dynamics, not only fundamentals. Source: [Brookings](https://www.brookings.edu/articles/stock-prices-and-social-dynamics/).
- Factor baseline: benchmark against Fama-French five factors, not CAPM alone. Source: [Fama-French citation](https://www.scirp.org/reference/referencespapers?referenceid=1795261).
- Sentiment: Baker-Wurgler sentiment is most relevant for hard-to-value, hard-to-arbitrage stocks. Source: [NBER](https://www.nber.org/papers/w10449).
- Momentum: use cross-sectional momentum and time-series momentum as core alternatives to valuation. Sources: [Jegadeesh-Titman](https://www.researchgate.net/publication/4992307_Returns_to_Buying_Winners_and_Selling_Losers_Implications_for_Stock_Market_Efficiency), [Moskowitz-Ooi-Pedersen](https://econpapers.repec.org/RePEc%3Aeee%3Ajfinec%3Av%3A104%3Ay%3A2012%3Ai%3A2%3Ap%3A228-250).
- Uncertainty: separate policy uncertainty from true macro uncertainty. Sources: [Baker-Bloom-Davis EPU](https://www.nber.org/papers/w21633), [Jurado-Ludvigson-Ng](https://www.aeaweb.org/articles?id=10.1257%2Faer.20131193&page=139).
- Regime allocation: use Markov/regime-switching logic because correlations and premia change in bad regimes. Source: [Ang-Bekaert](https://academic.oup.com/rfs/article/15/4/1137/1568247).
- Liquidity risk: liquidity is an asset-pricing state variable and can explain part of momentum profits. Source: [Pastor-Stambaugh](https://www.nber.org/papers/w8462).
- Term premia and inflation compensation: decompose nominal yields into expectations, inflation compensation, and term premium. Sources: [Fed yield curve models](https://www.federalreserve.gov/data/yield-curve-models.htm), [Fed TIPS curve](https://www.federalreserve.gov/data/tips-yield-curve-and-inflation-compensation.htm), [Cochrane-Piazzesi](https://www.aeaweb.org/articles?id=10.1257%2F0002828053828581).
- ML sequence models: deep momentum models and interpretable transformer-style forecasting justify the sequence layer, but must be benchmarked against simpler momentum. Sources: [Deep Momentum Networks](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3369195), [Temporal Fusion Transformer](https://research.google/pubs/temporal-fusion-transformers-for-interpretable-multi-horizon-time-series-forecasting/).
- Event/LLM layer: use LLMs for structured event classification, not unconstrained prediction. Source: [LLM stock-return predictability](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4412788).

## Indicator Library and Use
Build five feature blocks. Every indicator must have: raw value, YoY or MoM change, surprise vs consensus when available, z-score vs rolling history, percentile rank, and regime-specific historical response.

**1. Macro Growth and Labor**
- Indicators: real GDP, nowcasts, industrial production, retail sales, real consumption, ISM/PMI manufacturing and services, payrolls, unemployment, labor-force participation, prime-age participation, job openings, quits, claims, wage growth, productivity, breakeven job-growth estimate.
- Use: classify growth direction, labor tightness, recession risk, and Lecture 1's GDP-labor decoupling.
- Visualize: regime quadrant scatter of growth momentum vs inflation momentum; labor dashboard showing payroll growth versus breakeven job growth; hard-data vs soft-data divergence chart.
- Feeds: macro regime probabilities, earnings-growth forecasts, DCF revenue assumptions, event surprise priors.

**2. Inflation, Policy, and Rates**
- Indicators: CPI, core CPI, PCE, core PCE, PPI, import prices, wage inflation, oil/gasoline, food/fertilizer prices, 1y/5y/10y breakevens, inflation swaps, Michigan inflation expectations, SPF expectations, Fed funds, SOFR/OIS curve, futures-implied policy path, dot-plot dispersion, yield-curve slopes, real yields, term premium, Cochrane-Piazzesi bond risk premium.
- Use: distinguish demand inflation, supply-shock inflation, and policy-reaction risk.
- Visualize: nominal yield decomposition; inflation surprise heatmap; policy-path repricing before/after FOMC/CPI; real-rate versus equity duration sensitivity.
- Feeds: discount rates in DCF, bond/FX/commodity allocation, inflation-regime classification, event engine.

**3. Risk, Liquidity, Credit, and Dollar System**
- Indicators: VIX/VVIX, MOVE, credit spreads, HY/IG OAS, leveraged loan spreads, private credit stress proxies, bank lending standards, financial conditions indexes, repo/SOFR stress, Treasury liquidity, bid-ask spreads, dealer inventories, dollar index, cross-currency basis, reserve-currency share, gold central-bank purchases.
- Use: identify liquidity squeeze, credit deterioration, dollar stress, and loss of safe-haven behavior.
- Visualize: liquidity-risk dashboard; stock-bond correlation regime chart; DXY vs 10y yield correlation breakdown; credit waterfall from IG to HY to loans/private credit.
- Feeds: regime engine, momentum position sizing, drawdown controls, event severity scoring.

**4. Behavioral, Sentiment, and Reflexivity**
- Indicators: Michigan sentiment, Conference Board confidence, AAII sentiment, fund flows, ETF flows, retail options volume, 0DTE share, put-call ratios, short interest, margin debt, meme/attention proxies, Google Trends, news sentiment, Baker-Wurgler sentiment, analyst revision breadth, earnings-call tone.
- Use: measure hard-vs-soft data gap, retail/passive reflexivity, crowded positioning, and sentiment-driven valuation gaps.
- Visualize: sentiment vs consumption divergence; flow-momentum loop diagram; attention index overlaid on valuation gaps; crowding radar.
- Feeds: valuation-error decomposition, event engine, meta-labeling, risk throttles.

**5. Valuation, Fundamentals, Momentum, and Assets**
- Indicators: DCF-implied value, residual-income value, earnings yield, CAPE, dividend yield, FCF yield, EV/EBITDA, sales growth, margin, ROIC, buybacks, intangible intensity, R&D, analyst EPS revisions, accruals, FF5 factors, quality/profitability/investment, 1/3/6/12 month returns, 12-1 momentum, 36-60 month reversal, realized vol, volatility-scaled trend, cross-asset momentum in equities/bonds/FX/commodities.
- Use: separate fundamental under/overvaluation from momentum and risk-premium repricing.
- Visualize: DCF price-gap time series; valuation-gap decomposition bars; momentum term structure; sector valuation-duration map; return attribution by factor/regime.
- Feeds: Paper 1 pricing-error tests, Paper 2 momentum dominance tests, portfolio optimizer, dashboard signal layer.

## System Architecture
**Macro Regime Engine**
- Inputs: all macro, inflation, policy, liquidity, credit, FX, commodity, and sentiment indicators.
- Models: start with transparent PCA + GMM/HMM; compare to k-means, Markov switching, XGBoost, and transformer/TFT only after baseline validation.
- Regime labels: Goldilocks, Reflation, Stagflation, Disinflation/Recession, Liquidity Squeeze, Policy Credibility Shock.
- Outputs: `regime_probabilities`, `transition_matrix`, `regime_duration`, `regime_confidence`, `adjacent_regime_risk`.
- Visuals: probability stack over time, transition matrix, regime quadrant, global map, historical analogs.

**Valuation Divergence Engine**
- Compute DCF, residual-income, and multiples-implied fair value for equities.
- Main dependent variable: `valuation_gap = log(market_price / fundamental_value)`.
- Decompose gap into rates, earnings revisions, momentum, uncertainty, sentiment, liquidity, and regime.
- Critical controls: intangibles, sector mix, accounting changes, buybacks, profitability, investment, size, value, and duration exposure.
- Visuals: actual price vs DCF value; contribution waterfall; rolling R-squared of fundamentals vs behavioral/regime variables.

**Sequence and Momentum Engine**
- Baselines: 12-1 cross-sectional momentum, time-series momentum, volatility-scaled trend, moving-average trend.
- ML models: LSTM-attention, TFT, and transformer only if they beat baselines out-of-sample after costs.
- Inputs: multi-horizon returns, vol-normalized returns, regime embeddings, uncertainty, liquidity, sentiment, event proximity.
- Outputs: `signal_z in [-1,1]`, `momentum_confidence`, `regime_conditioned_trend`, `turnover_budget`.
- Visuals: signal history, attention/feature-importance heatmap, regime-conditioned performance, turnover and cost drag.

**Event-Driven Alpha Engine**
- Events: FOMC, CPI/PCE, payrolls, Treasury refunding, earnings, guidance, oil/geopolitical shocks, tariff/trade events, central-bank speeches, liquidity/credit stress events.
- For each event store: timestamp, consensus, actual, surprise, text, LLM classification, affected assets, pre-event positioning, post-event abnormal returns.
- LLM role: classify event type, causal channel, hawkish/dovish tone, inflation/growth/liquidity relevance, and confidence. Do not let the LLM directly trade without structured validation.
- Visuals: event calendar ranked by expected impact; pre/post event return distributions; analog-event cards; surprise-response scatter.

**Portfolio and Risk Layer**
- Convert signals into weights using volatility targeting, drawdown constraints, liquidity filters, and regime-dependent risk budgets.
- Compare allocations: static 60/40, FF5/factor portfolio, pure momentum, static macro allocation, regime-only, event-only, hybrid.
- Visuals: regime performance matrix, drawdown timeline, exposure heatmap, risk contribution, scenario stress tests for 2008, 2020, 2022, oil shock, dollar shock, AI bust.

## Experiments and Acceptance Tests
- Paper 1: show whether valuation-gap errors rise over time and whether momentum, uncertainty, sentiment, liquidity, and regime variables explain incremental error beyond DCF/factors. Acceptance: rolling out-of-sample R-squared and economically interpretable coefficients.
- Paper 2: compare DCF-only, FF5, momentum, macro-regime, uncertainty, and hybrid models. Acceptance: hybrid improves Sharpe, drawdown, turnover-adjusted returns, and regime robustness versus all baselines.
- Paper 3: build unified macro + sequence + event model. Acceptance: higher net Sharpe and lower tail loss than pure momentum and static macro allocation under walk-forward testing.
- Regime prediction: evaluate probability calibration, transition accuracy, and economic utility, not just classification accuracy.
- Event alpha: use event windows from -5 to +10 trading days, with tighter intraday windows for FOMC/CPI where data exists. Acceptance: abnormal return prediction beats naive surprise-only and text-only models after costs.
- Robustness: strict point-in-time data, no revised-data leakage, expanding/walk-forward splits, regime-balanced folds, transaction costs, borrow costs, survivorship-bias-free universes, and post-publication factor decay checks.

## Dashboard Blueprint
- Macro Regime Dashboard: current regime probabilities, regime drivers, transition risks, global map, yield/inflation decomposition.
- Momentum View: signal strength, trend horizon stack, attention/feature importance, regime-conditioned hit rate, turnover.
- Valuation Divergence Panel: market price vs fair value, valuation gap, decomposition, sector/stock ranking, confidence band.
- Event Engine: upcoming events, expected impact, surprise scenarios, predicted return distribution, historical analogs.
- Portfolio Command Center: target weights, risk contribution, scenario stress, attribution by valuation/momentum/regime/event.
- Research Lab: experiment results, rolling coefficients, model comparison, leakage checks, and falsification tests.

## Assumptions and Defaults
- Default asset universe: U.S. equities plus liquid ETFs/futures for Treasuries, credit, dollar, FX, commodities, gold, oil, copper, and global equity regions.
- Default frequency: daily market data, monthly macro data, event-level timestamps where available.
- Default regime method: probabilistic soft regimes, not hard labels.
- Default thesis test: behavioral/regime dominance is accepted only if it adds explanatory and predictive power beyond valuation, FF5, rates, liquidity, and accounting/intangible controls.
- Default product goal: research-grade dashboard and backtest first; live trading only after leakage, transaction-cost, and stability tests pass.


---