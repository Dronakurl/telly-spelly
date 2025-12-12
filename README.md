# Telly Spelly

Voice-to-text transcription for KDE Plasma using OpenAI's Whisper.

Press a keyboard shortcut, speak, press again - your words are transcribed and copied to the clipboard.

## Installation

### 1. Install system dependencies

**Ubuntu/Debian:**
```bash
sudo apt install portaudio19-dev libdbus-1-dev
```

**Arch Linux:**
```bash
sudo pacman -S portaudio dbus
```

### 2. Install Telly Spelly

**With uv (recommended):**
```bash
uv tool install telly-spelly --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/
```

**With pip:**
```bash
pip install telly-spelly --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/
```

### 3. Setup desktop integration

```bash
telly-spelly-install
```

This installs the app icon, desktop entry, and configures Ctrl+Alt+R shortcut.

## Usage

1. Press `Ctrl+Alt+R` or click the tray icon
2. Speak - a recording indicator appears
3. Press `Ctrl+Alt+R` again to stop
4. Text is copied to your clipboard

## Configuration

Right-click the tray icon → **Settings**:
- Whisper model (tiny, base, small, medium, large, turbo)
- Language
- Input device

## Requirements

- KDE Plasma 5 or 6
- Python 3.9+
- ~2GB disk space (Whisper model)
- NVIDIA GPU recommended (works on CPU)

## Troubleshooting

**Shortcuts not working?**
- Check System Settings → Shortcuts → Telly Spelly
- Log out and back in after first setup

**No audio?**
- Check microphone in system settings
- Try different input device in Telly Spelly settings

**Slow transcription?**
- Use smaller model (tiny/base)
- Install CUDA for GPU acceleration

## License

MIT License

## Credits

- [OpenAI Whisper](https://github.com/openai/whisper)
- Original concept by Guilherme da Silveira
