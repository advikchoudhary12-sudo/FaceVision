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
`%LOCALAPPDATA%\FaceVision`, creates private local settings, installs Python
3.12 with `winget` if necessary, detects CPU/NVIDIA GPU hardware, installs the
appropriate ONNX Runtime and CUDA/cuDNN runtime DLLs, then starts the launcher.

```powershell
.\Install-FaceVision.ps1
```

Later, run `%LOCALAPPDATA%\FaceVision\Start-FaceVision.ps1` to launch it from
any folder. The installer preserves an existing `local_settings.py` file, so
your ESP32 address and Blynk token are not replaced by updates.

If installation or GPU acceleration fails, run `%LOCALAPPDATA%\FaceVision\verify_install.py`
with Python. It explains common NVIDIA driver, CUDA, cuDNN, cuBLAS, package,
and network errors. See [the troubleshooting guide](docs/TROUBLESHOOTING.md).

The launcher and GPU scripts can be run from any PowerShell folder. Add `-Check`
to validate them without opening a camera window or changing packages.

## Install on Ubuntu

Run the Ubuntu installer from a checkout:

```bash
./Install-FaceVision.sh
```

It installs Python 3.12 and the required Ubuntu packages, downloads the project
when run outside a checkout, creates a private Python virtual environment, and
installs the CPU ONNX Runtime. If the configured Ubuntu repositories do not
provide Python 3.12, it enables the deadsnakes PPA. It preserves existing
`local_settings.py` and enrolled face images during updates. The installer opens
the launcher when a desktop display is available; use `--no-launch` to install
without opening it. Start the app later with `~/FaceVision/Run-FaceVision.sh`.

## Blind-stick recognition and audio

The separate ESP32-S3 blind-stick controller is in
[`FaceVision/BlindStick/ESP32/BlindStick.ino`](FaceVision/BlindStick/ESP32/BlindStick.ino).
Configure its sensor pins and Wi-Fi, and set the existing FaceVision
`BLYNK_AUTH_TOKEN` in the stick's secrets header. Add
V10 to the Blynk device/template used by that token. FaceVision reuses its
existing token to listen for V10 value transitions (default pin `V10`); no
additional Blynk token setting is needed. The stick resets the pin after the
obstacle has cleared and the cooldown has expired.

Pair the Bluetooth headphones with the PC through its operating system and set
them as the default audio output. Put prompts named exactly after the
recognition labels (for example, `FaceVision/BlindStick/Voice/Ayan.mp3`) in
`FaceVision/BlindStick/Voice/`. The optional `unknown.mp3` prompt is used for
unrecognized faces, and no audio plays when a frame contains no faces.
`AUDIO_REPLAY_COOLDOWN_MS` in `local_settings.py` controls how long the same
identity is suppressed after playback starts; it defaults to 5000 ms.

## Full project smoke test

From any PowerShell folder, run:

```powershell
& "C:\path\to\FaceVision\Test-FaceVision.ps1"
```

It validates project files, PowerShell entry points, Python imports, CUDA/cuDNN/
cuBLAS runtime availability, and the final-frame phone-stream server. It does
not open a camera, contact Blynk, expose credentials, or alter packages. ESP32
compilation needs Arduino CLI and the private `wifi_secrets.h` file, so it is
reported separately rather than treated as a desktop-project failure.

## Privacy and security

Never commit `FaceVision/local_settings.py` or `ESP_32/ESP_32/wifi_secrets.h`. The included example files are safe templates. Enrolled face images are ignored because they are personal biometric data.

## License

See [LICENSE](LICENSE).
