# FaceVision installation and GPU troubleshooting

Run this after installing whenever FaceVision starts slowly, errors, or seems to
use CPU instead of the NVIDIA GPU:

```powershell
python verify_install.py
```

## CUDA, cuDNN, or cuBLAS DLL errors

Errors mentioning `cudart`, `cublas`, `cudnn`, `cudnn64`, or `LoadLibrary` mean
that ONNX Runtime cannot load a required NVIDIA runtime DLL. Run
`FaceVision\setup_gpu.ps1` again while connected to the internet. It installs
the compatible CUDA/cuDNN runtime packages itself, so installing the complete
CUDA Toolkit is usually unnecessary.

Do not mix manually installed cuDNN 8 DLLs with cuDNN 9 DLLs. Current
FaceVision GPU setup uses cuDNN 9. Restart Windows after changing drivers or
runtime DLLs.

## NVIDIA driver too old

Errors such as `CUDA failure 35`, `insufficient driver`, or `driver version is
insufficient` mean the driver is older than the CUDA runtime it needs. Update
the NVIDIA driver from NVIDIA, restart Windows, then rerun `setup_gpu.ps1`.

The CUDA version shown by `nvidia-smi` is the newest CUDA family supported by
the driver; it is not proof that a separately installed CUDA Toolkit is needed.

## CUDAExecutionProvider is unavailable

This means ONNX Runtime did not start its NVIDIA provider. Run
`FaceVision\setup_gpu.ps1`. If the machine has no NVIDIA GPU, or GPU setup is
not practical, run it with `-ForceCpu`; FaceVision still works, only slower.

## Python/package/download errors

Use 64-bit Python 3.12. If downloads fail, check internet access, captive-portal
sign-in, Windows date/time, antivirus, firewall, and school/work proxy settings.
Run the installer again without `-SkipDependencies`.

## Installation updates

The installer backs up the existing installation and preserves
`FaceVision\local_settings.py` and enrolled images under
`FaceVision\data\known_faces`. Never share those files when asking for help.
