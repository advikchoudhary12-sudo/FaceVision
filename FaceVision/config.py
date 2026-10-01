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
import math

try:
    import local_settings as _local_settings
except ModuleNotFoundError:
    _local_settings = None
except Exception as error:
    raise RuntimeError(
        "FaceVision could not read local_settings.py. Fix its Python syntax or restore it from local_settings.example.py."
    ) from error


def _setting(name, default):
    return getattr(_local_settings, name, default)


def _bounded_float(name, default, minimum, maximum):
    value = float(_setting(name, default))
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be a finite number from {minimum} to {maximum}.")
    return value


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
SHARPENING_ENABLED = bool(_setting("SHARPENING_ENABLED", True))
SHARPENING_AMOUNT = _bounded_float("SHARPENING_AMOUNT", 0.35, 0.0, 1.0)

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
REMOTE_VIEWER_ENABLED = bool(_setting("REMOTE_VIEWER_ENABLED", True))
REMOTE_VIEWER_HOST = _setting("REMOTE_VIEWER_HOST", "0.0.0.0")
REMOTE_VIEWER_PORT = int(_setting("REMOTE_VIEWER_PORT", 8080))
REMOTE_VIEWER_MAX_WIDTH = int(_setting("REMOTE_VIEWER_MAX_WIDTH", 800))
REMOTE_VIEWER_JPEG_QUALITY = int(_setting("REMOTE_VIEWER_JPEG_QUALITY", 80))
REMOTE_VIEWER_MAX_FPS = int(_setting("REMOTE_VIEWER_MAX_FPS", 12))
CAPTURE_STILL_ENABLED = bool(_setting("CAPTURE_STILL_ENABLED", True))

# The blind stick reuses the existing FaceVision Blynk device token.
BLIND_STICK_PIN = str(_setting("BLIND_STICK_PIN", "V10")).upper()
BLIND_STICK_POLL_INTERVAL_SECONDS = float(
    _setting("BLIND_STICK_POLL_INTERVAL_SECONDS", 1.0)
)
if not math.isfinite(BLIND_STICK_POLL_INTERVAL_SECONDS) or BLIND_STICK_POLL_INTERVAL_SECONDS <= 0:
    raise ValueError("BLIND_STICK_POLL_INTERVAL_SECONDS must be greater than zero.")
BLIND_STICK_VOICE_DIRECTORY = BASE_DIR / "BlindStick" / "Voice"
VOICE_FILES = dict(_setting("VOICE_FILES", {"unknown": "unknown.mp3"}))
DEFAULT_VOICE_FILE = str(
    _setting("DEFAULT_VOICE_FILE", VOICE_FILES.get("default", "unknown.mp3"))
)
VOICE_FILES["default"] = DEFAULT_VOICE_FILE
AUDIO_REPLAY_COOLDOWN_MS = int(_setting("AUDIO_REPLAY_COOLDOWN_MS", 5000))
if AUDIO_REPLAY_COOLDOWN_MS < 0:
    raise ValueError("AUDIO_REPLAY_COOLDOWN_MS cannot be negative.")
