# FaceVision

FaceVision is a local, real-time face-recognition system with GPU-first InsightFace inference, selectable webcam and stream inputs, an AI Thinker ESP32-CAM firmware project, and optional Blynk IoT alerts.

## What it does

- Recognizes enrolled faces from a local dataset.
- Runs inference on NVIDIA CUDA when available, with a CPU fallback.
- Selects a laptop webcam, USB camera, ESP32-CAM MJPEG stream, RTSP stream, local video file, or another custom camera source from the launcher.
- Sends optional Blynk status, FPS, and unknown-person notifications.
- Keeps Wi-Fi credentials, Blynk tokens, camera addresses, and face images out of Git by default.

## Repository layout

| Path | Purpose |
| --- | --- |
| [`FaceVision/`](FaceVision/README.md) | Desktop recognition application. |
| [`ESP_32/`](ESP_32/README.md) | AI Thinker ESP32-CAM firmware. |
| [`docs/FILE_GUIDE.md`](docs/FILE_GUIDE.md) | File-by-file responsibility guide. |
| [`.gitignore`](.gitignore) | Keeps private credentials and enrolled face images local. |

## Quick start

1. Install the desktop dependencies:

   ```powershell
   cd FaceVision
   .\setup_gpu.ps1
   ```

2. Copy `local_settings.example.py` to `local_settings.py`, then add your ESP32-CAM stream address and optional Blynk device token. This local file is intentionally ignored by Git.

3. Start the launcher:

   ```powershell
   python launcher.py
   ```

4. Select a preset or type a camera index, HTTP/RTSP stream URL, or video path.

## Install on another Windows computer

Download [Install-FaceVision.ps1](Install-FaceVision.ps1), then run it in
PowerShell. It downloads the public project archive, installs it at
`%LOCALAPPDATA%\FaceVision`, creates private local settings, installs the
dependencies, and starts the launcher. Python 3.12 or newer must be installed
and available as `python` first.

```powershell
.\Install-FaceVision.ps1
```

Later, run `%LOCALAPPDATA%\FaceVision\Start-FaceVision.ps1` to launch it from
any folder. The installer preserves an existing `local_settings.py` file, so
your ESP32 address and Blynk token are not replaced by updates.

## Privacy and security

Never commit `FaceVision/local_settings.py` or `ESP_32/ESP_32/wifi_secrets.h`. The included example files are safe templates. Enrolled face images are ignored because they are personal biometric data.

## License

See [LICENSE](LICENSE).
