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
    import local_settings as _local_settings
except ModuleNotFoundError:
    _local_settings = None
except Exception as error:
    raise RuntimeError(
        "FaceVision could not read local_settings.py. Fix its Python syntax or restore it from local_settings.example.py."
    ) from error

BLYNK_AUTH_TOKEN = getattr(_local_settings, "BLYNK_AUTH_TOKEN", os.getenv("BLYNK_AUTH_TOKEN", ""))
ESP32_STREAM_URL = getattr(_local_settings, "ESP32_STREAM_URL", os.getenv("FACEVISION_ESP32_STREAM_URL", ""))

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
SHARPENING_ENABLED = True
SHARPENING_AMOUNT = 0.35

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

# Remote viewer. It serves only the finished, annotated OpenCV frame—not the
# ESP32 camera feed or a second recognition pipeline. Use Tailscale to reach
# http://<this-PC's-Tailscale-IP>:8080 from the phone on any network.
REMOTE_VIEWER_ENABLED = getattr(_local_settings, "REMOTE_VIEWER_ENABLED", True)
REMOTE_VIEWER_HOST = getattr(_local_settings, "REMOTE_VIEWER_HOST", "0.0.0.0")
REMOTE_VIEWER_PORT = getattr(_local_settings, "REMOTE_VIEWER_PORT", 8080)
REMOTE_VIEWER_MAX_WIDTH = getattr(_local_settings, "REMOTE_VIEWER_MAX_WIDTH", 800)
REMOTE_VIEWER_JPEG_QUALITY = getattr(_local_settings, "REMOTE_VIEWER_JPEG_QUALITY", 80)
REMOTE_VIEWER_MAX_FPS = getattr(_local_settings, "REMOTE_VIEWER_MAX_FPS", 12)
CAPTURE_STILL_ENABLED = getattr(_local_settings, "CAPTURE_STILL_ENABLED", True)
