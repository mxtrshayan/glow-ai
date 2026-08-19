# api/virtual_tryon/makeup_engine.py
# ── Virtual Makeup Engine Coordinator ────────────────────────────────────
import numpy as np
from api.virtual_tryon.face_landmarks import detect_face_landmarks
from api.virtual_tryon.lipstick import apply_lipstick
from api.virtual_tryon.blush import apply_blush
from api.virtual_tryon.eyeshadow import apply_eyeshadow
from api.virtual_tryon.eyeliner import apply_eyeliner


def apply_virtual_makeup(image_bgr: np.ndarray, makeup_config: dict) -> tuple[np.ndarray, list[str]]:
    """
    Coordinator function that detects facial landmarks and applies
    configured makeup items in realistic visual layering order:
    1. Eyeshadow
    2. Eyeliner
    3. Blush
    4. Lipstick
    """
    landmarks = detect_face_landmarks(image_bgr)
    result = image_bgr.copy()
    applied = []

    # 1. Eyeshadow
    eyeshadow_cfg = makeup_config.get("eyeshadow", {})
    if eyeshadow_cfg.get("enabled", True) and eyeshadow_cfg.get("color"):
        result = apply_eyeshadow(
            image_bgr=result,
            landmarks=landmarks,
            color_hex=eyeshadow_cfg["color"],
            opacity=float(eyeshadow_cfg.get("opacity", 0.45)),
        )
        applied.append("eyeshadow")

    # 2. Eyeliner
    eyeliner_cfg = makeup_config.get("eyeliner", {})
    if eyeliner_cfg.get("enabled", True) and eyeliner_cfg.get("color"):
        result = apply_eyeliner(
            image_bgr=result,
            landmarks=landmarks,
            color_hex=eyeliner_cfg["color"],
            opacity=float(eyeliner_cfg.get("opacity", 0.85)),
            style=eyeliner_cfg.get("style", "winged"),
        )
        applied.append("eyeliner")

    # 3. Blush
    blush_cfg = makeup_config.get("blush", {})
    if blush_cfg.get("enabled", True) and blush_cfg.get("color"):
        result = apply_blush(
            image_bgr=result,
            landmarks=landmarks,
            color_hex=blush_cfg["color"],
            opacity=float(blush_cfg.get("opacity", 0.35)),
        )
        applied.append("blush")

    # 4. Lipstick
    lipstick_cfg = makeup_config.get("lipstick", {})
    if lipstick_cfg.get("enabled", True) and lipstick_cfg.get("color"):
        result = apply_lipstick(
            image_bgr=result,
            landmarks=landmarks,
            color_hex=lipstick_cfg["color"],
            opacity=float(lipstick_cfg.get("opacity", 0.7)),
            finish=lipstick_cfg.get("finish", "satin"),
        )
        applied.append("lipstick")

    return result, applied
