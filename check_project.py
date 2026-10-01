"""Non-destructive FaceVision project smoke test.

It intentionally does not open a camera, download an InsightFace model, call
Blynk, or need any private credentials. It can run from any working folder.
"""

from __future__ import annotations

import compileall
import importlib
import json
import sys
import urllib.request
from pathlib import Path
from time import monotonic


ROOT = Path(__file__).resolve().parent
APP = ROOT / "FaceVision"
sys.path.insert(0, str(APP))
errors: list[str] = []
warnings: list[str] = []


def check(condition: bool, message: str) -> None:
    (print if condition else errors.append)(message if not condition else f"OK: {message}")


def main() -> int:
    print(f"FaceVision project root: {ROOT}")
    print(f"Working directory: {Path.cwd()}")

    for relative_path in (
        "Install-FaceVision.ps1",
        "Install-FaceVision.sh",
        "Start-FaceVision.ps1",
        "verify_install.py",
        "FaceVision/main.py",
        "FaceVision/launcher.py",
        "FaceVision/setup_gpu.ps1",
        "FaceVision/local_settings.example.py",
        "FaceVision/core/camera.py",
        "FaceVision/core/recognition.py",
        "FaceVision/core/overlay.py",
        "FaceVision/core/remote_viewer.py",
        "FaceVision/core/audio_narrator.py",
        "FaceVision/BlindStick/blindstick_bridge.py",
        "FaceVision/BlindStick/README.md",
        "ESP_32/ESP_32/ESP_32.ino",
        "FaceVision/BlindStick/ESP32/BlindStick.ino",
        "FaceVision/BlindStick/ESP32/blind_stick_secrets.example.h",
        "ESP_32/ESP_32/app_httpd.cpp",
        "ESP_32/ESP_32/wifi_secrets.example.h",
    ):
        check((ROOT / relative_path).is_file(), f"Required file exists: {relative_path}")

    check(compileall.compile_dir(APP, quiet=1), "All FaceVision Python files compile")

    for module_name in (
        "config",
        "launcher",
        "main",
        "core.camera",
        "core.recognition",
        "core.overlay",
        "core.fps",
        "core.blynk",
        "core.remote_viewer",
        "core.audio_narrator",
        "BlindStick.blindstick_bridge",
    ):
        try:
            importlib.import_module(module_name)
            print(f"OK: Import {module_name}")
        except Exception as error:
            errors.append(f"Import {module_name} failed: {error}")

    try:
        import config
        import cv2
        from core.remote_viewer import RemoteViewer
        from core.recognition import Recognition
        import numpy as np

        check(config.BASE_DIR == APP, "Configuration resolves the FaceVision folder from its own file")
        check(config.KNOWN_FACES_PATH.is_dir(), "Known-faces folder exists or was created")
        check(isinstance(config.REMOTE_VIEWER_PORT, int), "Remote viewer port is a number")
        sample = np.zeros((80, 120, 3), dtype=np.uint8)
        sharpened = Recognition._preprocess_for_recognition(sample)
        check(
            sharpened.shape == sample.shape and sharpened.dtype == sample.dtype,
            "Recognition preprocessing preserves frame dimensions and format",
        )

        viewer = RemoteViewer(host="127.0.0.1", port=0, max_fps=30)
        port = viewer.start()
        try:
            viewer.publish(np.zeros((80, 120, 3), dtype=np.uint8), monotonic())
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3) as response:
                health = json.loads(response.read())
            check(health == {"running": True, "has_frame": True}, "Remote viewer health endpoint")
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/stream", timeout=3) as response:
                preview = response.read(256)
            check(b"Content-Type: image/jpeg" in preview, "Remote viewer MJPEG frame delivery")
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/capture.jpg", timeout=3) as response:
                check(response.headers["Content-Type"] == "image/jpeg", "Remote viewer still capture")
        finally:
            viewer.stop()
    except Exception as error:
        errors.append(f"Remote viewer smoke test failed: {error}")

    if not (ROOT / "ESP_32" / "ESP_32" / "wifi_secrets.h").is_file():
        warnings.append("ESP32 firmware was not compiled: private wifi_secrets.h is absent (normal in a clean clone).")
    if not (ROOT / "FaceVision" / "local_settings.py").is_file():
        warnings.append("FaceVision has no local_settings.py yet; add the ESP32 stream URL before using that preset.")

    print("\nRESULT")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Project smoke test passed. Hardware camera, Blynk cloud, and ESP32 compilation were intentionally not exercised.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
