param(
    [string]$PythonCommand = "python",
    [switch]$ForceCpu
)

$ErrorActionPreference = "Stop"

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & $PythonCommand @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $PythonCommand $($Arguments -join ' ')"
    }
}

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name
$gpuNames = @(Get-CimInstance Win32_VideoController | ForEach-Object Name)
Write-Host "CPU: $cpu"
Write-Host "GPU: $($gpuNames -join '; ')"

# A working NVIDIA driver reports the highest CUDA version it supports. The
# selected ONNX Runtime wheel then downloads matching CUDA/cuDNN DLLs through
# pip; a separate CUDA Toolkit installation is not needed.
$cudaVersion = $null
$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if (-not $ForceCpu -and $null -ne $nvidiaSmi) {
    $smiOutput = & $nvidiaSmi.Source 2>$null | Out-String
    if ($LASTEXITCODE -eq 0 -and $smiOutput -match 'CUDA Version\s*:\s*(\d+)\.(\d+)') {
        $cudaVersion = [version]"$($Matches[1]).$($Matches[2])"
    }
}

Invoke-Python -Arguments @('-m', 'pip', 'install', '--upgrade', 'insightface', 'numpy', 'opencv-python', 'customtkinter')
Invoke-Python -Arguments @('-m', 'pip', 'uninstall', '-y', 'onnxruntime', 'onnxruntime-gpu')

if ($null -ne $cudaVersion -and $cudaVersion.Major -ge 13) {
    Write-Host "NVIDIA CUDA $cudaVersion detected. Installing CUDA 13 ONNX Runtime."
    Invoke-Python -Arguments @('-m', 'pip', 'install', '--timeout', '1200', '--retries', '5', 'onnxruntime-gpu[cuda,cudnn]>=1.27')
    Invoke-Python -Arguments @('-c', "import onnxruntime as ort; ort.preload_dlls(); print('ONNX Runtime providers:', ort.get_available_providers())")
}
elseif ($null -ne $cudaVersion -and $cudaVersion.Major -eq 12) {
    Write-Host "NVIDIA CUDA $cudaVersion detected. Installing CUDA 12 ONNX Runtime."
    Invoke-Python -Arguments @('-m', 'pip', 'install', '--timeout', '1200', '--retries', '5', 'onnxruntime-gpu[cuda,cudnn]==1.26.2')
    Invoke-Python -Arguments @('-c', "import onnxruntime as ort; ort.preload_dlls(); print('ONNX Runtime providers:', ort.get_available_providers())")
}
else {
    Write-Host "No supported NVIDIA CUDA driver detected. Installing CPU ONNX Runtime."
    Invoke-Python -Arguments @('-m', 'pip', 'install', '--upgrade', 'onnxruntime')
}
