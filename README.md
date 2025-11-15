# M8_KitCreator

A simple sliced audio file maker that creates files that are compatible with the M8. The idea here is to be able to take a selection of wav files and mash them into a sliced kit that the M8 likes.

## Installation

### Option 1: Download Standalone App (Recommended - No Python Required!)

**Coming Soon:** Download ready-to-run executables from [Releases](../../releases):
- **macOS**: `M8_KitCreator.dmg` - Just drag and drop to Applications!
- **Linux**: `M8_KitCreator-linux-x86_64.tar.gz` - Extract and run!

No Python, no pip, no dependencies needed - just download and run!

### Option 2: Run from Source (For Developers)

If you want to run from source or contribute:

1. **Install Python** 3.7 or later

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   This installs:
   - `pydub` - Audio processing
   - `customtkinter` - Modern UI
   - `static-ffmpeg` - Bundled ffmpeg (no system install needed!)

3. **Run the application:**
   ```bash
   python M8_KitBasher.py
   ```

### Building From Source

Want to create your own standalone executable? See [BUILD.md](BUILD.md) for complete instructions.

To use: You select your files, and the script puts them into one file, with markers (slices) at the start of each sample. It also throws out extra silence.

![interface](/images/app_022.png)

To install, grab the last version that's out there. Getting things set up is not my strong suit, but I'll try and add more install tips, as well as try and get it packed up into a Mac app. I got close, but not quite yet.

## What's New

**New in v0.27:** Progress bar and threading!
- **Visual progress feedback** - Real-time progress bar shows processing status
- **Responsive UI** - Background threading prevents UI freezing during processing
- **Status updates** - Shows which file is being processed (e.g., "Processing file 3 of 10...")
- **Better UX** - Buttons disabled during processing to prevent accidental clicks
- **Error handling** - Graceful error recovery with user-friendly messages

**New in v0.26:** Self-contained distribution!
- **No Python installation required** - Standalone executables for macOS and Linux
- **Bundled ffmpeg** - Uses `static-ffmpeg` package, no system ffmpeg needed
- **One-click builds** - Simple `./build.sh` script creates ready-to-distribute apps
- **PyInstaller configuration** - Professional build setup with M8_KitCreator.spec
- **Complete build documentation** - See BUILD.md for creating your own builds
- **~100MB executables** - Includes everything: Python runtime, libraries, and ffmpeg

**New in v0.25:** Modular architecture!
- Complete code refactoring into separate modules
- Clean separation of concerns: config, utils, audio processing, and GUI
- AudioProcessor can now be used without GUI (perfect for automation/CLI)
- Easier to test, maintain, and extend
- New package structure: `m8_kitcreator/` with dedicated modules
- Simple main entry point: `M8_KitBasher.py`

**New in v0.24:** Code quality improvements and validation!
- Input validation: Files are checked before processing to ensure they're valid WAV files
- Better error messages: Clear feedback when files can't be loaded or processed
- Constants extracted: All magic numbers moved to named constants at top of file
- Cleaner code: Duplicate variable names fixed, better documentation, proper docstrings
- Improved error handling: Specific error messages for different failure scenarios

**New in v0.23:** Stereo support! The app now preserves stereo files correctly. Previous versions forced mono conversion because the cue point calculation was using sample positions instead of frame positions. This has been fixed - cue points now use the correct frame-based positioning that works with any channel configuration (mono, stereo, or multi-channel). 

Here's the output:
![OceanAudio](/images/OceanShot.png)



