# Ten-minute presentation script

Each presenter has exactly two minutes. The timing includes transitions. Rehearse at roughly 120–135 words per minute and shorten pauses if necessary. Slides contain editable charts; speaker notes contain this script.

| Presenter | Slides | Time |
|---|---|---|
| Lufan (Rebecca) Wang | 1–2 | 0:00–2:00 |
| Wangying Zhang | 3–4 | 2:00–4:00 |
| Yinuo Zhu | 5–6 | 4:00–6:00 |
| Zhiyi Liu | 7–9 | 6:00–8:00 |
| Hongcheng Fu | 10–12 | 8:00–10:00 |

## Slide 1: Chicago crime data engineering project

**Lufan (Rebecca) Wang — 0:00 to 0:40**

Hello, we are Rebecca Wang, Wangying Zhang, Yinuo Zhu, Zhiyi Liu and Hongcheng Fu. Our project studies Chicago's reported crime records from 2020 through October 2026. We built the entire path from a public API to a database, reproducible analysis and visualizations. We ask when reported incidents occur, how communities differ, how categories change across years and how recorded arrest shares vary. Our main engineering goal is that another student can reproduce our work now, and still reproduce the frozen results years from now.

## Slide 2: Source, scope and comparison window

**Lufan (Rebecca) Wang — 0:40 to 2:00**

Our source is the City of Chicago Crimes API, which draws from the police department's CLEAR system. The completed extract contains 1,620,720 source records. We selected incident dates beginning January 1, 2020 and ending before November 1, 2026. The source currently reaches early November, but November is incomplete. For annual comparisons, we therefore use January through October in every year. Community totals use the entire extraction window. A record generally describes a reported incident, although the source notes that murders can have a record per victim. This is not a count of every crime that actually occurred. Unreported events are absent, and report classifications and arrest flags can change. The City explicitly cautions against comparisons over time. We treat our charts as exploratory summaries of one extract, rather than official measures of underlying crime trends. Equal calendar windows improve comparability, but do not remove those limitations. Wangying will now explain the pipeline.

## Slide 3: The measured pipeline DAG

**Wangying Zhang — 2:00 to 3:00**

The pipeline has five dependent tasks: extract, transform and load, validate, analyze, and visualize. The runner executes them in dependency order and records each task's elapsed time and status. If a task fails, its descendants do not run. Extraction uses pages of 50,000 records ordered by unique ID. Each request starts after the previous ID, and an initial maximum ID caps the extraction. This avoids the shifting offsets that can occur with offset pagination. We retry temporary server failures and rate limits. We preserve every downloaded page as compressed JSON and calculate a SHA-256 checksum. These files form our reproducible source snapshot. The same Python command can fetch fresh API data or replay the frozen pages completely offline. GitHub Actions provides tests and an optional monthly refresh of the fixed study window.

## Slide 4: Validation before analysis

**Wangying Zhang — 3:00 to 4:00**

We clean the data into typed SQLite columns. Dates produce the year, month, weekday, hour and season. Required IDs, categories and boolean flags must be valid or the load fails. Missing or invalid community codes become null, while the incidents remain in citywide totals. The finished dataset has 2,351 unknown community codes and 25,839 missing or invalid coordinate pairs. SQLite enforces the unique incident ID and boolean constraints. Loading happens in a staging database, which replaces the published database only after a successful load. Validation checks database integrity and reconciles the row count with the frozen manifest. Replaying the same input does not append duplicates. We also test malformed booleans, leap dates, checksum failures and retry behavior. A live API is not transactionally frozen, so our archived pages define exactly what we analyzed. Yinuo will present the trend results.

## Slide 5: Comparable annual totals peak in 2023

**Yinuo Zhu — 4:00 to 5:00**

This chart compares reported record counts for January through October in each year. The highest total in this extract is 221,027 in 2023. The 2026 count is 195,294, compared with 202,106 in 2025, a change of -3.4 percent. Every bar covers the same calendar months, so we avoid comparing ten months with twelve. We have not normalized for the extra day in leap years, and we have not estimated population exposure. These bars summarize the records available when we downloaded the data. They do not show that a particular policy caused an increase or decrease. Recent reports and classifications can still change, and the City's source disclaimer remains relevant. The next chart breaks the totals into categories, which helps us see why a single citywide total can hide different patterns.

## Slide 6: Crime categories follow different paths

**Yinuo Zhu — 5:00 to 6:00**

Here we show theft, battery and motor vehicle theft using the same January through October window each year. These are source categories, and the pipeline preserves their labels rather than silently combining different offenses. Motor vehicle theft reaches its highest comparable-period count in 2023, at 24,771. Its 2026 count is 15,165, or 38.8 percent below that peak. We chose these categories to show contrasting trajectories rather than assume all categories move together. The downloadable category-by-year table includes every category and its exact count, so the chart can be checked against the database. Interpretation still requires caution: recording practices and category definitions may differ over time. We would need additional evidence to explain any specific cause. Zhiyi will now discuss the timing and geographic patterns.

## Slide 7: Reported incident timing

**Zhiyi Liu — 6:00 to 6:45**

This chart pools incident records by hour of the day across the entire extraction window. The largest hourly total occurs at 00:00, with 117,012 records. Across weekdays, Friday has the largest pooled count, at 238,280. The offline dashboard also includes a weekday-by-hour heatmap, allowing us to inspect the combined pattern. These are recorded incident times, not necessarily the time police received a report. Midnight or other rounded times can reflect approximate entries, so a spike should not automatically be interpreted as a behavioral pattern. Weekday counts are pooled totals rather than exposure-adjusted rates.

## Slide 8: Seasonality in complete years

**Zhiyi Liu — 6:45 to 7:30**

For seasonality, we use only complete years, 2020 through 2025. Including only part of 2026 would underrepresent the end of the calendar year. We use meteorological seasons and divide each season's incident total by its actual number of calendar days. This accounts for different season lengths and leap days. Summer has the highest average, about 701 recorded incidents per day. Winter has the lowest, about 602. This is a pooled descriptive association. It does not isolate weather, school schedules or any other possible explanation. Monthly totals are also available for more detailed exploration.

## Slide 9: Community totals differ across Chicago

**Zhiyi Liu — 7:30 to 8:00**

The map joins crime community codes to the City's 77 official community boundaries. Darker areas have more recorded incidents over the full extraction window. Austin has the largest total, 84,214. These are counts, not population rates or neighborhood safety scores. Population, commuters, visitors and reporting all affect totals. Unknown community codes stay in citywide results but are excluded from the map. Hongcheng will close with recorded arrests and reproducibility.

## Slide 10: Recorded arrest share by category

**Hongcheng Fu — 8:00 to 8:50**

We define recorded arrest share as the number of incident records with arrest equal to true, divided by all records in that group. This chart shows the seven largest categories by incident count. Among those categories, battery has the highest share, 16.7%, while deceptive practice has the lowest, 2.6%. The downloadable table includes both the arrest numerator and incident denominator. This measure is not a conviction rate, a count of arrested people or an official clearance rate. Some categories are more likely to be recorded during an enforcement action, and older incidents have had more time to receive updated arrest flags. These differences prevent a simple interpretation as policing effectiveness.

## Slide 11: Recorded arrest share by community

**Hongcheng Fu — 8:50 to 9:20**

We also compare arrest shares in the seven communities with the most incident records. Within this set, North Lawndale has the highest share at 24.2%, and West Town has the lowest at 8.2%. This is an unadjusted comparison. Communities have different crime-category mixes and case histories. A stronger follow-up would compare communities within the same categories and account for case age before drawing conclusions.

## Slide 12: A reproducible project and a bounded conclusion

**Hongcheng Fu — 9:20 to 10:00**

Our analysis shows that record counts differ across years, crime categories, hours, seasons and communities. The most defensible conclusion is descriptive: these are patterns in reported records, subject to the source's limitations. Our engineering deliverable makes every chart traceable to SQL and a checksummed source snapshot. A new user can run the tests, execute the pipeline, or reproduce the frozen results offline. We include the database workflow, charts, documentation and automated job definitions in the repository. Preserving the snapshot matters because the live API may change or disappear. That is how the project can remain reproducible in five years. Thank you, and we welcome questions.

## Demo and Q&A preparation

Do not attempt a full API extraction during the ten-minute talk. Open the prepared dashboard and repository before class. If asked to demonstrate, run `python3 -m unittest discover -s tests -v`, show the DAG in `docs/ARCHITECTURE.md`, and show task timings in `reports/run.json`.

- Why SQLite? Portable, no database server setup, sufficient for approximately 1.6 million records.
- Why a custom DAG? It makes dependencies, failures and timings explicit without requiring an Airflow service.
- Why no population rates? The project has no validated population/exposure denominator. Counts are labeled accordingly.
- Why a snapshot? Live source revisions mean a fresh download may not reproduce the original findings.
- Why not call this a clearance rate? The API arrest flag is not the official clearance measure.
- Does a passing count check prove a consistent API snapshot? No. Existing records can change during extraction.
