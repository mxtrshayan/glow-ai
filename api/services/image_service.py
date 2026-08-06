# api/services/image_service.py
# ── Image preprocessing ───────────────────────────────────────
import io, base64
from PIL import Image


def preprocess_image(file_bytes: bytes) -> str:
    """Resize + compress image and return base64 JPEG string."""
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    if max(img.size) > 800:
        img.thumbnail((800, 800), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
