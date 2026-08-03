import pandas as pd

def enrich(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy().sort_values(["indicator_id", "country_code", "observation_date"])
    frame["year"] = frame.observation_date.dt.year
    frame["pct_change"] = frame.groupby(["indicator_id", "country_code"])["value"].pct_change(12) * 100
    frame["z_score"] = frame.groupby(["indicator_id", "country_code"])["value"].transform(
        lambda x: (x - x.mean()) / x.std() if x.std() else 0)
    return frame

def correlation_matrix(frame: pd.DataFrame, country="USA") -> pd.DataFrame:
    subset = frame[frame.country_code == country].copy()
    return subset.pivot_table(index="observation_date", columns="indicator_name", values="value", aggfunc="mean").corr()
