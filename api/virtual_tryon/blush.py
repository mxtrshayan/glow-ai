# api/virtual_tryon/blush.py
# ── Cheek blush application using feathered elliptical gradients ─────────
import cv2
import numpy as np
from api.virtual_tryon.face_landmarks import FaceLandmarksResult
from api.virtual_tryon.blending import hex_to_bgr, blend_color_lab


def apply_blush(
    image_bgr: np.ndarray,
    landmarks: FaceLandmarksResult,
    color_hex: str = "#E07A7A",
    opacity: float = 0.35,
) -> np.ndarray:
    """
    Apply soft feathered blush to left and right cheeks.
    """
    if opacity <= 0.01:
        return image_bgr

    h, w, _ = image_bgr.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    # Key cheek center landmarks in MediaPipe Face Mesh:
    # Left cheek: landmark 116 / 117 / 50 / 205 (prominence center ~ 116, 50, 205)
    # Right cheek: landmark 345 / 346 / 280 / 425 (prominence center ~ 345, 280, 425)
    left_cheek_pts = landmarks.get_points([116, 117, 50, 187, 205])
    right_cheek_pts = landmarks.get_points([345, 346, 280, 411, 425])

    # Left cheek center & radius
    left_center = np.mean(left_cheek_pts, axis=0).astype(int)
    right_center = np.mean(right_cheek_pts, axis=0).astype(int)

    # Scale blush ellipse dimensions relative to face/image size
    face_width_est = max(20, int(np.linalg.norm(left_center - right_center)))
    axes = (int(face_width_est * 0.28), int(face_width_est * 0.20))

    # Draw solid ellipses in mask
    cv2.ellipse(mask, tuple(left_center), axes, angle=15, startAngle=0, endAngle=360, color=255, thickness=-1)
    cv2.ellipse(mask, tuple(right_center), axes, angle=-15, startAngle=0, endAngle=360, color=255, thickness=-1)

    # Apply heavy Gaussian blur for smooth natural blush diffusion
    blur_k = int(face_width_est * 0.35)
    if blur_k % 2 == 0:
        blur_k += 1
    blur_k = max(15, blur_k)

    feathered_mask = cv2.GaussianBlur(mask, (blur_k, blur_k), sigmaX=blur_k / 2.5).astype(np.float32) / 255.0

    color_bgr = hex_to_bgr(color_hex)

    return blend_color_lab(
        image_bgr=image_bgr,
        mask=feathered_mask,
        color_bgr=color_bgr,
        opacity=opacity,
        lightness_influence=0.2,
    )
