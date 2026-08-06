# api/services/gemini_service.py
# ── Gemini AI caller ──────────────────────────────────────────
import io, base64, asyncio
from PIL import Image
import google.generativeai as genai
from api.config import GEMINI_API_KEY, GEMINI_MODEL

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _generate_sync(prompt: str, image_b64: str | None) -> str:
    model = genai.GenerativeModel(GEMINI_MODEL)
    if image_b64:
        img = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        response = model.generate_content([prompt, img])
    else:
        response = model.generate_content(prompt)
    return response.text


async def call_gemini(prompt: str, image_b64: str | None) -> str:
    """Call Gemini with retry logic for rate limits."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set")

    last_err = None
    for attempt in range(3):
        try:
            return await asyncio.to_thread(_generate_sync, prompt, image_b64)
        except Exception as e:
            last_err = e
            err = str(e).lower()
            if "429" in err or "quota" in err or "rate" in err:
                wait = (attempt + 1) * 10
                print(f"Rate limited. Waiting {wait}s — retry {attempt + 1}/3…")
                await asyncio.sleep(wait)
                continue
            raise
    raise last_err or Exception("Rate limit exceeded after 3 retries")
