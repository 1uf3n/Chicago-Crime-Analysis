-- Keep the NULL community group for reconciliation; omit it only on the map.
-- LEFT JOIN keeps unknown codes, whose community_name is NULL.
SELECT c.community_area, a.name AS community_name,
       COUNT(*) AS incidents, SUM(c.arrest) AS arrests,
       1.0 * SUM(c.arrest) / COUNT(*) AS arrest_rate
FROM crimes AS c
LEFT JOIN community_areas AS a ON a.area_num = c.community_area
GROUP BY c.community_area, a.name
ORDER BY incidents DESC;
