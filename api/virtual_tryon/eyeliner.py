# api/virtual_tryon/eyeliner.py
# ── Precision upper lash eyeliner with optional wing ─────────────────────
import cv2
import numpy as np
from api.virtual_tryon.face_landmarks import (
    FaceLandmarksResult,
    LEFT_EYE_LASH_INDICES,
    RIGHT_EYE_LASH_INDICES,
)
from api.virtual_tryon.blending import hex_to_bgr, blend_color_lab


def apply_eyeliner(
    image_bgr: np.ndarray,
    landmarks: FaceLandmarksResult,
    color_hex: str = "#1A1A1A",
    opacity: float = 0.85,
    style: str = "winged",  # natural, classic, winged
) -> np.ndarray:
    """
    Apply clean anti-aliased eyeliner along the upper lash lines.
    """
    if opacity <= 0.01:
        return image_bgr

    h, w, _ = image_bgr.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    left_lash = landmarks.get_points(LEFT_EYE_LASH_INDICES)
    right_lash = landmarks.get_points(RIGHT_EYE_LASH_INDICES)

    # Estimate eye size for line thickness
    eye_w = max(10, np.max(left_lash[:, 0]) - np.min(left_lash[:, 0]))
    thickness = max(2, int(eye_w * 0.05))

    left_pts_list = left_lash.tolist()
    right_pts_list = right_lash.tolist()

    # If winged style, extend outer corner
    if style == "winged":
        # Left eye outer corner is index 133 (last point in lash)
        # Vector from inner (33) to outer (133)
        p_prev = np.array(left_pts_list[-2])
        p_last = np.array(left_pts_list[-1])
        dir_vec = p_last - p_prev
        # Wing direction: outward and slightly up
        wing_len = eye_w * 0.22
        wing_left = (p_last + [int(dir_vec[0] * 0.7 + wing_len * 0.8), int(-wing_len * 0.4)]).astype(int)
        left_pts_list.append(wing_left.tolist())

        # Right eye outer corner is index 263 (last point in lash)
        p_prev_r = np.array(right_pts_list[-2])
        p_last_r = np.array(right_pts_list[-1])
        dir_vec_r = p_last_r - p_prev_r
        wing_right = (p_last_r + [int(dir_vec_r[0] * 0.7 + wing_len * 0.8), int(-wing_len * 0.4)]).astype(int)
        right_pts_list.append(wing_right.tolist())

    pts_l = np.array(left_pts_list, dtype=np.int32).reshape((-1, 1, 2))
    pts_r = np.array(right_pts_list, dtype=np.int32).reshape((-1, 1, 2))

    cv2.polylines(mask, [pts_l], isClosed=False, color=255, thickness=thickness, lineType=cv2.LINE_AA)
    cv2.polylines(mask, [pts_r], isClosed=False, color=255, thickness=thickness, lineType=cv2.LINE_AA)

    # Soft feathering on liner edge
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    feathered_mask = mask.astype(np.float32) / 255.0

    color_bgr = hex_to_bgr(color_hex)

    return blend_color_lab(
        image_bgr=image_bgr,
        mask=feathered_mask,
        color_bgr=color_bgr,
        opacity=opacity,
        lightness_influence=0.8,
    )
