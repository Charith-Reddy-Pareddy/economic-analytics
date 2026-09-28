import pandas as pd
from src.groups import group_trends

def test_group_trends_returns_equal_weight_group_means():
    frame = pd.DataFrame({"country_code":["USA","CAN","IND"], "indicator_name":["GDP Growth"]*3, "observation_date":pd.to_datetime(["2023-01-01"]*3), "value":[2.0,4.0,6.0]})
    result = group_trends(frame, "GDP Growth", {"North America":{"USA","CAN"}})
    assert result.loc[0, "value"] == 3.0
    assert result.loc[0, "countries_observed"] == 2
