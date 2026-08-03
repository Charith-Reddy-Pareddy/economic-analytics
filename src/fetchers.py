"""Public API clients. Failed API calls are handled by the loader's demo fallback."""
import requests
import pandas as pd
from .config import FRED_API_KEY, BLS_API_KEY

FRED_SERIES = {
    "CPIAUCSL": ("Consumer Price Index", "Inflation", "Index", "Monthly"),
    "UNRATE": ("Unemployment Rate", "Employment", "Percent", "Monthly"),
    "GDP": ("Gross Domestic Product", "Growth", "Billions USD", "Quarterly"),
    "FEDFUNDS": ("Federal Funds Rate", "Interest Rates", "Percent", "Monthly"),
    "PCE": ("Personal Consumption Expenditures", "Consumer Spending", "Billions USD", "Monthly"),
    "CES0500000003": ("Average Hourly Earnings", "Wages", "USD", "Monthly"),
}

def fetch_fred(start="2000-01-01"):
    if not FRED_API_KEY or FRED_API_KEY.startswith("replace_"):
        raise RuntimeError("FRED_API_KEY is not configured")
    output = []
    for series_id, (name, category, unit, frequency) in FRED_SERIES.items():
        response = requests.get("https://api.stlouisfed.org/fred/series/observations", params={
            "series_id": series_id, "api_key": FRED_API_KEY, "file_type": "json", "observation_start": start}, timeout=30)
        response.raise_for_status()
        values = [{"indicator_id": series_id, "country_code": "USA", "observation_date": r["date"],
                   "value": pd.to_numeric(r["value"], errors="coerce"), "source": "FRED"} for r in response.json()["observations"]]
        output.append(({"indicator_id": series_id, "indicator_name": name, "category": category, "unit": unit, "frequency": frequency, "source": "FRED"}, pd.DataFrame(values)))
    return output

WORLD_BANK = {
    "NY.GDP.MKTP.KD.ZG": ("GDP Growth", "Growth", "Percent", "Annual"),
    "FP.CPI.TOTL.ZG": ("Inflation, consumer prices", "Inflation", "Percent", "Annual"),
    "SL.UEM.TOTL.ZS": ("Unemployment", "Employment", "Percent", "Annual"),
    "NE.CON.PRVT.ZS": ("Household consumption", "Consumer Spending", "Percent GDP", "Annual"),
}

def fetch_world_bank(start_year=2000):
    """Retrieve annual indicators for all World Bank member economies, excluding aggregates."""
    catalog = requests.get("https://api.worldbank.org/v2/country", params={"format": "json", "per_page": 400}, timeout=30)
    catalog.raise_for_status()
    country_rows = catalog.json()[1]
    valid_codes = {row["id"] for row in country_rows if row.get("region", {}).get("id") != "NA" and len(row["id"]) == 3}
    output = []
    for code, (name, category, unit, frequency) in WORLD_BANK.items():
        try:
            response = requests.get(f"https://api.worldbank.org/v2/country/all/indicator/{code}",
                params={"format": "json", "date": f"{start_year}:2025", "per_page": 20000}, timeout=60)
            response.raise_for_status()
            body = response.json()
            rows = body[1] if len(body) > 1 else []
            records = [{"indicator_id": f"WB_{code}", "country_code": row["countryiso3code"],
                        "observation_date": f"{row['date']}-01-01", "value": row["value"], "source": "World Bank"}
                       for row in rows if row["countryiso3code"] in valid_codes and row["value"] is not None]
            output.append(({"indicator_id": f"WB_{code}", "indicator_name": name, "category": category,
                            "unit": unit, "frequency": frequency, "source": "World Bank"}, pd.DataFrame(records)))
        except requests.RequestException as exc:
            print(f"Skipped World Bank series {code}: {exc}")
    if not output:
        raise RuntimeError("World Bank returned no international records")
    return output

def fetch_bls_employment():
    headers = {"Content-Type": "application/json"}
    payload = {"seriesid": ["CES0000000001"], "startyear": "2000", "endyear": "2025"}
    if BLS_API_KEY: payload["registrationkey"] = BLS_API_KEY
    response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    series = response.json()["Results"]["series"][0]["data"]
    rows = [{"indicator_id": "BLS_EMPLOYMENT", "country_code": "USA", "observation_date": f"{r['year']}-{r['period'][1:]}-01", "value": float(r["value"]), "source": "BLS"} for r in series if r["period"].startswith("M")]
    meta = {"indicator_id": "BLS_EMPLOYMENT", "indicator_name": "Total Nonfarm Employment", "category": "Employment", "unit": "Thousands of persons", "frequency": "Monthly", "source": "BLS"}
    return [(meta, pd.DataFrame(rows))]
