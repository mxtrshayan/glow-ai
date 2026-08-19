# api/virtual_tryon/lipstick.py
# ── Lipstick application using lip contours and luminance preservation ──
import cv2
import numpy as np
from api.virtual_tryon.face_landmarks import (
    FaceLandmarksResult,
    LIPS_OUTER_INDICES,
    LIPS_INNER_INDICES,
)
from api.virtual_tryon.blending import (
    hex_to_bgr,
    create_feathered_mask,
    blend_color_lab,
)


def apply_lipstick(
    image_bgr: np.ndarray,
    landmarks: FaceLandmarksResult,
    color_hex: str = "#C8385A",
    opacity: float = 0.7,
    finish: str = "satin",  # matte, satin, gloss
) -> np.ndarray:
    """
    Apply realistic lipstick to detected lips.
    Preserves natural lip texture, wrinkles, and specular highlights.
    """
    if opacity <= 0.01:
        return image_bgr

    outer_pts = landmarks.get_points(LIPS_OUTER_INDICES)
    inner_pts = landmarks.get_points(LIPS_INNER_INDICES)

    h, w, _ = image_bgr.shape
    # Subtle blur for crisp yet soft edge matching image resolution
    blur_r = max(3, int(min(h, w) * 0.006))
    if blur_r % 2 == 0:
        blur_r += 1

    mask = create_feathered_mask(
        height=h,
        width=w,
        polygon_pts=outer_pts,
        blur_radius=blur_r,
        hole_pts=inner_pts,
    )

    color_bgr = hex_to_bgr(color_hex)

    # Adjust lightness influence according to finish
    lightness_inf = 0.25
    if finish == "matte":
        lightness_inf = 0.4
    elif finish == "gloss":
        lightness_inf = 0.15

    blended = blend_color_lab(
        image_bgr=image_bgr,
        mask=mask,
        color_bgr=color_bgr,
        opacity=opacity,
        lightness_influence=lightness_inf,
    )

    # Gloss highlight effect
    if finish == "gloss":
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        # Find brighter specular spots on lips
        _, highlight_mask = cv2.threshold(gray, 175, 255, cv2.THRESH_BINARY)
        highlight_mask = (highlight_mask.astype(np.float32) / 255.0) * mask
        highlight_mask = cv2.GaussianBlur(highlight_mask, (5, 5), 0)
        gloss_layer = np.clip(blended.astype(np.float32) + (highlight_mask[:, :, None] * 35.0), 0, 255).astype(np.uint8)
        return gloss_layer

    return blended
