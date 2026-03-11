-- Baseball Player Analysis
-- Demonstrates SQL window functions using MLB batting data
-- Data: Mike Trout, Aaron Judge, Mookie Betts (2019-2023)

-- 1. Regional/Player Total Home Runs
SELECT
    playerID,
    yearID,
    HR,
    SUM(HR) OVER (PARTITION BY playerID) AS career_hr
FROM batting;

-- 2. Top HR Season Per Player
WITH ranked AS (
    SELECT
        playerID,
        yearID,
        HR,
        ROW_NUMBER() OVER (PARTITION BY playerID ORDER BY HR DESC) AS rank
    FROM batting
)
SELECT playerID, yearID, HR
FROM ranked
WHERE rank = 1;

-- 3. Year-Over-Year HR Change
SELECT
    playerID,
    yearID,
    HR,
    HR - LAG(HR) OVER (PARTITION BY playerID ORDER BY yearID) AS yoy_hr_change
FROM batting;

-- 4.Year-Over-Year Batting Average Change
SELECT
    playerID,
    yearID,
    AVG,
    ROUND(AVG - LAG(AVG) OVER (PARTITION BY playerID ORDER BY yearID), 3) AS yoy_avg_change
FROM batting;
