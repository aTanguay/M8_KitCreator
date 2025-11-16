# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for M8 Kit Creator

This spec file configures PyInstaller to create a standalone executable
for M8 Kit Creator that works on macOS and Linux without requiring
Python or dependencies to be installed.

Usage:
    pyinstaller M8_KitCreator.spec

Output:
    dist/M8_KitCreator       (Linux executable)
    dist/M8_KitCreator.app   (macOS application bundle)
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect customtkinter data files (themes, assets)
datas = collect_data_files('customtkinter')

# Collect tkinterdnd2 data files (platform-specific DLLs)
try:
    import tkinterdnd2
    tkdnd_path = os.path.dirname(tkinterdnd2.__file__)
    datas += [(os.path.join(tkdnd_path, 'tkdnd'), 'tkinterdnd2/tkdnd')]
except ImportError:
    print("Warning: tkinterdnd2 not found - drag-and-drop will not work")
    pass

# Collect all submodules
hiddenimports = [
    'pydub',
    'pydub.silence',
    'customtkinter',
    'tkinterdnd2',
    'PIL._tkinter_finder',
    'm8_kitcreator',
    'm8_kitcreator.config',
    'm8_kitcreator.utils',
    'm8_kitcreator.audio_processor',
    'm8_kitcreator.octatrack_writer',
    'm8_kitcreator.gui',
    # Python 3.12+ compatibility - distutils was removed, now part of setuptools
    'setuptools',
]

# Collect ALL distutils submodules (Python 3.12+ compatibility)
try:
    distutils_modules = collect_submodules('distutils')
    hiddenimports.extend(distutils_modules)
except:
    pass

# Try to include static-ffmpeg if available
try:
    import staticffmpeg
    hiddenimports.append('staticffmpeg')
except ImportError:
    pass

a = Analysis(
    ['M8_KitBasher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook-distutils.py'],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Single file executable (easier distribution)
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
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file (icon.icns for macOS, icon.ico for Windows)
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='M8_KitCreator.app',
        icon=None,  # TODO: Add icon.icns
        bundle_identifier='com.andytanguay.m8kitcreator',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleShortVersionString': '0.31.0',
            'CFBundleVersion': '0.31.0',
            'NSHumanReadableCopyright': 'Copyright © 2023-2025 Andy Tanguay. MIT License.',
        },
    )
