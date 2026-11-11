# Methodology and interpretation

## Unit and source
Each row is one source record identified by the Crimes API's `id`. Count source records rather than unique offenders or households. The City notes that murders can have a record per victim, which is an exception to incident-level counting. Source records can be corrected, deleted, reclassified or reported late. The dataset reflects recorded incidents, not all crime. Approximate locations and historical classification changes limit interpretation.

The official source explicitly cautions against comparisons over time because preliminary reports and classifications can change. Our year-by-year charts are exploratory descriptions of the records present in one extraction, not validated estimates of changes in underlying crime or official CPD trend statistics. Matching calendar months addresses exposure duration only and does not resolve this source limitation. The source omits the most recent seven days.

## Extraction
Use an explicit half-open incident-date interval. Query the initial count and maximum ID, then fetch ascending IDs with `id > last_id AND id <= initial_max_id`. This avoids OFFSET drift and caps new high-ID additions. Store selected source fields as compressed JSON with page query parameters and SHA-256 hashes. Check strictly increasing IDs and total row reconciliation. These checks cannot create a transactional API snapshot: edits to already-existing rows during download can still produce a mixed-time extract. The frozen downloaded pages define our reproducible observation.

## Cleaning and loading
Required ID, datetime, category and boolean fields fail the run when malformed. Keep the source category spelling without merging categories. Convert booleans to 0/1. Map missing, zero or invalid community codes to SQL NULL. Coordinates outside a conservative Chicago bounding box become NULL as a pair, but keep the incident. Derive calendar year/month, Monday=0 weekday, hour and meteorological season from source local time without inventing a UTC offset. Winter is December–February.

Load into a staged database with a primary key, boolean constraints and indices. Duplicated IDs fail rather than silently disappearing. Atomically replace the published database after successful load. Then check SQLite integrity and reconcile the final count with the frozen manifest. Reports are overwritten only when their tasks run successfully; on failure inspect `run.json` before using any existing report, because older report files may remain.

## Research questions
1. Temporal patterns: pooled weekday/hour counts, monthly totals, and season counts divided by calendar days in complete years (2020–2025). Midnight spikes may reflect default or approximate incident times. Pooled counts are descriptive; do not infer causes or individual risk.
2. Geography: counts by official community area with an offline choropleth. Exclude unknown codes from map ranking but disclose their count. Count differences reflect population, visitors, land use and reporting as well as crime. They are not population-normalized rates.
3. Trends: January–October in each year for annual and category-by-year comparisons. Keep complete monthly series as a separate output. Leap years contribute one extra February day; annual totals are not normalized by days. Recent records remain subject to reporting lag and revisions even after excluding the partial month.
4. Recorded arrests: `sum(arrest) / count(records)` for each category and community. Each included row has a validated boolean flag. Report numerator and denominator, and emphasize categories/communities with large denominators. This is a snapshot share of incidents marked arrest, not convictions, individual arrests, causal policing effectiveness, or an official clearance rate. Later changes in arrest flags and different case maturity affect comparisons.

## Geographic reference
Join `community_area` to the boundary dataset's `area_num_1`. Preserve polygon holes and all multipolygon parts. Render a local equirectangular-style coordinate display; it is a descriptive map, not a navigation product. No external basemap or network request is needed to view it. Reference boundaries are captured in the same raw snapshot and checksummed.

## Automation and DAG
The topological runner checks prerequisites before running each task. It measures extract, transform/load, validate, analyze and visualize separately and records failure before raising. Monthly GitHub Actions and manual dispatch run the same script and archive results. The default project interval remains fixed for comparability; this automation refreshes corrections to that interval rather than extending it. Automatic schedules may be disabled by GitHub for inactive repositories and are not guaranteed execution times.

## Longevity and limitations
Offline replay is supported by archived input, stable SQL and standard-library Python. The project has no third-party Python package dependencies. The Docker image tag tracks a Python minor version and is not an immutable environment lock. Preserve its digest if bit-for-bit environment recreation matters. SQLite file bytes, run times and HTML metadata need not be identical across runtimes, while the analytical totals should match the frozen inputs. The PowerPoint is a frozen presentation of the supplied snapshot and does not automatically update after a new live extraction.
