# api/routes/tryon.py
# ── /tryon POST route for photo-based virtual makeup try-on ──
import json
import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from api.services.tryon_service import process_virtual_tryon

router = APIRouter()


def parse_makeup_config(value) -> dict:
    """Normalize multipart and JSON config values to a makeup dictionary."""
    if value in (None, ""):
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid makeup_config JSON.") from exc
        if isinstance(parsed, dict):
            return parsed
    raise HTTPException(status_code=400, detail="makeup_config must be a JSON object.")


@router.post("/tryon")
async def tryon(
    request: Request,
    image: UploadFile | None = File(default=None),
    image_b64: str = Form(default=""),
    makeup_config: str = Form(default="{}"),
):
    """
    Apply photo-based virtual makeup try-on.
    Accepts multipart form-data (file upload or image_b64) or application/json payload.
    """
    content_type = request.headers.get("content-type", "")
    config_dict = {}
    raw_bytes = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            config_dict = parse_makeup_config(body.get("makeup_config", {}))
            b64_data = body.get("image_b64", "")
            if b64_data:
                if "," in b64_data:
                    b64_data = b64_data.split(",", 1)[1]
                raw_bytes = base64.b64decode(b64_data)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")
    else:
        # Multipart form data
        if image and image.filename:
            raw_bytes = await image.read()
        elif image_b64:
            clean_b64 = image_b64
            if "," in clean_b64:
                clean_b64 = clean_b64.split(",", 1)[1]
            try:
                raw_bytes = base64.b64decode(clean_b64)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid base64 image data.")

        if makeup_config:
            config_dict = parse_makeup_config(makeup_config)

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Please provide a selfie photo to try on makeup.")

    try:
        result = process_virtual_tryon(raw_bytes, config_dict)
        return result
    except ValueError as val_err:
        return {
            "status": "error",
            "message": str(val_err),
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Try-on processing failed: {str(exc)}",
        }
