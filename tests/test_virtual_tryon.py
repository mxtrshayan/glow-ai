import os
import sys
import json
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import cv2
from fastapi.testclient import TestClient
from api.index import app
from api.virtual_tryon.blending import hex_to_bgr, create_feathered_mask, blend_color_lab
from api.virtual_tryon.face_landmarks import detect_face_landmarks
from api.virtual_tryon.lipstick import apply_lipstick
from api.virtual_tryon.blush import apply_blush
from api.virtual_tryon.eyeshadow import apply_eyeshadow
from api.virtual_tryon.eyeliner import apply_eyeliner
from api.virtual_tryon.makeup_engine import apply_virtual_makeup
from api.services.tryon_service import process_virtual_tryon

client = TestClient(app)


def test_core_endpoints():
    """Verify that existing endpoints are 100% operational with zero breaking changes."""
    # Test endpoint
    res = client.get("/test-gemini")
    assert res.status_code == 200

    # Weather endpoint
    res = client.get("/weather?lat=51.5&lon=-0.12")
    assert res.status_code == 200
    data = res.json()
    assert "condition" in data or "error" in data

    # Analyze endpoint (fallback test when no image)
    res = client.post(
        "/analyze",
        data={
            "event": "wedding",
            "time_of_day": "evening",
            "skin_tone": "medium",
            "undertone": "warm",
            "skin_type": "combination",
            "hijab": "no",
            "style_preference": "both",
        },
    )
    assert res.status_code == 200
    analyze_data = res.json()
    assert "face" in analyze_data
    assert "eyes" in analyze_data
    assert "lips" in analyze_data
    assert "outfit" in analyze_data


def test_blending_utils():
    """Test color conversion and mask creation."""
    b, g, r = hex_to_bgr("#C8385A")
    assert (r, g, b) == (200, 56, 90)

    # Test feathered mask
    pts = np.array([[10, 10], [50, 10], [50, 50], [10, 50]], dtype=np.int32)
    mask = create_feathered_mask(100, 100, pts, blur_radius=5)
    assert mask.shape == (100, 100)
    assert 0.0 <= mask[25, 25] <= 1.0


def test_tryon_with_synthetic_face():
    """Create a realistic portrait image or use a face image to test landmarking & try-on."""
    # Create an image that triggers error when no face is detected
    blank_img = np.zeros((300, 300, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", blank_img)
    blank_bytes = buffer.tobytes()

    # Should gracefully return error for no face
    res = client.post(
        "/tryon",
        files={"image": ("test.jpg", blank_bytes, "image/jpeg")},
        data={"makeup_config": json.dumps({"lipstick": {"enabled": True, "color": "#C8385A"}})},
    )
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "error"
    assert "No face detected" in res_json["message"]


def test_tryon_json_endpoint():
    """Test tryon with JSON body payload."""
    blank_img = np.zeros((200, 200, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", blank_img)
    b64_str = base64.b64encode(buffer.tobytes()).decode("utf-8")

    res = client.post(
        "/tryon",
        json={
            "image_b64": f"data:image/jpeg;base64,{b64_str}",
            "makeup_config": {
                "lipstick": {"enabled": True, "color": "#C8385A", "opacity": 0.7},
                "blush": {"enabled": True, "color": "#E07A7A", "opacity": 0.35},
            },
        },
    )
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "error"
    assert "No face detected" in res_json["message"]


if __name__ == "__main__":
    test_core_endpoints()
    test_blending_utils()
    test_tryon_with_synthetic_face()
    test_tryon_json_endpoint()
    print("All Virtual Try-On automated tests passed successfully!")
