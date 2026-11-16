# Class requirements: evidence in this repository

The classroom board lists four topics. All four are implemented.

| Requirement | Evidence to show | How to demonstrate |
|---|---|---|
| 1. API ingestion | `src/pipeline.py`: request and extract; `config/project.json` | Explain ID pagination, HTTP retries, selected fields and checksummed JSON pages. Run the live pipeline when internet is available. |
| 2. Data infrastructure (GitHub + Docker) | This GitHub repository; `Dockerfile`; `compose.yaml`; `.github/workflows/ci.yml` | Build and run with Compose. Show persistent `data/` and `reports/` mounts, the SQLite database and CI results. |
| 3. Data manipulation (SQL) | Seven executable queries in `sql/`; `src/pipeline.py`: load and analyze | Show WHERE, GROUP BY, COUNT, SUM, calculated arrest shares and typed SQLite storage. The pipeline executes these files directly. |
| 4. Visualization | `src/visualize.py`; `reports/figures/`; `reports/dashboard.html`; presentation | Open the trend plots, hour/day heatmap, seasonal chart, community choropleth and arrest-share charts. |

The original assignment's measured DAG is implemented by `DAG` and `run` in `src/pipeline.py`, with durations/status in `reports/run.json`. Failure stops downstream tasks. The README documents setup, and frozen input supports exact replay years later. An `.ipynb` notebook is optional, not required by these four items.

## Suggested class demo

1. Show this checklist and the source API configuration.
2. Show the DAG in `docs/ARCHITECTURE.md` and run the unit tests.
3. Open `sql/annual.sql`, explain the bound cutoff parameter, and inspect the result in `reports/annual.csv`.
4. Show `Dockerfile` and `compose.yaml`, then the GitHub Actions results.
5. Open the offline dashboard and explain one finding and one limitation.

Avoid downloading the complete dataset during a short presentation. Use the supplied prepared reports or an offline replay. The separate raw snapshot has not been published as a GitHub Release asset; exact offline replay requires the separately supplied archive. A live extraction can differ because the source changes.
