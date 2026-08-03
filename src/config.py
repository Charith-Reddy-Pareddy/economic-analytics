from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATA_DIR = ROOT / "data"
DATABASE_PATH = DATA_DIR / "economic_pulse.db"
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
BLS_API_KEY = os.getenv("BLS_API_KEY", "")
