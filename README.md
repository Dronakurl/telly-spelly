# Telly Spelly

Voice-to-text transcription for KDE Plasma using OpenAI's Whisper.

Press a keyboard shortcut, speak, press again - your words are transcribed and copied to the clipboard.

## Quick Install

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-pip python3-venv git pkg-config portaudio19-dev libdbus-1-dev libglib2.0-dev
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip python3-devel git pkg-config portaudio-devel dbus-devel glib2-devel
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip git pkg-config portaudio dbus glib2
```

### Step 2: Run the Installer

```bash
curl -sSL https://raw.githubusercontent.com/Dronakurl/telly-spelly/main/get-telly-spelly.sh | bash
```

Or with wget:
```bash
wget -qO- https://raw.githubusercontent.com/Dronakurl/telly-spelly/main/get-telly-spelly.sh | bash
```

The installer will:
- Download Telly Spelly to `~/.local/share/telly-spelly`
- Create a Python virtual environment
- Install all Python dependencies (including Whisper)
- Add a desktop entry to your application menu
- Register keyboard shortcuts

### Step 3: Launch

- Open **Telly Spelly** from your application menu, or
- Log out and back in, then use **Ctrl+Alt+R** to toggle recording

## Usage

1. **Start**: Press `Ctrl+Alt+R` or click the tray icon
2. **Speak**: A small recording indicator appears in the corner
3. **Stop**: Press `Ctrl+Alt+R` again or click "Stop Recording"
4. **Done**: Transcribed text is automatically copied to your clipboard

## Features

- **Global Shortcuts**: `Ctrl+Alt+R` to toggle recording (configurable)
- **System Tray**: Unobtrusive tray icon with quick access
- **Local Processing**: Uses Whisper locally - no cloud services, no API keys
- **Auto Clipboard**: Transcribed text is instantly available for pasting
- **KDE Integration**: Native look and feel on KDE Plasma

## Configuration

Right-click the tray icon and select **Settings** to configure:
- Whisper model (tiny, base, small, medium, large, turbo)
- Language selection
- Input device

Keyboard shortcuts can be customized in:
**System Settings → Shortcuts → Shortcuts → Telly Spelly**

## Requirements

- KDE Plasma desktop (5 or 6)
- Python 3.8+
- ~2GB disk space (for Whisper model)
- NVIDIA GPU recommended for faster transcription (works on CPU too)

## Uninstall

```bash
~/.local/share/telly-spelly/uninstall.sh
```

## Troubleshooting

**Shortcuts not working?**
- Make sure Telly Spelly is running (check system tray)
- Try logging out and back in after installation
- Check System Settings → Shortcuts → Telly Spelly

**No audio recording?**
- Check that your microphone is working in system settings
- Try selecting a different input device in Telly Spelly settings

**Slow transcription?**
- Use a smaller Whisper model (tiny or base) in settings
- If you have an NVIDIA GPU, ensure CUDA is installed

## License

MIT License - see LICENSE file for details.

## Credits

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- Original concept by Guilherme da Silveira
