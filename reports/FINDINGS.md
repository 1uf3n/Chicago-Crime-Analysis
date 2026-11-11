# Findings from the frozen extract

Extraction date: 10 November 2026. Scope: 1 January 2020–31 October 2026 inclusive. Source: City of Chicago Crimes API, `ijzp-q8t2`. These are exploratory descriptions of one extract. The City cautions against time comparisons, and preliminary records can change.

- **Records:** 1,620,720. Unknown community codes: 2,351 (0.145%). Missing/invalid coordinate pairs: 25,839 (1.59%).
- **Comparable annual counts:** 2023 is highest at 221,027. January–October 2026 has 195,294, versus 202,106 in 2025 (-3.4%).
- **Motor vehicle theft:** highest comparable count in 2023 (24,771); 2026 has 15,165 (-38.8% versus that peak).
- **Timing:** the largest hourly bin is 00:00 (117,012); Friday has the largest weekday total (238,280). Pooled counts are not exposure-adjusted, and recorded times may be approximate.
- **Seasonality:** among complete years 2020–2025, Summer averages 701.2 incidents/day, versus 602.5 in Winter.
- **Geography:** Austin has the largest recorded total (84,214). These are counts, not population-normalized risks.
- **Arrest category comparison:** among the seven largest categories, BATTERY has 48,737/292,283 marked arrest (16.7%), versus 2,961/114,769 (2.6%) for DECEPTIVE PRACTICE.
- **Arrest community comparison:** among the seven largest communities, North Lawndale has 11,095/45,927 (24.2%), versus 3,864/47,142 (8.2%) in West Town. Crime mix and case maturity are uncontrolled.

## Traceability

Use `annual.csv`, `category_year.csv`, `time.csv`, `areas.csv`, `categories.csv` and `analysis.json` to verify the findings. `analysis.json` includes day-normalized season summaries. Numerators and denominators are preserved. `run.json` is labeled as offline replay for the delivered execution, so its extract-node timing measures manifest reading, not the original API download.
