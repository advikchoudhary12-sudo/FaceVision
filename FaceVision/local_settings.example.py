# Copy this file to local_settings.py. It is ignored by Git.

# AI Thinker ESP32-CAM stream endpoint. The camera firmware serves MJPEG on
# port 81 at /stream. Use the local address printed by the ESP32 Serial Monitor.
ESP32_STREAM_URL = "http://<ESP32-IP>:81/stream"

# Blynk.Console -> Devices -> Device info -> Auth Token.
BLYNK_AUTH_TOKEN = "paste-your-blynk-device-token-here"
