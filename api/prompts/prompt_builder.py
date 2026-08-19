# api/prompts/prompt_builder.py
# ── Build the master prompt sent to Gemini ────────────────────


def build_prompt(
    skin_tone: str,
    undertone: str,
    skin_type: str,
    event: str,
    time_of_day: str,
    outfit_color: str,
    has_image: bool,
    weather: dict | None,
    hijab: bool,
    style_preference: str,
    owned_items: str,
) -> str:
    """Construct the full mega-prompt for Gemini."""

    # ── Image / skin tone context ──────────────────────────────
    if has_image:
        image_line = (
            "I have uploaded a face photo. Carefully analyze the person's exact skin tone, "
            "undertone (warm/cool/neutral/olive), skin texture, eye color, and facial features from the image."
        )
    else:
        image_line = (
            f"No photo provided. Base recommendations on: skin tone '{skin_tone or 'medium'}', "
            f"undertone '{undertone or 'neutral'}'."
        )

    # ── Weather context ────────────────────────────────────────
    if weather and not weather.get("error"):
        weather_line = (
            f"Current weather: {weather.get('condition','unknown')}, "
            f"{weather.get('temp_c','?')}°C, humidity {weather.get('humidity','?')}%. "
            f"Weather category: {weather.get('category','mild')}."
        )
        weather_instructions = {
            "rainy":    "Recommend waterproof mascara, waterproof eyeliner, long-wear setting spray, and waterproof foundation.",
            "hot_humid": "Recommend lightweight oil-free products, matte/long-lasting formulas, setting spray, and avoid heavy contouring.",
            "cold":     "Recommend hydrating moisturizing primer, dewy finish foundation, rich lip balm or lipstick, and nourishing products.",
            "mild":     "Standard recommendations apply; a satin or dewy finish looks beautiful in mild weather.",
        }.get(weather.get("category", "mild"), "Standard recommendations apply.")
        weather_note = f"{weather_line} {weather_instructions}"
    else:
        weather_note = "No weather data. Give general all-season recommendations."

    # ── Style context ──────────────────────────────────────────
    style_note = {
        "traditional": "The user prefers traditional South Asian / Pakistani style (shalwar kameez, lehenga, gharara, dupatta, Pakistani makeup trends like black kajal waterline).",
        "western":     "The user prefers Western style (jeans, dresses, blouses, Western makeup trends).",
        "both":        "The user appreciates both traditional Pakistani and Western styles. Blend recommendations naturally.",
    }.get((style_preference or "both").lower(), "Blend traditional and western style.")

    # ── Hijab context ──────────────────────────────────────────
    if hijab:
        hair_instruction = (
            "The user WEARS a hijab. Recommend: (1) a hijab style that suits their face shape and occasion, "
            "(2) hijab fabric and draping style (e.g. chiffon pleated, Turkish style, simple wrap), "
            "(3) no hairstyle is needed since hair is covered."
        )
    else:
        hair_instruction = (
            "The user does NOT wear a hijab. Recommend: (1) a flattering hairstyle for the occasion and face shape, "
            "(2) whether to leave hair open, tied, or styled with accessories."
        )

    # ── Owned items context ────────────────────────────────────
    if owned_items and owned_items.strip():
        owned_note = (
            f"The user has listed these items they already own: {owned_items.strip()}. "
            "Where possible, suggest how to incorporate their owned items into the look. "
            "Prioritise building the look using what they have."
        )
    else:
        owned_note = "No owned items provided. Give fresh general recommendations."

    # ── Skin type brand context ────────────────────────────────
    skin_type_note = f"Skin type: {skin_type or 'normal'}."

    # ── Intensity / formality ──────────────────────────────────
    intensity = "bold and dramatic" if time_of_day in ["evening", "night"] else "soft and natural"
    formality = "glamorous and polished" if event in ["wedding", "party", "date", "photoshoot", "mehndi", "dholki", "eid", "valima"] else "fresh and understated"

    return f"""
You are a world-class makeup artist and fashion stylist who specialises in both traditional South Asian / Pakistani looks AND modern Western looks.

{image_line}

Customer profile:
- Occasion: {event or 'casual'}
- Time of day: {time_of_day or 'daytime'}
- Outfit colour: {outfit_color or 'not specified'}
- Skin tone: {skin_tone or 'medium'} | Undertone: {undertone or 'neutral'} | {skin_type_note}
- Style preference: {style_preference or 'both'}
- Look intensity: {intensity}, {formality}

Weather: {weather_note}

Style context: {style_note}

Hair/Hijab: {hair_instruction}

Owned items: {owned_note}

STRICT RULES FOR RECOMMENDATIONS:
- Eyeshadow on waterline: ALWAYS use black kajal for everyday/casual/university looks (NOT brown eyeliner — that is NOT commonly used in Pakistani daily makeup).
- Brown eyeliner in the waterline is only acceptable for very light Western everyday looks.
- Contouring: SKIP for everyday, university, office looks. Only include for wedding, party, photoshoot.
- Skin tones range from porcelain/very fair (common in European/English backgrounds) to rich dark. Tailor recommendations precisely.
- Brand suggestions must consider skin type: oily skin → matte, oil-free; dry skin → hydrating, dewy; combination → balanced; sensitive → fragrance-free, gentle.
- Keep each field SHORT (max one sentence). No jargon.
- Include appropriate hex color codes for try-on (lips.hex, face.blush_hex, eyes.eyeshadow_hex, eyes.eyeliner_hex).
- Lens colour should complement outfit and occasion, not clash.
- VERY IMPORTANT: For Pakistani occasions (eid, wedding, mehndi, dholki, valima), suggest traditional outfits AND Western-fusion if style_preference includes 'western' or 'both'.

Respond ONLY with this exact JSON, no markdown, no extra text:

{{
  "skin_analysis": {{
    "detected_tone": "e.g. porcelain / very fair / fair / light / medium / tan / wheatish / brown / deep / rich",
    "undertone": "warm / cool / neutral / olive",
    "finish": "matte / dewy / satin"
  }},
  "face": {{
    "foundation": "e.g. light beige BB cream with SPF",
    "concealer": "e.g. one shade lighter than skin",
    "blush": "e.g. soft peach on cheeks",
    "blush_hex": "#E07A7A",
    "highlight": "e.g. soft gold on cheekbones (skip for everyday)",
    "contour": "skip for this look (or specific instruction for formal looks)",
    "primer": "e.g. hydrating primer for dry skin / mattifying primer for oily skin",
    "setting": "e.g. translucent setting powder + setting spray",
    "tip": "one simple tip for face"
  }},
  "eyes": {{
    "eyeshadow": "e.g. warm brown on lid",
    "eyeshadow_hex": "#8B5A2B",
    "eyeliner": "e.g. black kajal in waterline + thin black gel liner on upper lash line",
    "eyeliner_hex": "#1A1A1A",
    "mascara": "e.g. volumizing black mascara",
    "brows": "e.g. lightly filled with medium brown",
    "tip": "one simple tip for eyes"
  }},
  "lips": {{
    "liner": "e.g. dusty rose liner",
    "lipstick": "e.g. coral pink satin",
    "shade_name": "e.g. Dusty Rose or Berry Crush (descriptive shade name)",
    "hex": "#C8385A",
    "gloss": "e.g. clear gloss or skip",
    "tip": "one simple tip for lips"
  }},
  "outfit": {{
    "dressing": "e.g. emerald green chiffon shalwar kameez or floral midi dress",
    "dupatta": "e.g. matching green dupatta with gold lace (or N/A if Western style)",
    "footwear": "e.g. nude block heels or embroidered khussa",
    "style_note": "one sentence tip about the overall outfit"
  }},
  "accessories": {{
    "jewellery": "e.g. silver jhumkas or delicate gold chain",
    "bag": "e.g. silver clutch or tan crossbody",
    "extra": "e.g. hair pin / hair band / scarf if needed"
  }},
  "brands": {{
    "foundation_brand": "e.g. Huda Beauty FauxFilter (full coverage, good for oily skin)",
    "lip_brand": "e.g. Charlotte Tilbury Pillow Talk (neutral rose nude)",
    "eye_brand": "e.g. Maybelline Sky High mascara (lengthening)",
    "blush_brand": "e.g. NARS Orgasm blush (peachy gold shimmer)",
    "drugstore_pick": "e.g. L'Oreal Infallible foundation (budget-friendly)",
    "tip": "one sentence on choosing right products for your skin type"
  }},
  "lens": {{
    "color": "e.g. honey brown / warm grey / emerald green",
    "brand_suggestion": "e.g. Solotica Hidrocor Mel or FreshLook Illuminate",
    "reason": "why this lens complements the look",
    "tip": "always hydrate with lens-safe drops for comfort"
  }},
  "hair_hijab": {{
    "style": "e.g. silk pleated hijab with pearls / loose waves with side parting",
    "color_suggestion": "e.g. warm caramel highlights if applicable, or N/A",
    "accessory": "e.g. pearl pins for hijab or gold hair clip for open hair",
    "tip": "one sentence hair/hijab tip"
  }},
  "weather_tip": "e.g. Use waterproof mascara and setting spray today — it is humid. OR Moisturise well before makeup — the cold air will dry your skin.",
  "overall_tip": "one short friendly sentence about the whole look"
}}
""".strip()
