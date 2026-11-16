# SQL analysis

These are the actual SQL files executed by `src/pipeline.py:analyze`, not duplicate examples. They query the SQLite `crimes` table after extraction and cleaning. The pipeline binds `comparison_months` and `last_year` from the configured exclusive cutoff. The current study uses 10 and 2026.

| File | SQL concepts | Output |
|---|---|---|
| annual.sql | WHERE, GROUP BY, COUNT, SUM, ORDER BY | Comparable annual totals |
| category_year.sql | Multiple grouping columns | Category/year trends |
| monthly.sql | Calendar grouping | Monthly counts |
| time.sql | Weekday/hour grouping | Temporal heatmap |
| season.sql | Filter complete years | Seasonal counts |
| areas.sql | NULL grouping, numeric division | Community counts and arrest shares |
| categories.sql | Aggregation and calculated ratio | Category arrest shares |

Run the pipeline first to create `data/crimes.sqlite`. Example using Python, with no SQLite CLI dependency:

```python
import sqlite3
from pathlib import Path

with sqlite3.connect("data/crimes.sqlite") as db:
    query = Path("sql/annual.sql").read_text()
    for row in db.execute(query, {"comparison_months": 10}):
        print(row)
```

Counts represent source records. Arrest share is SUM(arrest)/COUNT(*), not a conviction or official clearance rate. Spatial NULLs stay in aggregate tables. Seasonal day normalization takes place in Python after SQL aggregation.
