"""Public API clients for the Economic Pulse data pipeline."""
from itertools import islice
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
WORLD_BANK = {
    "NY.GDP.MKTP.KD.ZG": ("GDP Growth", "Growth", "Percent", "Annual"),
    "FP.CPI.TOTL.ZG": ("Inflation, consumer prices", "Inflation", "Percent", "Annual"),
    "SL.UEM.TOTL.ZS": ("Unemployment", "Employment", "Percent", "Annual"),
    "NE.CON.PRVT.ZS": ("Household consumption", "Consumer Spending", "Percent GDP", "Annual"),
}

def chunks(values, size):
    iterator = iter(values)
    while batch := list(islice(iterator, size)):
        yield batch

def fetch_world_bank_catalog(session=requests):
    response = session.get("https://api.worldbank.org/v2/country", params={"format": "json", "per_page": 400}, timeout=30)
    response.raise_for_status()
    return {row["id"]: row["name"] for row in response.json()[1] if row.get("region", {}).get("id") != "NA" and len(row["id"]) == 3}

def fetch_fred(start="2000-01-01"):
    if not FRED_API_KEY or FRED_API_KEY.startswith("replace_"):
        raise RuntimeError("FRED_API_KEY is not configured")
    output = []
    for series_id, (name, category, unit, frequency) in FRED_SERIES.items():
        response = requests.get("https://api.stlouisfed.org/fred/series/observations", params={"series_id": series_id, "api_key": FRED_API_KEY, "file_type": "json", "observation_start": start}, timeout=30)
        response.raise_for_status()
        values = [{"indicator_id": series_id, "country_code": "USA", "observation_date": row["date"], "value": pd.to_numeric(row["value"], errors="coerce"), "source": "FRED"} for row in response.json()["observations"]]
        output.append(({"indicator_id": series_id, "indicator_name": name, "category": category, "unit": unit, "frequency": frequency, "source": "FRED"}, pd.DataFrame(values)))
    return output

def fetch_world_bank(start_year=2000, batch_size=40, session=requests):
    """Fetch annual indicators in bounded country batches, retaining partial success."""
    countries = fetch_world_bank_catalog(session)
    output = []
    for indicator_id, (name, category, unit, frequency) in WORLD_BANK.items():
        records = []
        for batch in chunks(sorted(countries), batch_size):
            try:
                response = session.get(f"https://api.worldbank.org/v2/country/{';'.join(batch)}/indicator/{indicator_id}", params={"format": "json", "date": f"{start_year}:2025", "per_page": 2000}, timeout=25)
                response.raise_for_status()
                payload = response.json()
                for row in payload[1] if len(payload) > 1 else []:
                    if row["countryiso3code"] in countries and row["value"] is not None:
                        records.append({"indicator_id": f"WB_{indicator_id}", "country_code": row["countryiso3code"], "observation_date": f"{row['date']}-01-01", "value": row["value"], "source": "World Bank"})
            except requests.RequestException:
                continue
        if records:
            output.append(({"indicator_id": f"WB_{indicator_id}", "indicator_name": name, "category": category, "unit": unit, "frequency": frequency, "source": "World Bank"}, pd.DataFrame(records)))
    if not output:
        raise RuntimeError("World Bank returned no international records")
    return output

def fetch_bls_employment():
    headers = {"Content-Type": "application/json"}; payload = {"seriesid": ["CES0000000001"], "startyear": "2000", "endyear": "2025"}
    if BLS_API_KEY: payload["registrationkey"] = BLS_API_KEY
    response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json=payload, headers=headers, timeout=30)
    response.raise_for_status(); series = response.json()["Results"]["series"][0]["data"]
    rows = [{"indicator_id": "BLS_EMPLOYMENT", "country_code": "USA", "observation_date": f"{row['year']}-{row['period'][1:]}-01", "value": float(row["value"]), "source": "BLS"} for row in series if row["period"].startswith("M")]
    return [({"indicator_id": "BLS_EMPLOYMENT", "indicator_name": "Total Nonfarm Employment", "category": "Employment", "unit": "Thousands of persons", "frequency": "Monthly", "source": "BLS"}, pd.DataFrame(rows))]
