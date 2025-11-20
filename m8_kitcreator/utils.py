"""
Utility functions for M8 Kit Creator.

Contains validation functions, helper functions, and other utilities.
"""

import os
import wave
from typing import Tuple, Optional, List, Dict, Union
from pydub import AudioSegment
from pydub.silence import split_on_silence
from m8_kitcreator import config


def validate_wav_file(file_path: str) -> Tuple[bool, Optional[str]]:
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


def get_channel_description(num_channels: int) -> str:
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


def format_file_list_error(invalid_files: List[Tuple[str, str]]) -> str:
    """
    Format a list of invalid files into a user-friendly error message.

    Args:
        invalid_files: List of tuples (filename, error_message)

    Returns:
        str: Formatted error message
    """
    return "\n".join([f"• {name}: {msg}" for name, msg in invalid_files])


def check_directory_writable(directory_path: str) -> bool:
    """
    Check if a directory is writable.

    Args:
        directory_path: Path to the directory to check

    Returns:
        bool: True if directory is writable, False otherwise
    """
    return os.access(directory_path, os.W_OK)


def get_audio_metadata(file_path: str) -> Optional[Dict[str, Union[int, float, str]]]:
    """
    Get metadata about an audio file.

    Args:
        file_path: Path to the audio file

    Returns:
        dict: Dictionary with 'channels' (int), 'duration_ms' (float), and 'duration_formatted' (str)
              Returns None if file cannot be read
    """
    try:
        with wave.open(file_path, 'rb') as wf:
            params = wf.getparams()
            nchannels = params.nchannels
            nframes = params.nframes
            framerate = params.framerate

            duration_seconds = nframes / float(framerate)
            duration_ms = duration_seconds * 1000

            # Format as MM:SS.mmm
            minutes = int(duration_seconds // 60)
            seconds = duration_seconds % 60
            duration_formatted = f"{minutes}:{seconds:06.3f}"

            return {
                'channels': nchannels,
                'duration_ms': duration_ms,
                'duration_formatted': duration_formatted,
                'channel_label': 'M' if nchannels == 1 else 'S'
            }
    except Exception:
        return None


def calculate_trimmed_duration(file_path: str, silence_thresh: float = -50.0, min_silence_len: int = 10) -> Optional[str]:
    """
    Calculate the duration of audio after silence removal.

    Args:
        file_path: Path to the audio file
        silence_thresh: Silence threshold in dBFS (default: -50.0)
        min_silence_len: Minimum silence length in ms (default: 10)

    Returns:
        str: Formatted duration as MM:SS.mmm, or None if calculation fails
    """
    try:
        # Load audio
        audio = AudioSegment.from_wav(file_path)

        # Split on silence (same logic as AudioProcessor)
        chunks = split_on_silence(
            audio,
            silence_thresh=silence_thresh,
            min_silence_len=min_silence_len
        )

        if chunks:
            # Calculate total duration of all chunks
            total_duration_ms = sum(len(chunk) for chunk in chunks)
            # Add retained silence between chunks (1ms per gap)
            total_duration_ms += (len(chunks) - 1) * config.DEFAULT_RETAINED_SILENCE
        else:
            # No silence detected, use original duration
            total_duration_ms = len(audio)

        # Format as MM:SS.mmm
        duration_seconds = total_duration_ms / 1000.0
        minutes = int(duration_seconds // 60)
        seconds = duration_seconds % 60
        return f"{minutes}:{seconds:06.3f}"

    except Exception:
        return None
