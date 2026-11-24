# Submission checklist and rubric mapping

| Assignment requirement | Implemented evidence |
|---|---|
| Read data from an API | `src/pipeline.py:request` and `extract`, actual frozen API pages |
| Store API data in a database | Staged, normalized SQLite: `crimes` fact table plus `crime_types` and `community_areas` dimensions, primary/foreign keys, checks and indices |
| DAG measures start to finish | Executable `DAG`, task durations/status in `reports/run.json` |
| Easy-to-run repository | Standard-library Python, README commands, Dockerfile, automated tests |
| Exploratory analysis and insights | SQL aggregation tables, eight SVG figures, offline dashboard, findings |
| PowerPoint presentation | Twelve-slide deck, five speakers, ten minutes, embedded speaker notes |
| Reproducible years later | Raw snapshot archive, SHA-256 checks, offline replay, fixed scope |

Before class:

1. Upload the repository files to your team's GitHub account. The ZIP excludes raw pages and the generated SQLite database from ordinary version control.
2. The [snapshot ZIP and SHA256SUMS.txt are published](https://github.com/1uf3n/Chicago-Crime-Analysis/releases/tag/snapshot-2026-11-10). Verify both downloads before class.
3. Update the README with the actual repository and release links.
4. Run the tests on the computer used for class and open the PowerPoint there to check fonts and chart appearance.
5. Rehearse the five two-minute sections. Keep the browser dashboard open as a backup.

The slides present the delivered frozen snapshot. A live refresh can change reports and does not automatically regenerate the PowerPoint. Update slide values and notes before presenting a different snapshot.
