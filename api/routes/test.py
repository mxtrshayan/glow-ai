# api/routes/test.py
# ── Test / debug routes ───────────────────────────────────────
from fastapi import APIRouter
from api.services.gemini_service import call_gemini
from api.config import GEMINI_API_KEY

router = APIRouter()


@router.get("/test-gemini")
async def test_gemini():
    if not GEMINI_API_KEY:
        return {"ok": False, "error": "GEMINI_API_KEY not set"}
    try:
        text = await call_gemini("Say exactly: API working", None)
        return {
            "ok":            True,
            "api_key_loaded": GEMINI_API_KEY[:8] + "…",
            "response":      text,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
