| Requirement | Evidence to show | How to demonstrate |
|---|---|---|
| 1. API ingestion | `src/pipeline.py`: request and extract; `config/project.json` | Explain ID pagination, HTTP retries, selected fields and checksummed JSON pages. Run the live pipeline when internet is available. |
| 2. Data infrastructure (GitHub + Docker) | This GitHub repository; `Dockerfile`; `compose.yaml`; `.github/workflows/ci.yml` | Build and run with Compose. Show persistent `data/` and `reports/` mounts, the SQLite database and CI results. |
| 3. Data manipulation (SQL) | Seven executable queries in `sql/`; `src/pipeline.py`: load and analyze | Show WHERE, GROUP BY, COUNT, SUM, calculated arrest shares and typed SQLite storage. The pipeline executes these files directly. |
| 4. Visualization | `src/visualize.py`; `reports/figures/`; `reports/dashboard.html`; presentation | Open the trend plots, hour/day heatmap, seasonal chart, community choropleth and arrest-share charts. |
