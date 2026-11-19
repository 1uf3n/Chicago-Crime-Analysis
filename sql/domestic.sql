-- Share of records flagged domestic-related, same calendar months in each year.
SELECT year, COUNT(*) AS incidents, SUM(domestic) AS domestic,
       1.0 * SUM(domestic) / COUNT(*) AS domestic_rate
FROM crimes
WHERE month <= :comparison_months
GROUP BY year
ORDER BY year;
