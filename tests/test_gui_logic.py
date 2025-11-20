import unittest
from unittest.mock import MagicMock, patch
import os

# Define a dummy base class
class DummyBase:
    def __init__(self, *args, **kwargs):
        pass
    def mainloop(self):
        pass
    def after(self, *args, **kwargs):
        pass

# Mock tkinter and customtkinter before importing gui
import sys
sys.modules['tkinter'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinterdnd2'] = MagicMock()

# Configure the mock to return our dummy base
sys.modules['tkinterdnd2'].TkinterDnD.Tk = DummyBase
sys.modules['tkinter'].Tk = DummyBase

from m8_kitcreator.gui import FileSelectorApp

class TestableFileSelectorApp(FileSelectorApp):
    def __init__(self):
        # Skip parent init
        self.file_names = []
        self.file_paths = []
        self.file_listbox = MagicMock()
        self.output_format = MagicMock()
        self.processor = MagicMock()

class TestGuiLogic(unittest.TestCase):
    def setUp(self):
        self.app = TestableFileSelectorApp()
        self.app._refresh_file_list = MagicMock()

    @patch('m8_kitcreator.gui.validate_wav_file')
    @patch('m8_kitcreator.gui.messagebox')
    def test_select_files_no_duplicates(self, mock_messagebox, mock_validate):
        # Setup
        mock_validate.return_value = (True, None)
        
        # Simulate selecting files
        with patch('m8_kitcreator.gui.filedialog.askopenfilenames', return_value=['/path/to/file1.wav', '/path/to/file2.wav']):
            self.app.select_files()
            
        # Verify files added
        self.assertEqual(len(self.app.file_paths), 2)
        self.assertIn('/path/to/file1.wav', self.app.file_paths)
        self.assertIn('/path/to/file2.wav', self.app.file_paths)
        
        # Verify no warning shown
        mock_messagebox.showwarning.assert_not_called()

    @patch('m8_kitcreator.gui.validate_wav_file')
    @patch('m8_kitcreator.gui.messagebox')
    def test_select_files_with_duplicates(self, mock_messagebox, mock_validate):
        # Setup
        mock_validate.return_value = (True, None)
        self.app.file_paths = ['/path/to/file1.wav']
        self.app.file_names = ['file1.wav']
        
        # Simulate selecting duplicate file
        with patch('m8_kitcreator.gui.filedialog.askopenfilenames', return_value=['/path/to/file1.wav', '/path/to/file2.wav']):
            self.app.select_files()
            
        # Verify only new file added
        self.assertEqual(len(self.app.file_paths), 2)
        self.assertIn('/path/to/file2.wav', self.app.file_paths)
        
        # Verify warning shown
        mock_messagebox.showwarning.assert_called_once()
        args, _ = mock_messagebox.showwarning.call_args
        self.assertIn("Skipped 1 duplicate file(s)", args[1])

    @patch('m8_kitcreator.gui.validate_wav_file')
    @patch('m8_kitcreator.gui.messagebox')
    def test_drop_files_with_duplicates(self, mock_messagebox, mock_validate):
        # Setup
        mock_validate.return_value = (True, None)
        self.app.file_paths = ['/path/to/file1.wav']
        self.app.file_names = ['file1.wav']
        
        # Create mock event
        mock_event = MagicMock()
        mock_event.data = "{/path/to/file1.wav} {/path/to/file2.wav}"
        
        # Call _on_drop
        self.app._on_drop(mock_event)
        
        # Verify only new file added
        self.assertEqual(len(self.app.file_paths), 2)
        self.assertIn('/path/to/file2.wav', self.app.file_paths)
        
        # Verify warning shown
        mock_messagebox.showwarning.assert_called_once()
        args, _ = mock_messagebox.showwarning.call_args
        self.assertIn("Skipped 1 duplicate file(s)", args[1])
