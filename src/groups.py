"""Named country groups used for transparent comparative analysis."""
import pandas as pd

G20 = frozenset("ARG AUS BRA CAN CHN FRA DEU IND IDN ITA JPN KOR MEX RUS SAU ZAF TUR GBR USA".split())
ADVANCED_ECONOMIES = frozenset("AUS AUT BEL CAN DNK FIN FRA DEU ISL IRL ITA JPN KOR LUX NLD NZL NOR PRT ESP SWE CHE GBR USA".split())

def group_trends(frame: pd.DataFrame, indicator: str, groups=None) -> pd.DataFrame:
    """Return equal-weight country averages for transparent benchmark groups."""
    groups = groups or {"G20": G20, "Advanced economies": ADVANCED_ECONOMIES}
    rows = []
    for group_name, codes in groups.items():
        subset = frame[(frame["indicator_name"] == indicator) & frame["country_code"].isin(codes)]
        grouped = subset.groupby("observation_date", as_index=False)["value"].mean()
        grouped["group"] = group_name
        grouped["countries_observed"] = subset.groupby("observation_date")["country_code"].nunique().values
        rows.append(grouped)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
