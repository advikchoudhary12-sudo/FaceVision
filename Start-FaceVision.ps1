param(
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"

$appDirectory = Join-Path $PSScriptRoot "FaceVision"
if (-not (Test-Path -LiteralPath $appDirectory)) {
    throw "FaceVision application folder was not found: $appDirectory"
}

Push-Location $appDirectory
try {
    & $PythonCommand launcher.py
}
finally {
    Pop-Location
}
