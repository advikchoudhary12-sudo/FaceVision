param(
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"

# InsightFace declares the CPU package as a dependency, while the GPU and CPU
# ONNX Runtime wheels install the same Python module. Install InsightFace first,
# then install the GPU wheel last so it owns that module.
& $PythonCommand -m pip install --upgrade insightface numpy opencv-python customtkinter
& $PythonCommand -m pip uninstall -y onnxruntime onnxruntime-gpu
& $PythonCommand -m pip install --timeout 1200 --retries 5 "onnxruntime-gpu[cuda,cudnn]==1.28.0"

& $PythonCommand -c "import onnxruntime as ort; ort.preload_dlls(); assert 'CUDAExecutionProvider' in ort.get_available_providers(); print('CUDAExecutionProvider is ready.')"
