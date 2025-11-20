import unittest
from m8_kitcreator.exceptions import (
    M8KitCreatorError,
    AudioProcessingError,
    FileValidationError,
    ExportError,
    OctatrackError
)

class TestExceptions(unittest.TestCase):
    """Test custom exceptions."""

    def test_inheritance(self):
        """Test that all custom exceptions inherit from M8KitCreatorError."""
        self.assertTrue(issubclass(AudioProcessingError, M8KitCreatorError))
        self.assertTrue(issubclass(FileValidationError, M8KitCreatorError))
        self.assertTrue(issubclass(ExportError, M8KitCreatorError))
        self.assertTrue(issubclass(OctatrackError, M8KitCreatorError))

    def test_raising(self):
        """Test raising and catching exceptions."""
        with self.assertRaises(AudioProcessingError):
            raise AudioProcessingError("Test error")

        with self.assertRaises(M8KitCreatorError):
            raise AudioProcessingError("Test error")
