# api/config.py
# ── Centralised environment / settings ───────────────────────
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY: str  = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL:   str  = os.getenv("GEMINI_MODEL",   "gemini-flash-latest")
WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
FRONTEND_DIR: Path   = Path(__file__).resolve().parent.parent / "frontend"
