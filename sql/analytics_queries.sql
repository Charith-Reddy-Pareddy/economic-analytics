-- Latest available value for each indicator and country
WITH ranked AS (
  SELECT o.*, ROW_NUMBER() OVER (
    PARTITION BY indicator_id, country_code ORDER BY observation_date DESC
  ) AS rank
  FROM observations o
)
SELECT r.country_code, i.indicator_name, r.observation_date, r.value, i.unit
FROM ranked r JOIN indicators i USING(indicator_id)
WHERE r.rank = 1
ORDER BY r.country_code, i.category;

-- Annual average indicators, useful for regional/country comparisons
SELECT country_code, indicator_id, SUBSTR(observation_date, 1, 4) AS year,
       ROUND(AVG(value), 2) AS annual_average
FROM observations
GROUP BY country_code, indicator_id, year
ORDER BY country_code, indicator_id, year;

-- Potential outliers: observations more than two standard deviations from their series mean
WITH stats AS (
  SELECT indicator_id, country_code, AVG(value) AS avg_value,
         AVG(value * value) - AVG(value) * AVG(value) AS variance
  FROM observations GROUP BY indicator_id, country_code
)
SELECT o.*
FROM observations o JOIN stats s USING(indicator_id, country_code)
WHERE ABS(o.value - s.avg_value) > 2 * SQRT(s.variance);
