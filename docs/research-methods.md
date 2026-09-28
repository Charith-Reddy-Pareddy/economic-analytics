# Research and Reproducibility Notes

## Research question

How do inflation, unemployment, GDP growth, household consumption, interest rates, and wage indicators co-move across countries and over time?

## Study design

The project uses a country-year (international) and US time-series (monthly or quarterly where available) observational design. It is intended for descriptive analysis and hypothesis generation, not causal identification.

## Data provenance

| Source | Coverage | Use |
| --- | --- | --- |
| World Bank | International annual indicators | GDP growth, CPI inflation, unemployment, household consumption |
| FRED | US historical macroeconomic series | CPI, unemployment, GDP, policy rate, PCE, earnings |
| BLS | US labor market series | Total nonfarm employment |

Every stored observation includes its source, indicator, country code, observation date, and unit. API responses may be revised; record the extraction date for a thesis submission or replicate the load before analysis.

## Data processing

1. Normalize observations to a tidy long format.
2. Remove duplicates by indicator, country, and date.
3. Preserve missing values during ingestion; analytical views exclude missing numeric observations explicitly.
4. Create year-over-year percent changes for monthly series and z-scores for anomaly screening.
5. Compare only like-for-like country indicators: annual World Bank series should not be merged directly with monthly US series without aggregation.

## Statistical interpretation

Correlation is descriptive. It does not establish causation, control for confounders, or resolve timing differences between indicators. Any thesis extension should pre-register hypotheses, state the sample window, assess stationarity, test lag structures, and use an explicit identification strategy.

## Reproducibility checklist

- Pin package versions in `requirements.txt`.
- Keep API keys in `.env`; never commit them.
- Run `python scripts/load_data.py` to refresh sources.
- Run `python -m pytest` before publishing changes.
- Export filtered dashboard data alongside figures and report the source/extraction date.
