import sys
from unittest.mock import MagicMock, patch

# Mock modules
sys.modules['tkinter'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinterdnd2'] = MagicMock()

# Define dummy base
class DummyBase:
    def __init__(self, *args, **kwargs): pass
    def mainloop(self): pass
    def after(self, *args, **kwargs): pass

sys.modules['tkinterdnd2'].TkinterDnD.Tk = DummyBase
sys.modules['tkinter'].Tk = DummyBase

# Import
from m8_kitcreator.gui import FileSelectorApp

# Subclass
class TestableApp(FileSelectorApp):
    def __init__(self):
        self.file_names = []
        self.file_paths = []
        self.file_listbox = MagicMock()
        self.output_format = MagicMock()
        self.processor = MagicMock()

# Test
def test_duplicates():
    app = TestableApp()
    app._refresh_file_list = MagicMock()
    
    # Pre-populate
    app.file_paths = ['/path/to/file1.wav']
    app.file_names = ['file1.wav']
    
    print(f"Before: {app.file_paths}")
    print(f"App ID: {id(app)}")
    
    # Mock filedialog and messagebox
    with patch('m8_kitcreator.gui.filedialog.askopenfilenames', return_value=['/path/to/file1.wav', '/path/to/file2.wav']):
        with patch('m8_kitcreator.gui.messagebox') as mock_mb:
            with patch('m8_kitcreator.gui.validate_wav_file', return_value=(True, None)):
                app.select_files()
                
                print(f"After: {app.file_paths}")
                
                if len(app.file_paths) == 2:
                    print("SUCCESS: Correct number of files.")
                else:
                    print(f"FAILURE: Expected 2 files, got {len(app.file_paths)}")
                    
                if mock_mb.showwarning.called:
                    print("SUCCESS: Warning shown.")
                else:
                    print("FAILURE: Warning NOT shown.")

if __name__ == "__main__":
    test_duplicates()
