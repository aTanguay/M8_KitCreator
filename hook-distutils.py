"""
PyInstaller runtime hook for distutils compatibility with Python 3.12+

In Python 3.12+, distutils was removed from stdlib and is now provided by setuptools.
This hook ensures distutils is available by installing setuptools' version.
"""
import sys

# Make setuptools' distutils available as 'distutils'
try:
    import setuptools
    # This triggers setuptools to install its distutils shim
    import distutils
except ImportError:
    pass
