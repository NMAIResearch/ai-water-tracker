-- AI Data-Centre Water: SQL analysis layer (DuckDB)
-- The shaping half of the project; the Power BI dashboard is the presentation half.
-- Runs locally, no server. Install: python3 -m pip install --user duckdb  (or the duckdb CLI)
-- Each query reads the CSV directly, no import step.
--   CLI:     duckdb  then  .read queries.sql
--   Python:  duckdb.sql("<paste a query>")

-- 1. Average water-consumption index per operator (operators with 2+ sites)
SELECT Operator, COUNT(*) AS sites, ROUND(AVG(WCI), 2) AS avg_wci
FROM read_csv_auto('ai_water_sites.csv')
GROUP BY Operator
HAVING COUNT(*) >= 2
ORDER BY avg_wci DESC;

-- 2. Primary-verified sites, highest index first
SELECT Operator, City, WCI, Cooling
FROM read_csv_auto('ai_water_sites.csv')
WHERE Status = 'Primary-verified'
ORDER BY WCI DESC;

-- 3. Window function: rank each site by WCI within its operator (top 2 each)
SELECT Operator, City, WCI,
       RANK() OVER (PARTITION BY Operator ORDER BY WCI DESC) AS rank_in_operator
FROM read_csv_auto('ai_water_sites.csv')
QUALIFY rank_in_operator <= 2
ORDER BY Operator, rank_in_operator;

-- 4. Measured vs excluded: water demand that counts vs planning-only figures
SELECT CASE WHEN Status = 'Primary-verified' THEN 'counts' ELSE 'excluded' END AS bucket,
       COUNT(*) AS sites,
       ROUND(SUM(WaterDemand_ML_d), 1) AS total_ML_per_day
FROM read_csv_auto('ai_water_sites.csv')
GROUP BY bucket
ORDER BY total_ML_per_day DESC;

-- 5. Hydro-coupled sites: water use that also draws on a dammed reservoir
SELECT Operator, City, Reservoir, Dam, WCI
FROM read_csv_auto('ai_water_sites.csv')
WHERE HydroCoupled = 'Yes'
ORDER BY WCI DESC;
