# api/virtual_tryon/face_landmarks.py
# ── MediaPipe Face Landmarker landmark extraction service ───────────
import os
import urllib.request
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python as mp_python

# Facial Landmark Indices (468 standard MediaPipe topology)
LIPS_OUTER_INDICES = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LIPS_INNER_INDICES = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
UPPER_LIP_INDICES  = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191, 78]
LOWER_LIP_INDICES  = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78]

LEFT_EYE_LASH_INDICES  = [33, 161, 160, 159, 158, 157, 173, 133]
RIGHT_EYE_LASH_INDICES = [362, 384, 385, 386, 387, 388, 398, 263]

LEFT_EYELID_INDICES  = [33, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
RIGHT_EYELID_INDICES = [362, 384, 385, 386, 387, 388, 398, 263, 382, 381, 380, 374, 373, 390, 249]

LEFT_CHEEK_INDICES  = [116, 117, 118, 101, 50, 187, 205, 207, 213, 192]
RIGHT_CHEEK_INDICES = [345, 346, 347, 330, 280, 411, 425, 427, 433, 416]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "face_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"

_landmarker_instance = None


def get_landmarker():
    """Lazily load and cache the MediaPipe FaceLandmarker instance."""
    global _landmarker_instance
    if _landmarker_instance is not None:
        return _landmarker_instance

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    if not os.path.exists(MODEL_PATH) or os.path.getsize(MODEL_PATH) < 1000:
        print("Downloading face_landmarker model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=2,
        min_face_detection_confidence=0.5,
    )
    _landmarker_instance = vision.FaceLandmarker.create_from_options(options)
    return _landmarker_instance


class FaceLandmarksResult:
    def __init__(self, height: int, width: int, landmarks: list):
        self.height = height
        self.width = width
        self.raw_landmarks = landmarks

    def get_points(self, indices: list) -> np.ndarray:
        """Convert normalized landmark indices to (x, y) pixel coordinates."""
        pts = []
        for idx in indices:
            lm = self.raw_landmarks[idx]
            x = int(lm.x * self.width)
            y = int(lm.y * self.height)
            pts.append([x, y])
        return np.array(pts, dtype=np.int32)


def detect_face_landmarks(image_bgr: np.ndarray) -> FaceLandmarksResult:
    """
    Detect face landmarks from a BGR OpenCV image.
    Raises ValueError if no face or multiple faces are detected.
    """
    h, w, _ = image_bgr.shape
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    landmarker = get_landmarker()
    results = landmarker.detect(mp_img)

    if not results.face_landmarks or len(results.face_landmarks) == 0:
        raise ValueError("No face detected in photo. Please upload a clear front-facing portrait.")

    if len(results.face_landmarks) > 1:
        raise ValueError("Multiple faces detected. Please upload a photo with a single person.")

    landmarks = results.face_landmarks[0]
    return FaceLandmarksResult(height=h, width=w, landmarks=landmarks)
