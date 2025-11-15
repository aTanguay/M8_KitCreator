import os
import struct
import tkinter as tk
import customtkinter as ctk
import wave
from tkinter import filedialog, messagebox
from pydub import AudioSegment
from pydub.silence import split_on_silence

#----------------------------------------------------------------
# ConcateM8 - A Dirtywave M8 Sliced Wav Kit Maker
# Version 0.24 - Code quality improvements and validation
# You'll need tkinter, customtkinter, pydub, wave, and os.
# Written in October 2023 - Andy Tanguay.
# Updated November 2025 - Code refactoring and input validation
#----------------------------------------------------------------

# UI Configuration Constants
WINDOW_TITLE = "ConcateM8"
WINDOW_WIDTH = 350
WINDOW_HEIGHT = 510
WINDOW_GEOMETRY = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"

# Font Configuration
TITLE_FONT = ("Arial", 16)
SUBTITLE_FONT = ("Arial", 11)
LABEL_FONT = ("Arial", 11)

# Listbox Configuration
LISTBOX_WIDTH = 30
LISTBOX_HEIGHT = 16

# Audio Processing Default Parameters
DEFAULT_MARKER_DURATION_MS = 1
DEFAULT_SILENCE_THRESHOLD = -50.0
DEFAULT_MIN_SILENCE_LEN = 10
DEFAULT_RETAINED_SILENCE = 1

# File Dialog Configuration
WAV_FILE_TYPES = [("WAV Files", "*.wav"), ("All Files", "*.*")]


class FileSelectorApp(tk.Tk):
    """
    Main application window for M8 Kit Creator.

    Provides a GUI for selecting WAV files, configuring processing parameters,
    and creating M8-compatible sliced audio kits with cue markers.
    """

    def __init__(self):
        """Initialize the application window and UI components."""
        super().__init__()

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_GEOMETRY)

        # State: Lists to store selected file names and their full paths
        self.file_names = []
        self.file_paths = []

        self._setup_ui()

    def _setup_ui(self):
        """Set up all UI components."""
        # Title section
        self.main_title_label = ctk.CTkLabel(
            self,
            text="Dirtywave M8 Sliced Wav Kit Maker",
            font=TITLE_FONT
        )
        self.main_title_label.pack(pady=2, padx=1)

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Select WAV files, Press Merge, Select Output Wav",
            font=SUBTITLE_FONT
        )
        self.subtitle_label.pack(pady=2, padx=1)

        # Button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=5, padx=5)

        self.select_button = ctk.CTkButton(
            self.button_frame,
            text="Select Files",
            command=self.select_files
        )
        self.select_button.grid(row=0, column=0, padx=5, pady=5)

        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="Clear Files",
            command=self.clear_files
        )
        self.clear_button.grid(row=0, column=1, padx=5, pady=5)

        # File list frame
        self.filelist_frame = ctk.CTkFrame(self)
        self.filelist_frame.pack(pady=5, padx=5)

        self.filelist_label = ctk.CTkLabel(
            self.filelist_frame,
            text="Current WAV files to process:",
            font=LABEL_FONT
        )
        self.filelist_label.pack(pady=1, padx=1)

        self.file_listbox = tk.Listbox(
            self.filelist_frame,
            width=LISTBOX_WIDTH,
            height=LISTBOX_HEIGHT
        )
        self.file_listbox.pack(pady=10, padx=10)

        # Bottom button frame
        self.bottom_button_frame = ctk.CTkFrame(self)
        self.bottom_button_frame.pack(pady=5, padx=5)

        self.merge_button = ctk.CTkButton(
            self.bottom_button_frame,
            text="Merge",
            command=self.merge_files
        )
        self.merge_button.grid(row=0, column=0, padx=5, pady=5)

        self.close_button = ctk.CTkButton(
            self.bottom_button_frame,
            text="Exit",
            command=self.close_app
        )
        self.close_button.grid(row=0, column=1, padx=5, pady=5)

    def select_files(self):
        """
        Open file dialog to select WAV files and validate selections.

        Clears existing selection and adds validated files to the list.
        """
        files = filedialog.askopenfilenames(
            title="Select WAV Files",
            filetypes=WAV_FILE_TYPES
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
            error_list = "\n".join([f"• {name}: {msg}" for name, msg in invalid_files])
            messagebox.showwarning(
                "Invalid Files",
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

        Validates that files are selected before proceeding.
        """
        if not self.file_paths:
            messagebox.showwarning(
                "No Files Selected",
                "Please select WAV files before merging."
            )
            return

        output_file = filedialog.asksaveasfilename(
            title="Save Merged Kit As",
            defaultextension=".wav",
            filetypes=WAV_FILE_TYPES
        )

        if not output_file:
            return

        # Check output directory is writable
        output_dir = os.path.dirname(output_file)
        if not os.access(output_dir, os.W_OK):
            messagebox.showerror(
                "Permission Denied",
                f"Cannot write to directory: {output_dir}"
            )
            return

        print(f"Merging {len(self.file_paths)} files into {output_file}...")
        success = concatenate_audio_files(self.file_paths, output_file)

        if success:
            self.clear_files()

    def close_app(self):
        """Close the application."""
        self.destroy()


def validate_wav_file(file_path):
    """
    Validate that a file is a readable WAV file.

    Args:
        file_path: Path to the file to validate

    Returns:
        tuple: (is_valid, error_message)
               is_valid is True if file is valid, False otherwise
               error_message is None if valid, error description if invalid
    """
    # Check file extension
    if not file_path.lower().endswith('.wav'):
        return False, "Not a WAV file (wrong extension)"

    # Check file exists
    if not os.path.isfile(file_path):
        return False, "File does not exist"

    # Check file is readable
    if not os.access(file_path, os.R_OK):
        return False, "Cannot read file (permission denied)"

    # Check file is not empty
    if os.path.getsize(file_path) == 0:
        return False, "File is empty"

    # Try to open as WAV file
    try:
        with wave.open(file_path, 'rb') as wf:
            params = wf.getparams()
            # Validate basic WAV properties
            if params.nchannels < 1 or params.nchannels > 8:
                return False, f"Unsupported channel count: {params.nchannels}"
            if params.sampwidth < 1 or params.sampwidth > 4:
                return False, f"Unsupported sample width: {params.sampwidth} bytes"
            if params.framerate < 8000 or params.framerate > 192000:
                return False, f"Unsupported sample rate: {params.framerate} Hz"
    except wave.Error as e:
        return False, f"Invalid WAV file: {str(e)}"
    except Exception as e:
        return False, f"Cannot read file: {str(e)}"

    return True, None


def concatenate_audio_files(file_names, output_file,
                            marker_duration_ms=DEFAULT_MARKER_DURATION_MS,
                            silence_thresh=DEFAULT_SILENCE_THRESHOLD,
                            min_silence_len=DEFAULT_MIN_SILENCE_LEN,
                            retained_silence=DEFAULT_RETAINED_SILENCE,
                            force_mono=False):
    """
    Concatenate audio files with M8-compatible cue markers.

    This function takes multiple WAV files and combines them into a single
    WAV file with cue point markers at the start of each sample. The cue
    points use frame-based positioning to work correctly with stereo and
    multi-channel audio.

    Args:
        file_names: List of WAV file paths to concatenate
        output_file: Path for the output WAV file
        marker_duration_ms: Duration of silent markers between samples (ms)
        silence_thresh: Silence detection threshold in dBFS
        min_silence_len: Minimum silence duration to detect (ms)
        retained_silence: Amount of silence to keep between chunks (ms)
        force_mono: If True, convert all audio to mono (default: False)

    Returns:
        bool: True if successful, False if an error occurred
    """
    # These will be set based on first file
    marker = None
    retain_silence = None
    target_channels = None

    concatenated_audio = AudioSegment.empty()
    cue_positions = []

    for i, file_path in enumerate(file_names):
        try:
            audio = AudioSegment.from_wav(file_path)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            messagebox.showerror(
                "File Load Error",
                f"Failed to load {os.path.basename(file_path)}:\n{str(e)}"
            )
            return False

        # On first file, determine target channel count and create markers
        if i == 0:
            target_channels = 1 if force_mono else audio.channels
            # Create markers with same sample rate as audio
            marker = AudioSegment.silent(
                duration=marker_duration_ms,
                frame_rate=audio.frame_rate
            )
            marker = marker.set_channels(target_channels)

            retain_silence = AudioSegment.silent(
                duration=retained_silence,
                frame_rate=audio.frame_rate
            )
            retain_silence = retain_silence.set_channels(target_channels)

            # Add initial marker and record FRAME position (not sample position!)
            concatenated_audio += marker
            marker_samples = len(marker.get_array_of_samples())
            marker_frames = marker_samples // marker.channels
            cue_positions.append(marker_frames)

        # Convert to target channel count if needed
        if audio.channels != target_channels:
            audio = audio.set_channels(target_channels)

        # Process silence removal
        chunks = split_on_silence(
            audio,
            silence_thresh=silence_thresh,
            min_silence_len=min_silence_len
        )

        if chunks:
            processed_audio = sum(
                [chunk + retain_silence for chunk in chunks],
                AudioSegment.empty()
            )[:-retained_silence]
        else:
            # No silence detected, use original audio
            processed_audio = audio

        concatenated_audio += processed_audio

        # Calculate FRAME position (not sample position!)
        # For stereo: samples = frames * 2, so frames = samples // channels
        sample_count = len(concatenated_audio.get_array_of_samples())
        frame_position = sample_count // concatenated_audio.channels
        cue_positions.append(frame_position)

        concatenated_audio += marker

    # Export audio file
    try:
        concatenated_audio.export(output_file, format="wav")
        channel_desc = get_channel_description(target_channels)
        print(f"Audio exported successfully! {channel_desc}")
    except Exception as e:
        print(f"Error exporting audio: {e}")
        messagebox.showerror(
            "Export Error",
            f"Failed to export audio:\n{str(e)}"
        )
        return False

    # Add cue points to WAV file
    try:
        with wave.open(output_file, 'rb') as wf:
            params = wf.getparams()
            num_frames = params.nframes
            data = wf.readframes(num_frames)

        cue_chunk_data = struct.pack('<L', len(cue_positions))
        for i, position in enumerate(cue_positions):
            cue_id = i + 1
            cue_chunk_data += struct.pack(
                '<LL4sLLL',
                cue_id, position, b'data', 0, 0, position
            )

        cue_chunk = b'cue ' + struct.pack('<L', len(cue_chunk_data)) + cue_chunk_data

        with wave.open(output_file, 'wb') as wf:
            wf.setparams(params)
            wf.writeframes(data)
            wf._file.write(cue_chunk)
    except Exception as e:
        print(f"Error adding cue points: {e}")
        messagebox.showerror(
            "Cue Point Error",
            f"Audio exported but failed to add cue points:\n{str(e)}"
        )
        return False

    # Success!
    channel_desc = get_channel_description(target_channels)
    print(f"Concatenated audio saved as {output_file}")
    print(f"Output format: {channel_desc}, {len(cue_positions)} cue points")

    messagebox.showinfo(
        "Success",
        f"Files have been merged successfully!\n\n"
        f"Output: {channel_desc}\n"
        f"Cue points: {len(cue_positions)}\n"
        f"Files merged: {len(file_names)}"
    )
    return True


def get_channel_description(num_channels):
    """
    Get a human-readable description of channel configuration.

    Args:
        num_channels: Number of audio channels

    Returns:
        str: Description like "mono", "stereo", or "6 channels (multi-channel)"
    """
    if num_channels == 1:
        return "mono"
    elif num_channels == 2:
        return "stereo"
    else:
        return f"{num_channels} channels (multi-channel)"


if __name__ == "__main__":
    app = FileSelectorApp()
    app.mainloop()
