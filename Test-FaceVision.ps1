param(
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSCommandPath
$startScript = Join-Path $projectRoot "Start-FaceVision.ps1"
$gpuScript = Join-Path $projectRoot "FaceVision\setup_gpu.ps1"
$projectCheck = Join-Path $projectRoot "check_project.py"

if (Test-Path -LiteralPath $PythonCommand -PathType Leaf) {
    $pythonExecutable = (Resolve-Path -LiteralPath $PythonCommand).Path
}
else {
    $pythonCommandInfo = Get-Command $PythonCommand -ErrorAction SilentlyContinue
    if ($null -eq $pythonCommandInfo) {
        throw "Python was not found: $PythonCommand. Pass -PythonCommand with the full python.exe path."
    }
    $pythonExecutable = $pythonCommandInfo.Source
}

& $startScript -PythonCommand $pythonExecutable -Check
& $gpuScript -PythonCommand $pythonExecutable -Check
& $pythonExecutable $projectCheck
if ($LASTEXITCODE -ne 0) {
    throw "FaceVision project smoke test failed. Read the ERROR lines above."
}
Write-Host "FaceVision full project smoke test passed." -ForegroundColor Green
