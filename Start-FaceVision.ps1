$ErrorActionPreference = "Stop"

# Force the working directory to exactly where this script lives (C:\Project)
Set-Location -Path $PSScriptRoot

# Combine the root with your slave application folder paths
$launcherPath = Join-Path $PSScriptRoot "FaceVision\launcher.py"

Write-Host "Forcing launch: $launcherPath"

# Direct brute-force execution using the stable 'py' launcher
& py $launcherPath
