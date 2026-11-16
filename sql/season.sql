-- Exclude the final partial year. Python divides these counts by calendar days.
SELECT season, COUNT(*) AS incidents
FROM crimes
WHERE year < :last_year
GROUP BY season
ORDER BY season;
