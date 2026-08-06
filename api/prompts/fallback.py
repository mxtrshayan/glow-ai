# api/prompts/fallback.py
# ── Fallback response when Gemini is unavailable ─────────────


def fallback_response(
    event: str,
    time_of_day: str,
    skin_tone: str,
    outfit_color: str,
    undertone: str = "",
    skin_type: str = "",
    hijab: bool = False,
    weather: dict | None = None,
) -> dict:
    """Return a sensible hardcoded recommendation when AI call fails."""
    is_night  = time_of_day in ["evening", "night"]
    is_formal = event in ["wedding", "mehndi", "dholki", "party", "eid", "photoshoot", "valima"]
    e         = event or "everyday"

    # ── Face ──────────────────────────────────────────────────
    face_looks = {
        "wedding":    {"foundation": "full coverage ivory beige", "concealer": "one shade lighter under eyes", "blush": "soft rose pink", "highlight": "champagne gold on cheekbones", "contour": "soft brown along jawline", "primer": "smoothing primer", "setting": "translucent powder + setting spray", "tip": "set with translucent powder for all-day wear"},
        "mehndi":     {"foundation": "light dewy coverage", "concealer": "peachy nude under eyes", "blush": "bright coral", "highlight": "golden shimmer on cheekbones", "contour": "light taupe along sides of nose", "primer": "hydrating primer", "setting": "dewy setting spray", "tip": "keep skin glowing and fresh for mehndi pictures"},
        "dholki":     {"foundation": "medium coverage", "concealer": "light peach under eyes", "blush": "hot pink", "highlight": "pink shimmer", "contour": "soft brown along jawline", "primer": "colour-correcting primer", "setting": "long-wear setting spray", "tip": "be bold — dholki is for fun colourful looks"},
        "eid":        {"foundation": "light satin coverage", "concealer": "nude beige under eyes", "blush": "peach pink", "highlight": "soft gold", "contour": "skip", "primer": "hydrating primer", "setting": "satin setting spray", "tip": "keep it elegant and fresh for Eid visits"},
        "party":      {"foundation": "full matte coverage", "concealer": "light under eyes", "blush": "deep rose sculpted", "highlight": "blinding gold on cheekbones", "contour": "deep taupe for sharp sculpt", "primer": "pore-minimising primer", "setting": "translucent powder + long-wear spray", "tip": "set everything with setting spray before going out"},
        "university": {"foundation": "light BB cream", "concealer": "light peach under eyes", "blush": "soft baby pink", "highlight": "subtle pearl", "contour": "skip", "primer": "lightweight primer", "setting": "light setting powder", "tip": "keep it minimal and fresh for daytime"},
        "office":     {"foundation": "medium matte coverage", "concealer": "light nude under eyes", "blush": "soft mauve", "highlight": "subtle champagne", "contour": "skip", "primer": "smoothing primer", "setting": "translucent powder", "tip": "keep it neat and professional"},
        "everyday":   {"foundation": "light tinted moisturiser", "concealer": "light peach where needed", "blush": "soft peach", "highlight": "subtle glow", "contour": "skip for everyday", "primer": "SPF moisturiser", "setting": "light setting spray", "tip": "just enhance your natural features"},
        "date":       {"foundation": "medium satin coverage", "concealer": "light peach under eyes", "blush": "soft coral", "highlight": "champagne gold", "contour": "light bronze along jawline", "primer": "hydrating primer", "setting": "satin setting spray", "tip": "a soft glow always looks romantic"},
    }

    # ── Eyes ──────────────────────────────────────────────────
    eyes_looks = {
        "wedding":    {"eyeshadow": "golden brown on lid, champagne on brow bone", "eyeliner": "black kajal in waterline + black gel liner on upper lash line", "mascara": "volumising black mascara", "brows": "defined arch filled with dark brown", "tip": "apply eyeshadow primer for long-lasting wear"},
        "mehndi":     {"eyeshadow": "bright green or yellow shimmer on lid", "eyeliner": "black kajal in waterline + thick black liner", "mascara": "volumising black mascara", "brows": "bold filled brows", "tip": "use colourful liner to match your outfit"},
        "dholki":     {"eyeshadow": "purple or pink shimmer on lid", "eyeliner": "black kajal + colourful or black winged liner", "mascara": "volumising black mascara", "brows": "bold brows", "tip": "go bold and colourful — have fun with it"},
        "eid":        {"eyeshadow": "copper brown on lid, nude on brow bone", "eyeliner": "black kajal in waterline + thin black liner", "mascara": "lengthening black mascara", "brows": "soft natural arch", "tip": "keep eyes elegant and simple"},
        "party":      {"eyeshadow": "dark smoky black with bronze shimmer", "eyeliner": "black kajal + sharp winged black liner", "mascara": "volumising black mascara", "brows": "bold defined brows", "tip": "blend well for a seamless smoky look"},
        "university": {"eyeshadow": "nude peach wash on lid", "eyeliner": "black kajal in waterline", "mascara": "lengthening mascara", "brows": "soft natural brows", "tip": "keep it light and natural"},
        "office":     {"eyeshadow": "neutral taupe on lid, ivory on brow bone", "eyeliner": "thin black liner on upper lash line + black kajal", "mascara": "lengthening black mascara", "brows": "neat arch", "tip": "avoid glitter for office looks"},
        "everyday":   {"eyeshadow": "light nude wash on lid", "eyeliner": "black kajal in waterline", "mascara": "light black mascara", "brows": "natural brows lightly filled", "tip": "keep it simple and quick"},
        "date":       {"eyeshadow": "warm rose on lid with gold shimmer", "eyeliner": "black kajal + thin liner", "mascara": "volumising black mascara", "brows": "defined soft arch", "tip": "a little shimmer on the lid makes eyes pop"},
    }

    # ── Lips ──────────────────────────────────────────────────
    lips_looks = {
        "wedding":    {"liner": "deep rose overlined", "lipstick": "deep rose satin", "shade_name": "Deep Rose", "gloss": "skip — long-lasting matte finish", "tip": "blot and reapply for all-day wear"},
        "mehndi":     {"liner": "bright orange-red liner", "lipstick": "bright orange-red matte", "shade_name": "Tangerine Blaze", "gloss": "skip gloss", "tip": "bold lips complete the mehndi look"},
        "dholki":     {"liner": "hot pink liner", "lipstick": "hot pink matte or satin", "shade_name": "Hot Fuchsia", "gloss": "clear gloss on centre for fun", "tip": "match lip colour to your outfit accent"},
        "eid":        {"liner": "nude pink liner", "lipstick": "soft rose satin", "shade_name": "Petal Rose", "gloss": "clear gloss for shine", "tip": "keep lips soft and elegant"},
        "party":      {"liner": "dark berry liner", "lipstick": "bold red or berry matte", "shade_name": "Berry Bold", "gloss": "skip — bold matte finish", "tip": "bold lips or bold eyes — not both"},
        "university": {"liner": "nude liner", "lipstick": "light nude pink", "shade_name": "Bare Blush", "gloss": "clear gloss or tinted balm", "tip": "tinted lip balm is perfect for quick looks"},
        "office":     {"liner": "mauve liner", "lipstick": "mauve satin", "shade_name": "Muted Mauve", "gloss": "very light gloss", "tip": "mauve and nude shades are professional"},
        "everyday":   {"liner": "nude liner", "lipstick": "sheer pink or tinted balm", "shade_name": "Sheer Blush", "gloss": "clear gloss", "tip": "keep lips moisturised and natural"},
        "date":       {"liner": "rose liner", "lipstick": "coral rose satin", "shade_name": "Coral Kiss", "gloss": "clear gloss on centre", "tip": "a glossy centre lip looks romantic and full"},
    }

    # ── Outfit ────────────────────────────────────────────────
    outfit_looks = {
        "wedding":    {"dressing": "deep red or maroon embroidered lehenga or shalwar kameez", "dupatta": "red or gold chiffon dupatta with heavy embroidery", "footwear": "golden heels or red embroidered khussa", "style_note": "go for rich jewel tones and heavy embroidery"},
        "mehndi":     {"dressing": "bright yellow or green gharara or lehenga", "dupatta": "yellow or orange dupatta with mirror work", "footwear": "yellow or green embroidered khussa", "style_note": "embrace bright happy colours for mehndi"},
        "dholki":     {"dressing": "colourful printed or embroidered shalwar kameez", "dupatta": "bright contrast dupatta", "footwear": "colourful block heels or khussa", "style_note": "be bold and colourful — dholki is fun!"},
        "eid":        {"dressing": "pastel or bright embroidered shalwar kameez or sharara", "dupatta": "matching chiffon or silk dupatta", "footwear": "nude or gold heels or embroidered khussa", "style_note": "fresh pastels or vibrant colours work beautifully for Eid"},
        "valima":     {"dressing": "elegant pastel or gold formal suit or saree", "dupatta": "sheer chiffon dupatta with border", "footwear": "golden or nude heels", "style_note": "soft and elegant is the perfect Valima vibe"},
        "party":      {"dressing": "elegant sharara or embroidered formal suit or sequin dress", "dupatta": "sheer chiffon dupatta or no dupatta for western", "footwear": "strappy heels or embellished sandals", "style_note": "dress to impress — go bold or elegant"},
        "date":       {"dressing": "soft pastel shalwar kameez or floral midi dress", "dupatta": "light chiffon or no dupatta", "footwear": "nude block heels or white sandals", "style_note": "keep it soft and feminine for a date"},
        "university": {"dressing": "simple printed shalwar kameez or jeans with a blouse", "dupatta": "simple cotton dupatta or scarf", "footwear": "white sneakers or comfortable flats", "style_note": "comfortable and stylish — keep it practical"},
        "office":     {"dressing": "solid colour formal shalwar kameez or a blazer with trousers", "dupatta": "plain or subtle dupatta or silk scarf", "footwear": "block heels or loafers", "style_note": "neat and professional — stick to neutrals and solids"},
        "everyday":   {"dressing": "comfortable cotton shalwar kameez or casual jeans and top", "dupatta": "light cotton dupatta or no dupatta", "footwear": "comfortable flats or sandals", "style_note": "everyday comfort meets casual style"},
    }

    # ── Accessories ────────────────────────────────────────────
    accessories_looks = {
        "wedding":    {"jewellery": "gold polki set — earrings, necklace and maang teeka", "bag": "small golden or red bridal clutch", "extra": "bangles and haath phool"},
        "mehndi":     {"jewellery": "colourful meenakari or floral jewellery with bangles", "bag": "small colourful potli bag", "extra": "flower jhoomar or floral accessories"},
        "dholki":     {"jewellery": "colourful jhumkas and bangles", "bag": "small colourful clutch", "extra": "colourful hair accessories"},
        "eid":        {"jewellery": "simple gold earrings and thin bangles", "bag": "small matching clutch", "extra": "delicate bracelet or watch"},
        "valima":     {"jewellery": "elegant pearl or gold earrings and bracelet", "bag": "small embellished clutch", "extra": "subtle hair pin or headband"},
        "party":      {"jewellery": "statement earrings and bracelet", "bag": "small evening clutch", "extra": "rings or bold cuff"},
        "date":       {"jewellery": "simple delicate earrings", "bag": "small crossbody bag", "extra": "delicate ring or charm bracelet"},
        "university": {"jewellery": "simple studs or small hoops", "bag": "tote bag or backpack", "extra": "watch or simple bracelet"},
        "office":     {"jewellery": "simple pearl or gold studs", "bag": "structured handbag", "extra": "simple watch"},
        "everyday":   {"jewellery": "simple earrings", "bag": "casual tote or shoulder bag", "extra": "everyday watch"},
    }

    # ── Brands (fallback by skin type) ────────────────────────
    skin_type_lower = (skin_type or "normal").lower()
    brand_tips = {
        "oily":        "For oily skin: choose oil-free, matte formulas — L'Oreal Infallible, Huda Beauty FauxFilter, or NYX.",
        "dry":         "For dry skin: choose hydrating, dewy formulas — Charlotte Tilbury, Fenty Beauty, or Dior Backstage.",
        "combination": "For combination skin: use a balanced formula — MAC Studio Fix, Maybelline Fit Me Matte+Poreless, or Bourjois.",
        "sensitive":   "For sensitive skin: choose fragrance-free, gentle formulas — Clinique, La Roche-Posay, or Bare Minerals.",
    }
    brands = {
        "foundation_brand": "Huda Beauty FauxFilter (full coverage) or Maybelline Fit Me (light-medium)",
        "lip_brand": "Charlotte Tilbury Pillow Talk or L'Oreal Color Riche",
        "eye_brand": "Maybelline Sky High mascara + Essence eyeliner",
        "blush_brand": "NARS Orgasm blush or e.l.f. Monochromatic Multi-Stick",
        "drugstore_pick": "L'Oreal Infallible 24H (budget-friendly option)",
        "tip": brand_tips.get(skin_type_lower, "Choose products suited to your skin type for the best finish."),
    }

    # ── Lens (fallback by skin tone) ──────────────────────────
    tone_lens = {
        "porcelain": "soft blue or violet", "very_fair": "grey or soft blue",
        "fair": "hazel or soft green", "light": "honey brown or warm hazel",
        "medium": "warm honey or light brown", "tan": "golden brown or amber",
        "wheatish": "chestnut brown or hazel", "brown": "dark honey or copper",
        "deep": "dark brown or subtle bronze", "rich": "deep brown or onyx",
    }
    lens_color = tone_lens.get((skin_tone or "medium").lower().replace(" ", "_"), "honey brown")
    lens = {
        "color": lens_color,
        "brand_suggestion": "FreshLook Illuminate or Solotica Hidrocor",
        "reason": f"{lens_color} lenses complement {skin_tone or 'medium'} skin beautifully",
        "tip": "always use lens-safe drops and never sleep in lenses",
    }

    # ── Hair / Hijab ──────────────────────────────────────────
    if hijab:
        hair_hijab_looks = {
            "wedding":  "silk or organza pleated hijab with pearl pins — draped elegantly",
            "mehndi":   "colourful chiffon hijab with flower pins — match outfit colour",
            "dholki":   "fun colourful hijab with jhoomar pin and frilly style",
            "eid":      "simple chiffon hijab neatly draped with minimal pins",
            "party":    "georgette or velvet hijab with a side brooch — elegant and modern",
            "office":   "neat cotton or jersey hijab in a neutral tone",
            "everyday": "simple jersey hijab — quick and comfortable wrap",
        }
        style = hair_hijab_looks.get(e, "simple neatly wrapped hijab suitable for the occasion")
        hair_hijab = {
            "style": style,
            "color_suggestion": "match hijab colour to outfit or complement with a neutral tone",
            "accessory": "pearl hijab pins or a brooch for formal occasions",
            "tip": "a silk undercap prevents slipping and keeps your hijab in place all day",
        }
    else:
        hair_looks = {
            "wedding":  "elegant updo or loose romantic curls with hair accessories",
            "mehndi":   "loose curls or braided half-up with flowers",
            "dholki":   "fun loose waves or high ponytail with colourful accessories",
            "eid":      "soft curls or a neat blowout — half-up looks beautiful",
            "party":    "sleek straight hair or voluminous curls",
            "office":   "neat bun or low ponytail — professional and polished",
            "everyday": "natural loose hair or a casual bun",
        }
        style = hair_looks.get(e, "natural loose hair styled to suit the occasion")
        hair_hijab = {
            "style": style,
            "color_suggestion": "warm highlights like caramel or honey complement most skin tones",
            "accessory": "a gold hair clip or pearl pins for formal events",
            "tip": "a light serum on ends gives a healthy glossy finish",
        }

    # ── Weather tip ───────────────────────────────────────────
    if weather and not weather.get("error"):
        cat = weather.get("category", "mild")
        weather_tips = {
            "rainy":     "Use waterproof mascara, waterproof liner, and a long-wear setting spray today.",
            "hot_humid": "Go oil-free and matte — use setting spray and blotting sheets to control shine.",
            "cold":      "Moisturise well before makeup; the cold air dries skin. A dewy finish looks gorgeous in winter.",
            "mild":      "Perfect makeup weather today — a satin or dewy finish will look beautiful.",
        }
        weather_tip = weather_tips.get(cat, "Standard recommendations apply today.")
    else:
        weather_tip = "Consider the weather when doing your makeup — waterproof products are great for humid or rainy days."

    face   = face_looks.get(e, face_looks["everyday"])
    eyes   = eyes_looks.get(e, eyes_looks["everyday"])
    lips   = lips_looks.get(e, lips_looks["everyday"])
    outfit = outfit_looks.get(e, outfit_looks["everyday"])
    accs   = accessories_looks.get(e, accessories_looks["everyday"])

    return {
        "skin_analysis": {
            "detected_tone": (skin_tone or "medium").replace("_", " ").capitalize(),
            "undertone": (undertone or "Warm").capitalize(),
            "finish": "Matte" if is_night else "Dewy",
        },
        "face": face,
        "eyes": eyes,
        "lips": lips,
        "outfit": outfit,
        "accessories": accs,
        "brands": brands,
        "lens": lens,
        "hair_hijab": hair_hijab,
        "weather_tip": weather_tip,
        "overall_tip": f"A {'glamorous' if is_formal else 'fresh'} look perfect for {e} — confidence is your best accessory! ✨",
    }
