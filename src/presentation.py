"""Presentation helpers for country-aware dashboard controls."""
from __future__ import annotations

COUNTRY_NAMES = {
    "BRA": "Brazil", "CHN": "China", "DEU": "Germany", "GBR": "United Kingdom",
    "IND": "India", "JPN": "Japan", "USA": "United States",
}


def country_label(code: str) -> str:
    """Return a readable country name while preserving the ISO-3 code."""
    name = COUNTRY_NAMES.get(code)
    return f"{name} ({code})" if name else code


def country_options(codes: list[str]) -> list[dict[str, str]]:
    """Create alphabetically ordered Dash dropdown options."""
    options = [{"label": country_label(code), "value": code} for code in codes]
    return sorted(options, key=lambda option: option["label"])


def comparison_subset(frame, countries: list[str], indicator: str, start_year: int, end_year: int):
    """Select one annual indicator across countries for a like-for-like comparison."""
    subset = frame[
        frame["country_code"].isin(countries)
        & frame["indicator_name"].eq(indicator)
        & frame["observation_date"].dt.year.between(start_year, end_year)
    ].copy()
    subset["country_name"] = subset["country_code"].map(country_label)
    return subset
