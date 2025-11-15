"""
M8 Kit Creator - A tool for creating M8-compatible sliced audio kits.

This package provides tools for concatenating WAV files with cue point markers
that are compatible with the Dirtywave M8 hardware sampler.
"""

__version__ = "0.27.0"
__author__ = "Andy Tanguay"
__license__ = "MIT"

from m8_kitcreator.audio_processor import AudioProcessor
from m8_kitcreator.gui import FileSelectorApp

__all__ = ["AudioProcessor", "FileSelectorApp"]
