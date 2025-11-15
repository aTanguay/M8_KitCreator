"""
GUI module for M8 Kit Creator.

Contains all user interface components and event handling.
"""

import os
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Try to import tkinterdnd2 for drag-and-drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    print("Warning: tkinterdnd2 not available. Drag-and-drop support disabled.")

from m8_kitcreator import config
from m8_kitcreator.audio_processor import AudioProcessor
from m8_kitcreator.utils import (
    validate_wav_file,
    format_file_list_error,
    check_directory_writable
)


# Choose base class based on drag-and-drop availability
if DND_AVAILABLE:
    _BaseWindow = TkinterDnD.Tk
else:
    _BaseWindow = tk.Tk


class FileSelectorApp(_BaseWindow):
    """
    Main application window for M8 Kit Creator.

    Provides a GUI for selecting WAV files, configuring processing parameters,
    and creating M8-compatible sliced audio kits with cue markers.

    Supports drag-and-drop file selection when tkinterdnd2 is available.
    """

    def __init__(self):
        """Initialize the application window and UI components."""
        super().__init__()

        self.title(config.WINDOW_TITLE)
        self.geometry(config.WINDOW_GEOMETRY)

        # State: Lists to store selected file names and their full paths
        self.file_names = []
        self.file_paths = []

        # Audio processor
        self.processor = AudioProcessor()

        # Set up UI
        self._setup_ui()

        # Set up drag-and-drop if available
        if DND_AVAILABLE:
            self._setup_drag_and_drop()

    def _setup_ui(self):
        """Set up all UI components."""
        self._create_title_section()
        self._create_button_section()
        self._create_file_list_section()
        self._create_progress_section()
        self._create_bottom_buttons()

    def _create_title_section(self):
        """Create the title and subtitle labels."""
        self.main_title_label = ctk.CTkLabel(
            self,
            text="Dirtywave M8 Sliced Wav Kit Maker",
            font=config.TITLE_FONT
        )
        self.main_title_label.pack(pady=2, padx=1)

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Select WAV files, Press Merge, Select Output Wav",
            font=config.SUBTITLE_FONT
        )
        self.subtitle_label.pack(pady=2, padx=1)

    def _create_button_section(self):
        """Create the file selection and clear buttons."""
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(
            pady=config.FRAME_PADDING_Y,
            padx=config.FRAME_PADDING_X
        )

        self.select_button = ctk.CTkButton(
            self.button_frame,
            text="Select Files",
            command=self.select_files
        )
        self.select_button.grid(
            row=0, column=0,
            padx=config.BUTTON_PADDING_X,
            pady=config.BUTTON_PADDING_Y
        )

        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="Clear Files",
            command=self.clear_files
        )
        self.clear_button.grid(
            row=0, column=1,
            padx=config.BUTTON_PADDING_X,
            pady=config.BUTTON_PADDING_Y
        )

    def _create_file_list_section(self):
        """Create the file list display section."""
        self.filelist_frame = ctk.CTkFrame(self)
        self.filelist_frame.pack(
            pady=config.FRAME_PADDING_Y,
            padx=config.FRAME_PADDING_X
        )

        self.filelist_label = ctk.CTkLabel(
            self.filelist_frame,
            text="Current WAV files to process:",
            font=config.LABEL_FONT
        )
        self.filelist_label.pack(pady=1, padx=1)

        self.file_listbox = tk.Listbox(
            self.filelist_frame,
            width=config.LISTBOX_WIDTH,
            height=config.LISTBOX_HEIGHT
        )
        self.file_listbox.pack(pady=10, padx=10)

    def _create_progress_section(self):
        """Create the progress bar and status label."""
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(
            pady=config.FRAME_PADDING_Y,
            padx=config.FRAME_PADDING_X
        )

        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text=config.STATUS_READY,
            font=config.STATUS_LABEL_FONT
        )
        self.status_label.pack(pady=2, padx=5)

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=config.PROGRESS_BAR_WIDTH,
            height=config.PROGRESS_BAR_HEIGHT
        )
        self.progress_bar.pack(pady=5, padx=5)
        self.progress_bar.set(0)

    def _create_bottom_buttons(self):
        """Create the merge and exit buttons."""
        self.bottom_button_frame = ctk.CTkFrame(self)
        self.bottom_button_frame.pack(
            pady=config.FRAME_PADDING_Y,
            padx=config.FRAME_PADDING_X
        )

        self.merge_button = ctk.CTkButton(
            self.bottom_button_frame,
            text="Merge",
            command=self.merge_files
        )
        self.merge_button.grid(
            row=0, column=0,
            padx=config.BUTTON_PADDING_X,
            pady=config.BUTTON_PADDING_Y
        )

        self.close_button = ctk.CTkButton(
            self.bottom_button_frame,
            text="Exit",
            command=self.close_app
        )
        self.close_button.grid(
            row=0, column=1,
            padx=config.BUTTON_PADDING_X,
            pady=config.BUTTON_PADDING_Y
        )

    def select_files(self):
        """
        Open file dialog to select WAV files and validate selections.

        Clears existing selection and adds validated files to the list.
        Shows warning message if any files are invalid.
        """
        files = filedialog.askopenfilenames(
            title=config.DIALOG_SELECT_FILES,
            filetypes=config.WAV_FILE_TYPES
        )

        if not files:
            return

        # Clear existing selections
        self.file_names.clear()
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)

        # Validate and add files
        invalid_files = []
        for file_path in files:
            is_valid, error_msg = validate_wav_file(file_path)
            if is_valid:
                file_name = os.path.basename(file_path)
                self.file_names.append(file_name)
                self.file_paths.append(file_path)
                self.file_listbox.insert(tk.END, file_name)
            else:
                invalid_files.append((os.path.basename(file_path), error_msg))

        # Show warning if any files were invalid
        if invalid_files:
            error_list = format_file_list_error(invalid_files)
            messagebox.showwarning(
                config.MSG_INVALID_FILES_TITLE,
                f"The following files could not be loaded:\n\n{error_list}\n\n"
                f"Valid files: {len(self.file_paths)}"
            )

    def clear_files(self):
        """Clear all selected files from the list."""
        self.file_names.clear()
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)

    def merge_files(self):
        """
        Prompt for output location and merge selected files.

        Validates that files are selected and output directory is writable
        before proceeding with the merge operation. Runs processing in a
        background thread to keep the UI responsive.
        """
        # Check if files are selected
        if not self.file_paths:
            messagebox.showwarning(
                config.MSG_NO_FILES_TITLE,
                config.MSG_NO_FILES_TEXT
            )
            return

        # Prompt for output file
        output_file = filedialog.asksaveasfilename(
            title=config.DIALOG_SAVE_OUTPUT,
            defaultextension=config.WAV_EXTENSION,
            filetypes=config.WAV_FILE_TYPES
        )

        if not output_file:
            return

        # Check output directory is writable
        output_dir = os.path.dirname(output_file)
        if not check_directory_writable(output_dir):
            messagebox.showerror(
                config.MSG_PERMISSION_DENIED_TITLE,
                f"Cannot write to directory: {output_dir}"
            )
            return

        # Start processing in background thread
        self._start_merge_thread(output_file)

    def _start_merge_thread(self, output_file):
        """
        Start the merge operation in a background thread.

        Args:
            output_file: Path for the output WAV file
        """
        # Disable buttons during processing
        self._set_buttons_enabled(False)

        # Reset progress bar
        self.progress_bar.set(0)
        self.status_label.configure(text=config.STATUS_PROCESSING.format(1, len(self.file_paths)))

        # Create and start processing thread
        def process():
            try:
                print(f"Merging {len(self.file_paths)} files into {output_file}...")
                success = self.processor.concatenate_audio_files(
                    self.file_paths,
                    output_file,
                    progress_callback=self._update_progress
                )

                # Update UI after completion (in main thread)
                self.after(0, lambda: self._on_merge_complete(success))

            except Exception as e:
                print(f"Error during merge: {e}")
                self.after(0, lambda: self._on_merge_error(str(e)))

        thread = threading.Thread(target=process, daemon=True)
        thread.start()

    def _on_merge_complete(self, success):
        """
        Handle merge completion (called in main thread).

        Args:
            success: True if merge was successful
        """
        # Re-enable buttons
        self._set_buttons_enabled(True)

        # Reset progress bar
        self.progress_bar.set(0)
        self.status_label.configure(text=config.STATUS_READY)

        # Clear file list on success
        if success:
            self.clear_files()

    def _on_merge_error(self, error_message):
        """
        Handle merge errors (called in main thread).

        Args:
            error_message: Error message to display
        """
        # Re-enable buttons
        self._set_buttons_enabled(True)

        # Reset progress bar
        self.progress_bar.set(0)
        self.status_label.configure(text=config.STATUS_READY)

        # Show error dialog
        messagebox.showerror(
            "Processing Error",
            f"An error occurred during processing:\n\n{error_message}"
        )

    def _set_buttons_enabled(self, enabled):
        """
        Enable or disable all buttons during processing.

        Args:
            enabled: True to enable buttons, False to disable
        """
        state = "normal" if enabled else "disabled"
        self.select_button.configure(state=state)
        self.clear_button.configure(state=state)
        self.merge_button.configure(state=state)
        self.close_button.configure(state=state)

    def _update_progress(self, current, total):
        """
        Update progress bar and status label.

        This method is called from the processing thread and uses
        after() to safely update the UI from the main thread.

        Args:
            current: Current file being processed (0-indexed)
            total: Total number of files
        """
        # Calculate progress (0.0 to 1.0)
        if total > 0:
            progress = current / total
        else:
            progress = 0

        # Update UI in main thread
        self.after(0, lambda: self._update_ui_elements(current, total, progress))

    def _update_ui_elements(self, current, total, progress):
        """
        Update UI elements (must be called from main thread).

        Args:
            current: Current file index
            total: Total number of files
            progress: Progress value (0.0 to 1.0)
        """
        self.progress_bar.set(progress)

        if current < total:
            status_text = config.STATUS_PROCESSING.format(current + 1, total)
            self.status_label.configure(text=status_text)
        else:
            self.status_label.configure(text=config.STATUS_COMPLETE)

    def close_app(self):
        """Close the application."""
        self.destroy()

    def _setup_drag_and_drop(self):
        """
        Configure drag-and-drop support for the file list.

        Registers the listbox as a drop target and sets up event handlers
        for visual feedback and file dropping.
        """
        # Register the listbox as a drop target
        self.file_listbox.drop_target_register(DND_FILES)

        # Bind drag-and-drop events
        self.file_listbox.dnd_bind('<<DropEnter>>', self._on_drag_enter)
        self.file_listbox.dnd_bind('<<DropLeave>>', self._on_drag_leave)
        self.file_listbox.dnd_bind('<<Drop>>', self._on_drop)

        # Update subtitle to indicate drag-and-drop support
        current_text = self.subtitle_label.cget("text")
        self.subtitle_label.configure(
            text=current_text + " (or drag & drop files here)"
        )

    def _on_drag_enter(self, event):
        """
        Handle drag enter event - show visual feedback.

        Args:
            event: Tkinter event object
        """
        # Change listbox background to indicate drop target
        self.file_listbox.configure(bg='#E8F5E9')  # Light green
        return event.action

    def _on_drag_leave(self, event):
        """
        Handle drag leave event - remove visual feedback.

        Args:
            event: Tkinter event object
        """
        # Restore default background
        self.file_listbox.configure(bg='white')
        return event.action

    def _on_drop(self, event):
        """
        Handle file drop event.

        Validates dropped files and adds them to the file list.

        Args:
            event: Tkinter event object containing dropped file paths
        """
        # Restore default background
        self.file_listbox.configure(bg='white')

        # Parse dropped files (tkinterdnd2 returns space-separated paths in curly braces)
        files = self._parse_dropped_files(event.data)

        if not files:
            return event.action

        # Validate and add files (same logic as select_files)
        invalid_files = []
        valid_count = 0

        for file_path in files:
            # Check if it's a WAV file
            if not file_path.lower().endswith('.wav'):
                invalid_files.append((os.path.basename(file_path), "Not a WAV file"))
                continue

            # Validate the file
            is_valid, error_msg = validate_wav_file(file_path)
            if is_valid:
                file_name = os.path.basename(file_path)
                # Check if file is already in the list
                if file_path not in self.file_paths:
                    self.file_names.append(file_name)
                    self.file_paths.append(file_path)
                    self.file_listbox.insert(tk.END, file_name)
                    valid_count += 1
            else:
                invalid_files.append((os.path.basename(file_path), error_msg))

        # Show status message
        if valid_count > 0:
            print(f"Added {valid_count} file(s) via drag-and-drop")

        # Show warning if any files were invalid
        if invalid_files:
            error_list = format_file_list_error(invalid_files)
            messagebox.showwarning(
                config.MSG_INVALID_FILES_TITLE,
                f"The following files could not be added:\n\n{error_list}\n\n"
                f"Valid files added: {valid_count}"
            )

        return event.action

    def _parse_dropped_files(self, data):
        """
        Parse file paths from drag-and-drop event data.

        tkinterdnd2 returns paths in various formats depending on the platform.
        This method handles the parsing correctly.

        Args:
            data: Raw data from drop event

        Returns:
            List of file paths
        """
        files = []

        # Handle different formats
        if isinstance(data, (list, tuple)):
            files = list(data)
        else:
            # String format: either space-separated or with curly braces
            data = str(data)

            # Remove outer curly braces if present
            if data.startswith('{') and data.endswith('}'):
                data = data[1:-1]

            # Split by spaces, but respect curly braces for paths with spaces
            current = []
            in_braces = False

            for char in data:
                if char == '{':
                    in_braces = True
                elif char == '}':
                    in_braces = False
                    if current:
                        files.append(''.join(current))
                        current = []
                elif char == ' ' and not in_braces:
                    if current:
                        files.append(''.join(current))
                        current = []
                else:
                    current.append(char)

            # Add last file if any
            if current:
                files.append(''.join(current))

        # Clean up paths
        files = [f.strip() for f in files if f.strip()]

        return files
