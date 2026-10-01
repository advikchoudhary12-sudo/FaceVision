param(
    [string]$PythonCommand
)

$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$launcherPath = Join-Path $PSScriptRoot "FaceVision\launcher.py"

if (-not $PythonCommand) {
    $localEnvironmentPython = Join-Path $PSScriptRoot "Faceinstaller test\Scripts\python.exe"
    if (Test-Path -LiteralPath $localEnvironmentPython -PathType Leaf) {
        $PythonCommand = $localEnvironmentPython
    }
    else {
        $pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
        if ($null -eq $pythonLauncher) {
            throw "Python 3.12 was not found. Pass -PythonCommand with the full python.exe path."
        }

        $PythonCommand = (& $pythonLauncher.Source -3.12 -c "import sys; print(sys.executable)" | Select-Object -Last 1).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $PythonCommand) {
            throw "Python 3.12 was not found. Pass -PythonCommand with the full python.exe path."
        }
    }
}

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

Write-Host "Using Python: $pythonExecutable"
Write-Host "Starting FaceVision: $launcherPath"
& $pythonExecutable $launcherPath
if ($LASTEXITCODE -ne 0) {
    throw "FaceVision failed to start with Python: $pythonExecutable"
}
