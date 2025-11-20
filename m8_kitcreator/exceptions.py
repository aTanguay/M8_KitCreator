"""
Custom exceptions for M8 Kit Creator.
"""

class M8KitCreatorError(Exception):
    """Base exception for M8 Kit Creator."""
    pass

class AudioProcessingError(M8KitCreatorError):
    """Raised when audio processing fails."""
    pass

class FileValidationError(M8KitCreatorError):
    """Raised when file validation fails."""
    pass

class ExportError(M8KitCreatorError):
    """Raised when exporting audio fails."""
    pass

class OctatrackError(M8KitCreatorError):
    """Raised when Octatrack file generation fails."""
    pass
