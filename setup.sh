#!/usr/bin/env bash
# ==============================================================================
# BombSquad Modded Server - Automated Setup & Installer Script
# Target OS: Ubuntu 26+ (Linux x86_64 / aarch64)
# Python: 3.14
# Branch: public-server
# ==============================================================================

# Interactivity detection
INTERACTIVE=true
AUTO_YES=false
# If stdin is not a terminal and /dev/tty is not accessible, fallback to non-interactive mode
if [ ! -t 0 ] && [ ! -c /dev/tty ]; then
    INTERACTIVE=false
    AUTO_YES=true
fi

# Exit on critical unhandled errors
set -o pipefail

# ANSI color codes
if [ -t 1 ]; then
    BOLD="\033[1m"
    DIM="\033[2m"
    RED="\033[31m"
    GREEN="\033[32m"
    YELLOW="\033[33m"
    BLUE="\033[34m"
    MAGENTA="\033[35m"
    CYAN="\033[36m"
    RESET="\033[0m"
else
    BOLD=""
    DIM=""
    RED=""
    GREEN=""
    YELLOW=""
    BLUE=""
    MAGENTA=""
    CYAN=""
    RESET=""
fi

# Logging functions
log_info() { echo -e "${CYAN}[i]${RESET} $1"; }
log_success() { echo -e "${GREEN}[✓]${RESET} $1"; }
log_warn() { echo -e "${YELLOW}[!]${RESET} $1"; }
log_error() { echo -e "${RED}[✗] ERROR:${RESET} $1" >&2; }
log_step() { echo -e "\n${BOLD}${BLUE}==>${RESET} ${BOLD}$1${RESET}"; }

# Banner
print_banner() {
    echo -e "${CYAN}${BOLD}"
    cat << "EOF"
 ____                  _     ____                      _ 
| __ )  ___  _ __ ___ | |__ / ___|  __ _ _   _  __ _  __| |
|  _ \ / _ \| '_ ` _ \| '_ \\___ \ / _` | | | |/ _` |/ _` |
| |_) | (_) | | | | | | |_) |___) | (_| | |_| | (_| | (_| |
|____/ \___/|_| |_| |_|_.__/|____/ \__, |\__,_|\__,_|\__,_|
                                      |_|                  
EOF
    echo -e "${RESET}${BOLD} BombSquad Ballistica Modded Server - Automated Setup${RESET}"
    echo -e "${DIM} Target: Ubuntu 26+ | Python 3.14 | Branch: public-server${RESET}\n"
}

# Defaults
TARGET_DIR="Bombsquad-Ballistica-Modded-Server"
REPO_BRANCH="public-server"
REPO_URL="https://github.com/imayushsaini/Bombsquad-Ballistica-Modded-Server.git"
TMUX_SESSION="bombsquad"
START_SERVER=true
SKIP_CLONE=false
INSTALL_DIR=""

# Parse CLI arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes|--non-interactive)
            AUTO_YES=true
            INTERACTIVE=false
            shift
            ;;
        -d|--dir)
            TARGET_DIR="$2"
            shift 2
            ;;
        -b|--branch)
            REPO_BRANCH="$2"
            shift 2
            ;;
        -s|--session)
            TMUX_SESSION="$2"
            shift 2
            ;;
        --no-start)
            START_SERVER=false
            shift
            ;;
        -h|--help)
            echo "Usage: bash setup.sh [options]"
            echo "Options:"
            echo "  -y, --yes              Non-interactive mode (accept defaults)"
            echo "  -d, --dir <path>       Custom directory to install server"
            echo "  -b, --branch <name>    Git branch to clone (default: public-server)"
            echo "  -s, --session <name>   Tmux session name (default: bombsquad)"
            echo "  --no-start             Do not start server after installation"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            log_warn "Unknown option: $1"
            shift
            ;;
    esac
done

# Prompt helper with default value
ask_prompt() {
    local prompt_text="$1"
    local default_val="$2"
    local var_name="$3"
    if [ "$AUTO_YES" = true ]; then
        eval "$var_name=\"$default_val\""
        return
    fi
    echo -ne "${BOLD}${prompt_text}${RESET} "
    local user_val=""
    if [ -c /dev/tty ] && [ -r /dev/tty ]; then
        read -r user_val < /dev/tty
    else
        read -r user_val
    fi
    if [ -z "$user_val" ]; then
        eval "$var_name=\"$default_val\""
    else
        eval "$var_name=\"$user_val\""
    fi
}

# Yes/No prompt helper
ask_yes_no() {
    local prompt_text="$1"
    local default_val="$2" # "y" or "n"
    if [ "$AUTO_YES" = true ]; then
        [ "$default_val" = "y" ] && return 0 || return 1
    fi
    local suffix="[Y/n]"
    [ "$default_val" = "n" ] && suffix="[y/N]"
    while true; do
        echo -ne "${BOLD}${prompt_text}${RESET} ${DIM}${suffix}${RESET}: "
        local answer=""
        if [ -c /dev/tty ] && [ -r /dev/tty ]; then
            read -r answer < /dev/tty
        else
            read -r answer
        fi
        answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]' | xargs)
        if [ -z "$answer" ]; then
            answer="$default_val"
        fi
        case "$answer" in
            y|yes) return 0 ;;
            n|no) return 1 ;;
            *) echo -e "${YELLOW}Please enter 'y' or 'n'.${RESET}" ;;
        esac
    done
}

# ==============================================================================
# START OF SCRIPT
# ==============================================================================
print_banner

# Step 1: Privilege Verification
log_step "Checking user privileges..."
if [ "$EUID" -ne 0 ]; then
    log_error "Root privileges are required to run this installer."
    echo -e "\n${YELLOW}${BOLD}Please re-run the installation command with sudo:${RESET}"
    echo -e "  ${CYAN}curl -sSL https://raw.githubusercontent.com/imayushsaini/Bombsquad-Ballistica-Modded-Server/public-server/setup.sh | sudo bash${RESET}"
    echo -e "  Or: ${CYAN}sudo bash setup.sh${RESET}\n"
    exit 1
fi
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ]; then
    log_info "Running via sudo on behalf of user: $SUDO_USER"
else
    log_info "Running as root user."
fi
log_success "Privilege check passed."

# Step 2: OS Check (Minimum Ubuntu 26 required)
log_step "Validating operating system..."
if [ "$(uname -s)" != "Linux" ]; then
    log_error "Unsupported operating system: $(uname -s). Linux is required."
    exit 1
fi

IS_UBUNTU=false
UBUNTU_VER=0
OS_NAME="Linux"

if [ -f /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    OS_NAME="${PRETTY_NAME:-$NAME}"
    if [ "${ID:-}" = "ubuntu" ] || [[ "${ID_LIKE:-}" =~ "ubuntu" ]]; then
        IS_UBUNTU=true
        UBUNTU_VER=$(echo "${VERSION_ID:-0}" | cut -d. -f1 | tr -cd '0-9')
    fi
fi

if [ "$IS_UBUNTU" = true ]; then
    if [ "$UBUNTU_VER" -lt 26 ]; then
        log_warn "Detected: $OS_NAME (Version ${VERSION_ID:-unknown})"
        log_warn "BombSquad Modded Server requires minimum Ubuntu 26."
        log_warn "Pre-compiled native extensions (.cpython-314-*.so) and Python 3.14 require Ubuntu 26+ runtime."
        if ! ask_yes_no "Do you want to continue anyway? (Experimental / Installation may fail)" "n"; then
            log_error "Installation cancelled. Please upgrade to Ubuntu 26 or higher."
            exit 1
        fi
    else
        log_success "Ubuntu version check passed: $OS_NAME (Version $VERSION_ID)"
    fi
else
    log_warn "Non-Ubuntu distribution detected: $OS_NAME"
    log_warn "This server is pre-configured and compiled for Ubuntu 26+ (apt package manager and Python 3.14)."
    if ! ask_yes_no "Do you want to proceed anyway?" "n"; then
        log_error "Installation cancelled."
        exit 1
    fi
fi

# Step 3: Architecture Validation
log_step "Checking processor architecture..."
ARCH=$(uname -m)
case "$ARCH" in
    x86_64)
        log_success "Architecture supported: x86_64 (amd64)"
        ;;
    aarch64|arm64)
        log_success "Architecture supported: $ARCH (arm64)"
        ;;
    *)
        log_error "Unsupported architecture: $ARCH"
        log_error "BombSquad headless binaries are only provided for x86_64 and aarch64."
        exit 1
        ;;
esac

# Step 4: Memory Check & Swap Creation
log_step "Checking system memory and swap..."
if [ -f /proc/meminfo ]; then
    MEM_TOTAL_KB=$(grep -m1 MemTotal /proc/meminfo | awk '{print $2}')
    MEM_TOTAL_MB=$((MEM_TOTAL_KB / 1024))
    SWAP_TOTAL_KB=$(grep -m1 SwapTotal /proc/meminfo | awk '{print $2}')
    SWAP_TOTAL_MB=$((SWAP_TOTAL_KB / 1024))
    TOTAL_MEM_AVAIL=$((MEM_TOTAL_MB + SWAP_TOTAL_MB))

    log_info "Detected RAM: ${MEM_TOTAL_MB} MB | Swap: ${SWAP_TOTAL_MB} MB"

    if [ "$TOTAL_MEM_AVAIL" -lt 1500 ]; then
        log_warn "Low system memory detected (${MEM_TOTAL_MB} MB RAM, ${SWAP_TOTAL_MB} MB Swap)."
        log_warn "BombSquad recommends at least 1.5 GB - 2 GB of memory to prevent Out-Of-Memory (OOM) crashes."
        if ask_yes_no "Would you like to automatically create and activate a 2 GB swap file (/swapfile)?" "y"; then
            log_info "Creating 2 GB swap file at /swapfile..."
            if fallocate -l 2G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=2048 2>/dev/null; then
                chmod 600 /swapfile
                mkswap /swapfile >/dev/null 2>&1
                swapon /swapfile >/dev/null 2>&1
                if ! grep -q "/swapfile" /etc/fstab 2>/dev/null; then
                    echo "/swapfile none swap sw 0 0" | tee -a /etc/fstab >/dev/null
                fi
                log_success "2 GB swap file activated successfully!"
            else
                log_warn "Unable to create swap file. Ensure there is enough free disk space."
            fi
        fi
    else
        log_success "Memory requirements satisfied (${MEM_TOTAL_MB} MB RAM + ${SWAP_TOTAL_MB} MB Swap)."
    fi
fi

# Step 5: Install System Prerequisites
log_step "Updating package repositories & installing dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y software-properties-common curl git tmux ca-certificates procps lsof net-tools

# Step 6: Install Python 3.14
log_step "Checking Python 3.14..."
if ! command -v python3.14 >/dev/null 2>&1; then
    log_info "Python 3.14 not found. Installing Python 3.14 and development headers..."
    if ! apt-cache show python3.14 >/dev/null 2>&1; then
        log_info "Adding deadsnakes PPA..."
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update -y
    fi
    apt-get install -y python3.14 python3.14-dev python3.14-venv python3-pip
fi

if ! command -v python3.14 >/dev/null 2>&1; then
    log_error "Python 3.14 could not be installed automatically."
    log_error "Please install python3.14 manually and re-run this script."
    exit 1
fi
PY_VER=$(python3.14 --version 2>&1)
log_success "Python 3.14 verified: $PY_VER"

# Step 7: Clone Repository (public-server branch with depth 1)
log_step "Setting up server repository..."

# Check if current directory is already the server repository
if [ -f "./bombsquad_server" ] && [ -d "./dist/ba_root" ]; then
    log_info "Current working directory appears to be an existing BombSquad server repository."
    if ask_yes_no "Use current directory as the installation directory?" "y"; then
        INSTALL_DIR="$(pwd)"
        SKIP_CLONE=true
    fi
fi

if [ "$SKIP_CLONE" != true ]; then
    if [ -d "$TARGET_DIR" ]; then
        log_warn "Directory '$TARGET_DIR' already exists."
        echo -e "Choose an option:"
        echo -e "  1) Use existing directory (skip cloning)"
        echo -e "  2) Backup existing directory and clone fresh"
        echo -e "  3) Cancel installation"
        ask_prompt "Enter choice [1/2/3, default: 1]:" "1" DIR_CHOICE
        case "$DIR_CHOICE" in
            1)
                INSTALL_DIR="$(cd "$TARGET_DIR" && pwd)"
                SKIP_CLONE=true
                ;;
            2)
                BACKUP_DIR="${TARGET_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
                log_info "Backing up '$TARGET_DIR' -> '$BACKUP_DIR'..."
                mv "$TARGET_DIR" "$BACKUP_DIR"
                ;;
            *)
                log_error "Installation cancelled by user."
                exit 1
                ;;
        esac
    fi
fi

if [ "$SKIP_CLONE" != true ]; then
    log_info "Cloning branch '$REPO_BRANCH' (depth=1) from $REPO_URL..."
    if ! git clone --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" "$TARGET_DIR"; then
        log_error "Failed to clone repository. Please check your network connection."
        exit 1
    fi
    INSTALL_DIR="$(cd "$TARGET_DIR" && pwd)"
    log_success "Repository successfully cloned to: $INSTALL_DIR"
fi

cd "$INSTALL_DIR" || { log_error "Failed to enter directory: $INSTALL_DIR"; exit 1; }

# Step 8: Set File Permissions (chmod)
log_step "Setting file permissions..."
chmod 777 bombsquad_server 2>/dev/null || chmod +x bombsquad_server
if [ -f "dist/bombsquad_headless" ]; then
    chmod 777 dist/bombsquad_headless 2>/dev/null || chmod +x dist/bombsquad_headless
fi
if [ -f "dist/bombsquad_headless_aarch64" ]; then
    chmod 777 dist/bombsquad_headless_aarch64 2>/dev/null || chmod +x dist/bombsquad_headless_aarch64
fi
log_success "Executable permissions applied to server binaries."

# If executed via sudo from a non-root SSH user, ensure that user owns the directory
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ] && [ "$EUID" -eq 0 ]; then
    chown -R "$SUDO_USER:$SUDO_USER" "$INSTALL_DIR" 2>/dev/null || true
fi

# Step 9: Pre-install Python Dependencies
log_step "Checking Python site-packages dependencies..."
TARGET_SITE="$INSTALL_DIR/dist/ba_data/python-site-packages"
mkdir -p "$TARGET_SITE"
python3.14 -m pip install --target "$TARGET_SITE" --break-system-packages ecdsa flask waitress websockets >/dev/null 2>&1 || {
    python3.14 -m ensurepip --default-pip >/dev/null 2>&1 || true
    python3.14 -m pip install --target "$TARGET_SITE" --break-system-packages ecdsa flask waitress websockets >/dev/null 2>&1 || true
}
log_success "Python package dependencies prepared."

# Step 10: Interactive Server Configuration
log_step "Server Configuration"
CFG_FILE="$INSTALL_DIR/config.json"
ROLES_FILE="$INSTALL_DIR/dist/ba_root/mods/playersData/roles.json"
SETTING_FILE="$INSTALL_DIR/dist/ba_root/mods/setting.json"

if ask_yes_no "Would you like to configure server settings interactively now?" "y"; then
    # Server Name
    ask_prompt "Enter Server Name [default: 'BombSquad Community Server 1.8']:" "BombSquad Community Server 1.8" CFG_NAME

    # Server Port
    while true; do
        ask_prompt "Enter UDP Port [default: 43211]:" "43211" CFG_PORT
        if [[ "$CFG_PORT" =~ ^[0-9]+$ ]] && [ "$CFG_PORT" -ge 1024 ] && [ "$CFG_PORT" -le 65535 ]; then
            if lsof -i :"$CFG_PORT" >/dev/null 2>&1 || (command -v ss >/dev/null 2>&1 && ss -uln | grep -q ":$CFG_PORT "); then
                log_warn "Port $CFG_PORT is currently in use by another process!"
                if ! ask_yes_no "Use port $CFG_PORT anyway?" "n"; then
                    continue
                fi
            fi
            break
        else
            echo -e "${RED}Invalid port. Please enter a valid number between 1024 and 65535.${RESET}"
        fi
    done

    # Max Players
    while true; do
        ask_prompt "Enter Max Players (Party Size) [default: 6]:" "6" CFG_MAX_PLAYERS
        if [[ "$CFG_MAX_PLAYERS" =~ ^[0-9]+$ ]] && [ "$CFG_MAX_PLAYERS" -ge 1 ] && [ "$CFG_MAX_PLAYERS" -le 32 ]; then
            break
        else
            echo -e "${RED}Please enter a number between 1 and 32.${RESET}"
        fi
    done

    # Game Session Type
    echo -e "Select Game Mode:"
    echo -e "  1) Teams (default: 2 Teams, Red vs Blue)"
    echo -e "  2) Free-for-all (ffa: everyone against everyone)"
    echo -e "  3) Co-op (coop: cooperative campaign missions)"
    ask_prompt "Choice [1/2/3, default: 1]:" "1" MODE_CHOICE
    case "$MODE_CHOICE" in
        2) CFG_MODE="ffa" ;;
        3) CFG_MODE="coop" ;;
        *) CFG_MODE="teams" ;;
    esac

    # Owner PB-ID
    echo -e "${CYAN}Note: Find your PB-ID in BombSquad -> Settings -> Advanced -> Account Details (e.g. pb-IF48VWkBFQ)${RESET}"
    ask_prompt "Enter your Owner PB-ID [Press Enter to skip]:" "" CFG_OWNER_ID

    # Server Manager Web Password
    echo -e "${CYAN}Note: Server Manager password for Ballistica Web Stats console (https://bombsquad-community.web.app)${RESET}"
    ask_prompt "Enter Server Manager Web Password [Press Enter to keep default]:" "" CFG_WEB_PASSWORD

    # Safely update config.json, roles.json, and setting.json with Python
    python3.14 - "$CFG_FILE" "$ROLES_FILE" "$SETTING_FILE" "$CFG_NAME" "$CFG_PORT" "$CFG_MAX_PLAYERS" "$CFG_MODE" "$CFG_OWNER_ID" "$CFG_WEB_PASSWORD" << 'PYEOF'
import sys, json, os

cfg_path = sys.argv[1]
roles_path = sys.argv[2]
setting_path = sys.argv[3]
party_name = sys.argv[4]
port = int(sys.argv[5])
max_players = int(sys.argv[6])
session_type = sys.argv[7]
owner_id = sys.argv[8].strip()
web_password = sys.argv[9].strip()

# Update config.json
if os.path.exists(cfg_path):
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    if party_name:
        cfg["party_name"] = party_name
    if port:
        cfg["port"] = port
    if max_players:
        cfg["max_party_size"] = max_players
    if session_type:
        cfg["session_type"] = session_type
        # If user explicitly chooses FFA or Co-op, reset playlist_code to null
        # so it doesn't force-load the default shared Teams playlist (622903)
        if session_type != "teams":
            cfg["playlist_code"] = None
        elif cfg.get("playlist_code") is None:
            cfg["playlist_code"] = 622903
    if owner_id:
        admins = [a for a in cfg.get("admins", []) if not a.startswith("a-YOUR-ID") and not a.startswith("a-ANOTHER-ID")]
        if owner_id not in admins:
            admins.append(owner_id)
        cfg["admins"] = admins
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

# Update roles.json
if owner_id and os.path.exists(roles_path):
    try:
        with open(roles_path, "r", encoding="utf-8") as f:
            roles = json.load(f)
        if "owner" in roles and "ids" in roles["owner"]:
            if owner_id not in roles["owner"]["ids"]:
                roles["owner"]["ids"].insert(0, owner_id)
        with open(roles_path, "w", encoding="utf-8") as f:
            json.dump(roles, f, indent=4)
    except Exception as e:
        print(f"Warning: could not update roles.json: {e}", file=sys.stderr)

# Update setting.json ballistica_web password if provided (keep HostName untouched)
if web_password and os.path.exists(setting_path):
    try:
        with open(setting_path, "r", encoding="utf-8") as f:
            setting = json.load(f)
        if "ballistica_web" not in setting:
            setting["ballistica_web"] = {}
        setting["ballistica_web"]["server_password"] = web_password
        with open(setting_path, "w", encoding="utf-8") as f:
            json.dump(setting, f, indent=2)
    except Exception as e:
        print(f"Warning: could not update setting.json: {e}", file=sys.stderr)
PYEOF

    log_success "Configuration updated successfully."
else
    log_info "Skipping interactive configuration. Using default server settings."
fi

# Print installation summary
print_summary() {
    echo -e "\n${GREEN}${BOLD}================================================================${RESET}"
    echo -e "${GREEN}${BOLD}       🎉 BombSquad Modded Server Setup Complete! 🎉            ${RESET}"
    echo -e "${GREEN}${BOLD}================================================================${RESET}"
    echo -e " ${BOLD}Installation Directory:${RESET}  $INSTALL_DIR"
    echo -e " ${BOLD}Tmux Session Name:${RESET}       $TMUX_SESSION"
    echo -e " ${BOLD}Server Config File:${RESET}      $INSTALL_DIR/config.json"
    echo -e " ${BOLD}Roles Configuration:${RESET}     $INSTALL_DIR/dist/ba_root/mods/playersData/roles.json"
    echo -e " ${BOLD}Extra Mod Settings:${RESET}      $INSTALL_DIR/dist/ba_root/mods/setting.json"
    echo -e "----------------------------------------------------------------"
    echo -e " ${BOLD}Tmux Management Cheat Sheet:${RESET}"
    echo -e "   • Attach to console:    ${CYAN}tmux attach -t $TMUX_SESSION${RESET}"
    echo -e "   • Detach from console:  Press ${YELLOW}Ctrl + B${RESET}, then press ${YELLOW}D${RESET}"
    echo -e "   • Stop server session:  ${CYAN}tmux kill-session -t $TMUX_SESSION${RESET}"
    echo -e "   • Stop from inside:     Type ${CYAN}shutdown${RESET} in the server console"
    echo -e "----------------------------------------------------------------"
    echo -e " ${BOLD}Firewall Notice:${RESET}"
    echo -e "   Ensure your server's UDP port is open in your cloud/VPS firewall:"
    echo -e "   ${DIM}sudo ufw allow ${CFG_PORT:-43211}/udp${RESET}"
    echo -e "${GREEN}${BOLD}================================================================${RESET}\n"
}

# Step 11: Tmux Session & Server Execution
log_step "Server Execution & Tmux Setup"

# If invoked via sudo from a non-root user, run tmux as that user
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ] && [ "$EUID" -eq 0 ]; then
    run_user() { sudo -u "$SUDO_USER" "$@"; }
else
    run_user() { "$@"; }
fi

if [ "$START_SERVER" = true ]; then
    if run_user tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
        log_warn "A tmux session named '$TMUX_SESSION' is already active."
        echo -e "Choose an option:"
        echo -e "  1) Attach to existing tmux session"
        echo -e "  2) Kill existing session and start fresh"
        echo -e "  3) Use a different session name"
        echo -e "  4) Do not start server now"
        ask_prompt "Enter choice [1/2/3/4, default: 1]:" "1" TMUX_CHOICE
        case "$TMUX_CHOICE" in
            1)
                print_summary
                log_info "Attaching to tmux session '$TMUX_SESSION'..."
                run_user tmux attach-session -t "$TMUX_SESSION"
                exit 0
                ;;
            2)
                log_info "Killing existing tmux session '$TMUX_SESSION'..."
                run_user tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
                ;;
            3)
                ask_prompt "Enter new session name:" "${TMUX_SESSION}_2" TMUX_SESSION
                ;;
            *)
                START_SERVER=false
                ;;
        esac
    fi

    if [ "$START_SERVER" = true ]; then
        if ask_yes_no "Start the BombSquad server now inside tmux session '$TMUX_SESSION'?" "y"; then
            log_info "Launching server inside tmux session '$TMUX_SESSION'..."
            run_user tmux new-session -d -s "$TMUX_SESSION" -c "$INSTALL_DIR" "./bombsquad_server"
            sleep 2

            if run_user tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
                log_success "Server successfully started in tmux session '$TMUX_SESSION'!"
                print_summary
                if ask_yes_no "Would you like to attach to the server console right now?" "y"; then
                    run_user tmux attach-session -t "$TMUX_SESSION"
                    exit 0
                fi
            else
                log_error "Server process exited prematurely. Run './bombsquad_server' manually to inspect logs."
                print_summary
            fi
        else
            print_summary
        fi
    else
        print_summary
    fi
else
    print_summary
fi
