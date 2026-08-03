# Economic Pulse Analytics

An end-to-end Python economic-intelligence platform for studying inflation, employment, economic growth, interest rates, wages, and consumer spending. It combines public API ingestion, SQLite, Pandas/NumPy analysis, and an interactive Plotly Dash dashboard.

## Features

- Integrates FRED, World Bank, and BLS public economic data into normalized SQLite tables.
- Cleans missing values, removes duplicates, aligns time series, and engineers year-over-year changes and z-score anomaly signals.
- Supports correlations, trends, country comparisons, downloadable data, KPI cards, a searchable table, and visual analysis.
- Runs with synthetic demo data if an API is unavailable, so reviewers can launch it immediately.

## Architecture

```
Public APIs → fetchers.py → cleaning/feature engineering → SQLite → Dash dashboard
```

## Quick start

1. Install Python 3.10+.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate       # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and place your **newly regenerated** FRED key in it.
4. Load public data:
   ```bash
   python scripts/load_data.py
   ```
5. Start the dashboard:
   ```bash
   python app.py
   ```
6. Open `http://127.0.0.1:8050` in your browser.

## Database model

`indicators` holds canonical metadata. `observations` stores one country, indicator, date, value, and source per row. The primary key prevents duplicate observations during repeated loads.

## GitHub publishing

Never commit `.env` or `data/economic_pulse.db`. Both are excluded by `.gitignore`.

```bash
git init
git add .
git commit -m "Build Economic Pulse Analytics dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/economic-pulse-analytics.git
git push -u origin main
```

## Data sources

- FRED: US CPI, unemployment, GDP, federal funds rate, PCE, and earnings.
- World Bank: international GDP growth, inflation, unemployment, and consumption.
- BLS: US total nonfarm employment.

Public APIs can revise historical values. This project is for analysis and education, not investment advice.
