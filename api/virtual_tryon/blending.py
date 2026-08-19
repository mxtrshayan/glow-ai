# api/virtual_tryon/blending.py
# ── Color conversions and texture-preserving blending routines ───────────
import cv2
import numpy as np


def hex_to_bgr(hex_code: str) -> tuple[int, int, int]:
    """Convert hex color string (e.g. '#D44A6A' or 'D44A6A') to BGR tuple."""
    hex_code = hex_code.lstrip("#").strip()
    if len(hex_code) == 3:
        hex_code = "".join([c * 2 for c in hex_code])
    if len(hex_code) != 6:
        # Default fallback to a pleasant rose
        return (106, 74, 212)
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    return (b, g, r)


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    b, g, r = hex_to_bgr(hex_code)
    return (r, g, b)


def create_feathered_mask(
    height: int,
    width: int,
    polygon_pts: np.ndarray,
    blur_radius: int = 15,
    hole_pts: np.ndarray | None = None,
) -> np.ndarray:
    """
    Create a smoothed, feathered float32 mask (values 0.0 to 1.0)
    for a given polygon with optional cutout hole.
    """
    mask = np.zeros((height, width), dtype=np.uint8)

    if polygon_pts is not None and len(polygon_pts) > 0:
        cv2.fillPoly(mask, [polygon_pts], 255)

    if hole_pts is not None and len(hole_pts) > 0:
        cv2.fillPoly(mask, [hole_pts], 0)

    if blur_radius > 0:
        k = blur_radius if blur_radius % 2 == 1 else blur_radius + 1
        mask = cv2.GaussianBlur(mask, (k, k), sigmaX=blur_radius / 2)

    return mask.astype(np.float32) / 255.0


def blend_color_lab(
    image_bgr: np.ndarray,
    mask: np.ndarray,
    color_bgr: tuple[int, int, int],
    opacity: float = 0.6,
    lightness_influence: float = 0.25,
) -> np.ndarray:
    """
    Texture-preserving color blending using LAB color space.
    Preserves luminance details (wrinkles, specular highlights, textures)
    while smoothly transferring hue and chroma.
    """
    opacity = np.clip(opacity, 0.0, 1.0)
    if opacity <= 0.001:
        return image_bgr.copy()

    # Convert base image to LAB
    lab_img = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

    # Convert target color to LAB
    target_patch = np.zeros((1, 1, 3), dtype=np.uint8)
    target_patch[0, 0] = color_bgr
    target_lab = cv2.cvtColor(target_patch, cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0]

    # Effective blend factor across 3 channels
    alpha = np.clip(mask * opacity, 0.0, 1.0)
    alpha_3d = np.dstack([alpha, alpha, alpha])

    # Blend A and B channels (chroma) strongly
    blended_lab = lab_img.copy()
    blended_lab[:, :, 1] = lab_img[:, :, 1] * (1.0 - alpha) + target_lab[1] * alpha
    blended_lab[:, :, 2] = lab_img[:, :, 2] * (1.0 - alpha) + target_lab[2] * alpha

    # Adjust L (lightness) subtly if requested, preserving high-frequency texture
    if lightness_influence > 0:
        l_alpha = alpha * lightness_influence
        blended_lab[:, :, 0] = lab_img[:, :, 0] * (1.0 - l_alpha) + target_lab[0] * l_alpha

    blended_bgr = cv2.cvtColor(np.clip(blended_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    return blended_bgr


def blend_overlay_soft(
    image_bgr: np.ndarray,
    mask: np.ndarray,
    color_bgr: tuple[int, int, int],
    opacity: float = 0.4,
) -> np.ndarray:
    """
    Soft overlay tint blending for blush and subtle eyeshadows.
    """
    opacity = np.clip(opacity, 0.0, 1.0)
    if opacity <= 0.001:
        return image_bgr.copy()

    color_layer = np.full_like(image_bgr, color_bgr, dtype=np.uint8)

    # Alpha blend using feathered mask
    alpha = np.clip(mask * opacity, 0.0, 1.0)
    alpha_3d = np.dstack([alpha, alpha, alpha])

    blended = image_bgr.astype(np.float32) * (1.0 - alpha_3d) + color_layer.astype(np.float32) * alpha_3d
    return np.clip(blended, 0, 255).astype(np.uint8)
