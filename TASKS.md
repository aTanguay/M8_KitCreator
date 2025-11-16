# M8_KitCreator - Improvement Tasks

This document outlines improvements, refactoring tasks, and distribution strategies for the M8_KitCreator application.

**Current Status:** Working prototype with known limitations
**Goal:** Production-ready, easily distributable application

---

## Priority 1: Code Quality & Cleanup

### TASK-001: Fix Code Quality Issues
**Priority:** HIGH | **Effort:** 1-2 hours | **Impact:** HIGH

**Problems identified:**
- Duplicate variable names (`title_label` used 3x on lines 31, 33, 56)
- Commented-out old code (line 155)
- Unnecessary assumption comments (lines 38, 52, 60, 67)
- Inconsistent spacing and formatting
- Magic numbers scattered throughout

**Actions:**
- [ ] Rename UI elements uniquely (`title_label`, `subtitle_label`, `filelist_label`)
- [ ] Remove commented-out code (line 155: "OLD CODE")
- [ ] Remove assumption comments about customtkinter (they're no longer needed)
- [ ] Extract all magic numbers to constants at top of file
- [ ] Add proper docstrings to all functions and class methods
- [ ] Run code through formatter (black or autopep8)

**Example constants to add:**
```python
# UI Configuration
WINDOW_WIDTH = 350
WINDOW_HEIGHT = 510
WINDOW_TITLE = "ConcateM8"
LISTBOX_WIDTH = 30
LISTBOX_HEIGHT = 16

# Audio Processing
DEFAULT_MARKER_DURATION_MS = 1
DEFAULT_SILENCE_THRESHOLD = -50.0
DEFAULT_MIN_SILENCE_LEN = 10
DEFAULT_RETAINED_SILENCE = 1
```

---

### TASK-002: Separate Concerns (Refactor Architecture)
**Priority:** HIGH | **Effort:** 3-4 hours | **Impact:** HIGH

**Problems:**
- All code in one file (UI + audio processing)
- FileSelectorApp class mixes UI and business logic
- Hard to test, hard to maintain

**Actions:**
- [ ] Create modular file structure:
  ```
  M8_KitCreator/
  ├── m8_kitcreator/
  │   ├── __init__.py
  │   ├── audio_processor.py    # Audio processing logic
  │   ├── gui.py                # GUI components
  │   ├── config.py             # Configuration constants
  │   └── utils.py              # Helper functions
  ├── M8_KitBasher.py           # Main entry point (imports from package)
  ├── tests/
  │   ├── test_audio_processor.py
  │   └── test_utils.py
  └── ...
  ```
- [ ] Move `concatenate_audio_files()` to `audio_processor.py` as a class
- [ ] Create `AudioProcessor` class with methods for each processing step
- [ ] Move all constants to `config.py`
- [ ] Keep only GUI code in `gui.py`
- [ ] Update main script to import from package

**Benefits:**
- Easier to test
- Easier to maintain
- Clearer separation of concerns
- Can use audio processor in CLI or other interfaces

---

### TASK-003: Add Input Validation
**Priority:** HIGH | **Effort:** 2-3 hours | **Impact:** HIGH

**Problems:**
- No validation that selected files are actually WAV files
- No check for file readability
- No check for write permissions
- No validation of audio file properties (sample rate, bit depth)
- Can crash with corrupted or invalid files

**Actions:**
- [ ] Add file extension validation (`.wav` only)
- [ ] Add WAV header validation before processing
- [ ] Check file read permissions before adding to list
- [ ] Check output directory write permissions before merge
- [ ] Validate audio properties (sample rate, bit depth, channels)
- [ ] Show user-friendly error messages for invalid files
- [ ] Add file size limits (warn if total size > 100MB)
- [ ] Prevent duplicate files in selection

**Example validation:**
```python
def validate_wav_file(filepath):
    """Validate that file is a readable WAV file."""
    if not filepath.lower().endswith('.wav'):
        return False, "File must be a WAV file"

    if not os.path.isfile(filepath):
        return False, "File does not exist"

    if not os.access(filepath, os.R_OK):
        return False, "Cannot read file (permission denied)"

    try:
        with wave.open(filepath, 'rb') as wf:
            params = wf.getparams()
            # Validate sample rate, channels, etc.
    except Exception as e:
        return False, f"Invalid WAV file: {e}"

    return True, "Valid"
```

---

### TASK-004: Improve Error Handling
**Priority:** HIGH | **Effort:** 2 hours | **Impact:** MEDIUM

**Problems:**
- Broad exception catching (`except Exception`)
- Cue point writing has no error handling (line 158-173)
- No graceful handling of out-of-memory errors
- No handling of disk space issues

**Actions:**
- [ ] Add specific exception types instead of broad `Exception`
- [ ] Wrap cue point writing in try/except
- [ ] Add disk space check before processing
- [ ] Add memory check for large files
- [ ] Create custom exceptions (`InvalidWavFileError`, `ProcessingError`)
- [ ] Add error logging to file (not just console)
- [ ] Show detailed error messages with recovery suggestions

---

### TASK-005: Fix Typo in Header Comment
**Priority:** LOW | **Effort:** 1 minute | **Impact:** LOW

**Problem:**
- Line 14: "OCtober" should be "October"

**Action:**
- [ ] Fix typo: `Written on October 2023`

---

## Priority 2: User Experience Improvements

### TASK-006: Add Progress Indication
**Priority:** MEDIUM | **Effort:** 2-3 hours | **Impact:** HIGH

**Problem:**
- Long operations appear frozen
- No feedback during processing
- Users don't know if app is working or crashed

**Actions:**
- [ ] Add progress bar (customtkinter has CTkProgressBar)
- [ ] Show current file being processed
- [ ] Show percentage complete
- [ ] Add "Processing..." status label
- [ ] Disable buttons during processing
- [ ] Add threading to prevent UI freeze
- [ ] Show estimated time remaining

**Example:**
```python
import threading

def merge_files_threaded(self):
    """Run merge in background thread."""
    self.progress_bar.set(0)
    self.status_label.configure(text="Processing...")
    self.merge_button.configure(state="disabled")

    def process():
        try:
            concatenate_audio_files(
                self.file_paths,
                output_file,
                progress_callback=self.update_progress
            )
        finally:
            self.merge_button.configure(state="normal")
            self.progress_bar.set(0)

    thread = threading.Thread(target=process)
    thread.start()
```

---

### TASK-007: Add User Configuration Options
**Priority:** MEDIUM | **Effort:** 3-4 hours | **Impact:** MEDIUM

**Problem:**
- All processing parameters are hardcoded
- Users can't adjust silence detection threshold
- No control over mono conversion behavior

**Actions:**
- [ ] Add "Settings" or "Advanced" panel
- [ ] Make silence threshold adjustable (-60dB to -30dB slider)
- [ ] Make minimum silence length adjustable (1-100ms)
- [ ] Add option to skip silence removal entirely
- [ ] Add option to preserve stereo (with warning about cue points)
- [ ] Save user preferences to config file (JSON or INI)
- [ ] Add "Reset to Defaults" button
- [ ] Show tooltip help for each setting

---

### TASK-008: Add Drag-and-Drop Support
**Priority:** MEDIUM | **Effort:** 2 hours | **Impact:** MEDIUM

**Problem:**
- Users must click "Select Files" button
- No drag-and-drop functionality

**Actions:**
- [ ] Add drag-and-drop to listbox area
- [ ] Show visual feedback when dragging files over window
- [ ] Validate dropped files (WAV only)
- [ ] Add dropped files to existing selection (or replace based on setting)

---

### TASK-009: Add File Reordering
**Priority:** LOW | **Effort:** 2-3 hours | **Impact:** LOW

**Problem:**
- Files are processed in selection order
- No way to reorder files after selection

**Actions:**
- [ ] Add "Move Up" / "Move Down" buttons
- [ ] Add drag-to-reorder in listbox
- [ ] Add "Sort Alphabetically" button
- [ ] Show file numbers (1, 2, 3...) in listbox

---

### TASK-010: Add Audio Preview Functionality
**Priority:** MEDIUM | **Effort:** 2-3 hours | **Impact:** HIGH

**User Request:** "I'd like to preview what the kit is going to sound like before making the final WAV."

**Proposed Features:**
1. **Per-file preview** - Double-click a file in the list to hear it with silence trimming applied
2. **Full kit preview** - Play all trimmed samples in sequence to hear the complete output

**Implementation Details:**

**Dependencies:**
- Add `simpleaudio` package for lightweight audio playback
- Uses existing trimming logic from `utils.calculate_trimmed_duration()`

**UI Changes:**
- Option A (Simple): Double-click file to preview, add "Preview Full Kit" button
- Option B (Rich): Add "▶" play buttons inline with each file, playback progress bar, volume control
- Recommendation: Start with Option A for simplicity

**Code Changes:**
- [ ] Add `simpleaudio` to requirements.txt
- [ ] Create `preview_trimmed_audio()` function in utils.py
- [ ] Create `preview_full_kit()` function in utils.py
- [ ] Add double-click event handler to file listbox in gui.py
- [ ] Add "Preview Full Kit" button to GUI
- [ ] Add "⏸ Stop Preview" button (shown during playback)
- [ ] Use threading to prevent UI freeze during playback
- [ ] Handle playback errors gracefully

**Example Implementation:**
```python
# In utils.py
def preview_trimmed_audio(file_path, silence_thresh=-50.0, min_silence_len=10):
    """Load, trim silence, and play audio preview."""
    import simpleaudio as sa
    audio = AudioSegment.from_wav(file_path)
    chunks = split_on_silence(audio, silence_thresh=silence_thresh, min_silence_len=min_silence_len)
    if chunks:
        trimmed = sum(chunks, AudioSegment.empty())
    else:
        trimmed = audio
    playback = sa.play_buffer(
        trimmed.raw_data,
        num_channels=trimmed.channels,
        bytes_per_sample=trimmed.sample_width,
        sample_rate=trimmed.frame_rate
    )
    return playback  # Caller can use playback.stop()

def preview_full_kit(file_paths, silence_thresh=-50.0, min_silence_len=10, retained_silence=1):
    """Preview all files concatenated with trimming applied."""
    # Similar to AudioProcessor but just plays instead of exporting
```

**Testing:**
- [ ] Test with mono and stereo files
- [ ] Test with various sample rates
- [ ] Test stop functionality
- [ ] Test multiple rapid clicks (prevent overlapping playback)
- [ ] Test on macOS and Linux

---

## Priority 3: Distribution & Packaging

### TASK-011: Cross-Platform Distribution with PyInstaller
**Priority:** HIGH | **Effort:** 4-6 hours | **Impact:** CRITICAL

**Problem:**
- Current py2app setup only works for macOS
- Users must install Python + dependencies
- Incomplete even for macOS ("got close, but not quite yet")

**Solution: Use PyInstaller (cross-platform)**

**Actions:**
- [ ] Install PyInstaller: `pip install pyinstaller`
- [ ] Create PyInstaller spec file
- [ ] Bundle ffmpeg binary (required by pydub)
- [ ] Test on macOS (create .app bundle)
- [ ] Test on Linux (create standalone executable)
- [ ] Add application icon
- [ ] Configure one-file mode for easier distribution
- [ ] Test on clean systems without Python installed

**Create `M8_KitCreator.spec`:**
```python
# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect customtkinter data files
datas = collect_data_files('customtkinter')

# Add ffmpeg binary
if sys.platform == 'darwin':
    ffmpeg_path = '/usr/local/bin/ffmpeg'  # Homebrew path
elif sys.platform.startswith('linux'):
    ffmpeg_path = '/usr/bin/ffmpeg'
else:
    ffmpeg_path = None

binaries = []
if ffmpeg_path:
    binaries.append((ffmpeg_path, '.'))

a = Analysis(
    ['M8_KitBasher_0.22.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['pydub', 'customtkinter', 'PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='M8_KitCreator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.icns',  # Add icon file
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='M8_KitCreator.app',
        icon='icon.icns',
        bundle_identifier='com.andytanguay.m8kitcreator',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
        },
    )
```

**Build commands:**
```bash
# macOS
pyinstaller M8_KitCreator.spec
# Output: dist/M8_KitCreator.app

# Linux
pyinstaller M8_KitCreator.spec
# Output: dist/M8_KitCreator
```

---

### TASK-012: Bundle ffmpeg Binary
**Priority:** HIGH | **Effort:** 3-4 hours | **Impact:** CRITICAL

**Problem:**
- pydub requires ffmpeg or libav
- Users must install separately
- Biggest barrier to "just works" distribution

**Solutions:**

**Option A: Bundle static ffmpeg binary**
- [ ] Download static ffmpeg builds for macOS/Linux
- [ ] Include in `binaries/` folder
- [ ] Configure pydub to use bundled ffmpeg
- [ ] Update PyInstaller spec to include binary
- [ ] Test that bundled version works

**Option B: Use pydub alternatives**
- [ ] Replace pydub with `soundfile` + `scipy` (pure Python, no ffmpeg)
- [ ] Rewrite audio processing to use wave module only
- [ ] Trade-off: More code but fewer dependencies

**Option C: Use static-ffmpeg Python package**
```bash
pip install static-ffmpeg
```
```python
from static_ffmpeg import run
AudioSegment.converter = run.get_or_fetch_platform_executables_else_raise()[0]
```

**Recommended: Option C** (easiest, most maintainable)

---

### TASK-013: Create GitHub Releases with Pre-built Binaries
**Priority:** MEDIUM | **Effort:** 2-3 hours | **Impact:** HIGH

**Actions:**
- [ ] Create GitHub Actions workflow for automated builds
- [ ] Build for macOS (Intel + Apple Silicon)
- [ ] Build for Linux (x86_64)
- [ ] Create release artifacts (.zip, .dmg, .AppImage)
- [ ] Add installation instructions to README
- [ ] Sign macOS app (requires Apple Developer account)
- [ ] Notarize macOS app for Gatekeeper

**Example GitHub Actions workflow:**
```yaml
name: Build Binaries

on:
  push:
    tags:
      - 'v*'

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install pyinstaller pydub customtkinter static-ffmpeg
      - name: Build
        run: pyinstaller M8_KitCreator.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: M8_KitCreator-macOS
          path: dist/M8_KitCreator.app
```

---

### TASK-014: Consider Alternative GUI Framework
**Priority:** LOW | **Effort:** 20+ hours | **Impact:** MEDIUM

**Problem:**
- tkinter/customtkinter can be hard to bundle
- Appearance is platform-dependent
- Limited modern UI capabilities

**Alternatives to consider:**

**Option A: Keep tkinter/customtkinter**
- Pros: Already working, lightweight
- Cons: Bundling issues, dated appearance

**Option B: PyQt6/PySide6**
- Pros: Professional appearance, better bundling, cross-platform
- Cons: Larger binary size, steeper learning curve, licensing (LGPL)

**Option C: Dear PyGui**
- Pros: Modern, GPU-accelerated, easy to bundle
- Cons: Different paradigm, less documentation

**Option D: Flet (Flutter for Python)**
- Pros: Modern UI, cross-platform (including web)
- Cons: Newer, less mature, larger binaries

**Recommendation: Stick with customtkinter for now, revisit for v2.0**

---

## Priority 4: Feature Enhancements

### TASK-015: Investigate Stereo Support
**Priority:** MEDIUM | **Effort:** 6-8 hours | **Impact:** HIGH

**Problem:**
- Files are forced to mono (line 136)
- Cue points don't work correctly with stereo
- Root cause unknown ("Can't seem to figure this one out" - line 15)

**Actions:**
- [ ] Research WAV cue chunk specification for stereo files
- [ ] Test cue point positioning with stereo files
- [ ] Calculate sample positions correctly for multi-channel audio
- [ ] Hypothesis: `get_array_of_samples()` returns interleaved samples
- [ ] Adjust cue position calculation for channel count
- [ ] Test with M8 hardware
- [ ] Add option to preserve stereo (default: mono for compatibility)

**Potential fix:**
```python
# Current (mono): position in samples
cue_positions.append(len(concatenated_audio.get_array_of_samples()))

# Stereo: position in frames (samples / channels)
num_channels = concatenated_audio.channels
sample_count = len(concatenated_audio.get_array_of_samples())
frame_count = sample_count // num_channels
cue_positions.append(frame_count)
```

---

### TASK-016: Add Batch Processing
**Priority:** LOW | **Effort:** 3-4 hours | **Impact:** MEDIUM

**Actions:**
- [ ] Add "Batch Mode" option
- [ ] Process multiple folders at once
- [ ] Auto-generate output filenames
- [ ] Add batch processing queue
- [ ] Show batch progress

---

### TASK-017: Add Undo/Redo
**Priority:** LOW | **Effort:** 4-5 hours | **Impact:** LOW

**Actions:**
- [ ] Implement command pattern
- [ ] Add undo/redo buttons
- [ ] Store operation history

---

### TASK-018: Add Preset Management
**Priority:** LOW | **Effort:** 3-4 hours | **Impact:** MEDIUM

**Actions:**
- [ ] Save/load processing presets
- [ ] Include file selections in presets
- [ ] Add preset dropdown
- [ ] Export/import preset files

---

## Priority 5: Testing & Quality Assurance

### TASK-019: Add Unit Tests
**Priority:** MEDIUM | **Effort:** 6-8 hours | **Impact:** HIGH

**Actions:**
- [ ] Set up pytest framework
- [ ] Test audio processing functions
- [ ] Test file validation
- [ ] Test cue point generation
- [ ] Create test WAV files (various sample rates, bit depths)
- [ ] Aim for 80%+ code coverage
- [ ] Add CI/CD to run tests automatically

**Example test structure:**
```python
# tests/test_audio_processor.py
import pytest
from m8_kitcreator.audio_processor import AudioProcessor

def test_validate_wav_file_valid():
    result = AudioProcessor.validate_wav_file('test_data/valid.wav')
    assert result[0] == True

def test_validate_wav_file_invalid_extension():
    result = AudioProcessor.validate_wav_file('test.mp3')
    assert result[0] == False
    assert 'WAV file' in result[1]

def test_concatenate_two_files():
    processor = AudioProcessor()
    output = processor.concatenate(['file1.wav', 'file2.wav'], 'output.wav')
    assert os.path.exists(output)
    # Verify cue points exist
```

---

### TASK-020: Add Integration Tests
**Priority:** LOW | **Effort:** 4-5 hours | **Impact:** MEDIUM

**Actions:**
- [ ] Test complete end-to-end workflows
- [ ] Test with real M8 hardware
- [ ] Test with various audio file types
- [ ] Create test suite of known-good files

---

### TASK-021: Add Performance Testing
**Priority:** LOW | **Effort:** 2-3 hours | **Impact:** LOW

**Actions:**
- [ ] Benchmark processing time vs. file size
- [ ] Profile memory usage
- [ ] Optimize bottlenecks
- [ ] Test with 100+ files

---

## Priority 6: Documentation

### TASK-022: Add Code Documentation
**Priority:** MEDIUM | **Effort:** 2-3 hours | **Impact:** MEDIUM

**Actions:**
- [ ] Add docstrings to all functions (Google or NumPy style)
- [ ] Add type hints (Python 3.10+)
- [ ] Generate API documentation with Sphinx
- [ ] Add inline comments for complex logic

**Example:**
```python
def concatenate_audio_files(
    file_names: list[str],
    output_file: str,
    marker_duration_ms: int = 1,
    silence_thresh: float = -50.0,
    min_silence_len: int = 10,
    retained_silence: int = 1,
    progress_callback: callable = None
) -> bool:
    """
    Concatenate multiple WAV files with M8-compatible cue markers.

    Args:
        file_names: List of WAV file paths to concatenate
        output_file: Path for output WAV file
        marker_duration_ms: Duration of silent markers between samples (default: 1ms)
        silence_thresh: Silence detection threshold in dBFS (default: -50.0)
        min_silence_len: Minimum silence duration to detect in ms (default: 10)
        retained_silence: Silence to keep between chunks in ms (default: 1)
        progress_callback: Optional callback for progress updates

    Returns:
        True if successful, False otherwise

    Raises:
        InvalidWavFileError: If input files are invalid
        ProcessingError: If audio processing fails

    Note:
        Files are converted to mono for correct M8 cue point positioning.
    """
```

---

### TASK-023: Create User Manual
**Priority:** MEDIUM | **Effort:** 3-4 hours | **Impact:** MEDIUM

**Actions:**
- [ ] Create docs/ folder
- [ ] Write getting started guide
- [ ] Add screenshots of each step
- [ ] Explain M8 import process
- [ ] Add troubleshooting section
- [ ] Create FAQ
- [ ] Add video tutorial (optional)

---

### TASK-024: Update README
**Priority:** HIGH | **Effort:** 1 hour | **Impact:** MEDIUM

**Actions:**
- [ ] Add badges (build status, version, license)
- [ ] Add clear download links for binaries
- [ ] Add system requirements
- [ ] Add usage examples with screenshots
- [ ] Add contributing guidelines
- [ ] Add known limitations section
- [ ] Add roadmap/future features

---

## Priority 7: Advanced Features (Future)

### TASK-025: Add Command-Line Interface
**Priority:** LOW | **Effort:** 3-4 hours | **Impact:** LOW

**Actions:**
- [ ] Add argparse CLI interface
- [ ] Support headless operation
- [ ] Enable scripting/automation
- [ ] Add to PyPI for `pip install m8-kitcreator`

**Example:**
```bash
m8-kitcreator --input file1.wav file2.wav --output kit.wav --threshold -45
```

---

### TASK-026: Add Waveform Visualization
**Priority:** LOW | **Effort:** 8-10 hours | **Impact:** LOW

**Actions:**
- [ ] Add matplotlib or similar
- [ ] Show waveform with cue markers
- [ ] Interactive waveform editor
- [ ] Visual silence detection preview

---

### TASK-027: Add Cloud/Web Version
**Priority:** LOW | **Effort:** 40+ hours | **Impact:** MEDIUM

**Actions:**
- [ ] Create web interface (Flask/FastAPI backend)
- [ ] File upload/download
- [ ] Process files server-side
- [ ] No installation required for users

---

## Implementation Roadmap

### Phase 1: Foundation (1-2 weeks)
**Goal: Clean, testable, maintainable codebase**
- TASK-001: Code quality cleanup
- TASK-002: Refactor architecture
- TASK-003: Input validation
- TASK-004: Error handling
- TASK-005: Fix typo

### Phase 2: Distribution (1-2 weeks)
**Goal: Self-contained executables for macOS and Linux**
- TASK-011: PyInstaller setup
- TASK-012: Bundle ffmpeg
- TASK-013: GitHub releases
- TASK-024: Update README

### Phase 3: User Experience (1-2 weeks)
**Goal: Professional, user-friendly application**
- TASK-006: Progress indication
- TASK-007: User configuration
- TASK-008: Drag-and-drop
- TASK-023: User manual

### Phase 4: Testing & Quality (1 week)
**Goal: Robust, reliable application**
- TASK-019: Unit tests
- TASK-020: Integration tests
- TASK-022: Code documentation

### Phase 5: Features (2-3 weeks)
**Goal: Enhanced functionality**
- TASK-015: Stereo support investigation
- TASK-009: File reordering
- TASK-018: Preset management
- TASK-025: CLI interface

---

## Quick Wins (Do First)

These tasks provide immediate value with minimal effort:

1. **TASK-005** (1 min): Fix typo
2. **TASK-001** (1-2 hrs): Code cleanup
3. **TASK-024** (1 hr): Update README with current state
4. **TASK-003** (2-3 hrs): Input validation (prevents crashes)
5. **TASK-012** (3-4 hrs): Bundle ffmpeg with static-ffmpeg package

---

## Critical Path to v1.0 Release

To reach a production-ready v1.0:

1. TASK-002: Refactor architecture ⭐
2. TASK-003: Input validation ⭐
3. TASK-006: Progress indication ⭐
4. TASK-011: PyInstaller distribution ⭐
5. TASK-012: Bundle ffmpeg ⭐
6. TASK-019: Unit tests ⭐
7. TASK-013: GitHub releases ⭐
8. TASK-023: User manual ⭐

**Estimated effort: 4-6 weeks part-time**

---

## Notes

**About the mono conversion issue (line 136):**
The root cause is likely that pydub's `get_array_of_samples()` returns interleaved samples for stereo, so the position calculation is off by a factor of 2. The cue chunk expects frame positions (not sample positions). This should be investigated in TASK-015.

**About distribution:**
PyInstaller is strongly recommended over py2app because:
- Cross-platform (macOS + Linux with one tool)
- Better maintained
- Easier to bundle dependencies
- More predictable results

**About ffmpeg:**
Using the `static-ffmpeg` Python package is the cleanest solution. It downloads platform-specific binaries automatically and integrates seamlessly with pydub.

---

**Document version:** 1.0
**Created:** 2025-11-15
**Last updated:** 2025-11-15
