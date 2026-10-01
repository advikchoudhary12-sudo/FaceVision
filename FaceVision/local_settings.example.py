# Copy this file to local_settings.py. It is ignored by Git.

# AI Thinker ESP32-CAM stream endpoint. The camera firmware serves MJPEG on
# port 81 at /stream. Use the local address printed by the ESP32 Serial Monitor.
ESP32_STREAM_URL = "http://<ESP32-IP>:81/stream"

# Blynk.Console -> Devices -> Device info -> Auth Token.
BLYNK_AUTH_TOKEN = "paste-your-blynk-device-token-here"

# The blind stick reuses BLYNK_AUTH_TOKEN above. Add V10 to that device's
# Blynk template and keep the same token in the ESP32-S3 secrets header.
BLIND_STICK_PIN = "V10"
BLIND_STICK_POLL_INTERVAL_SECONDS = 1.0

# Voice prompts in BlindStick/Voice/. "default" is used for V10 activations
# when no face is detected or no identity-specific prompt exists.
# Set DEFAULT_VOICE_FILE to an MP3 filename in that folder. Identity-specific
# prompts can be mapped separately with VOICE_FILES.
DEFAULT_VOICE_FILE = "unknown.mp3"
VOICE_FILES = {"unknown": "unknown.mp3"}
AUDIO_REPLAY_COOLDOWN_MS = 5000

# Recognition preprocessing. This sharpens frames without resizing or stretching
# them before they are passed to InsightFace.
SHARPENING_ENABLED = True
SHARPENING_AMOUNT = 0.35

# The phone viewer is enabled by default. Install Tailscale on this PC and your
# phone, sign into the same tailnet, then open http://<PC-Tailscale-IP>:8080/.
# Set this to False if you need to disable it temporarily.
REMOTE_VIEWER_ENABLED = True

# Show the still-capture button in the local/phone viewer. Set False to hide it
# and disable the /capture.jpg endpoint.
CAPTURE_STILL_ENABLED = True
