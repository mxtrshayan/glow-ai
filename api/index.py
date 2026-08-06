# api/index.py
# ── GlowAI FastAPI entry point ────────────────────────────────
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.config import FRONTEND_DIR
from api.routes import analyze, weather, static, test

app = FastAPI(title="GlowAI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount modular frontend assets ────────────────────────────
# These serve /css/** and /js/** directly from the frontend subdirs
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js",  StaticFiles(directory=str(FRONTEND_DIR / "js")),  name="js")

# ── Mount API routers ─────────────────────────────────────────
app.include_router(analyze.router)
app.include_router(weather.router)
app.include_router(test.router)
app.include_router(static.router)   # must be last (catch-all paths)