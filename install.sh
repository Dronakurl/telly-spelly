#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="telly-spelly"
VENV_DIR="$SCRIPT_DIR/.venv"

echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Telly Spelly Installer           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo

# Check system dependencies
check_dependencies() {
    local missing=()

    echo -e "${YELLOW}Checking system dependencies...${NC}"

    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    else
        echo -e "  ${GREEN}✓${NC} Python 3 found: $(python3 --version)"
    fi

    # Check for pip
    if ! python3 -m pip --version &> /dev/null; then
        missing+=("python3-pip")
    else
        echo -e "  ${GREEN}✓${NC} pip found"
    fi

    # Check for uv (preferred) or venv
    if command -v uv &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} uv found (will use for fast installation)"
        USE_UV=1
    elif python3 -c "import venv" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} venv module found"
        USE_UV=0
    else
        missing+=("python3-venv")
    fi

    # Check for portaudio (required for PyAudio)
    if ! pkg-config --exists portaudio-2.0 2>/dev/null; then
        if ! [ -f /usr/include/portaudio.h ]; then
            missing+=("portaudio19-dev")
        else
            echo -e "  ${GREEN}✓${NC} PortAudio found"
        fi
    else
        echo -e "  ${GREEN}✓${NC} PortAudio found"
    fi

    # Check for D-Bus development files (for dbus-python)
    if ! pkg-config --exists dbus-1 2>/dev/null; then
        missing+=("libdbus-1-dev")
    else
        echo -e "  ${GREEN}✓${NC} D-Bus development files found"
    fi

    # Check for GLib (for dbus-python)
    if ! pkg-config --exists glib-2.0 2>/dev/null; then
        missing+=("libglib2.0-dev")
    else
        echo -e "  ${GREEN}✓${NC} GLib found"
    fi

    # Check for pkg-config itself
    if ! command -v pkg-config &> /dev/null; then
        missing+=("pkg-config")
    fi

    echo

    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}Missing system dependencies:${NC}"
        for dep in "${missing[@]}"; do
            echo -e "  ${RED}✗${NC} $dep"
        done
        echo
        echo -e "${YELLOW}Please install them first with:${NC}"
        echo -e "  ${GREEN}sudo apt install ${missing[*]}${NC}"
        echo
        echo -e "On Fedora/RHEL:"
        echo -e "  ${GREEN}sudo dnf install python3-devel portaudio-devel dbus-devel glib2-devel${NC}"
        echo
        echo -e "On Arch:"
        echo -e "  ${GREEN}sudo pacman -S python portaudio dbus glib2${NC}"
        echo
        return 1
    fi

    echo -e "${GREEN}All system dependencies are met!${NC}"
    return 0
}

# Create virtual environment and install Python packages
install_python_deps() {
    echo
    echo -e "${YELLOW}Setting up Python virtual environment...${NC}"

    if [ "$USE_UV" = "1" ]; then
        uv venv "$VENV_DIR"
        echo -e "${YELLOW}Installing Python packages with uv...${NC}"
        uv pip install -r "$SCRIPT_DIR/requirements.txt"
    else
        python3 -m venv "$VENV_DIR"
        echo -e "${YELLOW}Installing Python packages with pip...${NC}"
        "$VENV_DIR/bin/pip" install --upgrade pip
        "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    fi

    echo -e "${GREEN}Python packages installed!${NC}"
}

# Install desktop entry
install_desktop_entry() {
    echo
    echo -e "${YELLOW}Installing desktop entry...${NC}"

    local desktop_dir="$HOME/.local/share/applications"
    mkdir -p "$desktop_dir"

    # Generate desktop file with correct paths
    cat > "$desktop_dir/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=Telly Spelly
Comment=Voice to text transcription using Whisper
Exec=$VENV_DIR/bin/python $SCRIPT_DIR/main.py
Icon=telly-spelly
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Utility;
Keywords=voice;speech;transcription;whisper;
X-DBUS-ServiceName=org.kde.telly_spelly

Actions=StartRecording;StopRecording;ToggleRecording;

[Desktop Action StartRecording]
Name=Start Recording
Exec=dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.StartRecording
Icon=media-record

[Desktop Action StopRecording]
Name=Stop Recording
Exec=dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.StopRecording
Icon=media-playback-stop

[Desktop Action ToggleRecording]
Name=Toggle Recording
Exec=dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.ToggleRecording
Icon=media-record
EOF

    update-desktop-database "$desktop_dir" 2>/dev/null || true

    echo -e "${GREEN}Desktop entry installed!${NC}"
}

# Register KDE global shortcuts
register_kde_shortcuts() {
    echo
    echo -e "${YELLOW}Registering KDE global shortcuts...${NC}"

    local shortcuts_file="$HOME/.config/kglobalshortcutsrc"
    local toggle_cmd="dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.ToggleRecording"
    local start_cmd="dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.StartRecording"
    local stop_cmd="dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.StopRecording"

    # Check if kwriteconfig5 or kwriteconfig6 is available
    local kwriteconfig=""
    if command -v kwriteconfig6 &> /dev/null; then
        kwriteconfig="kwriteconfig6"
    elif command -v kwriteconfig5 &> /dev/null; then
        kwriteconfig="kwriteconfig5"
    else
        echo -e "  ${YELLOW}!${NC} kwriteconfig not found, skipping automatic shortcut registration"
        echo -e "  ${YELLOW}!${NC} You can manually add shortcuts in System Settings → Shortcuts"
        return
    fi

    # Add telly-spelly section to kglobalshortcutsrc
    # Format: action=shortcut,default_shortcut,friendly_name
    $kwriteconfig --file "$shortcuts_file" --group "telly-spelly.desktop" --key "_k_friendly_name" "Telly Spelly"
    $kwriteconfig --file "$shortcuts_file" --group "telly-spelly.desktop" --key "ToggleRecording" "Ctrl+Alt+R,Ctrl+Alt+R,Toggle Recording"
    $kwriteconfig --file "$shortcuts_file" --group "telly-spelly.desktop" --key "StartRecording" ",none,Start Recording"
    $kwriteconfig --file "$shortcuts_file" --group "telly-spelly.desktop" --key "StopRecording" "Ctrl+Alt+S,Ctrl+Alt+S,Stop Recording"

    # Create custom shortcuts using khotkeys (KDE's custom shortcut system)
    local khotkeys_file="$HOME/.config/khotkeysrc"

    # Get next available data group number
    local next_num=1
    if [ -f "$khotkeys_file" ]; then
        next_num=$(grep -oP 'Data_\K\d+' "$khotkeys_file" 2>/dev/null | sort -n | tail -1)
        next_num=$((next_num + 1))
    fi

    # Add custom shortcut for Toggle Recording
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}" --key "Comment" "Toggle Telly Spelly Recording"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}" --key "Enabled" "true"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}" --key "Name" "Telly Spelly Toggle"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}" --key "Type" "SIMPLE_ACTION_DATA"

    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Actions" --key "ActionsCount" "1"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Actions0" --key "CommandURL" "$toggle_cmd"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Actions0" --key "Type" "COMMAND_URL"

    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Conditions" --key "Comment" ""
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Conditions" --key "ConditionsCount" "0"

    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Triggers" --key "Comment" "Simple_action"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Triggers" --key "TriggersCount" "1"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Triggers0" --key "Key" "Ctrl+Alt+R"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Triggers0" --key "Type" "SHORTCUT"
    $kwriteconfig --file "$khotkeys_file" --group "Data_${next_num}Triggers0" --key "Uuid" "{$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)}"

    # Update Data count in Main group (use kreadconfig to read)
    local kreadconfig=""
    if command -v kreadconfig6 &> /dev/null; then
        kreadconfig="kreadconfig6"
    elif command -v kreadconfig5 &> /dev/null; then
        kreadconfig="kreadconfig5"
    fi

    local current_count="0"
    if [ -n "$kreadconfig" ]; then
        current_count=$($kreadconfig --file "$khotkeys_file" --group "Main" --key "DataCount" 2>/dev/null || echo "0")
    fi
    # Handle empty or non-numeric values
    if ! [[ "$current_count" =~ ^[0-9]+$ ]]; then
        current_count=0
    fi
    $kwriteconfig --file "$khotkeys_file" --group "Main" --key "DataCount" "$((current_count + 1))"

    # Reload khotkeys
    if command -v qdbus &> /dev/null; then
        qdbus org.kde.kglobalaccel /kglobalaccel reloadConfig 2>/dev/null || true
        qdbus org.kde.kded5 /modules/khotkeys reread_configuration 2>/dev/null || true
        qdbus org.kde.kded6 /modules/khotkeys reread_configuration 2>/dev/null || true
    fi

    echo -e "${GREEN}KDE shortcuts registered!${NC}"
    echo -e "  ${GREEN}✓${NC} Ctrl+Alt+R: Toggle Recording"
    echo -e "  ${GREEN}✓${NC} Ctrl+Alt+S: Stop Recording"
}

# Print success message
print_success() {
    echo
    echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     Installation Complete!           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
    echo
    echo -e "You can now:"
    echo -e "  1. Launch ${GREEN}Telly Spelly${NC} from your application menu"
    echo -e "  2. Or run: ${GREEN}$VENV_DIR/bin/python $SCRIPT_DIR/main.py${NC}"
    echo
    echo -e "${YELLOW}To configure keyboard shortcuts:${NC}"
    echo -e "  Go to ${GREEN}System Settings → Shortcuts → Custom Shortcuts${NC}"
    echo -e "  Add a new shortcut with command:"
    echo -e "  ${GREEN}dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.ToggleRecording${NC}"
    echo
    echo -e "${YELLOW}To uninstall:${NC}"
    echo -e "  ${GREEN}$SCRIPT_DIR/uninstall.sh${NC}"
    echo
}

# Install icon
install_icon() {
    echo
    echo -e "${YELLOW}Installing application icon...${NC}"

    local icon_dir="$HOME/.local/share/icons/hicolor/scalable/apps"
    mkdir -p "$icon_dir"

    # Create a simple SVG icon if none exists
    if [ ! -f "$SCRIPT_DIR/telly-spelly.svg" ]; then
        cat > "$icon_dir/telly-spelly.svg" << 'SVGEOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <circle cx="24" cy="24" r="20" fill="#e74c3c"/>
  <circle cx="24" cy="24" r="12" fill="#c0392b"/>
  <circle cx="24" cy="24" r="6" fill="#ecf0f1"/>
</svg>
SVGEOF
    else
        cp "$SCRIPT_DIR/telly-spelly.svg" "$icon_dir/"
    fi

    # Update icon cache
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

    echo -e "${GREEN}Icon installed!${NC}"
}

# Main installation
main() {
    if ! check_dependencies; then
        exit 1
    fi

    install_python_deps
    install_icon
    install_desktop_entry
    register_kde_shortcuts
    print_success
}

main "$@"
