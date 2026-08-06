# File guide

This guide describes the tracked project files. Generated Python cache folders, local credentials, and enrolled face images are deliberately excluded.

## Desktop recognition path

```text
launcher.py -> main.py -> Camera -> Recognition -> Overlay -> display/Blynk
```

`launcher.py` converts a preset or custom input into a source accepted by OpenCV. `main.py` manages the application lifecycle and runs expensive recognition every configured number of frames. `Camera` captures the most recent frame on a background thread. `Recognition` uses InsightFace embeddings to compare detected faces with locally enrolled images. `Overlay` draws the result, while the optional Blynk client reports status without blocking video.

## Firmware path

```text
wifi_secrets.h -> ESP_32.ino -> app_httpd.cpp -> /stream -> FaceVision
```

The ESP32 firmware reads credentials only from a local ignored header, connects to Wi-Fi, starts its camera server, and exposes an MJPEG feed at `/stream` on port 81.
