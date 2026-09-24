# Copilot instructions for FaceVision

## Repository overview

This repository contains two related but separate systems:

- `FaceVision/` is the Windows desktop recognition app. It is a Python application built around OpenCV, InsightFace, and CustomTkinter.
- `ESP_32/` contains the AI Thinker ESP32-CAM firmware that exposes an MJPEG stream over Wi-Fi and is fed into the desktop app as a camera source.
- The root-level scripts (`Start-FaceVision.ps1`, `Test-FaceVision.ps1`, `check_project.py`, `verify_install.py`) validate the setup and smoke-test the project without opening the camera or requiring private credentials.

The big-picture runtime path is:

- `launcher.py` -> `main.py`
- `main.py` creates a `Camera`, `Recognition`, `Overlay`, and optional `BlynkClient`/`RemoteViewer`
- `Recognition` loads embeddings from `FaceVision/data/known_faces/` and compares live detected faces against them
- The app can use a laptop webcam, USB camera, ESP32-CAM stream, RTSP feed, or local video path

## Build, test, and validation commands

There is no dedicated `pytest` or lint configuration in this repo. The project relies on PowerShell and Python smoke checks.

From any PowerShell directory:

```powershell
& "C:\path\to\FaceVision\Start-FaceVision.ps1" -Check
```

This validates the launcher and GPU helper without opening the camera or changing packages.

Run the full non-destructive smoke test:

```powershell
& "C:\path\to\FaceVision\Test-FaceVision.ps1"
```

This checks the project files, imports, compileability, and the remote-viewer MJPEG endpoint. It does not exercise the camera, Blynk, or ESP32 compilation.

Run the Python project health check directly:

```powershell
python C:\path\to\FaceVision\check_project.py
```

For a quick local compile check on the desktop app only:

```powershell
python -m compileall FaceVision
```

To install or repair the Python/InsightFace stack on Windows:

```powershell
cd FaceVision
.\setup_gpu.ps1
```

This script installs the correct ONNX Runtime package for the detected NVIDIA driver; if no supported NVIDIA driver is present, it falls back to CPU mode.

## High-level architecture notes

- `FaceVision/config.py` is the central configuration file for camera dimensions, model settings, thresholds, Blynk pins, viewer settings, and the path to `data/known_faces/`.
- `FaceVision/local_settings.py` is intentionally local-only and Git-ignored. It provides private runtime values such as `ESP32_STREAM_URL` and `BLYNK_AUTH_TOKEN` without polluting the repo.
- `FaceVision/launcher.py` is a CustomTkinter UI that resolves a camera source from presets or raw index/URL input. It does not do inference itself; it selects the capture source and hands control back to `main.py`.
- `FaceVision/core/recognition.py` does the heavy lifting: it initializes InsightFace, loads known-face embeddings, and scores live faces against them using a threshold.
- `FaceVision/core/camera.py` is the threaded capture layer and owns safe failure handling for bad camera sources or stream errors.
- `FaceVision/core/overlay.py` draws boxes/names/FPS on frame output; `core/blynk.py` sends optional status updates without blocking the capture loop; `core/remote_viewer.py` exposes the final annotated frame over HTTP/MJPEG for remote viewing.
- `ESP_32/ESP_32/ESP_32.ino` and `ESP_32/ESP_32/app_httpd.cpp` are the hardware-side camera server. They expect a private `wifi_secrets.h` file that is not tracked in Git.

## Key conventions and repository-specific patterns

- Keep secrets local: never commit `FaceVision/local_settings.py`, `ESP_32/ESP_32/wifi_secrets.h`, or images under `FaceVision/data/known_faces/`.
- Prefer script-relative filesystem handling rather than assuming the current working directory. This repo intentionally resolves paths from the script location so commands work from any PowerShell folder.
- `config.py` is intentionally split from local secrets: tracked defaults live in the repo, while private values are resolved from `local_settings.py` or environment variables.
- The classifier is GPU-first but tolerant of CUDA failures. `CTX_ID` defaults to 0 for GPU and will fall back to CPU in `Recognition._prepare()` if CUDA cannot initialize.
- The app intentionally does not block on Blynk updates or remote-viewer startup. The main loop keeps video processing responsive while optional integrations run in the background.
- The project is Windows-first. PowerShell utilities and the installer scripts assume a Windows environment and call out Python 3.12 64-bit requirements.
- If you add or rearrange tracked files, update the smoke checks in `check_project.py` and the docs if the runtime path changes.

## Existing guidance to preserve

- Follow the repository’s privacy model: local credentials and biometric training data stay out of Git.
- Keep the desktop app and ESP32 firmware in sync with the documented camera flow and expected private files.
- Preserve the non-destructive validation style: when possible, prefer checks that do not require hardware, cloud credentials, or camera access.
