"""
This is a setup.py script generated by py2applet

Usage:
    python3 setup.py py2app
"""

from setuptools import setup

APP = ['M8_KitBasher_0.22.py']
DATA_FILES = []
OPTIONS = {
	'argv_emulation': True,
	'packages':['pydub','customtkinter']
	}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
