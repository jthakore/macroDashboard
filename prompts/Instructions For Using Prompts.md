I am using prompts as inspiration for the quantitative analysis. Isolate quantitative, deterministic processes, and qualitiative areas of analysis.
When using LLMs, they are not deterministic. So to ensure accuracy and consistency write code for quantitative analysis  nd chart generation and only use LLM for the narrative and sentiment analysis (generating JSON output) and never for quantitative analysis.
Instead for quantitative analysis, use python with libraries pandas, numpy, matplotlib, seaborn, and plotly. 
For JSON output use strict schema enforcement and validate the output before using it.
The chart generation should be done using matplotlib and seaborn. The JSON output should be generated using LLM. The narrative should be generated using LLM.
For the data, use the latest available data from the sources. The latest available date is May 3, 2026.