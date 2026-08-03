"""Integration, cleaning, feature engineering, and reproducible demo data."""
import numpy as np
import pandas as pd
from .database import initialize_database, upsert_indicator, upsert_observations
from .fetchers import fetch_fred, fetch_world_bank, fetch_bls_employment

def load_sources(include_fred=True):
    initialize_database()
    loaders = [fetch_world_bank, fetch_bls_employment]
    if include_fred:
        loaders.append(fetch_fred)
    loaded = []
    for loader in loaders:
        try:
            for metadata, observations in loader():
                upsert_indicator(metadata)
                upsert_observations(clean_observations(observations))
            loaded.append(loader.__name__)
        except Exception as exc:
            print(f"Skipped {loader.__name__}: {exc}")
    return loaded

def clean_observations(frame):
    frame = frame.copy()
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame.dropna(subset=["value"]).drop_duplicates(["indicator_id", "country_code", "observation_date"])

def make_demo_data():
    """Create a varied five-country dataset when public APIs are unavailable."""
    initialize_database()
    rng = np.random.default_rng(42)
    dates = pd.date_range("2000-01-01", "2025-12-01", freq="MS")
    specs = {"CPI": ("Consumer Price Index", "Inflation", "Index", 170, .22),
             "UNRATE": ("Unemployment Rate", "Employment", "Percent", 4.8, 0),
             "GDP": ("Gross Domestic Product", "Growth", "Billions USD", 10000, 32),
             "FEDFUNDS": ("Federal Funds Rate", "Interest Rates", "Percent", 2.5, 0),
             "PCE": ("Personal Consumption Expenditures", "Consumer Spending", "Billions USD", 7000, 20),
             "WAGES": ("Average Hourly Earnings", "Wages", "USD", 14, .08)}
    countries = {"USA": (1.00, 0.0), "CAN": (.94, -.3), "DEU": (.86, .8), "JPN": (.78, .5), "GBR": (.91, .2)}
    for country, (scale, rate_shift) in countries.items():
        for key, (name, category, unit, base, trend) in specs.items():
            noise = rng.normal(0, 1.5 if key == "UNRATE" else .7, len(dates))
            adjusted_base = base + rate_shift if key in {"UNRATE", "FEDFUNDS"} else base * scale
            adjusted_trend = trend if key in {"UNRATE", "FEDFUNDS"} else trend * scale
            value = adjusted_base + adjusted_trend * np.arange(len(dates)) + noise
            if key in {"UNRATE", "FEDFUNDS"}:
                value = np.clip(value, .1, None)
            metadata = {"indicator_id": key, "indicator_name": name, "category": category, "unit": unit, "frequency": "Monthly", "source": "Demo"}
            rows = pd.DataFrame({"indicator_id": key, "country_code": country, "observation_date": dates, "value": value, "source": "Demo"})
            upsert_indicator(metadata)
            upsert_observations(rows)
