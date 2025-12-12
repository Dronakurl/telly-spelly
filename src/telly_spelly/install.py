#!/usr/bin/env python3
"""Install desktop integration for Telly Spelly (icon, desktop entry, KDE shortcuts)"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


DESKTOP_ENTRY = """[Desktop Entry]
Name=Telly Spelly
Comment=Voice to text transcription using Whisper
Exec=telly-spelly
Icon=telly-spelly
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Utility;Qt;KDE;
Keywords=voice;speech;transcription;whisper;
X-DBUS-ServiceName=org.kde.telly_spelly

Actions=ToggleRecording;

[Desktop Action ToggleRecording]
Name=Toggle Recording
Exec=dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.ToggleRecording
Icon=media-record
"""

SHORTCUT_ENTRY = """[Desktop Entry]
Name=Telly Spelly
Comment=Voice to text transcription

[Desktop Action ToggleRecording]
Name=Toggle Recording
Exec=dbus-send --session --type=method_call --dest=org.kde.telly_spelly /TellySpelly org.kde.telly_spelly.ToggleRecording
"""


def get_package_dir():
    """Get the directory where this package is installed"""
    return Path(__file__).parent


def install_icon():
    """Install the application icon"""
    icon_dest = Path.home() / ".local/share/icons/hicolor/128x128/apps"
    icon_dest.mkdir(parents=True, exist_ok=True)

    # Look for icon in package directory or current directory
    icon_sources = [
        get_package_dir() / "telly-spelly.png",
        get_package_dir().parent.parent / "telly-spelly.png",
        Path.cwd() / "telly-spelly.png",
    ]

    icon_src = None
    for src in icon_sources:
        if src.exists():
            icon_src = src
            break

    if icon_src:
        shutil.copy(icon_src, icon_dest / "telly-spelly.png")
        print(f"✓ Icon installed to {icon_dest}")
    else:
        print("⚠ Icon file not found, using system theme icon")

    # Update icon cache
    try:
        subprocess.run(
            ["gtk-update-icon-cache", "-f", "-t", str(Path.home() / ".local/share/icons/hicolor")],
            capture_output=True
        )
    except FileNotFoundError:
        pass


def install_desktop_entry():
    """Install the desktop entry"""
    apps_dir = Path.home() / ".local/share/applications"
    apps_dir.mkdir(parents=True, exist_ok=True)

    desktop_file = apps_dir / "telly-spelly.desktop"
    desktop_file.write_text(DESKTOP_ENTRY)

    # Update desktop database
    try:
        subprocess.run(["update-desktop-database", str(apps_dir)], capture_output=True)
    except FileNotFoundError:
        pass

    print(f"✓ Desktop entry installed to {desktop_file}")


def install_kde_shortcuts():
    """Install KDE shortcut configuration"""
    # Install shortcut desktop file for KDE
    shortcuts_dir = Path.home() / ".local/share/kglobalaccel"
    shortcuts_dir.mkdir(parents=True, exist_ok=True)

    shortcut_file = shortcuts_dir / "telly-spelly.desktop"
    shortcut_file.write_text(SHORTCUT_ENTRY)

    # Add to kglobalshortcutsrc
    kglobal_rc = Path.home() / ".config/kglobalshortcutsrc"

    shortcut_config = """
[telly-spelly.desktop]
ToggleRecording=Ctrl+Alt+R,Ctrl+Alt+R,Toggle Recording
_k_friendly_name=Telly Spelly
"""

    # Check if already configured
    if kglobal_rc.exists():
        content = kglobal_rc.read_text()
        if "[telly-spelly.desktop]" not in content:
            with open(kglobal_rc, "a") as f:
                f.write(shortcut_config)
            print("✓ KDE shortcut Ctrl+Alt+R configured")
        else:
            print("✓ KDE shortcut already configured")
    else:
        kglobal_rc.write_text(shortcut_config.strip() + "\n")
        print("✓ KDE shortcut Ctrl+Alt+R configured")

    # Reload KDE shortcuts
    try:
        subprocess.run(
            ["dbus-send", "--session", "--type=signal", "/kglobalaccel",
             "org.kde.kglobalaccel.reloadConfig"],
            capture_output=True
        )
    except Exception:
        pass


def main():
    """Main install function"""
    print("Installing Telly Spelly desktop integration...\n")

    install_icon()
    install_desktop_entry()
    install_kde_shortcuts()

    print("\n✓ Installation complete!")
    print("\nTo start Telly Spelly:")
    print("  - Run 'telly-spelly' from terminal")
    print("  - Or find 'Telly Spelly' in your application menu")
    print("  - Use Ctrl+Alt+R to toggle recording (may need logout/login)")

    return 0


def uninstall():
    """Remove desktop integration"""
    print("Removing Telly Spelly desktop integration...\n")

    files_to_remove = [
        Path.home() / ".local/share/applications/telly-spelly.desktop",
        Path.home() / ".local/share/icons/hicolor/128x128/apps/telly-spelly.png",
        Path.home() / ".local/share/kglobalaccel/telly-spelly.desktop",
    ]

    for f in files_to_remove:
        if f.exists():
            f.unlink()
            print(f"✓ Removed {f}")

    print("\n✓ Uninstall complete!")
    print("Note: You may need to manually remove the shortcut from")
    print("      System Settings → Shortcuts → Telly Spelly")

    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        sys.exit(uninstall())
    sys.exit(main())
