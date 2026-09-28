"""Presentation helpers for country-aware dashboard controls."""
from __future__ import annotations

import pandas as pd
import pycountry


def country_label(code: str) -> str:
    """Return a readable country name while preserving the ISO-3 code."""
    country = pycountry.countries.get(alpha_3=code)
    return f"{country.name} ({code})" if country else code


def country_options(codes: list[str]) -> list[dict[str, str]]:
    """Create alphabetically ordered Dash dropdown options."""
    options = [{"label": country_label(code), "value": code} for code in codes]
    return sorted(options, key=lambda option: option["label"])


def data_coverage(frame: pd.DataFrame) -> dict[str, object]:
    """Summarize the loaded dataset for transparent dashboard reporting."""
    if frame.empty:
        return {"countries": 0, "observations": 0, "sources": 0, "start": None, "end": None}
    return {
        "countries": frame["country_code"].nunique(),
        "observations": len(frame),
        "sources": frame["source"].nunique(),
        "start": frame["observation_date"].min(),
        "end": frame["observation_date"].max(),
    }


def comparison_subset(frame, countries: list[str], indicator: str, start_year: int, end_year: int):
    """Select one annual indicator across countries for a like-for-like comparison."""
    subset = frame[
        frame["country_code"].isin(countries)
        & frame["indicator_name"].eq(indicator)
        & frame["observation_date"].dt.year.between(start_year, end_year)
    ].copy()
    subset["country_name"] = subset["country_code"].map(country_label)
    return subset
