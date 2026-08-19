# api/virtual_tryon/eyeshadow.py
# ── Eyeshadow application on upper eyelid contours ───────────────────────
import cv2
import numpy as np
from api.virtual_tryon.face_landmarks import FaceLandmarksResult
from api.virtual_tryon.blending import hex_to_bgr, blend_color_lab


# Landmark indices for eyelid / crease region above lash line
LEFT_EYESHADOW_INDICES = [33, 246, 161, 160, 159, 158, 157, 173, 133, 243, 190, 56, 28, 27, 29, 30, 247, 226]
RIGHT_EYESHADOW_INDICES = [263, 466, 388, 387, 386, 385, 384, 398, 362, 463, 414, 286, 258, 257, 259, 260, 467, 446]

# Left / right eye socket boundaries to avoid bleeding onto eyeball/iris
LEFT_EYE_SOCKET = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE_SOCKET = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]


def apply_eyeshadow(
    image_bgr: np.ndarray,
    landmarks: FaceLandmarksResult,
    color_hex: str = "#8B5A2B",
    opacity: float = 0.45,
) -> np.ndarray:
    """
    Apply soft blended eyeshadow on the upper eyelids.
    """
    if opacity <= 0.01:
        return image_bgr

    h, w, _ = image_bgr.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    left_shadow_pts = landmarks.get_points(LEFT_EYESHADOW_INDICES)
    right_shadow_pts = landmarks.get_points(RIGHT_EYESHADOW_INDICES)

    cv2.fillPoly(mask, [left_shadow_pts], 255)
    cv2.fillPoly(mask, [right_shadow_pts], 255)

    # Calculate blur radius based on eye size
    left_eye_pts = landmarks.get_points(LEFT_EYE_SOCKET)
    eye_w = np.max(left_eye_pts[:, 0]) - np.min(left_eye_pts[:, 0])
    blur_k = max(7, int(eye_w * 0.35))
    if blur_k % 2 == 0:
        blur_k += 1

    feathered_mask = cv2.GaussianBlur(mask, (blur_k, blur_k), sigmaX=blur_k / 2.0).astype(np.float32) / 255.0

    color_bgr = hex_to_bgr(color_hex)

    return blend_color_lab(
        image_bgr=image_bgr,
        mask=feathered_mask,
        color_bgr=color_bgr,
        opacity=opacity,
        lightness_influence=0.3,
    )
