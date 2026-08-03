"""Run this after adding API keys: python scripts/load_data.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline import load_sources, make_demo_data

try:
    load_sources()
    print("Public-source data loaded successfully.")
except Exception as exc:
    print(f"Live data load failed ({exc}). Creating demo data instead.")
    make_demo_data()
