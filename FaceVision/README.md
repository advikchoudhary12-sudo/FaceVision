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
| `core/remote_viewer.py` | Built-in HTTP/MJPEG viewer for the final annotated frame. |
| `core/worker.py` | Reserved placeholder for a future background recognition worker. |
| `data/known_faces/` | Local enrolled-face images; ignored by Git. |

## Blynk setup

Set `BLYNK_AUTH_TOKEN` in `local_settings.py`, then create:

- `V0`: Integer status/alert datastream.
- `V1`: Numeric FPS datastream.
- `unknown_detected`: Event code for notifications.

The app remains fully functional when no Blynk token is configured.

## Script checks and running from any folder

The PowerShell launcher and GPU setup script locate FaceVision relative to their
own files, so they can be run from any PowerShell folder. These checks do not
open the camera window or change installed packages:

```powershell
& "C:\path\to\FaceVision\Start-FaceVision.ps1" -Check
& "C:\path\to\FaceVision\FaceVision\setup_gpu.ps1" -Check
```

## Phone viewer from anywhere (free)

FaceVision includes a lightweight viewer for the **final annotated OpenCV
frames**. It does not expose the raw ESP32 stream and does not run recognition
twice. The local FaceVision window remains available as usual.

1. Install [Tailscale](https://tailscale.com/download) on the FaceVision PC and
   your phone, then sign in to the same account/tailnet.
2. Start FaceVision normally. It prints `Remote viewer ready ...` when the
   viewer is available.
3. On the PC, run `tailscale ip -4` and note the displayed IP address.
4. On the phone (with Tailscale connected), open
   `http://<PC-Tailscale-IP>:8080/` in a browser.

If Tailscale is unavailable during setup, the same URL with the PC's local
network IP works as a same-Wi-Fi fallback. The viewer is optional: if port 8080
is occupied or it cannot start, FaceVision keeps running locally and prints a
warning. Change the port or turn the feature off in `local_settings.py` if
needed.
