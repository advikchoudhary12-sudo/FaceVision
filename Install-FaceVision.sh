#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${FACEVISION_INSTALL_DIR:-${HOME}/FaceVision}"
NO_LAUNCH=false
SKIP_DEPENDENCIES=false
SKIP_SYSTEM_DEPENDENCIES=false

usage() {
    cat <<'EOF'
Usage: Install-FaceVision.sh [options]

Install FaceVision on Ubuntu using an isolated Python virtual environment.

Options:
  --install-dir PATH             Install location (default: ~/FaceVision)
  --no-launch                    Install without opening the desktop launcher
  --skip-dependencies            Reuse the install's existing Python environment
  --skip-system-dependencies    Do not install Ubuntu packages with apt
  -h, --help                     Show this help
EOF
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

while (($#)); do
    case "$1" in
        --install-dir)
            (($# >= 2)) || fail "--install-dir requires a path."
            INSTALL_DIR="$2"
            shift 2
            ;;
        --no-launch)
            NO_LAUNCH=true
            shift
            ;;
        --skip-dependencies)
            SKIP_DEPENDENCIES=true
            shift
            ;;
        --skip-system-dependencies)
            SKIP_SYSTEM_DEPENDENCIES=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            fail "Unknown option: $1 (use --help for usage)."
            ;;
    esac
done

[[ -r /etc/os-release ]] || fail "This installer supports Ubuntu only."
# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || fail "This installer supports Ubuntu only (detected: ${PRETTY_NAME:-unknown})."
command -v apt-get >/dev/null 2>&1 || fail "apt-get was not found; install this project on Ubuntu."

if [[ "$SKIP_SYSTEM_DEPENDENCIES" != true ]]; then
    apt_command=(apt-get)
    if ((EUID != 0)); then
        command -v sudo >/dev/null 2>&1 || fail "Install system packages as root or install sudo, then rerun."
        apt_command=(sudo apt-get)
    fi
    printf 'Installing Ubuntu packages required by Python, OpenCV, and the desktop UI...\n'
    "${apt_command[@]}" update
    "${apt_command[@]}" install -y \
        ca-certificates \
        build-essential \
        cmake \
        curl \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        python3 \
        python3-dev \
        python3-tk \
        python3-venv
fi

command -v python3 >/dev/null 2>&1 || fail "python3 is required. Install it with: sudo apt-get install python3"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' ||
    fail "Python 3.10 or newer is required; install a supported Ubuntu Python and rerun."

TEMP_DIR="$(mktemp -d)"
cleanup() {
    rm -rf -- "$TEMP_DIR"
}
trap cleanup EXIT

if [[ -f "$SCRIPT_DIR/FaceVision/launcher.py" ]]; then
    printf 'Preparing project files from %s...\n' "$SCRIPT_DIR"
    tar -C "$SCRIPT_DIR" \
        --exclude='./.git' \
        --exclude='./.venv' \
        --exclude='./venv' \
        --exclude='./node_modules' \
        --exclude='./FaceVision/local_settings.py' \
        --exclude='./FaceVision/data/known_faces' \
        --exclude='./ESP_32/ESP_32/wifi_secrets.h' \
        --exclude='./.env' \
        --exclude='./FaceVision/.env' \
        --exclude='./work' \
        --exclude='./ESP_32/ESP_32/build' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        -czf "$TEMP_DIR/FaceVision.tar.gz" .
else
    archive_url="https://github.com/advikchoudhary12-sudo/FaceVision/archive/refs/heads/main.tar.gz"
    printf 'Downloading FaceVision source...\n'
    curl --fail --location --silent --show-error "$archive_url" -o "$TEMP_DIR/FaceVision.tar.gz"
fi

mkdir -p "$TEMP_DIR/source" "$INSTALL_DIR"
tar -xzf "$TEMP_DIR/FaceVision.tar.gz" -C "$TEMP_DIR/source" --strip-components=1
cp -a "$TEMP_DIR/source/." "$INSTALL_DIR/"

app_dir="$INSTALL_DIR/FaceVision"
[[ -f "$app_dir/launcher.py" ]] || fail "The downloaded source did not contain FaceVision/launcher.py."
mkdir -p "$app_dir/data/known_faces"
if [[ ! -f "$app_dir/local_settings.py" && -f "$app_dir/local_settings.example.py" ]]; then
    cp "$app_dir/local_settings.example.py" "$app_dir/local_settings.py"
fi

python_env="$INSTALL_DIR/.venv"
if [[ "$SKIP_DEPENDENCIES" != true ]]; then
    printf 'Creating/updating the FaceVision Python environment...\n'
    python3 -m venv "$python_env"
    "$python_env/bin/python" -m pip install --upgrade pip
    for package in onnxruntime onnxruntime-gpu; do
        if "$python_env/bin/python" -m pip show "$package" >/dev/null 2>&1; then
            "$python_env/bin/python" -m pip uninstall -y "$package"
        fi
    done
    "$python_env/bin/python" -m pip install insightface numpy onnxruntime opencv-python customtkinter pygame
else
    [[ -x "$python_env/bin/python" ]] || fail "No existing virtual environment found at $python_env."
fi

cat > "$INSTALL_DIR/Run-FaceVision.sh" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
install_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$install_dir/.venv/bin/python" "$install_dir/FaceVision/launcher.py" "$@"
EOF
chmod +x "$INSTALL_DIR/Run-FaceVision.sh"

printf 'FaceVision installed at %s\n' "$INSTALL_DIR"
printf 'Private settings: %s\n' "$app_dir/local_settings.py"
printf 'Enrolled face images: %s\n' "$app_dir/data/known_faces"
printf 'Launcher: %s/Run-FaceVision.sh\n' "$INSTALL_DIR"
if [[ "$NO_LAUNCH" != true ]]; then
    if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
        "$INSTALL_DIR/Run-FaceVision.sh"
    else
        printf 'No desktop display detected; start the app later from a graphical session.\n'
    fi
fi
