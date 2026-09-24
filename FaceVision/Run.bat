$ErrorActionPreference = "Stop"

# Force context to the root folder where this script lives
Set-Location -Path $PSScriptRoot

# Build the exact launcher path dynamically
$launcherPath = Join-Path $PSScriptRoot "FaceVision\launcher.py"

# Brute-force execute using the globally stable Python 'py' launcher
& py $launcherPath
