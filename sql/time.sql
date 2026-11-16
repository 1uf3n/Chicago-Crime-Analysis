-- Local incident time; Monday=0, Sunday=6.
SELECT weekday, hour, COUNT(*) AS incidents
FROM crimes
GROUP BY weekday, hour
ORDER BY weekday, hour;
