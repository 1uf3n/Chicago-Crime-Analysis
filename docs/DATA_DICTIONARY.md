# SQLite data dictionary

| Column | Type | Meaning |
|---|---|---|
| id | INTEGER PRIMARY KEY | Source record ID, unique and positive |
| date | TEXT | Local incident datetime, ISO format |
| primary_type | TEXT | Source category, preserved |
| description | TEXT | Source offense description |
| arrest | INTEGER | Required flag: 1 true, 0 false |
| domestic | INTEGER | Required domestic flag: 1 true, 0 false |
| community_area | INTEGER / NULL | Official code 1–77, otherwise unknown |
| latitude, longitude | REAL / NULL | Approximate coordinate pair within validation box |
| updated_on | TEXT / NULL | Source update timestamp |
| year, month | INTEGER | Derived calendar year and month |
| weekday | INTEGER | Monday=0 through Sunday=6 |
| hour | INTEGER | 0–23, source local time |
| season | TEXT | Winter Dec–Feb, Spring Mar–May, Summer Jun–Aug, Autumn Sep–Nov |

The raw selected fields do not include case numbers or block addresses. Data are public, but the published Git repository emphasizes aggregate outputs. `metadata` stores key/value JSON provenance.
