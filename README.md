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

### 3. Run

```bash
telly-spelly
```

On first launch, desktop integration (icon, menu entry) is set up automatically.

### 4. Configure shortcut

Open **System Settings → Shortcuts → Telly Spelly** and set Ctrl+Alt+R for "Toggle Recording".

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

## Flatpak (CPU-only)

A CPU-only Flatpak build is available that doesn't require NVIDIA drivers.

### Building from source

```bash
# Install flatpak-builder
sudo apt install flatpak-builder  # Debian/Ubuntu
sudo pacman -S flatpak-builder    # Arch

# Install KDE runtime
flatpak install flathub org.kde.Platform//6.8 org.kde.Sdk//6.8

# Build
cd flatpak
flatpak-builder --force-clean builddir org.kde.TellySpelly.yml

# Install locally
flatpak-builder --user --install --force-clean builddir org.kde.TellySpelly.yml

# Run
flatpak run org.kde.TellySpelly
```

### Regenerating Python dependencies

If you need to update Python dependencies:

```bash
pip install req2flatpak
python -m req2flatpak \
  --requirements "numpy==2.0.0" "scipy==1.13.0" "tiktoken==0.8.0" "regex==2024.5.15" \
    "more-itertools==10.2.0" "tqdm==4.66.4" "requests==2.32.3" "urllib3==2.2.3" \
    "certifi==2024.8.30" "charset-normalizer==3.4.0" "idna==3.10" \
  --target-platforms 312-x86_64 \
  --outfile flatpak/python-deps-wheels.json
```

## Requirements

- KDE Plasma 5 or 6
- Python 3.9+
- ~2GB disk space (Whisper model)
- NVIDIA GPU recommended (works on CPU, Flatpak is CPU-only)

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
