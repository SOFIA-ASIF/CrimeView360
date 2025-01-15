-- 1. What are the most common crime types in each district?":
        WITH CrimeCounts AS (
            SELECT 
                l.District,
                c.Type,
                COUNT(*) AS TotalIncidents
            FROM Incident AS i
            JOIN Location AS l ON i.Location_ID = l.ID
            JOIN Crime AS c ON i.Crime_ID = c.ID
            GROUP BY 
                l.District,
                c.Type
        ),
        MostCommonCrimes AS (
            SELECT 
                District,
                Type,
                TotalIncidents,
                RANK() OVER (PARTITION BY District ORDER BY TotalIncidents DESC) AS Ranks
            FROM CrimeCounts
        )
        SELECT 
            District,
            Type AS MostCommonCrime,
            TotalIncidents
        FROM MostCommonCrimes
        WHERE Ranks = 1
        ORDER BY District;


-- 2. What is the distribution of crime incidents by time of day?
        SELECT 
            HOUR(STR_TO_DATE(i.Date, '%m/%d/%Y %H:%i')) AS HourOfDay,
            COUNT(*) AS TotalIncidents
        FROM Incident AS i
        WHERE i.Date IS NOT NULL
        GROUP BY HourOfDay
        ORDER BY HourOfDay;
       


-- 3. What is the distribution of incidents across different weeks for each crime type?
SELECT
            MONTHNAME(STR_TO_DATE(i.Date, '%m/%d/%Y %H:%i')) AS MonthName,
            WEEK(STR_TO_DATE(i.Date, '%m/%d/%Y %H:%i')) - WEEK(DATE_SUB(STR_TO_DATE(i.Date, '%m/%d/%Y %H:%i'), INTERVAL DAYOFMONTH(STR_TO_DATE(i.Date, '%m/%d/%Y %H:%i')) - 1 DAY)) + 1 AS WeekOfMonth,
            c.Type,
            COUNT(*) AS TotalIncidents
        FROM Incident AS i
        JOIN Crime AS c ON i.Crime_ID = c.ID
        WHERE i.Date IS NOT NULL
        GROUP BY
            MonthName,
            WeekOfMonth,
            c.Type
        ORDER BY
            MonthName,
            WeekOfMonth,
            c.Type;
