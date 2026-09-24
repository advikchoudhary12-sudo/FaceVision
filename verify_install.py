"""FaceVision dependency and NVIDIA GPU diagnostic.

This never exposes private settings, tokens, camera URLs, or face images.
"""

import importlib
import os
import platform
import shutil
import subprocess
import sys


def heading(text):
    print(f"\n{'=' * 12} {text} {'=' * 12}")


def explain(error):
    text = str(error).lower()
    if any(value in text for value in ("cudnn", "cudnn64", "cudnn_ops")):
        return "cuDNN is missing or incompatible. Re-run setup_gpu.ps1 with internet access; do not mix cuDNN 8 and cuDNN 9 DLLs."
    if any(value in text for value in ("cublas", "cudart", "cuda.dll", "loadlibrary")):
        return "A CUDA DLL could not load. Update the NVIDIA driver, restart Windows, then rerun setup_gpu.ps1."
    if any(value in text for value in ("insufficient driver", "cuda failure 35", "driver version is insufficient")):
        return "The NVIDIA driver is too old. Update it from nvidia.com, restart Windows, then rerun setup_gpu.ps1."
    if "cudaexecutionprovider" in text:
        return "ONNX Runtime is not exposing CUDA. Re-run setup_gpu.ps1, or use CPU mode if this PC has no supported NVIDIA GPU."
    if "no module named" in text:
        return "A Python package is missing. Run Install-FaceVision.ps1 again without -SkipDependencies."
    return "See the error above. If it persists, reinstall dependencies with setup_gpu.ps1."


heading("SYSTEM")
print("Python:", sys.version.replace("\n", " "))
print("Python executable:", sys.executable)
print("Windows:", platform.platform())
print("Architecture:", platform.architecture()[0])

nvidia_smi = shutil.which("nvidia-smi")
if nvidia_smi:
    try:
        result = subprocess.run(
            [nvidia_smi, "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15, check=True,
        )
        print("NVIDIA GPU / driver:", result.stdout.strip())
    except Exception as error:
        print("NVIDIA driver check ERROR:", error)
        print("HELP:", explain(error))
else:
    print("NVIDIA GPU / driver: nvidia-smi was not found (CPU mode is expected).")

heading("PYTHON PACKAGES")
failed = False
for module_name in ("insightface", "onnxruntime", "cv2", "customtkinter"):
    try:
        module = importlib.import_module(module_name)
        print(f"{module_name}: OK ({getattr(module, '__version__', 'version unavailable')})")
    except Exception as error:
        failed = True
        print(f"{module_name}: ERROR: {error}")
        print("HELP:", explain(error))

heading("ONNX RUNTIME / CUDA")
try:
    import onnxruntime as ort

    print("ONNX Runtime version:", ort.__version__)
    print("Available providers:", ", ".join(ort.get_available_providers()))
    if "CUDAExecutionProvider" in ort.get_available_providers():
        try:
            ort.preload_dlls(directory="")
            print("CUDA, cuDNN, cuBLAS, and MSVC runtime preload: OK")
        except Exception as error:
            failed = True
            print("CUDA runtime preload ERROR:", error)
            print("HELP:", explain(error))
    elif nvidia_smi:
        print("GPU NOTE: NVIDIA driver exists, but CUDAExecutionProvider is unavailable.")
        print("HELP: Run FaceVision\\setup_gpu.ps1. If the driver is old, update it first.")
    else:
        print("CPU NOTE: No NVIDIA driver was detected, so CPU mode is normal.")
except Exception as error:
    failed = True
    print("ONNX Runtime ERROR:", error)
    print("HELP:", explain(error))

heading("RESULT")
if failed:
    print("Some checks failed. Fix the HELP item above, then rerun this file.")
    sys.exit(1)
print("Core installation checks passed.")
