# M8 Kit Creator Package

This package contains the modular implementation of M8 Kit Creator.

## Module Structure

```
m8_kitcreator/
├── __init__.py           # Package initialization
├── config.py             # Configuration constants
├── utils.py              # Utility functions (validation, helpers)
├── audio_processor.py    # Audio processing logic
└── gui.py                # GUI components
```

## Modules

### `config.py`
Contains all configuration constants:
- UI configuration (window size, fonts, padding)
- Audio processing parameters (thresholds, defaults)
- File handling configuration
- Error messages and UI text

### `utils.py`
Utility functions:
- `validate_wav_file()` - Comprehensive WAV file validation
- `get_channel_description()` - Format channel count as human-readable string
- `format_file_list_error()` - Format invalid file list for display
- `check_directory_writable()` - Check directory write permissions

### `audio_processor.py`
`AudioProcessor` class handles:
- Audio file concatenation
- Silence removal
- Cue point generation (frame-based for stereo support)
- WAV file export with cue chunks

### `gui.py`
`FileSelectorApp` class provides:
- Main application window
- File selection and validation UI
- File list display
- Merge operation interface

## Usage

```python
from m8_kitcreator import FileSelectorApp, AudioProcessor

# Launch GUI application
app = FileSelectorApp()
app.mainloop()

# Or use AudioProcessor directly
processor = AudioProcessor()
processor.concatenate_audio_files(['file1.wav', 'file2.wav'], 'output.wav')
```

## Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Configurability**: All constants in config.py for easy customization
3. **Testability**: Business logic separated from UI for unit testing
4. **Reusability**: AudioProcessor can be used without GUI
5. **Maintainability**: Clear module boundaries and documentation

## Future Enhancements

- CLI interface using AudioProcessor
- Progress callback support in GUI
- Plugin system for custom processing
- Configuration file support
- Unit tests for each module
