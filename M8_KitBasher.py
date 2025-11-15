#!/usr/bin/env python3
"""
M8 Kit Creator - Main Entry Point

A tool for creating M8-compatible sliced audio kits.

This script launches the M8 Kit Creator GUI application, which allows users to:
- Select multiple WAV files
- Concatenate them with M8-compatible cue markers
- Remove silence from audio
- Preserve stereo or mono audio
- Export a single WAV file ready for M8 import

Usage:
    python M8_KitBasher.py

Requirements:
    - Python 3.7+
    - pydub
    - customtkinter
    - tkinter (usually bundled with Python)

Author: Andy Tanguay
License: MIT
Version: 0.25.0
"""

import sys
from m8_kitcreator.gui import FileSelectorApp


def main():
    """
    Launch the M8 Kit Creator application.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        app = FileSelectorApp()
        app.mainloop()
        return 0
    except Exception as e:
        print(f"Error launching application: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
