-- Recorded arrest share, not conviction or official clearance rate.
SELECT primary_type, COUNT(*) AS incidents, SUM(arrest) AS arrests,
       1.0 * SUM(arrest) / COUNT(*) AS arrest_rate
FROM crimes
GROUP BY primary_type
ORDER BY incidents DESC;
