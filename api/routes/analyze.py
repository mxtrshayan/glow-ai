# api/routes/analyze.py
# ── /analyze POST route ───────────────────────────────────────
import json, re
from fastapi import APIRouter, File, UploadFile, Form

from api.services.image_service import preprocess_image
from api.services.gemini_service import call_gemini
from api.prompts.prompt_builder import build_prompt
from api.prompts.fallback import fallback_response

router = APIRouter()


def extract_json(text: str) -> dict:
    """Strip markdown fences and parse JSON from AI response."""
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Could not parse AI response as JSON")


@router.post("/analyze")
async def analyze(
    # Original fields
    image:        UploadFile | None = File(default=None),
    skin_tone:    str = Form(default=""),
    event:        str = Form(default=""),
    time_of_day:  str = Form(default=""),
    outfit_color: str = Form(default=""),
    # New fields
    undertone:        str  = Form(default=""),
    skin_type:        str  = Form(default=""),
    hijab:            str  = Form(default="no"),         # "yes" / "no"
    style_preference: str  = Form(default="both"),       # "traditional" / "western" / "both"
    owned_items:      str  = Form(default=""),
    # Weather (passed from frontend if user opted in)
    weather_condition: str   = Form(default=""),
    weather_temp:      float = Form(default=0.0),
    weather_humidity:  int   = Form(default=0),
    weather_category:  str   = Form(default=""),
):
    print(
        f"event={event}, time={time_of_day}, skin={skin_tone}, undertone={undertone}, "
        f"skin_type={skin_type}, hijab={hijab}, style={style_preference}, weather={weather_condition}"
    )

    # ── Process image ─────────────────────────────────────────
    image_b64 = None
    if image and image.filename:
        raw       = await image.read()
        image_b64 = preprocess_image(raw)
        print("Image preprocessed")

    # ── Build weather dict ────────────────────────────────────
    weather: dict | None = None
    if weather_condition:
        weather = {
            "condition": weather_condition,
            "temp_c":    weather_temp,
            "humidity":  weather_humidity,
            "category":  weather_category or "mild",
        }

    # ── Build prompt ──────────────────────────────────────────
    hijab_bool = hijab.lower() == "yes"
    prompt = build_prompt(
        skin_tone        = skin_tone,
        undertone        = undertone,
        skin_type        = skin_type,
        event            = event,
        time_of_day      = time_of_day,
        outfit_color     = outfit_color,
        has_image        = image_b64 is not None,
        weather          = weather,
        hijab            = hijab_bool,
        style_preference = style_preference,
        owned_items      = owned_items,
    )

    # ── Call Gemini ───────────────────────────────────────────
    try:
        raw_text = await call_gemini(prompt, image_b64)
        print("AI responded")
        result = extract_json(raw_text)
        result["status"] = "success"
    except Exception as exc:
        print(f"AI error: {exc} — using fallback")
        result = fallback_response(
            event        = event,
            time_of_day  = time_of_day,
            skin_tone    = skin_tone,
            outfit_color = outfit_color,
            undertone    = undertone,
            skin_type    = skin_type,
            hijab        = hijab_bool,
            weather      = weather,
        )
        result["status"] = "fallback"

    result["inputs_received"] = {
        "skin_tone":    skin_tone    or "not provided",
        "undertone":    undertone    or "not provided",
        "skin_type":    skin_type    or "not provided",
        "event":        event        or "not provided",
        "time_of_day":  time_of_day  or "not provided",
        "outfit_color": outfit_color or "not provided",
        "hijab":        hijab,
        "style":        style_preference,
        "image":        "provided" if image_b64 else "not provided",
        "weather":      weather_condition or "not provided",
    }

    return result
