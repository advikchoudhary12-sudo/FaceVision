# =========================
# FaceVision Config
# =========================

# Camera
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Launcher and Blynk settings are loaded from local_settings.py when present.
# That file is ignored by Git so private network and device-token data stays local.
import os

try:
    from local_settings import BLYNK_AUTH_TOKEN, ESP32_STREAM_URL
except ImportError:
    BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN", "")
    ESP32_STREAM_URL = os.getenv("FACEVISION_ESP32_STREAM_URL", "")

CAMERA_PRESETS = {
    "ESP32-CAM": ESP32_STREAM_URL,
    "Laptop Webcam": 0,
    "Camera Index 1 (USB Webcam)": 1,
}
DEFAULT_CAMERA = "Laptop Webcam"
LAUNCHER_TITLE = "FaceVision Launcher"

# Blynk IoT: configure V0 as an integer LED/status datastream, V1 as an FPS
# datastream, and create the `unknown_detected` event in your Blynk template.
BLYNK_SERVER = "https://blynk.cloud"
BLYNK_STATUS_PIN = "V0"
BLYNK_FPS_PIN = "V1"
BLYNK_UNKNOWN_EVENT = "unknown_detected"
BLYNK_UPDATE_INTERVAL_SECONDS = 5.0
UNKNOWN_DETECTIONS_REQUIRED = 45

# AI Model
MODEL_NAME = "buffalo_s"
CTX_ID = 0  # 0 = GPU, -1 = CPU (the app falls back to CPU if GPU init fails)
DET_SIZE = (320, 320)

# Recognition
THRESHOLD = 0.55

# Performance
PROCESS_EVERY_N_FRAMES = 4

# Paths
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KNOWN_FACES_PATH = BASE_DIR / "data" / "known_faces"

# UI
WINDOW_NAME = "FaceVision"
SHOW_FPS = True
DISPLAY_SCALE = 2.0
