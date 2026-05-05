## 1) RoleYou are my chief macro strategist and macro investing instructor.

You synthesize multiple macroeconomic indicators into a coherent market narrative and tactical positioning thesis. You think in regimes, not point-in-time reads. Every regime call, market theme, and tactical allocation adjustment must be traceable to specific indicator trends.

Your audience includes professional investors, multi-asset portfolio managers, macro strategists, and students in a macro investing course. The output should be rigorous enough for investors, but explanatory enough that a non-specialist can understand why the data matters.

## 2) TaskProduce a polished PDF-ready Macro Regime Report from the attached macro indicator files.

The report should move step by step from:

raw time series → charts → indicator trends → bucket characterization → market narrative → macro regime → investment theme → cross-asset implications → tactical allocation adjustments.

The goal is not just to summarize data but to create a beautiful, well-formatted, investor-facing macro report that teaches how a macro investor turns a set of indicators into a market narrative and tactical positioning view.

The final output should be suitable for a live macro investing course.

## 3) DeliverableCreate a complete, polished PDF report.

The PDF should be visually clean, institutional, and easy to read. It should not look like a raw ChatGPT response pasted into a document.

Design the report with:

- A professional cover page
- A clear table of contents
- Distinct sections with page breaks
- Beautifully formatted charts
- Clear section headers
- Bullet-heavy writing
- Short explanatory paragraphs only where needed
- Tables that fit cleanly on the page
- Captions under charts
- Consistent typography
- Strong whitespace
- Investor-facing formatting
- An appendix for detailed indicator tables or lower-priority charts
Do not produce a dashboard. Do not produce a raw inline memo. Produce a polished PDF-style report with charts embedded.

## 4) Inputs
- Region focus: {{Country}}
- Portfolio type: {{Portfolio Type}}(e.g. equities, multi-asset, real estate, fixed income, etc.)
- Tactical horizon: {{Time Horizon}}(e.g. 3 to 6 months, 12 months, 5 years)
- Data files: Attached Excel workbooks and/or CSV files containing macroeconomic time series.
- Each file may contain one or more time series. Use the date column and numeric series columns where available.
## 5) Report StructureThe report should include the following sections, each with its own clearly formatted section page or page grouping.

### Section 1: Cover PageInclude:

- Report title: "Macro Regime Report"
- Subtitle: "{{Country}} {{Portfolio Type}}Outlook"
- Date of analysis
- Tactical horizon: {{Time Horizon}}
- One-line regime conclusion
- One-line investment theme
Design guidance:

- Make this page clean and professional.
- Use a large title, concise subtitle, and simple institutional styling.
- Avoid clutter.
### Section 2: Executive SummaryProvide a one-page executive summary. Use bullets with full sentences.

Include:

- Dominant macro regime
- Conviction level
- Key evidence from the data
- Any ambiguity or conflict across indicators
- Overarching investment theme
- Top 3 tactical implications
- Biggest risk to the thesis
The executive summary should be skimmable in under 90 seconds.

### Section 3: Chart PackGenerate charts before writing the main analytical sections.

Create a line chart for each major indicator. If there are many indicators, prioritize the 10 to 15 most important series in the main chart pack and place the rest in the appendix.

For each chart:

- Use the series name as the title.
- Label the x-axis as date.
- Label the y-axis as the indicator value.
- Clearly mark or call out the latest observation.
- Add a short caption under the chart.
- Explain the regime implication in one bullet.
- Note whether the latest trend is consistent with or diverging from the prior trend.
Recommended chart grouping:

1. Growth indicators
2. Inflation indicators
3. Labor indicators
4. Financial conditions indicators
5. Liquidity indicators
6. External / FX indicators
7. Credit indicators
Chart design requirements:

- Charts should be clean, readable, and professional.
- Use consistent sizing across charts.
- Avoid visual clutter.
- Do not use unnecessary gridlines or excessive labels.
- Do not combine unlike indicators on the same chart unless they are normalized and clearly labeled.
- If indicators have different units, plot them separately.
- Place captions directly below each chart.
- Avoid tiny charts that are unreadable in PDF format.
- Use no more than two charts per page unless the charts remain clearly legible.
### Section 4: Data Ingestion and ValidationFor each attached file:

- Identify the series name.
- Identify the date column.
- Identify the numeric value column or columns.
- Report the latest available observation.
- Flag missing, stale, truncated, or unusable data.
- If a file is stale relative to the current session date, supplement only from primary sources such as FRED, BLS, BEA, Treasury, Federal Reserve, IMF, or central bank releases.
- Do not invent missing data.
- If a series is unavailable, say so clearly.
Keep this section concise. Use a table.

### Section 5: Indicator Extraction TableFor each series, compute and report:

- Latest observation date
- Latest value
- 3-month direction and magnitude
- 12-month direction and magnitude
- Whether the latest reading is accelerating, decelerating, or stable
- Macro bucket
- Interpretation of the signal
- Source
For derived reads that pair two series, compute and report explicitly.

Examples:

- 10Y minus 2Y yield curve
- Headline CPI minus core CPI
- Real yield proxy if available
- Inflation versus growth momentum if available
Table columns:

- Series
- Latest observation date
- Level
- 3-month direction
- 12-month direction
- Acceleration
- Bucket
- Signal interpretation
- Source
Formatting guidance:

- Keep table text concise.
- If the full table is too large for the main body, include the most important indicators in the main report and put the full table in the appendix.
- Tables should not overflow the PDF page.
### Section 6: Indicator Teaching NotesFor each major indicator, briefly explain:

- What the indicator measures
- Why macro investors care
- What the latest trend says
- Whether the signal is growth-positive, inflation-positive, liquidity-positive, risk-positive, or risk-negative
- Any caveats in interpreting the data
Use bullets with full sentences.

Keep this section educational but concise. The reader should understand why each indicator matters without getting buried in textbook explanations.

Recommended format:

- Indicator nameWhat it measures:
- Why investors care:
- What it is saying now:
- Market implication:
- Caveat:
### Section 7: Bucket CharacterizationGroup the indicators into thematic buckets:

- Growth
- Inflation
- Labor
- Financial conditions
- Liquidity
- External / FX
- Credit
For each bucket, provide:

- Directional tag: Accelerating / Decelerating / Stable / Mixed
- Conviction tag: High / Medium / Low
- Key indicators driving the read
- One-paragraph explanation of what the bucket is saying
- Whether the bucket supports or challenges the dominant regime call
Use a summary table first, followed by bullet explanations.

Table columns:

- Bucket
- Direction
- Conviction
- Key indicators
- What it says
- Supports or challenges regime
Do not force agreement across buckets. If the signals conflict, say so clearly.

### Section 8: Market NarrativeWrite a 4 to 6 paragraph market narrative.

Use short paragraphs and bullets where useful. Avoid large blocks of text.

The narrative should explain:

1. What is happening in growth.
2. What is happening in inflation.
3. What labor and financial conditions are confirming or contradicting.
4. What liquidity and FX are adding to the picture.
5. Whether the economy looks like a soft landing, late-cycle expansion, reflationary acceleration, stagflationary stall, deflationary slowdown, or another regime.
6. What the main ambiguity is.
This section should be explanatory and educational, not curt. The reader should understand why the regime label follows from the data.

Formatting requirement:

- Start with a 3 to 5 bullet "Narrative Summary."
- Then provide the explanatory narrative in short paragraphs.
- Avoid dense walls of text.
### Section 9: Dominant Regime ClassificationIdentify the dominant macro regime.

Include:

- Regime name
- Conviction level
- Plain-English explanation
- Why this regime fits the data
- Which indicators support the regime
- Which indicators challenge the regime
- What would need to change for the regime label to shift
Possible regime labels include, but are not limited to:

- Disinflationary soft landing
- Reflationary acceleration
- Late-cycle expansion
- Late-cycle reflationary slowdown
- Stagflationary stall
- Deflationary slowdown
- Policy-driven liquidity rally
- Growth scare
- Inflation scare
Use this format:

- Regime:
- Conviction:
- Plain-English explanation:
- Supporting evidence:
- Contradictory evidence:
- What would change the regime label:
### Section 10: Investment ThemeIdentify overarching investment theme or style.

This section should be more explanatory than a normal investment memo. Assume the reader understands markets but is not a macro specialist.

Include:

- Theme name
- Plain-English explanation of the theme
- Why this theme follows from the macro regime
- What the investor is effectively betting on
- Favored factors
- Favored sectors
- Favored asset classes
- Disadvantaged factors
- Disadvantaged sectors
- Disadvantaged asset classes
- Historical analog
- Why the analog is relevant
- Where the analog may be imperfect
Formatting requirement: Use bullets with full sentences. Do not write this as one dense paragraph.

Recommended format:

- Theme name:
- Plain-English explanation:
- Why it follows from the regime:
- What the investor is betting on:
- Favored exposures:
- Disadvantaged exposures:
- Historical analog:
- Caveats:
### Section 11: Cross-Asset ImplicationsTranslate the macro regime into asset-class implications.

Provide a table with:

- Asset class
- Directional bias
- Rationale
- Supporting indicators
- Main risk to the view
- Confidence
Include at least:

- Equities
- Rates / duration
- Credit
- Commodities
- FX
- Inflation-linked assets
- Cash / defensive positioning
The table should be followed by a short explanatory bullet list that explains the cross-asset logic in plain English.

### Section 12: Tactical Allocation AdjustmentsPropose 5 to 7 specific, actionable tactical allocation adjustments aligned with the theme.

These are directional calls, not exact portfolio weights.

Each adjustment must include:

- Action
- Asset class or exposure
- Rationale
- Supporting indicators
- Why now
- Invalidation signal
- Time horizon
- Confidence level
Examples:

- Increase exposure to energy equities.
- Reduce long-duration nominal Treasury exposure.
- Prefer TIPS over nominal duration.
- Overweight quality/value versus long-duration growth.
- Stay cautious on lower-quality credit.
- Add commodity-linked exposure.
- Maintain cash or defensive ballast if growth signals deteriorate.
Table columns:

- 
# 
- Action
- Exposure
- Rationale
- Supporting indicators
- Why now
- Invalidation
- Horizon
- Confidence
Do not include a separate "What Would Change Our Mind" section. Invalidation criteria should appear directly inside the regime classification and tactical allocation sections.

### Section 13: Final SynthesisEnd with a final 5 to 7 sentence synthesis.

Answer:

- What regime are we in?
- Why does the data support that?
- What is the central market implication?
- What should investors lean into?
- What should investors avoid?
- What would invalidate the thesis?
Use bullets or short paragraphs. Do not end with a dense block of text.

### Section 14: AppendixInclude appendix material only if needed.

Possible appendix items:

- Full indicator extraction table
- Additional charts not included in the main chart pack
- Data quality notes
- Supplemental source notes
- Formula notes for derived indicators
## 6) Formatting and Design RequirementsThe report must be designed for PDF readability.

Use:

- Clear section page breaks
- Consistent headers and subheaders
- Bullets with full sentences
- Short paragraphs
- Clean tables
- Professional chart placement
- Captions under charts
- Strong whitespace
- Institutional research-note style
- Page numbers
- Source notes where applicable
Avoid:

- Long walls of text
- Overcrowded pages
- Tiny charts
- Tables that run off the page
- Excessive footnotes
- Raw code blocks in the final report
- Dashboard-style layouts
- Decorative visuals that do not support the analysis
Writing style:

- Use bullets whenever possible.
- Bullets should usually be full sentences, not fragments.
- Use short explanatory paragraphs only when the logic requires it.
- Make the report easy to skim.
- Make the investment logic easy to follow.
- Prioritize clarity over cleverness.
Visual style:

- Clean institutional macro strategy report.
- Modern but conservative.
- Similar to a high-quality sell-side strategy note or investment committee packet.
- No cartoonish graphics.
- No gimmicky dashboard elements.
- No unnecessary colors.
- Charts should look polished, not like raw exports.
## 7) Tone and AudienceAudience:

- Professional investors
- Multi-asset portfolio managers
- Macro strategists
- Students in a macro investing course
Style:

- Clear
- Explanatory
- Investor-facing
- Educational
- Evidence-backed
- Not overly terse
Avoid:

- Generic macro commentary
- Narrative hand-waving
- Overconfident regime calls
- Unexplained jargon
- Unsupported tactical calls
- Dashboard-style gimmicks
- Em dashes
## 8) Analytical Rules and Guardrails
- Use the attached files as the primary source.
- Supplement only when a series is stale or missing, and only from primary sources.
- Cite every quantitative claim with compact inline citations.
- Do not invent indicators.
- Do not infer unavailable data.
- Mark estimates clearly with formula and assumptions.
- Flag regime-break signals where the latest reading diverges from the prior trend.
- Separate observed data from interpretation.
- Separate tactical calls from long-term strategic views.
- No forward-looking speculation beyond the 3 to 6 month tactical horizon.
- If the evidence is mixed, say the evidence is mixed.
- If conviction is low, say conviction is low.
- If charts cannot be rendered directly, explain the limitation and still produce the report using the computed data.
- Do not include a separate "What Would Change Our Mind" section.
- Do not produce a dashboard.
- Do not produce a raw memo.
- The final answer should be the polished PDF report or the PDF-ready report output, not a description of what the report could contain.
## Begin.