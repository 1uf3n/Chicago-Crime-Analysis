-- Crime-category trends over comparable calendar months.
SELECT year, primary_type, COUNT(*) AS incidents, SUM(arrest) AS arrests
FROM crimes
WHERE month <= :comparison_months
GROUP BY year, primary_type
ORDER BY year, primary_type;
