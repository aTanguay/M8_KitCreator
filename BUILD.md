# Building M8 Kit Creator

This document explains how to build standalone executables of M8 Kit Creator for distribution.

## Overview

M8 Kit Creator can be built as a standalone application that doesn't require Python or any dependencies to be installed. This is achieved using PyInstaller and static-ffmpeg.

## Quick Start

### macOS or Linux

```bash
# Install build dependencies
pip install -r requirements-build.txt

# Build
./build.sh

# Output will be in dist/
# macOS: dist/M8_KitCreator.app
# Linux: dist/M8_KitCreator
```

## Prerequisites

### All Platforms

- Python 3.7 or later
- pip (Python package installer)

### Optional

- Git (for cloning the repository)
- `create-dmg` (macOS only, for creating DMG installers)

## Installation of Build Tools

### 1. Install Python Dependencies

```bash
# Install runtime requirements
pip install -r requirements.txt

# Install build requirements
pip install -r requirements-build.txt
```

This will install:
- `pydub` - Audio processing
- `customtkinter` - Modern UI
- `static-ffmpeg` - Bundled ffmpeg binaries
- `pyinstaller` - Application bundler

### 2. Verify Installation

```bash
python3 --version    # Should be 3.7+
pyinstaller --version # Should be 5.0+
```

## Building

### Automated Build (Recommended)

Use the provided build script:

```bash
# Build for current platform
./build.sh

# Clean build artifacts
./build.sh clean

# Clean and rebuild
./build.sh rebuild
```

### Manual Build

```bash
# Clean previous builds
rm -rf build dist

# Run PyInstaller
pyinstaller M8_KitCreator.spec

# Executable will be in dist/
```

## Build Output

### macOS

```
dist/
└── M8_KitCreator.app/          # macOS application bundle
    ├── Contents/
    │   ├── MacOS/
    │   │   └── M8_KitCreator    # Executable
    │   ├── Resources/
    │   └── Info.plist
```

**Size:** ~80-120 MB (includes Python runtime, libraries, and ffmpeg)

**To run:**
```bash
open dist/M8_KitCreator.app
```

**To create DMG:**
```bash
# Install create-dmg (if not installed)
brew install create-dmg

# Create DMG
create-dmg \
  --volname "M8 Kit Creator" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  dist/M8_KitCreator.dmg \
  dist/M8_KitCreator.app
```

### Linux

```
dist/
└── M8_KitCreator              # Single executable file
```

**Size:** ~80-100 MB (includes Python runtime, libraries, and ffmpeg)

**To run:**
```bash
chmod +x dist/M8_KitCreator
./dist/M8_KitCreator
```

**To create portable archive:**
```bash
cd dist
tar -czf M8_KitCreator-linux-$(uname -m).tar.gz M8_KitCreator
```

## What Gets Bundled

The standalone executable includes:

✅ Python runtime
✅ All Python packages (pydub, customtkinter, etc.)
✅ **ffmpeg binary** (via static-ffmpeg)
✅ Application code
✅ CustomTkinter themes and assets

**Users don't need to install:**
- Python
- pip
- pydub
- customtkinter
- ffmpeg

## How static-ffmpeg Works

The `static-ffmpeg` package provides platform-specific ffmpeg binaries:

```python
from staticffmpeg import run

# Automatically downloads and provides ffmpeg for current platform
ffmpeg_path, ffprobe_path = run.get_or_fetch_platform_executables_else_raise()

# Configure pydub to use bundled ffmpeg
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path
```

**Benefits:**
- No system ffmpeg installation required
- Works on systems without ffmpeg
- Consistent ffmpeg version across platforms
- No PATH configuration needed

**Platform Support:**
- macOS (Intel and Apple Silicon)
- Linux (x86_64, ARM)
- Windows (x86, x64)

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

**Solution:** Add missing module to `hiddenimports` in `M8_KitCreator.spec`:

```python
hiddenimports = [
    # ... existing imports ...
    'missing_module_name',
]
```

### "Cannot find ffmpeg"

**Solution 1:** Install static-ffmpeg:
```bash
pip install static-ffmpeg
```

**Solution 2:** If static-ffmpeg fails, install system ffmpeg:
```bash
# macOS
brew install ffmpeg

# Linux (Debian/Ubuntu)
sudo apt-get install ffmpeg

# Linux (Fedora/RHEL)
sudo dnf install ffmpeg
```

### Application too large

The bundled app is large (~100MB) because it includes:
- Python runtime (~40MB)
- Libraries (~30MB)
- ffmpeg binary (~30MB)

**To reduce size:**

1. **Use system ffmpeg instead** (removes ~30MB):
   - Don't install static-ffmpeg
   - Update spec file to exclude it
   - Users must install ffmpeg separately

2. **Enable UPX compression**:
   ```python
   # In M8_KitCreator.spec
   upx=True,
   ```
   Note: May cause issues on some systems

3. **Directory mode instead of one-file**:
   - Faster startup
   - Easier debugging
   - Slightly smaller total size

### macOS "App is damaged" error

**Cause:** macOS Gatekeeper blocking unsigned apps

**Solution:** Sign the application (requires Apple Developer account):

```bash
# Sign the app
codesign --deep --force --sign "Developer ID Application: Your Name" \
  dist/M8_KitCreator.app

# Notarize with Apple
xcrun notarytool submit dist/M8_KitCreator.dmg \
  --apple-id "your@email.com" \
  --team-id "TEAM_ID" \
  --password "app-specific-password" \
  --wait
```

**Temporary workaround** (for testing):
```bash
# Remove quarantine flag
xattr -cr dist/M8_KitCreator.app
```

### Linux dependencies missing

Some Linux distributions may need additional packages:

```bash
# Debian/Ubuntu
sudo apt-get install libxcb-xinerama0 libxkbcommon-x11-0

# Fedora/RHEL
sudo dnf install xcb-util-wm xcb-util-renderutil
```

## Testing the Build

### macOS

```bash
# Run the app
open dist/M8_KitCreator.app

# Check for errors in Console.app
# Filter by process: M8_KitCreator

# Test with sample files
open dist/M8_KitCreator.app
# Use GUI to select test WAV files
# Verify output WAV has correct cue points
```

### Linux

```bash
# Run the executable
./dist/M8_KitCreator

# Check console output for errors
# Test with sample files
./dist/M8_KitCreator
# Use GUI to select test WAV files
# Verify output WAV has correct cue points
```

## Distribution

### macOS

**Option 1: DMG Disk Image (Recommended)**
```bash
# Create DMG with create-dmg
create-dmg --volname "M8 Kit Creator" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  dist/M8_KitCreator.dmg \
  dist/M8_KitCreator.app

# Upload DMG to GitHub Releases
```

**Option 2: ZIP Archive**
```bash
cd dist
zip -r M8_KitCreator-macOS.zip M8_KitCreator.app
```

### Linux

**Tarball Archive:**
```bash
cd dist
tar -czf M8_KitCreator-linux-$(uname -m).tar.gz M8_KitCreator

# Upload to GitHub Releases
```

**AppImage** (advanced):
```bash
# Use appimagetool to create AppImage
# See: https://appimage.org/
```

## GitHub Releases

### Manual Release

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version (e.g., `v0.26.0`)
4. Upload build artifacts:
   - `M8_KitCreator.dmg` (macOS)
   - `M8_KitCreator-linux-x86_64.tar.gz` (Linux)
5. Add release notes
6. Publish release

### Automated Builds (GitHub Actions)

See `.github/workflows/build.yml` for automated builds on:
- Push to main branch
- New version tags
- Pull requests

## Version Information

Update version in these files before building:

1. `m8_kitcreator/__init__.py`:
   ```python
   __version__ = "0.26.0"
   ```

2. `M8_KitCreator.spec`:
   ```python
   'CFBundleShortVersionString': '0.26.0',
   'CFBundleVersion': '0.26.0',
   ```

3. `README.md`:
   ```markdown
   **Current Version:** v0.26.0
   ```

## Build Script Reference

### build.sh Commands

```bash
./build.sh build    # Build application (default)
./build.sh clean    # Remove build artifacts
./build.sh rebuild  # Clean then build
```

### Environment Variables

```bash
# Verbose output
VERBOSE=1 ./build.sh

# Skip UPX compression
UPX=0 pyinstaller M8_KitCreator.spec

# Custom PyInstaller options
PYINSTALLER_OPTS="--debug all" ./build.sh
```

## Further Reading

- [PyInstaller Documentation](https://pyinstaller.org/)
- [static-ffmpeg Documentation](https://github.com/zackees/static-ffmpeg-bin)
- [CustomTkinter PyInstaller Guide](https://github.com/TomSchimansky/CustomTkinter/wiki/Packaging)
- [Apple Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

## Support

For build issues:
1. Check this document's Troubleshooting section
2. Check [GitHub Issues](https://github.com/aTanguay/M8_KitCreator/issues)
3. Open a new issue with:
   - Platform and version
   - Python version
   - Build command used
   - Full error output
   - PyInstaller log files from `build/` directory
