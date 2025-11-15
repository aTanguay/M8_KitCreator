"""
Utility functions for M8 Kit Creator.

Contains validation functions, helper functions, and other utilities.
"""

import os
import wave
from m8_kitcreator import config


def validate_wav_file(file_path):
    """
    Validate that a file is a readable WAV file.

    Performs comprehensive validation including:
    - File extension check
    - File existence and readability
    - WAV header validation
    - Audio parameter validation (channels, sample width, sample rate)

    Args:
        file_path: Path to the file to validate

    Returns:
        tuple: (is_valid, error_message)
               is_valid is True if file is valid, False otherwise
               error_message is None if valid, error description if invalid
    """
    # Check file extension
    if not file_path.lower().endswith(config.WAV_EXTENSION):
        return False, config.ERROR_NOT_WAV

    # Check file exists
    if not os.path.isfile(file_path):
        return False, config.ERROR_FILE_NOT_FOUND

    # Check file is readable
    if not os.access(file_path, os.R_OK):
        return False, config.ERROR_PERMISSION_DENIED

    # Check file is not empty
    if os.path.getsize(file_path) == 0:
        return False, config.ERROR_FILE_EMPTY

    # Try to open as WAV file and validate parameters
    try:
        with wave.open(file_path, 'rb') as wf:
            params = wf.getparams()

            # Validate channel count
            if params.nchannels < config.MIN_CHANNELS or params.nchannels > config.MAX_CHANNELS:
                return False, config.ERROR_INVALID_CHANNELS.format(params.nchannels)

            # Validate sample width
            if params.sampwidth < config.MIN_SAMPLE_WIDTH or params.sampwidth > config.MAX_SAMPLE_WIDTH:
                return False, config.ERROR_INVALID_SAMPLE_WIDTH.format(params.sampwidth)

            # Validate sample rate
            if params.framerate < config.MIN_SAMPLE_RATE or params.framerate > config.MAX_SAMPLE_RATE:
                return False, config.ERROR_INVALID_SAMPLE_RATE.format(params.framerate)

    except wave.Error as e:
        return False, config.ERROR_INVALID_WAV.format(str(e))
    except Exception as e:
        return False, config.ERROR_CANNOT_READ.format(str(e))

    return True, None


def get_channel_description(num_channels):
    """
    Get a human-readable description of channel configuration.

    Args:
        num_channels: Number of audio channels

    Returns:
        str: Description like "mono", "stereo", or "6 channels (multi-channel)"
    """
    if num_channels == 1:
        return "mono"
    elif num_channels == 2:
        return "stereo"
    else:
        return f"{num_channels} channels (multi-channel)"


def format_file_list_error(invalid_files):
    """
    Format a list of invalid files into a user-friendly error message.

    Args:
        invalid_files: List of tuples (filename, error_message)

    Returns:
        str: Formatted error message
    """
    return "\n".join([f"• {name}: {msg}" for name, msg in invalid_files])


def check_directory_writable(directory_path):
    """
    Check if a directory is writable.

    Args:
        directory_path: Path to the directory to check

    Returns:
        bool: True if directory is writable, False otherwise
    """
    return os.access(directory_path, os.W_OK)
