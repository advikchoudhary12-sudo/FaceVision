param(
    [string]$InstallPath = (Join-Path $env:LOCALAPPDATA "FaceVision"),
    [switch]$SkipDependencies,
    [switch]$NoLaunch
)

$ErrorActionPreference = "Stop"
$repoArchiveUrl = "https://github.com/advikchoudhary12-sudo/FaceVision/archive/refs/heads/main.zip"
$temporaryDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("FaceVision-" + [guid]::NewGuid())

function Get-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        & $python.Source --version *> $null
        if ($LASTEXITCODE -eq 0) {
            return $python.Source
        }
    }

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($null -eq $winget) {
        throw "Python was not found and winget is unavailable. Install Python 3.12 or newer, add it to PATH, then run this installer again."
    }

    Write-Host "Installing Python 3.12..."
    & $winget.Source install --exact --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "Python installation failed. Install Python 3.12 manually, add it to PATH, then run this installer again."
    }

    $pythonPath = Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA "Programs\Python") -Filter python.exe -Recurse -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        Select-Object -First 1 -ExpandProperty FullName
    if (-not $pythonPath) {
        throw "Python was installed but could not be located. Restart PowerShell and run this installer again."
    }
    return $pythonPath
}

try {
    $pythonCommand = Get-PythonCommand

    New-Item -ItemType Directory -Path $temporaryDirectory -Force | Out-Null
    $archivePath = Join-Path $temporaryDirectory "FaceVision.zip"
    $extractPath = Join-Path $temporaryDirectory "extracted"

    Write-Host "Downloading FaceVision..."
    Invoke-WebRequest -Uri $repoArchiveUrl -OutFile $archivePath
    Expand-Archive -LiteralPath $archivePath -DestinationPath $extractPath -Force

    $sourceDirectory = Get-ChildItem -LiteralPath $extractPath -Directory | Select-Object -First 1
    if ($null -eq $sourceDirectory) {
        throw "The downloaded archive did not contain a project directory."
    }

    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Copy-Item -Path (Join-Path $sourceDirectory.FullName "*") -Destination $InstallPath -Recurse -Force

    $settingsPath = Join-Path $InstallPath "FaceVision\local_settings.py"
    $settingsExamplePath = Join-Path $InstallPath "FaceVision\local_settings.example.py"
    if (-not (Test-Path -LiteralPath $settingsPath)) {
        Copy-Item -LiteralPath $settingsExamplePath -Destination $settingsPath
    }

    if (-not $SkipDependencies) {
        Write-Host "Installing FaceVision dependencies..."
        & (Join-Path $InstallPath "FaceVision\setup_gpu.ps1") -PythonCommand $pythonCommand
    }

    Write-Host "FaceVision installed at: $InstallPath"
    Write-Host "Set Wi-Fi/Blynk values in: $settingsPath"

    if (-not $NoLaunch) {
        & (Join-Path $InstallPath "Start-FaceVision.ps1") -PythonCommand $pythonCommand
    }
}
finally {
    $tempRoot = [System.IO.Path]::GetTempPath()
    if ($temporaryDirectory.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $temporaryDirectory)) {
        Remove-Item -LiteralPath $temporaryDirectory -Recurse -Force
    }
}
