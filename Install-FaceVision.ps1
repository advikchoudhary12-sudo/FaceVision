param(
    [string]$InstallPath = (Join-Path $env:LOCALAPPDATA "FaceVision"),
    [switch]$SkipDependencies,
    [switch]$ForceCpu,
    [switch]$NoLaunch
)

$ErrorActionPreference = "Stop"
$repoArchiveUrl = "https://github.com/advikchoudhary12-sudo/FaceVision/archive/refs/heads/main.zip"
$temporaryDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("FaceVision-" + [guid]::NewGuid())
$logFile = Join-Path $temporaryDirectory "install.log"
$installSucceeded = $false
# Ensure the temporary directory exists before attempting to log
New-Item -ItemType Directory -Path $temporaryDirectory -Force | Out-Null

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$ts`t$Message" | Out-File -FilePath $logFile -Append -Encoding UTF8
    Write-Host $Message
}

function Get-Python312 {
    # Return path to a usable Python 3.12 executable. Will attempt multiple fallbacks.
    $candidates = @('python','python3','py')
    foreach ($c in $candidates) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($null -ne $cmd) {
            try {
                $ver = & $cmd.Source -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null | Out-String
                if ($ver -match "(\d+)\.(\d+)\.(\d+)") {
                    $v = [version]"$($Matches[1]).$($Matches[2]).$($Matches[3])"
                    if ($v.Major -eq 3 -and $v.Minor -eq 12) { return $cmd.Source }
                }
            } catch { }
        }
    }

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($null -ne $winget) {
        Write-Log "Attempting winget install of Python 3.12"
        & $winget.Source install --exact --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Log "winget installed Python 3.12; locating python.exe"
            $pythonPath = Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA "Programs\Python") -Filter python.exe -Recurse -ErrorAction SilentlyContinue |
                Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
            if ($pythonPath) { return $pythonPath }
            $cmd = Get-Command python -ErrorAction SilentlyContinue
            if ($cmd) { return $cmd.Source }
        }
        Write-Log "winget install failed or did not produce usable python"
    } else { Write-Log "winget not found" }

    # Embeddable fallback (no admin rights)
    Write-Log "Falling back to embeddable Python 3.12"
    $is64 = [Environment]::Is64BitOperatingSystem
    $version = "3.12.0"
    if ($is64) { $embedFileName = "python-$version-embed-amd64.zip" } else { $embedFileName = "python-$version-embed-win32.zip" }
    $embedUrl = "https://www.python.org/ftp/python/$version/$embedFileName"
    $embedArchive = Join-Path $temporaryDirectory $embedFileName
    New-Item -ItemType Directory -Path $temporaryDirectory -Force | Out-Null
    try {
        Invoke-WebRequest -Uri $embedUrl -OutFile $embedArchive -UseBasicParsing -ErrorAction Stop
        $embedExtract = Join-Path $temporaryDirectory "python-embed"
        Expand-Archive -LiteralPath $embedArchive -DestinationPath $embedExtract -Force
        $pythonPath = Get-ChildItem -Path $embedExtract -Filter python.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
        if ($pythonPath) {
            # Ensure pip exists
            & $pythonPath -m pip --version *> $null 2>&1
            if ($LASTEXITCODE -ne 0) {
                & $pythonPath -m ensurepip --default-pip *> $null 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $getpipUrl = "https://bootstrap.pypa.io/get-pip.py"
                    $getpipPath = Join-Path $temporaryDirectory "get-pip.py"
                    Invoke-WebRequest -Uri $getpipUrl -OutFile $getpipPath -UseBasicParsing -ErrorAction Stop
                    & $pythonPath $getpipPath
                }
            }
            & $pythonPath -m pip install --upgrade pip | Out-Null
            return $pythonPath
        }
    } catch {
        Write-Log "Embeddable Python fallback failed: $($_.Exception.Message)"
    }

    throw "Unable to obtain Python 3.12. Install Python 3.12 (64-bit) from python.org, reopen PowerShell, then rerun this installer."
}

function Write-ProblemHelp {
    param([string]$Message)

    $lower = $Message.ToLowerInvariant()
    Write-Log ""
    Write-Log "========== WHAT TO DO NEXT =========="
    if ($lower -match 'cudnn|cudnn64|cudnn_ops') {
        Write-Log "cuDNN could not be loaded. Re-run the installer with internet access so it can install ONNX Runtime's CUDA/cuDNN runtime packages. Do not mix cuDNN 8 and cuDNN 9 DLLs in PATH."
    }
    elseif ($lower -match 'cublas|cudart|cuda.*dll|loadlibrary') {
        Write-Log "A CUDA runtime DLL could not be loaded. Update the NVIDIA driver, then rerun the installer. A separate CUDA Toolkit is normally not required because the installer installs the matching runtime DLLs."
    }
    elseif ($lower -match 'cuda.*driver|driver.*cuda|cuda failure 35|insufficient driver') {
        Write-Log "The NVIDIA driver is too old for the CUDA runtime selected by ONNX Runtime. Update the NVIDIA driver from nvidia.com, restart Windows, and run the installer again."
    }
    elseif ($lower -match 'cudaexecutionprovider|execution provider|gpu initialization') {
        Write-Log "ONNX Runtime installed, but GPU acceleration did not start. Check the NVIDIA driver, then run verify_install.py from the FaceVision folder for a detailed report. FaceVision can still run on CPU."
    }
    elseif ($lower -match 'no matching distribution|requires-python|python version|win32') {
        Write-Log "Python or Windows architecture is unsupported. Use 64-bit Python 3.12 on 64-bit Windows, then run the installer again."
    }
    elseif ($lower -match 'ssl|certificate|timed out|connection|proxy|download') {
        Write-Log "A download failed. Check your internet connection, captive-portal sign-in, date/time, firewall, antivirus, or school/work proxy, then rerun the installer."
    }
    elseif ($lower -match 'access.*denied|permission') {
        Write-Log "Windows denied file access. Close any running FaceVision/Python windows, then rerun PowerShell normally. If the selected install folder is protected, choose a folder you own."
    }
    else {
        Write-Log "Read the saved installer log below. If you need help, share the error section only—never share Blynk tokens, Wi-Fi passwords, or face images."
    }
}

try {
    Write-Log "Starting FaceVision installer"
    $pythonCommand = Get-Python312
    Write-Log "Using Python: $pythonCommand"

    New-Item -ItemType Directory -Path $temporaryDirectory -Force | Out-Null
    $archivePath = Join-Path $temporaryDirectory "FaceVision.zip"
    $extractPath = Join-Path $temporaryDirectory "extracted"

    Write-Log "Downloading FaceVision..."
    Invoke-WebRequest -Uri $repoArchiveUrl -OutFile $archivePath -UseBasicParsing -ErrorAction Stop
    Expand-Archive -LiteralPath $archivePath -DestinationPath $extractPath -Force

    $sourceDirectory = Get-ChildItem -LiteralPath $extractPath -Directory | Select-Object -First 1
    if ($null -eq $sourceDirectory) { throw "Downloaded archive did not contain a project directory." }

    # Backup and preserve local/private files before replacing an installation.
    $savedSettingsPath = $null
    $savedKnownFacesPath = $null
    if (Test-Path -LiteralPath $InstallPath) {
        $backupPath = "$InstallPath-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-Log "Backing up existing installation to: $backupPath"
        Copy-Item -LiteralPath $InstallPath -Destination $backupPath -Recurse -Force
        $existingSettings = Join-Path $InstallPath "FaceVision\local_settings.py"
        $existingFaces = Join-Path $InstallPath "FaceVision\data\known_faces"
        if (Test-Path -LiteralPath $existingSettings) {
            $savedSettingsPath = Join-Path $temporaryDirectory "local_settings.py"
            Copy-Item -LiteralPath $existingSettings -Destination $savedSettingsPath -Force
        }
        if (Test-Path -LiteralPath $existingFaces) {
            $savedKnownFacesPath = Join-Path $temporaryDirectory "known_faces"
            Copy-Item -LiteralPath $existingFaces -Destination $savedKnownFacesPath -Recurse -Force
        }
    }

    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Copy-Item -Path (Join-Path $sourceDirectory.FullName "*") -Destination $InstallPath -Recurse -Force

    # Ensure data and known_faces directories exist to avoid runtime errors
    $knownFacesPath = Join-Path $InstallPath "FaceVision\data\known_faces"
    New-Item -ItemType Directory -Path $knownFacesPath -Force | Out-Null

    $settingsPath = Join-Path $InstallPath "FaceVision\local_settings.py"
    $settingsExamplePath = Join-Path $InstallPath "FaceVision\local_settings.example.py"
    if ($savedSettingsPath) {
        Copy-Item -LiteralPath $savedSettingsPath -Destination $settingsPath -Force
        Write-Log "Restored private local_settings.py."
    }
    elseif (-not (Test-Path -LiteralPath $settingsPath) -and (Test-Path -LiteralPath $settingsExamplePath)) {
        Copy-Item -LiteralPath $settingsExamplePath -Destination $settingsPath
    }
    if ($savedKnownFacesPath) {
        $savedFaceItems = Get-ChildItem -LiteralPath $savedKnownFacesPath -Force
        if ($savedFaceItems) {
            Copy-Item -LiteralPath $savedFaceItems.FullName -Destination $knownFacesPath -Recurse -Force
            Write-Log "Restored enrolled face images."
        }
    }

    if (-not $SkipDependencies) {
        Write-Log "Installing FaceVision dependencies (safe mode)"
        try {
            & (Join-Path $InstallPath "FaceVision\setup_gpu.ps1") -PythonCommand $pythonCommand -ForceCpu:$ForceCpu
        } catch {
            Write-Log "Dependency install failed: $($_.Exception.Message)"
            Write-Log "Attempting best-effort recovery: restoring backup if exists"
            if ($backupPath -and (Test-Path $backupPath)) {
                Remove-Item -LiteralPath $InstallPath -Recurse -Force -ErrorAction SilentlyContinue
                Copy-Item -LiteralPath $backupPath -Destination $InstallPath -Recurse -Force
                Write-Log "Restored backup to $InstallPath"
            }
            throw
        }
    }

    Write-Log "FaceVision installed at: $InstallPath"
    Write-Log "Set Wi-Fi/Blynk values in: $settingsPath"
    Write-Log "Running installation diagnostic..."
    & $pythonCommand (Join-Path $InstallPath "verify_install.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Log "[WARNING] The diagnostic found a problem. FaceVision may still run on CPU; see the report above before relying on GPU acceleration."
    }

    $installSucceeded = $true
    if (-not $NoLaunch) {
        & (Join-Path $InstallPath "Start-FaceVision.ps1") -PythonCommand $pythonCommand
    }
} catch {
    Write-Log "Installer failed: $($_.Exception.Message)"
    Write-ProblemHelp $_.Exception.Message
    Write-Log "Detailed installer log kept at: $logFile"
    throw
} finally {
    Write-Log "Installer finished (success or failure logged)"
    $tempRoot = [System.IO.Path]::GetTempPath()
    if ($installSucceeded -and $temporaryDirectory.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $temporaryDirectory)) {
        Remove-Item -LiteralPath $temporaryDirectory -Recurse -Force -ErrorAction SilentlyContinue
    }
}
