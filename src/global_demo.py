"""Clearly labelled worldwide fallback data for offline dashboard demonstrations."""
import numpy as np
import pandas as pd
from .database import initialize_database, upsert_indicator, upsert_observations

# ISO-3 codes for UN member states, including India (IND), China (CHN), and
# low-income/developing economies. Values produced here are illustrative only.
UN_MEMBER_CODES = """AFG ALB DZA AND AGO ATG ARG ARM AUS AUT AZE BHS BHR BGD BRB BLR BEL BLZ BEN BTN BOL BIH BWA BRA BRN BGR BFA BDI CPV KHM CMR CAN CAF TCD CHL CHN COL COM COG COD CRI CIV HRV CUB CYP CZE DNK DJI DMA DOM ECU EGY SLV GNQ ERI EST SWZ ETH FJI FIN FRA GAB GMB GEO DEU GHA GRC GRD GTM GIN GNB GUY HTI HND HUN ISL IND IDN IRN IRQ IRL ISR ITA JAM JPN JOR KAZ KEN KIR PRK KOR KWT KGZ LAO LVA LBN LSO LBR LBY LIE LTU LUX MDG MWI MYS MDV MLI MLT MHL MRT MUS MEX FSM MDA MCO MNG MNE MAR MOZ MMR NAM NRU NPL NLD NZL NIC NER NGA MKD NOR OMN PAK PLW PAN PNG PRY PER PHL POL PRT QAT ROU RUS RWA KNA LCA VCT WSM SMR STP SAU SEN SRB SYC SLE SGP SVK SVN SLB SOM ZAF SSD ESP LKA SDN SUR SWE CHE SYR TJK TZA THA TLS TGO TON TTO TUN TUR TKM TUV UGA UKR ARE GBR USA URY UZB VUT VEN VNM YEM ZMB ZWE""".split()

SPECS = {
    "CPI": ("Consumer Price Index", "Inflation", "Index", 100.0, 1.8),
    "UNRATE": ("Unemployment Rate", "Employment", "Percent", 6.0, 0.0),
    "GDP": ("Gross Domestic Product", "Growth", "Billions USD", 180.0, 4.0),
    "FEDFUNDS": ("Policy Interest Rate", "Interest Rates", "Percent", 3.0, 0.0),
    "PCE": ("Household Consumption", "Consumer Spending", "Billions USD", 130.0, 3.0),
    "WAGES": ("Average Wage Index", "Wages", "Index", 100.0, 1.5),
}

def seed_global_demo_data():
    """Seed annual illustrative values so every UN-member country is explorable offline."""
    initialize_database()
    dates = pd.date_range("2000-01-01", "2025-01-01", freq="YS")
    for indicator_id, (name, category, unit, base, trend) in SPECS.items():
        frames = []
        for country in UN_MEMBER_CODES:
            seed = sum(ord(letter) for letter in country) + sum(ord(letter) for letter in indicator_id)
            rng = np.random.default_rng(seed)
            scale = .55 + (seed % 115) / 100
            adjusted_base = base * scale if indicator_id not in {"UNRATE", "FEDFUNDS"} else base + (scale - 1) * 5
            values = adjusted_base + trend * scale * np.arange(len(dates)) + rng.normal(0, max(.35, abs(base) * .008), len(dates))
            if indicator_id in {"UNRATE", "FEDFUNDS"}:
                values = np.clip(values, .1, None)
            frames.append(pd.DataFrame({"indicator_id": indicator_id, "country_code": country, "observation_date": dates, "value": values, "source": "International demo (illustrative)"}))
        upsert_indicator({"indicator_id": indicator_id, "indicator_name": name, "category": category, "unit": unit, "frequency": "Annual", "source": "International demo (illustrative)"})
        upsert_observations(pd.concat(frames, ignore_index=True))
