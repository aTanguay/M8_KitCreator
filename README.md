# M8_KitCreator

A modern, user-friendly tool for creating sliced audio kits compatible with the [Dirtywave M8](https://dirtywave.com/) hardware sampler and [Elektron Octatrack](https://www.elektron.se/products/octatrack-mkii/). Simply select your WAV files, choose your output format, and M8_KitCreator will intelligently combine them into a single file with perfectly positioned markers that your hardware recognizes as individual slices.

![M8 Kit Creator Interface](/images/app_022.png)

## Features

✨ **Easy to Use**
- Drag & drop WAV files directly onto the window
- Simple, clean interface with real-time progress feedback
- No audio engineering knowledge required
- Choose your output format: M8, Octatrack, or both!

🎵 **Smart Audio Processing**
- Automatic silence removal with configurable threshold (-50dBFS)
- Preserves stereo or mono audio (your choice!)
- Frame-accurate cue point positioning for perfect M8 compatibility
- Octatrack .ot metadata file generation for slice playback
- 1ms silent markers between samples for clean slicing

⚡ **Modern & Responsive**
- Real-time progress bar with file-by-file status updates
- Background processing keeps the UI responsive
- Visual drag-and-drop feedback
- Comprehensive file validation with helpful error messages

🔧 **Professional Quality**
- Self-contained executables (no Python installation needed!)
- Bundled ffmpeg - works out of the box
- Cross-platform: macOS and Linux support
- Modular codebase perfect for automation and scripting
- Support for multiple hardware samplers (M8 and Octatrack)

## Installation

### Option 1: Download Standalone App (Recommended)

**Coming Soon:** Download ready-to-run executables from [Releases](../../releases):

- **macOS**: `M8_KitCreator.dmg` - Just drag and drop to Applications!
- **Linux**: `M8_KitCreator-linux-x86_64.tar.gz` - Extract and run!

No Python, no pip, no dependencies needed - just download and run!

### Option 2: Run from Source (For Developers)

If you want to run from source or contribute to development:

1. **Install Python 3.7 or later**

2. **Clone this repository:**
   ```bash
   git clone https://github.com/aTanguay/M8_KitCreator.git
   cd M8_KitCreator
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `pydub` - Audio processing library
   - `customtkinter` - Modern UI framework
   - `tkinterdnd2` - Drag-and-drop support
   - `static-ffmpeg` - Bundled ffmpeg (no system install needed!)

4. **Run the application:**
   ```bash
   python M8_KitBasher.py
   ```

### Building From Source

Want to create your own standalone executable? See [BUILD.md](BUILD.md) for complete instructions on building distributable apps for macOS and Linux.

## How to Use

1. **Launch the application**

2. **Add your WAV files** using either method:
   - Click "Select Files" and choose your WAV files
   - Drag & drop WAV files directly onto the window

3. **Choose your output format** from the dropdown:
   - **M8**: Creates WAV file with cue points for Dirtywave M8
   - **Octatrack**: Creates WAV file with .ot metadata for Elektron Octatrack
   - **Both (M8 + Octatrack)**: Creates both formats at once

4. **Click "Merge"** to combine them

5. **Choose where to save** your kit

6. **Load the kit on your hardware** and start making music! 🎶

The app will automatically:
- Remove excess silence from each sample
- Add 1ms markers between samples
- Insert cue points (for M8) or generate .ot metadata (for Octatrack)
- Create files ready for your hardware sampler

### Tips

- Files are processed in the order they appear in the list
- The app preserves stereo or mono (configure in AudioProcessor if needed)
- Invalid WAV files are automatically skipped with error messages
- Progress bar shows real-time processing status

## What's New

**New in v0.30:** Elektron Octatrack support!
- **Multi-format output** - Choose between M8, Octatrack, or both formats
- **Octatrack .ot files** - Generates proper .ot metadata files for slice playback
- **Format selector dropdown** - Easy selection of output format
- **Dual export** - Create both M8 and Octatrack versions in one pass
- **Based on reverse-engineered format** - Uses the community-documented .ot file specification
- **832-byte binary format** - Proper tempo, trim, loop, and slice data for Octatrack

**New in v0.29:** File reordering controls!
- **Move Up/Down buttons** - Easily reorder files in your kit
- **Sort A-Z button** - Instantly alphabetize your file list
- **Numbered display** - Files now show as "1. filename.wav" for clarity
- **Selection tracking** - Move operations maintain your current selection

**New in v0.28:** Drag-and-drop file support!
- **Drag & drop files** - Simply drag WAV files directly onto the window
- **Visual feedback** - Listbox highlights in green when dragging files over
- **Smart validation** - Only accepts valid WAV files, shows errors for invalid files
- **Duplicate prevention** - Won't add the same file twice
- **Seamless integration** - Works alongside the "Select Files" button

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

**New in v0.25:** Modular architecture!
- Complete code refactoring into separate modules
- Clean separation of concerns: config, utils, audio processing, and GUI
- AudioProcessor can now be used without GUI (perfect for automation/CLI)
- Easier to test, maintain, and extend
- New package structure: `m8_kitcreator/` with dedicated modules

**New in v0.24:** Code quality improvements and validation!
- Input validation: Files are checked before processing
- Better error messages: Clear feedback when files can't be loaded
- Constants extracted: All magic numbers moved to named constants
- Cleaner code: Better documentation and proper docstrings

**New in v0.23:** Stereo support!
- The app now preserves stereo files correctly
- Fixed cue point calculation to use frame positions instead of sample positions
- Works with mono, stereo, or multi-channel audio

## Technical Details

### Audio Processing Parameters

- **Marker Duration:** 1ms silent markers between samples
- **Silence Threshold:** -50.0 dBFS (configurable)
- **Minimum Silence Length:** 10ms
- **Retained Silence:** 1ms between chunks
- **Cue Point Format:** WAV standard cue chunks with frame-based positioning

### Hardware Compatibility

**M8 Compatibility:**
The output WAV files are fully compatible with the Dirtywave M8's slice/kit functionality. The cue chunks follow the WAV standard and use frame-based positioning to ensure correct slice alignment regardless of channel configuration.

**Octatrack Compatibility:**
The .ot metadata files follow the reverse-engineered Elektron Octatrack format (832-byte binary specification). Each .ot file contains:
- Tempo information (BPM)
- Trim and loop lengths
- Up to 64 slice positions with start/end/loop points
- Gain, stretch, and quantization settings
- 16-bit checksum for validation

The .ot file is generated alongside the WAV file and should be placed in the same directory on your Octatrack's CF card.

### Output Example

Here's what the processed output looks like in an audio editor (showing cue markers):

![Audio Output with Cue Markers](/images/OceanShot.png)

Each vertical line represents a cue point that the M8 uses to identify slice boundaries.

## Project Structure

```
M8_KitCreator/
├── M8_KitBasher.py          # Main entry point
├── m8_kitcreator/           # Core package
│   ├── config.py           # Configuration constants
│   ├── utils.py            # Validation and helper functions
│   ├── audio_processor.py  # Audio processing logic
│   ├── octatrack_writer.py # Octatrack .ot file generation
│   └── gui.py              # User interface
├── requirements.txt         # Python dependencies
├── BUILD.md                # Build instructions
├── CLAUDE.md               # AI assistant development guide
└── TASKS.md                # Future improvements roadmap
```

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with details about what went wrong
2. **Suggest features** - Check [TASKS.md](TASKS.md) for planned features or suggest new ones
3. **Submit pull requests** - Fork, make changes, and submit a PR
4. **Improve documentation** - Help make the docs clearer and more comprehensive

### Development

The codebase uses a modular architecture with clear separation of concerns:
- `config.py` - All constants and configuration
- `utils.py` - Pure helper functions (easy to test)
- `audio_processor.py` - Audio processing business logic (framework-agnostic)
- `octatrack_writer.py` - Octatrack .ot file generation (independent module)
- `gui.py` - User interface (can be swapped with CLI or web interface)

See [CLAUDE.md](CLAUDE.md) for comprehensive development documentation.

## Support

- **Issues:** [GitHub Issues](https://github.com/aTanguay/M8_KitCreator/issues)
- **M8 Community:** [Dirtywave Discord](https://discord.gg/WEavjFNYHh)
- **Documentation:** Check the [BUILD.md](BUILD.md) and [CLAUDE.md](CLAUDE.md) files

## License

MIT License - See [LICENSE](LICENSE) file for details

Copyright © 2023-2025 Andy Tanguay

## Acknowledgments

- Built for the amazing [Dirtywave M8](https://dirtywave.com/) and [Elektron Octatrack](https://www.elektron.se/) communities
- Uses [pydub](https://github.com/jiaaro/pydub) for audio processing
- UI powered by [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- Drag-and-drop via [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2)
- Octatrack .ot format based on reverse-engineering work by [OctaChainer](https://github.com/KaiDrange/OctaChainer) and the Elektronauts community

---

**Made with ❤️ for M8 and Octatrack music makers**
