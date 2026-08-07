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
    if ($null -ne $winget) {
        Write-Host "Installing Python 3.12 via winget..."
        & $winget.Source install --exact --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) {
            $pythonPath = Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA "Programs\Python") -Filter python.exe -Recurse -ErrorAction SilentlyContinue |
                Sort-Object FullName -Descending |
                Select-Object -First 1 -ExpandProperty FullName
            if ($pythonPath) { return $pythonPath }
            Write-Host "Python installed but not found in expected location; trying to find in PATH..."
            $python = Get-Command python -ErrorAction SilentlyContinue
            if ($null -ne $python) { return $python.Source }
        }
        Write-Host "winget install failed or did not produce a usable python; falling back to embeddable distribution..."
    }
    else {
        Write-Host "winget not available; attempting embeddable Python fallback..."
    }

    # Attempt to download and use the embeddable Python distribution (works without admin rights)
    $is64 = [Environment]::Is64BitOperatingSystem
    $version = "3.12.0"
    if ($is64) { $embedFileName = "python-$version-embed-amd64.zip" } else { $embedFileName = "python-$version-embed-win32.zip" }
    $embedUrl = "https://www.python.org/ftp/python/$version/$embedFileName"
    $embedArchive = Join-Path $temporaryDirectory $embedFileName

    Write-Host "Downloading embeddable Python from $embedUrl..."
    try {
        Invoke-WebRequest -Uri $embedUrl -OutFile $embedArchive -UseBasicParsing
    } catch {
        throw "Failed to download embeddable Python from $embedUrl. Install Python 3.12 manually and rerun the installer."
    }

    $embedExtract = Join-Path $temporaryDirectory "python-embed"
    Expand-Archive -LiteralPath $embedArchive -DestinationPath $embedExtract -Force

    $pythonPath = Join-Path $embedExtract "python.exe"
    if (-not (Test-Path $pythonPath)) {
        $pythonFound = Get-ChildItem -Path $embedExtract -Filter python.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
        if ($pythonFound) { $pythonPath = $pythonFound }
    }
    if (-not (Test-Path $pythonPath)) { throw "Failed to extract embeddable Python. Install Python 3.12 manually and rerun the installer." }

    # Ensure pip is available for setup scripts that expect pip to exist
    & $pythonPath -m pip --version *> $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Bootstrapping pip for embeddable Python..."
        & $pythonPath -m ensurepip --default-pip *> $null 2>&1
        if ($LASTEXITCODE -ne 0) {
            $getpipUrl = "https://bootstrap.pypa.io/get-pip.py"
            $getpipPath = Join-Path $temporaryDirectory "get-pip.py"
            try {
                Invoke-WebRequest -Uri $getpipUrl -OutFile $getpipPath -UseBasicParsing
                & $pythonPath $getpipPath
            } catch {
                throw "Failed to install pip for embeddable Python. Install Python 3.12 manually and rerun the installer."
            }
        }
        & $pythonPath -m pip install --upgrade pip
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
