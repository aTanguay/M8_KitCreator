import os
from pydub import AudioSegment
from pydub.generators import Sine
import tkinter as tk
from tkinter import filedialog, messagebox

# This script works, but it only puts a bleep at the start of the files.
# If it added markers instead, it would be great

def concatenate_audio_files(files, output_file, marker_duration_ms=1, marker_frequency=440, silence_thresh=-40.0, silence_len=1000):
    # Generate the audio marker
    marker = Sine(marker_frequency).to_audio_segment(duration=marker_duration_ms)

    # Concatenate audio files with a marker in between and remove long silences
    concatenated_audio = AudioSegment.empty()
    for file in files:
        audio = AudioSegment.from_wav(file)

        # Remove silences longer than silence_len
        audio = strip_long_silence(audio, silence_thresh, silence_len)

        concatenated_audio += audio + marker

    # Remove the last marker
    concatenated_audio = concatenated_audio[:-marker_duration_ms]

    # Export the concatenated audio
    concatenated_audio.export(output_file, format="wav")
def strip_long_silence(audio, silence_thresh=-40.0, silence_len=500):
    """Remove silences longer than silence_len from the audio."""
    return audio.strip_silence(silence_thresh=silence_thresh, silence_len=silence_len)

def gui_select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Let the user select multiple .wav files
    files = filedialog.askopenfilenames(title="Select WAV Files", filetypes=[("WAV files", "*.wav")])
    if not files:
        return

    # Let the user select an output file location
    output_file = filedialog.asksaveasfilename(title="Save Concatenated WAV as", defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if not output_file:
        return

    concatenate_audio_files(files, output_file)

    messagebox.showinfo("Success", f"Concatenated audio saved as {output_file}")

if __name__ == "__main__":
    gui_select_files()
