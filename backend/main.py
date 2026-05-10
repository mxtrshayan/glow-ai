from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PIL import Image
import httpx
import io, os, base64, json, re
import asyncio

load_dotenv()

OPENROUTER_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
MODEL              = "google/gemini-2.0-flash-lite-001"

app = FastAPI(title="Makeup AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Image Preprocessor ─────────────────────────────────────
def preprocess_image(file_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    if max(img.size) > 800:
        img.thumbnail((800, 800), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

# ── Prompt Builder ─────────────────────────────────────────
def build_prompt(skin_tone, event, time_of_day, outfit_color, has_image):
    image_line = (
        "I have uploaded a face photo. Carefully analyze the person's exact skin tone, "
        "undertone (warm/cool/neutral), skin texture, eye color, and facial features from the image."
        if has_image else
        f"No photo provided. Base everything on the selected skin tone: '{skin_tone or 'medium'}'."
    )

    intensity = "bold and dramatic"  if time_of_day in ["evening", "night"] else "soft and natural"
    formality = "glamorous and polished" if event in ["wedding", "party", "date", "photoshoot"] else "fresh and understated"

    return f"""
You are a Pakistani fashion and beauty expert giving simple friendly advice.

{image_line}

Customer details:
- Occasion: {event or 'casual'}
- Time: {time_of_day or 'daytime'}
- Outfit color: {outfit_color or 'not specified'}
- Skin tone: {skin_tone or 'medium'}
- Style: {intensity}, {formality}

STRICT RULES:
- Makeup advice must be ULTRA-SIMPLE and very short. E.g., just say "soft peach blush" or "thin black eyeliner".
- NO brand names, NO product names.
- NO hex codes or confusing technical makeup terms. Keep it highly readable.
- Suggest a wide variety of rich and beautiful Pakistani dress colors (e.g., emerald green, deep plum, pastel peach, mustard yellow).
- Max ONE short sentence per field.
- Must perfectly suit Pakistani culture and skin tones.

Respond ONLY with this exact JSON, no markdown, no extra text:

{{
  "skin_analysis": {{
    "detected_tone": "e.g. wheatish, fair, dark",
    "undertone": "warm / cool / neutral",
    "finish": "matte / dewy / satin"
  }},
  "face": {{
    "foundation": "e.g. light beige medium coverage",
    "concealer": "e.g. one shade lighter than skin",
    "blush": "e.g. soft peach on cheeks",
    "highlight": "e.g. soft gold on cheekbones",
    "contour": "e.g. light brown along jawline",
    "tip": "one simple tip for face"
  }},
  "eyes": {{
    "eyeshadow": "e.g. warm brown on lid",
    "eyeliner": "e.g. thin black liner",
    "mascara": "e.g. black mascara",
    "brows": "e.g. lightly filled with brown",
    "tip": "one simple tip for eyes"
  }},
  "lips": {{
    "liner": "e.g. dusty rose liner",
    "lipstick": "e.g. coral pink satin",
    "gloss": "e.g. clear gloss or skip",
    "tip": "one simple tip for lips"
  }},
  "outfit": {{
    "dressing": "e.g. emerald green chiffon shalwar kameez",
    "dupatta": "e.g. matching green dupatta with gold lace"
  }},
  "accessories": {{
    "jewellery": "e.g. silver jhumkas",
    "bag": "e.g. silver clutch",
    "sandals": "e.g. silver block heels"
  }},
  "overall_tip": "one short friendly sentence about the whole look"
}}
""".strip()

# ── JSON Extractor ─────────────────────────────────────────
# ── JSON Extractor ─────────────────────────────────────────
def extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Could not parse response as JSON")

# ── Fallback ───────────────────────────────────────────────
def fallback_response(event, time_of_day, skin_tone, outfit_color):
    is_night  = time_of_day in ["evening", "night"]
    is_formal = event in ["wedding", "mehndi", "dholki", "party", "eid", "photoshoot", "valima"]

    face_looks = {
        "wedding":    { "foundation": "full coverage ivory beige", "concealer": "one shade lighter under eyes", "blush": "soft rose pink on cheeks", "highlight": "champagne gold on cheekbones", "contour": "soft brown along jawline", "tip": "set with translucent powder for all day wear" },
        "mehndi":     { "foundation": "light dewy coverage", "concealer": "peachy nude under eyes", "blush": "bright coral on cheeks", "highlight": "golden shimmer on cheekbones", "contour": "light taupe along sides of nose", "tip": "keep skin glowing and fresh for mehndi pictures" },
        "dholki":     { "foundation": "medium coverage", "concealer": "light peach under eyes", "blush": "hot pink on cheeks", "highlight": "pink shimmer on cheekbones", "contour": "soft brown along jawline", "tip": "be bold — dholki is for fun colorful looks" },
        "eid":        { "foundation": "light satin coverage", "concealer": "nude beige under eyes", "blush": "peach pink on cheeks", "highlight": "soft gold on cheekbones", "contour": "light taupe along jawline", "tip": "keep it elegant and fresh for Eid visits" },
        "party":      { "foundation": "full matte coverage", "concealer": "light under eyes", "blush": "deep rose sculpted on cheeks", "highlight": "blinding gold on cheekbones", "contour": "deep taupe for sharp sculpt", "tip": "set everything with setting spray before going out" },
        "university": { "foundation": "light BB coverage", "concealer": "light peach under eyes", "blush": "soft baby pink on cheeks", "highlight": "subtle pearl on cheekbones", "contour": "skip or very light taupe", "tip": "keep it minimal and fresh for daytime" },
        "office":     { "foundation": "medium matte coverage", "concealer": "light nude under eyes", "blush": "soft mauve on cheeks", "highlight": "subtle champagne on cheekbones", "contour": "soft taupe along jawline", "tip": "keep it neat and professional" },
        "everyday":   { "foundation": "light tinted moisturizer", "concealer": "light peach where needed", "blush": "soft peach on cheeks", "highlight": "subtle glow on cheekbones", "contour": "skip for everyday look", "tip": "just enhance your natural features" },
    }

    eyes_looks = {
        "wedding":    { "eyeshadow": "golden brown on lid, champagne on brow bone", "eyeliner": "black gel liner on upper lash line", "mascara": "volumizing black mascara", "brows": "defined arch filled with dark brown", "tip": "apply eyeshadow primer for long lasting wear" },
        "mehndi":     { "eyeshadow": "bright green or yellow shimmer on lid", "eyeliner": "thick black liner with small flick", "mascara": "volumizing black mascara", "brows": "bold filled brows with dark brown", "tip": "use colorful liner to match your outfit" },
        "dholki":     { "eyeshadow": "purple or pink shimmer on lid", "eyeliner": "colorful or black winged liner", "mascara": "volumizing black mascara", "brows": "bold brows filled with dark brown", "tip": "go bold and colorful — have fun with it" },
        "eid":        { "eyeshadow": "copper brown on lid, nude on brow bone", "eyeliner": "thin brown or black liner", "mascara": "lengthening black mascara", "brows": "soft natural arch with taupe", "tip": "keep eyes elegant and simple" },
        "party":      { "eyeshadow": "dark smoky black with bronze shimmer", "eyeliner": "sharp winged black liner", "mascara": "volumizing black mascara", "brows": "bold defined brows with dark brown", "tip": "blend well for a seamless smoky look" },
        "university": { "eyeshadow": "nude peach wash on lid", "eyeliner": "thin brown pencil on waterline", "mascara": "lengthening brown mascara", "brows": "soft natural brows with taupe", "tip": "keep it light and natural" },
        "office":     { "eyeshadow": "neutral taupe on lid, ivory on brow bone", "eyeliner": "thin brown liner on upper lash line", "mascara": "lengthening black mascara", "brows": "neat arch filled with taupe", "tip": "avoid glitter for office looks" },
        "everyday":   { "eyeshadow": "light nude wash on lid", "eyeliner": "simple brown pencil", "mascara": "light black or brown mascara", "brows": "natural brows lightly filled", "tip": "keep it simple and quick" },
    }

    lips_looks = {
        "wedding":    { "liner": "deep rose slightly overlined", "lipstick": "deep rose satin", "gloss": "skip for long lasting matte finish", "tip": "blot and reapply for all day wear" },
        "mehndi":     { "liner": "bright orange red liner", "lipstick": "bright orange red matte", "gloss": "skip gloss", "tip": "bold lips complete the mehndi look" },
        "dholki":     { "liner": "hot pink liner", "lipstick": "hot pink matte or satin", "gloss": "clear gloss on centre for fun look", "tip": "match lip color to your outfit accent color" },
        "eid":        { "liner": "nude pink liner", "lipstick": "soft rose satin", "gloss": "clear gloss for shine", "tip": "keep lips soft and elegant for Eid" },
        "party":      { "liner": "dark berry liner", "lipstick": "bold red or berry matte", "gloss": "skip for bold matte finish", "tip": "bold lips or bold eyes — not both" },
        "university": { "liner": "nude liner", "lipstick": "light nude pink", "gloss": "clear gloss or tinted balm", "tip": "tinted lip balm is perfect for quick looks" },
        "office":     { "liner": "mauve liner", "lipstick": "mauve satin", "gloss": "skip or very light gloss", "tip": "mauve and nude shades are very professional" },
        "everyday":   { "liner": "nude liner", "lipstick": "sheer pink or tinted balm", "gloss": "clear gloss", "tip": "keep lips moisturized and natural" },
    }

    outfit_looks = {
        "wedding":    { "dressing": "deep red or maroon embroidered lehnga or shalwar kameez", "dupatta": "red or gold chiffon dupatta with heavy embroidery" },
        "mehndi":     { "dressing": "bright yellow or green gharara or lehenga", "dupatta": "yellow or orange dupatta with mirror work" },
        "dholki":     { "dressing": "colorful printed or embroidered shalwar kameez", "dupatta": "bright contrast dupatta" },
        "eid":        { "dressing": "pastel or bright embroidered shalwar kameez or sharara", "dupatta": "matching chiffon or silk dupatta" },
        "valima":     { "dressing": "elegant pastel or gold formal suit or saree", "dupatta": "sheer chiffon dupatta with border" },
        "party":      { "dressing": "elegant sharara or embroidered formal suit", "dupatta": "sheer chiffon dupatta" },
        "date":       { "dressing": "soft pastel shalwar kameez or casual dress", "dupatta": "light chiffon or no dupatta" },
        "university": { "dressing": "simple printed or solid shalwar kameez", "dupatta": "simple cotton dupatta" },
        "office":     { "dressing": "solid color formal shalwar kameez", "dupatta": "plain or subtle dupatta" },
        "everyday":   { "dressing": "comfortable cotton shalwar kameez", "dupatta": "light cotton dupatta" },
        "shopping":   { "dressing": "casual comfortable shalwar kameez or jeans with top", "dupatta": "light scarf or no dupatta" },
    }

    accessories_looks = {
        "wedding":    { "jewellery": "gold polki set — earrings, necklace and maang teeka", "bag": "small golden or red bridal clutch", "sandals": "golden heels or red embroidered khussa" },
        "mehndi":     { "jewellery": "colorful meenakari or floral jewellery with bangles", "bag": "small colorful potli bag", "sandals": "yellow or green embroidered khussa" },
        "dholki":     { "jewellery": "colorful jhumkas and bangles", "bag": "small colorful clutch", "sandals": "bright colored block heels or khussa" },
        "eid":        { "jewellery": "simple gold earrings and thin bangles", "bag": "small matching clutch", "sandals": "nude or gold heels or embroidered khussa" },
        "valima":     { "jewellery": "elegant pearl or gold earrings and bracelet", "bag": "small embellished clutch", "sandals": "golden or nude heels" },
        "party":      { "jewellery": "statement earrings and bracelet", "bag": "small evening clutch", "sandals": "strappy heels or embellished sandals" },
        "date":       { "jewellery": "simple delicate earrings", "bag": "small crossbody bag", "sandals": "nude or white block heels" },
        "university": { "jewellery": "simple studs or small hoops", "bag": "tote bag or backpack", "sandals": "comfortable flats or white sneakers" },
        "office":     { "jewellery": "simple pearl or gold studs", "bag": "structured handbag", "sandals": "block heels or loafers" },
        "everyday":   { "jewellery": "simple earrings", "bag": "casual tote or shoulder bag", "sandals": "comfortable flats or sandals" },
        "shopping":   { "jewellery": "simple small earrings", "bag": "casual shoulder bag", "sandals": "comfortable flats or sneakers" },
    }

    e           = event or "everyday"
    face        = face_looks.get(e,        face_looks["everyday"])
    eyes        = eyes_looks.get(e,        eyes_looks["everyday"])
    lips        = lips_looks.get(e,        lips_looks["everyday"])
    outfit      = outfit_looks.get(e,      outfit_looks["everyday"])
    accessories = accessories_looks.get(e, accessories_looks["everyday"])

    return {
        "skin_analysis": {
            "detected_tone": (skin_tone or "medium").capitalize(),
            "undertone":     "Warm" if (skin_tone or "") in ["tan","deep","rich","wheatish","medium"] else "Neutral",
            "finish":        "Matte" if is_night else "Dewy"
        },
        "face":        face,
        "eyes":        eyes,
        "lips":        lips,
        "outfit":      outfit,
        "accessories": accessories,
        "overall_tip": f"A {'glamorous' if is_formal else 'fresh'} look perfect for {e} — confidence is your best accessory! ✨"
    }

# ── Test Route ─────────────────────────────────────────────
@app.get("/test-gemini")
async def test_gemini():
    test_payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Say exactly: API working"}]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "http://localhost:8000",
                "X-Title":       "MakeupAI"
            },
            json=test_payload
        )
        return {
            "status_code":    response.status_code,
            "api_key_loaded": OPENROUTER_API_KEY[:10] + "...",
            "response":       response.json()
        }

# ── Call AI via OpenRouter ─────────────────────────────────
async def call_gemini(prompt: str, image_b64: str | None) -> str:
    if image_b64:
        content = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            {"type": "text",      "text": prompt}
        ]
    else:
        content = prompt

    payload = {
        "model":    MODEL,
        "messages": [{"role": "user", "content": content}]
    }

    for attempt in range(3):
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type":  "application/json",
                    "HTTP-Referer":  "http://localhost:8000",
                    "X-Title":       "MakeupAI"
                },
                json=payload
            )
            if response.status_code == 429:
                wait = (attempt + 1) * 10
                print(f"⏳ Rate limited. Waiting {wait}s — retry {attempt+1}/3...")
                await asyncio.sleep(wait)
                continue
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    raise Exception("Rate limit exceeded after 3 retries")

# ── Routes ─────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "online", "message": "Makeup AI API is running! 💄"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze(
    image:        UploadFile | None = File(default=None),
    skin_tone:    str = Form(default=""),
    event:        str = Form(default=""),
    time_of_day:  str = Form(default=""),
    outfit_color: str = Form(default=""),
):
    print(f"📥 event={event}, time={time_of_day}, skin={skin_tone}, outfit={outfit_color}")

    image_b64 = None
    if image and image.filename:
        raw       = await image.read()
        image_b64 = preprocess_image(raw)
        print("🖼️  Image preprocessed")

    prompt = build_prompt(skin_tone, event, time_of_day, outfit_color, image_b64 is not None)

    try:
        raw_text = await call_gemini(prompt, image_b64)
        print("✅ AI responded")
        result = extract_json(raw_text)
        result["status"] = "success"
    except Exception as e:
        print(f"⚠️  AI error: {e} — using fallback")
        result = fallback_response(event, time_of_day, skin_tone, outfit_color)
        result["status"] = "fallback"

    result["inputs_received"] = {
        "skin_tone":    skin_tone    or "not provided",
        "event":        event        or "not provided",
        "time_of_day":  time_of_day  or "not provided",
        "outfit_color": outfit_color or "not provided",
        "image":        "provided" if image_b64 else "not provided",
    }
    return result