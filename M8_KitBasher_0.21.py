import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import wave
import struct
from pydub import AudioSegment
from pydub.silence import split_on_silence


#----------------------------------------------------------------

# Seemingly working version with a GUI.
# You'll need tkinter, customtkinter, pydub, wave, and os.

#----------------------------------------------------------------

class FileSelectorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ConcateM8")
        self.geometry("400x400")

        # Lists to store selected file names and their full paths
        self.file_names = []
        self.file_paths = []

        # Frame for buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=20)

        # Button to select files
        self.select_button = ctk.CTkButton(self.button_frame, text="Select Files", command=self.select_files)
        self.select_button.grid(row=0, column=0, padx=5)

        # Button to clear files from the list
        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear Files", command=self.clear_files)
        self.clear_button.grid(row=0, column=1, padx=5)

        # Listbox to display selected file names (not full paths)
        self.file_listbox = tk.Listbox(self, width=30, height=10)
        self.file_listbox.pack(pady=20)

        # Frame for bottom buttons
        self.bottom_button_frame = tk.Frame(self)
        self.bottom_button_frame.pack(pady=20)

        # Button to merge files
        self.merge_button = ctk.CTkButton(self.bottom_button_frame, text="Merge", command=self.merge_files)
        self.merge_button.grid(row=0, column=0, padx=5)

        # Button to close the application
        self.close_button = ctk.CTkButton(self.bottom_button_frame, text="Close", command=self.close_app)
        self.close_button.grid(row=0, column=1, padx=5)

    def select_files(self):
        # Open file dialog to select files
        files = filedialog.askopenfilenames(title="Select Files")

        # Clear the file_names and file_paths lists, and the listbox
        self.file_names.clear()
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)

        # Add selected file names (not full paths) to the file_names list and the listbox
        # Also add the full paths to the file_paths list
        for file in files:
            file_name = os.path.basename(file)
            self.file_names.append(file_name)
            self.file_paths.append(file)
            self.file_listbox.insert(tk.END, file_name)

    def clear_files(self):
        # Clear the file_names, file_paths lists, and the listbox
        self.file_names.clear()
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)

    def merge_files(self):
        # Prompt the user for the output file location
        output_file = filedialog.asksaveasfilename(title="Select Output File", defaultextension=".wav", filetypes=[("Wav Files", "*.wav"), ("All Files", "*.*")])

        # Check if a valid output file location is provided
        if output_file:
            # For now, just print the selected output location.
            # The actual merging logic can be added here.
            print(f"Merging files into {output_file}...")
            concatenate_audio_files(self.file_paths, output_file)

            self.clear_files()

    def close_app(self):
        self.destroy()



def concatenate_audio_files(file_names, output_file, marker_duration_ms=1, silence_thresh=-50.0, min_silence_len=10, retained_silence=1):
    marker = AudioSegment.silent(duration=marker_duration_ms)
    retain_silence = AudioSegment.silent(duration=retained_silence)

    concatenated_audio = AudioSegment.empty()
    cue_positions = [len(marker.get_array_of_samples())]  # Add initial marker position

    concatenated_audio += marker  # Add marker at 00 position

    for file in file_names:
        audio = AudioSegment.from_wav(file)

        # Convert to mono
        audio = audio.set_channels(1)

        chunks = split_on_silence(audio, silence_thresh=silence_thresh, min_silence_len=min_silence_len)
        processed_audio = sum([chunk + retain_silence for chunk in chunks], AudioSegment.empty())[:-retained_silence]

        concatenated_audio += processed_audio
        cue_positions.append(len(concatenated_audio.get_array_of_samples()))
        concatenated_audio += marker

    try:
        concatenated_audio.export(output_file, format="wav")
        # If no errors, you can notify the user or log a success message if desired
        print("Audio exported successfully!")
    except Exception as e:
        # Handle the error
        print(f"Error exporting audio: {e}")
        # Optionally, you can use tkinter's messagebox to show the error in a popup
        messagebox.showerror("Error", f"Failed to export audio: {e}")

    ### OLD CODE   concatenated_audio.export(output_file, format="wav")

    # Add cue points
    with wave.open(output_file, 'rb') as wf:
        params = wf.getparams()
        num_frames = params.nframes
        data = wf.readframes(num_frames)

    cue_chunk_data = struct.pack('<L', len(cue_positions))
    for i, position in enumerate(cue_positions):
        cue_id = i + 1
        cue_chunk_data += struct.pack('<LL4sLLL', cue_id, position, b'data', 0, 0, position)

    cue_chunk = b'cue ' + struct.pack('<L', len(cue_chunk_data)) + cue_chunk_data

    with wave.open(output_file, 'wb') as wf:
        wf.setparams(params)
        wf.writeframes(data)
        wf._file.write(cue_chunk)

    print(f"Concatenated audio saved as {output_file}")
    messagebox.showinfo("Success", "Files have been merged successfully.")
    

if __name__ == "__main__":
    app = FileSelectorApp()
    app.mainloop()
