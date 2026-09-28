import pandas as pd

from src.presentation import comparison_subset, country_label, country_options, data_coverage


def test_country_label_includes_name_and_iso_code():
    assert country_label("IND") == "India (IND)"


def test_country_options_are_sorted_by_readable_label():
    options = country_options(["USA", "IND", "CHN"])
    assert [item["label"] for item in options] == ["China (CHN)", "India (IND)", "United States (USA)"]


def test_comparison_subset_filters_country_indicator_and_year():
    frame = pd.DataFrame({
        "country_code": ["IND", "USA", "IND"],
        "indicator_name": ["GDP Growth", "GDP Growth", "Inflation"],
        "observation_date": pd.to_datetime(["2020-01-01", "2020-01-01", "2021-01-01"]),
        "value": [5.0, 2.0, 4.0],
    })
    result = comparison_subset(frame, ["IND"], "GDP Growth", 2020, 2020)
    assert result[["country_code", "indicator_name"]].to_dict("records") == [{"country_code": "IND", "indicator_name": "GDP Growth"}]


def test_data_coverage_reports_dataset_scope():
    frame = pd.DataFrame({
        "country_code": ["IND", "USA", "IND"],
        "source": ["World Bank", "World Bank", "BLS"],
        "observation_date": pd.to_datetime(["2020-01-01", "2022-01-01", "2021-01-01"]),
    })
    coverage = data_coverage(frame)
    assert coverage == {"countries": 2, "observations": 3, "sources": 2,
                        "start": pd.Timestamp("2020-01-01"), "end": pd.Timestamp("2022-01-01")}
