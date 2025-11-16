"""
M8 Kit Creator - A tool for creating M8 and Octatrack compatible sliced audio kits.

This package provides tools for concatenating WAV files with cue point markers
for the Dirtywave M8 hardware sampler and .ot metadata files for the Elektron Octatrack.
"""

__version__ = "0.31.0"
__author__ = "Andy Tanguay"
__license__ = "MIT"

# Lazy imports to avoid importing GUI dependencies during testing
__all__ = ["AudioProcessor", "FileSelectorApp", "OctatrackWriter"]


def __getattr__(name):
    """Lazy import of modules to avoid importing tkinter during testing."""
    if name == "AudioProcessor":
        from m8_kitcreator.audio_processor import AudioProcessor
        return AudioProcessor
    elif name == "FileSelectorApp":
        from m8_kitcreator.gui import FileSelectorApp
        return FileSelectorApp
    elif name == "OctatrackWriter":
        from m8_kitcreator.octatrack_writer import OctatrackWriter
        return OctatrackWriter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

