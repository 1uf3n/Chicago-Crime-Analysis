# SQLite data dictionary

The database has one fact table (`crimes`), two dimension tables (`crime_types`, `community_areas`) and a `metadata` table.

## crimes

| Column | Type | Meaning |
|---|---|---|
| id | INTEGER PRIMARY KEY | Source record ID, unique and positive |
| date | TEXT | Local incident datetime, ISO format |
| primary_type | TEXT | Source category, preserved; foreign key to `crime_types.primary_type` |
| description | TEXT | Source offense description |
| arrest | INTEGER | Required flag: 1 true, 0 false |
| domestic | INTEGER | Required domestic flag: 1 true, 0 false |
| community_area | INTEGER / NULL | Official code 1–77, otherwise unknown; foreign key to `community_areas.area_num` |
| latitude, longitude | REAL / NULL | Approximate coordinate pair within validation box |
| updated_on | TEXT / NULL | Source update timestamp |
| year, month | INTEGER | Derived calendar year and month |
| weekday | INTEGER | Monday=0 through Sunday=6 |
| hour | INTEGER | 0–23, source local time |
| season | TEXT | Winter Dec–Feb, Spring Mar–May, Summer Jun–Aug, Autumn Sep–Nov |

The raw selected fields do not include case numbers or block addresses. Data are public, but the published Git repository emphasizes aggregate outputs. `metadata` stores key/value JSON provenance.

## crime_types

| Column | Type | Meaning |
|---|---|---|
| type_id | INTEGER PRIMARY KEY | Surrogate key assigned in alphabetical order for each load |
| primary_type | TEXT UNIQUE | Source category exactly as published |

## community_areas

| Column | Type | Meaning |
|---|---|---|
| area_num | INTEGER PRIMARY KEY | Official community area number, 1–77 |
| name | TEXT UNIQUE | Community name from the boundary dataset `igwz-8jzy`, title case |

Both dimension tables are rebuilt from the same frozen snapshot on every load, so replay reproduces them exactly.
