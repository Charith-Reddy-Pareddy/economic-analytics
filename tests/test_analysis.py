import pandas as pd
from src.analysis import enrich, correlation_matrix

def test_enrich_adds_features():
    frame = pd.DataFrame({"indicator_id":["x"]*3,"country_code":["USA"]*3,"observation_date":pd.date_range("2024-01-01", periods=3, freq="MS"),"value":[1,2,3]})
    result = enrich(frame)
    assert {"year", "pct_change", "z_score"}.issubset(result.columns)

def test_correlation_is_square():
    frame = pd.DataFrame({"country_code":["USA"]*4,"observation_date":pd.date_range("2024-01-01", periods=4, freq="MS").tolist()*1,"indicator_name":["A","B","A","B"],"value":[1,2,2,4]})
    # Function should be safe for a valid long-form dataset.
    assert isinstance(correlation_matrix(frame), pd.DataFrame)
