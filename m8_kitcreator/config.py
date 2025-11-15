"""
Configuration constants for M8 Kit Creator.

Contains all configuration values for UI, audio processing, and file handling.
"""

# ============================================================================
# UI Configuration
# ============================================================================

# Window Configuration
WINDOW_TITLE = "ConcateM8"
WINDOW_WIDTH = 350
WINDOW_HEIGHT = 570  # Increased for reorder buttons
WINDOW_GEOMETRY = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"

# Font Configuration
TITLE_FONT = ("Arial", 16)
SUBTITLE_FONT = ("Arial", 11)
LABEL_FONT = ("Arial", 11)

# Listbox Configuration
LISTBOX_WIDTH = 30
LISTBOX_HEIGHT = 16

# Progress Bar Configuration
PROGRESS_BAR_WIDTH = 300
PROGRESS_BAR_HEIGHT = 20
STATUS_LABEL_FONT = ("Arial", 10)

# Padding Configuration
FRAME_PADDING_X = 5
FRAME_PADDING_Y = 5
BUTTON_PADDING_X = 5
BUTTON_PADDING_Y = 5

# ============================================================================
# Audio Processing Configuration
# ============================================================================

# Default Audio Processing Parameters
DEFAULT_MARKER_DURATION_MS = 1
DEFAULT_SILENCE_THRESHOLD = -50.0
DEFAULT_MIN_SILENCE_LEN = 10
DEFAULT_RETAINED_SILENCE = 1

# Audio Validation Limits
MIN_SAMPLE_RATE = 8000
MAX_SAMPLE_RATE = 192000
MIN_CHANNELS = 1
MAX_CHANNELS = 8
MIN_SAMPLE_WIDTH = 1
MAX_SAMPLE_WIDTH = 4

# ============================================================================
# File Handling Configuration
# ============================================================================

# File Dialog Configuration
WAV_FILE_TYPES = [("WAV Files", "*.wav"), ("All Files", "*.*")]
WAV_EXTENSION = ".wav"

# File Size Limits (in bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

# ============================================================================
# Application Messages
# ============================================================================

# UI Messages
MSG_NO_FILES_TITLE = "No Files Selected"
MSG_NO_FILES_TEXT = "Please select WAV files before merging."
MSG_PERMISSION_DENIED_TITLE = "Permission Denied"
MSG_INVALID_FILES_TITLE = "Invalid Files"
MSG_SUCCESS_TITLE = "Success"

# Dialog Titles
DIALOG_SELECT_FILES = "Select WAV Files"
DIALOG_SAVE_OUTPUT = "Save Merged Kit As"

# Status Messages
STATUS_READY = "Ready"
STATUS_PROCESSING = "Processing file {} of {}..."
STATUS_EXPORTING = "Exporting audio..."
STATUS_ADDING_CUES = "Adding cue points..."
STATUS_COMPLETE = "Complete!"

# ============================================================================
# Error Messages
# ============================================================================

ERROR_NOT_WAV = "Not a WAV file (wrong extension)"
ERROR_FILE_NOT_FOUND = "File does not exist"
ERROR_PERMISSION_DENIED = "Cannot read file (permission denied)"
ERROR_FILE_EMPTY = "File is empty"
ERROR_INVALID_CHANNELS = "Unsupported channel count: {}"
ERROR_INVALID_SAMPLE_WIDTH = "Unsupported sample width: {} bytes"
ERROR_INVALID_SAMPLE_RATE = "Unsupported sample rate: {} Hz"
ERROR_INVALID_WAV = "Invalid WAV file: {}"
ERROR_CANNOT_READ = "Cannot read file: {}"
