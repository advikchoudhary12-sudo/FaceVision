param(
    [string]$PythonCommand = "python",
    [switch]$ForceCpu,
    [switch]$Check
)

$ErrorActionPreference = "Stop"
$scriptDirectory = Split-Path -Parent $PSCommandPath
$diagnosticPath = Join-Path (Split-Path -Parent $scriptDirectory) "verify_install.py"

if (Test-Path -LiteralPath $PythonCommand -PathType Leaf) {
    $pythonExecutable = (Resolve-Path -LiteralPath $PythonCommand).Path
}
else {
    $pythonCommandInfo = Get-Command $PythonCommand -ErrorAction SilentlyContinue
    if ($null -eq $pythonCommandInfo) {
        throw "Python was not found: $PythonCommand. Install 64-bit Python 3.12 or pass -PythonCommand with the full python.exe path."
    }
    $pythonExecutable = $pythonCommandInfo.Source
}

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & $pythonExecutable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $pythonExecutable $($Arguments -join ' ')"
    }
}

function Write-GpuHelp {
    param([string]$Message)
    $lower = $Message.ToLowerInvariant()
    Write-Host ""
    Write-Host "========== GPU INSTALL HELP ==========" -ForegroundColor Yellow
    if ($lower -match 'cudnn|cudnn64') {
        Write-Host "cuDNN DLLs could not be loaded. Re-run this script with internet access; it installs the matching CUDA/cuDNN runtime packages automatically." -ForegroundColor Yellow
    } elseif ($lower -match 'cublas|cudart|cuda.*dll') {
        Write-Host "CUDA runtime DLLs could not be loaded. Update the NVIDIA driver and restart Windows. A full CUDA Toolkit is not normally required." -ForegroundColor Yellow
    } elseif ($lower -match 'cuda.*driver|driver.*cuda|insufficient driver') {
        Write-Host "Your NVIDIA driver is too old for this CUDA runtime. Update it from nvidia.com, restart Windows, and rerun this script." -ForegroundColor Yellow
    } elseif ($lower -match 'no matching distribution|requires-python') {
        Write-Host "Use 64-bit Python 3.12. The required package is unavailable for this Python/Windows combination." -ForegroundColor Yellow
    } else {
        Write-Host "FaceVision will fall back to CPU if GPU setup cannot complete. Run verify_install.py for a detailed diagnostic." -ForegroundColor Yellow
    }
}

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name
$gpuNames = @(Get-CimInstance Win32_VideoController | ForEach-Object Name)
Write-Host "CPU: $cpu"
Write-Host "GPU: $($gpuNames -join '; ')"
Invoke-Python -Arguments @('-c', "import platform, sys; print(f'Python: {sys.version.split()[0]} ({platform.architecture()[0]})'); assert sys.version_info[:2] == (3, 12), 'FaceVision requires Python 3.12'; assert platform.architecture()[0] == '64bit', 'FaceVision requires 64-bit Python'")

# A working NVIDIA driver reports the highest CUDA version it supports. The
# selected ONNX Runtime wheel then downloads matching CUDA/cuDNN DLLs through
# pip; a separate CUDA Toolkit installation is not needed.
$cudaVersion = $null
$driverVersion = $null
$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if (-not $ForceCpu -and $null -ne $nvidiaSmi) {
    $smiOutput = & $nvidiaSmi.Source 2>$null | Out-String
    if ($LASTEXITCODE -eq 0 -and $smiOutput -match 'CUDA Version\s*:\s*(\d+)\.(\d+)') {
        $cudaVersion = [version]"$($Matches[1]).$($Matches[2])"
    }
    $driverOutput = & $nvidiaSmi.Source --query-gpu=driver_version --format=csv,noheader 2>$null | Select-Object -First 1
    if ($LASTEXITCODE -eq 0 -and $driverOutput) { $driverVersion = $driverOutput.Trim() }
}

if ($driverVersion) { Write-Host "NVIDIA driver: $driverVersion" }

if ($Check) {
    if (-not (Test-Path -LiteralPath $diagnosticPath)) {
        throw "FaceVision diagnostic was not found: $diagnosticPath"
    }
    Write-Host "Running dependency and GPU diagnostic (no packages will be changed)..."
    Invoke-Python -Arguments @($diagnosticPath)
    Write-Host "GPU setup check passed."
}

else {
try {
    Invoke-Python -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip', 'insightface', 'numpy', 'opencv-python', 'customtkinter')
    Invoke-Python -Arguments @('-m', 'pip', 'uninstall', '-y', 'onnxruntime', 'onnxruntime-gpu')

    if (-not $ForceCpu -and $null -ne $cudaVersion -and $cudaVersion.Major -ge 13) {
        Write-Host "NVIDIA driver supports CUDA $cudaVersion. Installing CUDA 13 / cuDNN 9 ONNX Runtime."
        Invoke-Python -Arguments @('-m', 'pip', 'install', '--timeout', '1200', '--retries', '5', 'onnxruntime-gpu[cuda,cudnn]>=1.28')
        Invoke-Python -Arguments @('-c', "import onnxruntime as ort; ort.preload_dlls(directory=''); print('ONNX Runtime providers:', ort.get_available_providers()); ort.print_debug_info()")
    }
    elseif (-not $ForceCpu -and $null -ne $cudaVersion -and $cudaVersion.Major -eq 12) {
        Write-Host "NVIDIA driver supports CUDA $cudaVersion. Installing CUDA 12 / cuDNN 9 ONNX Runtime."
        Invoke-Python -Arguments @('-m', 'pip', 'install', '--timeout', '1200', '--retries', '5', 'onnxruntime-gpu[cuda,cudnn]==1.26.2')
        Invoke-Python -Arguments @('-c', "import onnxruntime as ort; ort.preload_dlls(directory=''); print('ONNX Runtime providers:', ort.get_available_providers()); ort.print_debug_info()")
    }
    else {
        if ($ForceCpu) { Write-Host "CPU mode requested. Installing CPU ONNX Runtime." }
        else { Write-Host "No supported NVIDIA CUDA driver detected. Installing CPU ONNX Runtime." }
        Invoke-Python -Arguments @('-m', 'pip', 'install', '--upgrade', 'onnxruntime')
    }
}
catch {
    Write-GpuHelp $_.Exception.Message
    throw
}
}
