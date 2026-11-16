-- Annual comparison: same calendar months in each year.
SELECT year, COUNT(*) AS incidents, SUM(arrest) AS arrests
FROM crimes
WHERE month <= :comparison_months
GROUP BY year
ORDER BY year;
