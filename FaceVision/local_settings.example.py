# Copy this file to local_settings.py. It is ignored by Git.

# AI Thinker ESP32-CAM stream endpoint. The camera firmware serves MJPEG on
# port 81 at /stream. Use the local address printed by the ESP32 Serial Monitor.
ESP32_STREAM_URL = "http://<ESP32-IP>:81/stream"

# Blynk.Console -> Devices -> Device info -> Auth Token.
BLYNK_AUTH_TOKEN = "paste-your-blynk-device-token-here"

# The phone viewer is enabled by default. Install Tailscale on this PC and your
# phone, sign into the same tailnet, then open http://<PC-Tailscale-IP>:8080/.
# Set this to False if you need to disable it temporarily.
REMOTE_VIEWER_ENABLED = True

# Show the still-capture button in the local/phone viewer. Set False to hide it
# and disable the /capture.jpg endpoint.
CAPTURE_STILL_ENABLED = True
