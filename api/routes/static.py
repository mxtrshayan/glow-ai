# api/routes/static.py
# ── Static file serving routes ────────────────────────────────
from fastapi import APIRouter
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from api.config import FRONTEND_DIR

router = APIRouter()


@router.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@router.get("/api")
def api_status():
    return {"status": "online", "message": "GlowAI API is running! 💄"}


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@router.get("/health")
def health():
    return {"status": "healthy"}

# Note: /css/** and /js/** are served via StaticFiles mounted in index.py
