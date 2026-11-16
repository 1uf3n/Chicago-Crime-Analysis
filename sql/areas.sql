-- Keep the NULL community group for reconciliation; omit it only on the map.
SELECT community_area, COUNT(*) AS incidents, SUM(arrest) AS arrests,
       1.0 * SUM(arrest) / COUNT(*) AS arrest_rate
FROM crimes
GROUP BY community_area
ORDER BY incidents DESC;
