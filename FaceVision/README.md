# FaceVision desktop application

This folder contains the Python application that captures a video source, detects and recognizes faces, and renders the results.

| File or folder | Responsibility |
| --- | --- |
| `launcher.py` | CustomTkinter camera-source picker and normal desktop entry point. |
| `main.py` | Application loop: source selection, recognition scheduling, display, alerts, cleanup. |
| `config.py` | Safe tracked defaults for model, UI, camera presets, and Blynk pins. |
| `local_settings.example.py` | Template for private ESP32 URL and Blynk token settings. |
| `local_settings.py` | Local private settings; ignored by Git. |
| `setup_gpu.ps1` | Installs the GPU ONNX Runtime stack without the CPU/GPU package conflict. |
| `requirements.txt` | Python dependency list. |
| `core/camera.py` | Threaded OpenCV capture with safe failure and shutdown handling. |
| `core/recognition.py` | InsightFace model setup, CUDA verification, dataset loading, and matching. |
| `core/overlay.py` | Bounding boxes, names, scores, and FPS rendering. |
| `core/fps.py` | FPS measurement helper. |
| `core/blynk.py` | Non-blocking Blynk device HTTPS client. |
| `core/worker.py` | Reserved placeholder for a future background recognition worker. |
| `data/known_faces/` | Local enrolled-face images; ignored by Git. |

## Blynk setup

Set `BLYNK_AUTH_TOKEN` in `local_settings.py`, then create:

- `V0`: Integer status/alert datastream.
- `V1`: Numeric FPS datastream.
- `unknown_detected`: Event code for notifications.

The app remains fully functional when no Blynk token is configured.
