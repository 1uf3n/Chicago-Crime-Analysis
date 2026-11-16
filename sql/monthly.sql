-- Full monthly record counts; incomplete years remain visible.
SELECT year, month, COUNT(*) AS incidents
FROM crimes
GROUP BY year, month
ORDER BY year, month;
