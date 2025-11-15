# CLAUDE.md - AI Assistant Guide for M8_KitCreator

## Project Overview

**M8_KitCreator** (also known as M8_KitBasher) is a Python GUI application that creates sliced WAV audio kits compatible with the Dirtywave M8 hardware sampler. The tool takes multiple WAV files, concatenates them with markers (cue points), removes excess silence, and outputs a single WAV file that the M8 can use as a sliced instrument.

**Current Version:** 0.24 (M8_KitBasher_0.24.py)
**Language:** Python 3.x
**Author:** Andy Tanguay
**License:** MIT
**Repository:** https://github.com/aTanguay/M8_KitCreator

### Core Functionality

- Select multiple WAV files via GUI
- Concatenate files with 1ms silent markers between each sample
- Remove silence from audio (configurable threshold: -50dBFS, min 10ms)
- **Preserve stereo or mono** (v0.23+) - Correctly calculates cue points for any channel count
- Insert WAV cue chunks at the start of each sample slice
- Export single WAV file ready for M8 import

## Codebase Structure

### Directory Layout

```
M8_KitCreator/
├── M8_KitBasher_0.24.py          # LATEST - Refactored with validation and clean code
├── setup.py                      # py2app macOS bundling config
├── README.md                     # User-facing documentation
├── CLAUDE.md                     # AI assistant guide (this file)
├── TASKS.md                      # Improvement tasks and roadmap
├── STEREO_FIX_ANALYSIS.md       # Technical analysis of stereo fix
├── LICENSE                       # MIT license
├── Records_01.png                # Documentation screenshot
├── versions/                     # ALL archived versions and prototypes
│   ├── M8_KitBasher.py          # Original/legacy version
│   ├── M8_KitBasher_0.01.py     # Initial version with sine wave markers
│   ├── M8_KitBasher_0.07.py     # Historical version
│   ├── M8_KitBasher_0.08.py     # Historical version
│   ├── M8_KitBasher_0.09.py     # Historical version
│   ├── M8_KitBasher_0.10.py     # Historical version
│   ├── M8_KitBasher_0.11.py     # First cue point implementation
│   ├── M8_KitBasher_0.12.py     # Historical version
│   ├── M8_KitBasher_0.13.py     # Without mono (broken markers)
│   ├── M8_KitBasher_0.14.py     # First version with mono fix
│   ├── M8_KitBasher_0.20.py     # First customtkinter version
│   ├── M8_KitBasher_0.21.py     # Previous version with error handling
│   ├── M8_KitBasher_0.22.py     # Mono only version
│   ├── M8_KitBasher_0.23.py     # Stereo support added
│   ├── InterfaceTest_01.py      # UI prototype experiment
│   ├── InterfaceTest_02.py      # UI prototype experiment
│   └── InterfaceTest_03.py      # UI prototype experiment
└── images/                       # Documentation images
    ├── app_022.png              # Application screenshot
    └── OceanShot.png            # Output waveform example
```

### Key Files Reference

- **Primary file:** `M8_KitBasher_0.24.py` - Always use this as the main reference (root directory)
- **Setup file:** `setup.py` - For macOS app bundling (currently incomplete)
- **Archives:** `versions/` folder contains ALL historical implementations and UI prototypes (17 versions)
- **Analysis docs:** `STEREO_FIX_ANALYSIS.md` explains the stereo cue point fix in detail

## Architecture

### Main Components

#### 1. FileSelectorApp Class (GUI)
**Location:** M8_KitBasher_0.22.py:10-181

Main application class inheriting from `tk.Tk`:

```python
class FileSelectorApp(tk.Tk):
    def __init__(self):
        # Initialize UI with customtkinter widgets
        # Manage two parallel lists: file_names and file_paths

    def select_files(self):    # Open file dialog, update listbox
    def clear_files(self):     # Clear selection
    def merge_files(self):     # Process and export
    def close_app(self):       # Exit application
```

**State Management:**
- `self.file_names` - List of display names (basenames only)
- `self.file_paths` - List of full file paths for processing

#### 2. concatenate_audio_files() Function (Audio Processing)
**Location:** M8_KitBasher_0.22.py:13-90

Standalone function that handles all audio processing:

```python
def concatenate_audio_files(file_names, output_file,
                           marker_duration_ms=1,
                           silence_thresh=-50.0,
                           min_silence_len=10,
                           retained_silence=1):
```

**Processing Pipeline:**
1. Create 1ms silent markers
2. Load each WAV file
3. **Convert to mono** (critical for correct cue positioning)
4. Split on silence (remove quiet sections)
5. Concatenate with markers
6. Export WAV file
7. Re-open and insert cue chunk with marker positions

### Technology Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| GUI Framework | tkinter | Base windowing system (stdlib) |
| Modern UI | customtkinter | Styled buttons, frames, labels |
| Audio Processing | pydub | Load, concatenate, export audio |
| Silence Detection | pydub.silence | split_on_silence() function |
| WAV Manipulation | wave | Low-level WAV file operations |
| Binary Packing | struct | Build cue chunk byte data |
| File Dialogs | tkinter.filedialog | File/folder selection |
| Message Boxes | tkinter.messagebox | User notifications |

### Dependencies

**Required Packages:**
```bash
pip install pydub customtkinter
```

**System Requirements:**
- Python 3.x
- tkinter (usually bundled with Python)
- ffmpeg or libav (required by pydub for audio processing)

## Development Conventions

### Version Numbering

**Format:** `M8_KitBasher_X.YY.py` where X.YY is the version number

**Versioning Strategy:**
- Sequential minor versions: 0.01, 0.07, 0.08, ..., 0.14
- Jump to 0.20 for major UI overhaul (customtkinter introduction)
- Current: 0.22
- **Keep old versions:** Move to `versions/` folder when archived
- **Keep recent versions:** Last 4-5 versions in root directory for reference

### Code Style

**Observed Patterns:**
- 4-space indentation
- Snake_case for functions and variables
- PascalCase for class names
- Descriptive variable names (`concatenated_audio`, `cue_positions`)
- Inline comments for complex operations
- Print statements for debugging and user feedback

**UI Layout Style:**
```python
# Hybrid approach: customtkinter for modern widgets, tkinter for Listbox
label = ctk.CTkLabel(self, text="...", font=("Arial", 16))
button = ctk.CTkButton(frame, text="...", command=self.method)
listbox = tk.Listbox(frame, width=30, height=16)  # tkinter fallback
```

### File Organization

**Principle:** Keep root directory clean, archive all old versions

- **Latest version only in root:** `M8_KitBasher_0.24.py` (always run this)
- **All archived versions in `versions/`:** Complete history from 0.01 to 0.23
- **UI prototypes archived:** `InterfaceTest_XX.py` files in `versions/` folder
- **Original version archived:** `M8_KitBasher.py` (legacy) in `versions/` folder

**New file versioning workflow:**
1. When creating a new version (e.g., 0.23), copy current latest to new filename
2. Make changes in new file
3. Test thoroughly
4. Move old latest (0.22) to `versions/` folder
5. New version becomes the only .py file in root

### Error Handling Pattern

**Current Approach (v0.21+):**
```python
try:
    concatenated_audio.export(output_file, format="wav")
    print("Audio exported successfully!")
except Exception as e:
    print(f"Error exporting audio: {e}")
    messagebox.showerror("Error", f"Failed to export audio: {e}")
```

**Characteristics:**
- Broad exception catching (all Exception types)
- User-facing error dialogs (messagebox.showerror)
- Developer console logging (print statements)
- Graceful degradation (show error, don't crash)

**Current Limitations:**
- No input validation (assumes selected files are valid WAVs)
- No pre-flight checks for write permissions
- No validation of output path
- Cue point writing lacks error handling

### Git Workflow

**Branch Strategy:**
- Main development branch: `main` (or master)
- Feature branches: Use `claude/` prefix for AI-generated branches
- Current branch: `claude/claude-md-mhzto2cviwzmd8my-01USoPoJ71gKPDgnWKirnzYg`

**Commit Message Style:**
```
Update README.md
UI Tweaks and error handling
Added images
```
- Descriptive but informal
- Focus on what changed, not why
- Short, single-line messages

**Push Protocol:**
```bash
git push -u origin claude/claude-md-XXXXXXXXX-YYYYYYYY
```
- Always use `-u` flag for branch tracking
- Retry up to 4 times on network errors (2s, 4s, 8s, 16s backoff)

## Key Technical Details

### Audio Processing Parameters

**Hardcoded Constants:**
```python
MARKER_DURATION_MS = 1        # Silent marker between slices
SILENCE_THRESH = -50.0        # dBFS threshold for silence detection
MIN_SILENCE_LEN = 10          # Minimum silence length in ms
RETAINED_SILENCE = 1          # Silence to keep between chunks in ms
```

**Critical Operation - Mono Conversion:**
```python
audio = audio.set_channels(1)  # REQUIRED for correct cue positioning
```

**Why mono is required:** Unknown root cause, but stereo files result in incorrect cue point positions. This is a known limitation documented in the README.

### WAV Cue Chunk Format

**Structure:** Uses low-level `struct.pack()` to build binary WAV chunks

```python
# Cue chunk format
cue_chunk_data = struct.pack('<4sL', b'cue ', len(cue_positions) * 24 + 4)
cue_chunk_data += struct.pack('<L', len(cue_positions))

# Each cue point
for i, pos in enumerate(cue_positions):
    cue_chunk_data += struct.pack('<LL4sLLL',
                                   i,           # Cue point ID
                                   pos,         # Sample position
                                   b'data',     # Chunk ID
                                   0,           # Chunk start
                                   0,           # Block start
                                   pos)         # Sample offset
```

**Direct file writing:**
```python
wav_file._file.write(cue_chunk_data)  # Uses private attribute _file
```
**Note:** This is technically fragile but works with current Python `wave` module.

## Known Issues and Limitations

### 1. Mono Conversion Requirement
**Issue:** Files must be converted to mono for correct cue point positioning
**Impact:** Loss of stereo information
**Status:** Accepted limitation (documented in README)
**Reference:** v0.13 vs v0.14 comparison

### 2. No Input Validation
**Issue:** No checks that selected files are valid WAV files
**Impact:** Crashes or errors on non-WAV files
**Workaround:** User responsibility to select correct files

### 3. Hardcoded Parameters
**Issue:** No user control over silence detection thresholds
**Impact:** May not work well for all audio material
**Potential improvement:** Add settings UI panel

### 4. No Progress Indication
**Issue:** Long operations appear frozen (no progress bar)
**Impact:** Poor UX for large file sets
**Workaround:** Console prints provide some feedback

### 5. Incomplete macOS App Bundling
**Issue:** setup.py configured but not fully working
**Status:** "got close, but not quite yet" (per README)
**Current deployment:** Users must install Python + dependencies

### 6. Private Attribute Access
**Issue:** Uses `wave._file.write()` (private attribute)
**Impact:** May break in future Python versions
**Risk:** Low (wave module is stable)

## Common Development Tasks

### Running the Application

```bash
# Ensure dependencies are installed
pip install pydub customtkinter

# Run the latest version
python M8_KitBasher_0.22.py
```

### Creating a New Version

**When to increment version:**
- Bug fixes: Increment by 0.01 (e.g., 0.22 → 0.23)
- New features: Increment by 0.10 (e.g., 0.22 → 0.30)
- Major changes: Increment to next integer (e.g., 0.22 → 1.00)

**Process:**
1. Copy current version: `cp M8_KitBasher_0.22.py M8_KitBasher_0.23.py`
2. Make changes in new file
3. Test thoroughly
4. Update README.md with new version number
5. **Archive old version:** `git mv M8_KitBasher_0.22.py versions/`
6. Commit changes:
   ```bash
   git add M8_KitBasher_0.23.py README.md versions/M8_KitBasher_0.22.py
   git commit -m "Version 0.23: [description of changes]"
   git push -u origin [branch-name]
   ```

**Important:** Always move the previous version to `versions/` folder to keep root directory clean. Only the latest version should remain in root.

### Testing Changes

**Manual Testing Checklist:**
1. Launch application - verify window appears correctly (350x510)
2. Click "Select Files" - verify file dialog opens
3. Select multiple WAV files - verify they appear in listbox
4. Click "Clear Files" - verify listbox clears
5. Re-select files
6. Click "Merge" - verify save dialog appears
7. Save file - verify success message appears
8. Open output in audio editor (e.g., Audacity, Ocenaudio)
9. Verify cue markers appear at start of each sample
10. Import to M8 hardware - verify slices work correctly

**Test Cases:**
- Single file processing
- Multiple files (2-10 files)
- Large file sets (50+ files)
- Files with varying sample rates (22050, 44100, 48000 Hz)
- Files with silence vs. without
- Very short files (<1 second)
- Long files (>1 minute)

### Adding Features

**UI Changes:**
- Modify `FileSelectorApp.__init__()` to add new widgets
- Use customtkinter components for consistency: `ctk.CTkButton`, `ctk.CTkFrame`, `ctk.CTkLabel`
- Maintain window size: 350x510 unless redesigning layout
- Add command handlers as class methods

**Audio Processing Changes:**
- Modify `concatenate_audio_files()` function
- Add new parameters with sensible defaults
- Preserve backward compatibility where possible
- Add error handling with try/except + messagebox.showerror

**Example - Adding a Progress Bar:**
```python
# In __init__
self.progress = ctk.CTkProgressBar(self, width=300)
self.progress.pack(pady=10)
self.progress.set(0)

# In merge_files (before processing)
self.progress.set(0)

# In concatenate_audio_files (pass progress callback)
for i, file in enumerate(file_names):
    # ... processing ...
    if progress_callback:
        progress_callback(i / len(file_names))
```

### Debugging

**Common Issues:**

1. **"No module named 'customtkinter'"**
   - Solution: `pip install customtkinter`

2. **"No module named 'pydub'"**
   - Solution: `pip install pydub`

3. **"Couldn't find ffmpeg or libav"**
   - Solution: Install ffmpeg
   - macOS: `brew install ffmpeg`
   - Linux: `apt-get install ffmpeg` or `yum install ffmpeg`
   - Windows: Download from ffmpeg.org

4. **Cue markers in wrong positions**
   - Verify mono conversion is happening: `audio = audio.set_channels(1)`
   - Check that marker_duration_ms is being added correctly

5. **Application window doesn't appear**
   - Check tkinter installation: `python -m tkinter`
   - Verify display environment (DISPLAY variable on Linux)

**Debug Mode:**
Add verbose logging to concatenate_audio_files:
```python
print(f"Processing file {i+1}/{len(file_names)}: {file}")
print(f"Audio duration: {len(audio)}ms, Chunks: {len(chunks)}")
print(f"Cue position {i}: {len(concatenated_audio)} samples")
```

## AI Assistant Guidelines

### When Analyzing This Codebase

1. **Always reference the latest version** (M8_KitBasher_0.22.py) unless specifically asked about version history
2. **Understand the mono conversion requirement** - don't suggest removing it without understanding the cue positioning issue
3. **Preserve backward compatibility** - many users may have older versions
4. **Test audio processing changes carefully** - incorrect cue points break M8 compatibility
5. **Maintain simplicity** - this is a focused tool, not a full-featured audio editor

### When Making Changes

1. **Create new version file** - don't overwrite existing working versions
2. **Increment version number appropriately** - follow the established pattern
3. **Add error handling** - use try/except with messagebox.showerror
4. **Maintain UI consistency** - keep customtkinter style and 350x510 window size
5. **Update README.md** - reflect version changes and new features
6. **Test with real M8 hardware if possible** - or at minimum verify cue points in audio editor
7. **Document known issues** - be transparent about limitations

### When Answering Questions

1. **Check version context** - user may be running older version
2. **Reference specific line numbers** - format: `M8_KitBasher_0.22.py:75`
3. **Explain audio processing steps** - users may not understand DSP concepts
4. **Provide installation help** - many users struggle with Python setup
5. **Link to M8 documentation** - context about the M8 hardware helps

### Code Review Checklist

Before committing changes, verify:

- [ ] Version number incremented in filename
- [ ] All imports present and correct
- [ ] Error handling added for new operations
- [ ] UI elements use customtkinter (ctk) components
- [ ] Mono conversion preserved in audio processing
- [ ] Cue point calculation logic intact
- [ ] Print statements for user feedback
- [ ] Success/error messageboxes for important operations
- [ ] File paths handled with os.path
- [ ] No hardcoded absolute paths
- [ ] README.md updated with version number
- [ ] Code tested with multiple WAV files
- [ ] Output verified in audio editor

## Build and Distribution

### Current Status
- **Goal:** Standalone macOS app bundle
- **Tool:** py2app
- **Status:** Incomplete ("got close, but not quite yet")
- **Blocker:** Unknown (likely signing or dependency bundling)

### setup.py Configuration

```python
APP = ['M8_KitBasher_0.22.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pydub', 'customtkinter'],
}
setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### Building macOS App (Experimental)

```bash
# Install py2app
pip install py2app

# Clean previous builds
rm -rf build dist

# Build app
python setup.py py2app

# Test
open dist/M8_KitBasher_0.22.app
```

**Known Issues:**
- May fail to bundle ffmpeg (required by pydub)
- Signing may be required for distribution
- Large app size due to dependencies

### Alternative Distribution

**Recommended for now:**
1. Provide Python script directly
2. Include clear installation instructions in README
3. Consider Docker container for Linux users
4. Investigate PyInstaller as alternative to py2app

## Resources

### M8 Documentation
- [Dirtywave M8 Manual](https://dirtywave.com/pages/manual) - Understanding slice/kit requirements
- M8 WAV specifications: 16-bit, mono/stereo, various sample rates

### Audio Processing
- [pydub Documentation](https://github.com/jiaaro/pydub) - Audio manipulation
- [WAV Format Specification](http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html) - Understanding cue chunks
- [customtkinter Documentation](https://github.com/TomSchimansky/CustomTkinter) - Modern UI widgets

### Python Packaging
- [py2app Documentation](https://py2app.readthedocs.io/) - macOS app bundling
- [PyInstaller](https://pyinstaller.org/) - Alternative bundling tool

## Version History Summary

| Version | Lines | Key Changes |
|---------|-------|-------------|
| 0.01 | 52 | Initial version with sine wave markers |
| 0.11 | - | First cue point implementation |
| 0.13 | 76 | Without mono conversion (broken markers) |
| 0.14 | 75 | Added mono conversion fix |
| 0.20 | 140 | Major UI overhaul with customtkinter |
| 0.21 | 156 | Added error handling |
| 0.22 | 181 | UI polish, 350x510 window, Exit button |

## Contact and Contribution

**Author:** Andy Tanguay
**Repository:** https://github.com/aTanguay/M8_KitCreator
**License:** MIT

**Contributing:**
- Fork repository
- Create feature branch
- Make changes following conventions above
- Test thoroughly (especially cue point positioning)
- Submit pull request with clear description
- Reference issue number if applicable

---

**Last Updated:** 2025-11-15 (Repository reorganization - all old versions archived)
**Analyzed Version:** M8_KitBasher_0.22.py
**Document Version:** 1.1
