# Chicago Crime Patterns & Trends Analysis (2020–2026)

**Team:** Lufan (Rebecca) Wang, Wangying Zhang, Yinuo Zhu, Zhiyi Liu, Hongcheng Fu.

An end-to-end, dependency-free Python pipeline: Chicago's public API → compressed raw snapshots → validated SQLite database → SQL analysis → offline charts and community choropleth. A dependency-aware DAG records task timing and failure state.

## Quick start

Requires Python **3.9 or newer**, internet for a fresh extraction, and approximately 2 GB of free disk space. No pip installation or API secret is required. Run commands from this repository's root.

```bash
python3 -m unittest discover -s tests -v
python3 src/pipeline.py
```

On Windows use `python` instead of `python3`. The full download can take several minutes or longer depending on API load. Requests retry transient failures six times. Optional: set `SOCRATA_APP_TOKEN` to your own Socrata application token to improve throttling limits. Never commit the token.

Open **reports/dashboard.html** directly in a browser. It works offline and includes ten charts, including the community choropleth. Hover over map polygons for names and counts. Prepared results are included, so you can inspect findings before downloading data.

## Classroom requirements

All four topics are covered: **API ingestion, GitHub + Docker infrastructure, SQL manipulation, and visualization**.

With Docker running:

```bash
docker compose build
docker compose run --rm pipeline python -m unittest discover -s tests -v
docker compose run --rm pipeline
```

The database and reports persist in local `data/` and `reports/`. See [Docker instructions](docs/DOCKER.md) for offline replay and [SQL documentation](sql/README.md) for runnable queries. Python-only execution above remains supported. CI runs tests and builds the Docker image; no scheduled live refresh is configured.

## Exact offline replay

The separate `chicago-crime-snapshot.zip` delivery contains the frozen raw snapshot. Extract it into the repository root so that `data/raw/snapshot-2026-11-10/manifest.json` exists, then run:

```bash
python3 src/pipeline.py --snapshot data/raw/snapshot-2026-11-10
```

Replay checks every raw page's SHA-256, rebuilds SQLite, reruns SQL and recreates charts without internet. It replaces `data/crimes.sqlite` only after a successful load. Repeated replay does not duplicate records. Reports and metrics are regenerated. Retain the snapshot ZIP as a GitHub Release asset or in durable object storage, not ordinary Git. The snapshot is essential for exact historical reproduction. A future live API pull can yield revised results.

## Scope and comparisons

`config/project.json` fixes the incident window to **2020-01-01 inclusive through 2026-11-01 exclusive**, using Chicago's local incident timestamps. Annual and category-year comparisons use January–October of every year. Full-window community and arrest summaries include all extracted months. Seasonality uses complete years 2020–2025 and divides counts by actual calendar days. Do not interpret January–October 2026 as a full year. The source cautions against comparisons over time, so these are exploratory record summaries rather than official crime trend estimates. See [methodology](docs/METHODOLOGY.md).

## Repository guide

- `src/pipeline.py`: API retries, keyset pagination, checksums, cleaning, SQLite load, validation, SQL, measured DAG
- `src/visualize.py`: self-contained SVG charts and HTML dashboard
- `tests/`: correctness and failure-path checks
- `config/project.json`: fixed API endpoints, interval and page size
- `reports/`: prepared aggregate CSV/JSON, charts, run timings and findings
- `docs/`: architecture, methodology, data dictionary and presentation guide
- `presentation/`: final PowerPoint
- `sql/`: eight executable SQL queries used directly by the pipeline
- `Dockerfile` and `compose.yaml`: container runtime with persistent outputs
- `.github/workflows/ci.yml`: Python tests, Compose validation and Docker build/tests

## Database schema

`data/crimes.sqlite` is normalized into one fact table and two dimension tables:

| Table | Grain | Keys |
|---|---|---|
| `crimes` | One row per source record ID | `id` primary key; `primary_type` → `crime_types`; `community_area` → `community_areas` |
| `crime_types` | One row per source category | `type_id` primary key; `primary_type` unique |
| `community_areas` | One row per official community area (77) | `area_num` primary key; `name` unique |
| `metadata` | Key/value provenance | Stores the frozen snapshot manifest |

Validation runs `PRAGMA foreign_key_check` and fails the DAG if any record points to an unknown category or community. Unknown community codes stay NULL, which the foreign key allows. See the [data dictionary](docs/DATA_DICTIONARY.md).

## Database queries

Use any SQLite client, or Python's built-in `sqlite3` module. Example:

```sql
SELECT year, COUNT(*) AS incidents,
       ROUND(100.0 * SUM(arrest) / COUNT(*), 2) AS recorded_arrest_pct
FROM crimes WHERE month <= 10 GROUP BY year ORDER BY year;
```

`reports/run.json` records seconds and status for each executed DAG task. A failing task stops descendants. `reports/quality.json` reconciles row count and reports missing geography. A fresh extraction uses a new immutable directory. Failed download directories lack a completed manifest and cannot be replayed. Restart a failed live run with a fresh command.

## Reproducibility in five years

The runtime needs only Python's standard library. The Dockerfile fixes the Python minor series; archive a built image by digest for stronger environment preservation. Keep the raw ZIP, its checksum, code version and prepared report files together. A live service cannot be guaranteed to exist in five years. Frozen data plus offline replay removes that dependency. Source schemas, endpoints and category definitions may change, so live refreshes intentionally fail when required fields are invalid. See docs for remaining limitations.

## GitHub repository

Project repository: https://github.com/1uf3n/Chicago-Crime-Analysis

Download or clone this repository, then follow the quick-start commands above. The PowerPoint is in `presentation/`.

The frozen raw snapshot is distributed separately as `chicago-crime-snapshot.zip`. It is not stored in ordinary Git, and a GitHub Release asset has not yet been published. Use the separately provided archive for exact offline replay, or run the API extraction for a fresh dataset.

## Sources and attribution

- Crimes: https://data.cityofchicago.org/resource/ijzp-q8t2.json
- Catalog and limitations: https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2
- Community area boundaries: https://data.cityofchicago.org/resource/igwz-8jzy.json
- API documentation: https://dev.socrata.com/docs/queries/

Code is MIT licensed. Data remain subject to the City of Chicago's terms. Do not infer individual guilt, neighborhood safety or policing effectiveness from these aggregates.
