import wave
import struct
import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment

def concatenate_audio_files(output_file, marker_duration_ms=1000):
    marker = AudioSegment.silent(duration=marker_duration_ms)

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    audio_files = filedialog.askopenfilenames(title="Select WAV files", filetypes=[("WAV files", "*.wav")])

    if not audio_files:
        print("No files selected. Exiting.")
        return

    concatenated_audio = AudioSegment.empty()
    cue_positions = []

    for idx, file in enumerate(audio_files):
        audio = AudioSegment.from_wav(file)

        cue_positions.append(len(concatenated_audio.get_array_of_samples()))  # this is where the new audio will start

        concatenated_audio += audio

        # Add marker only if it's not the last file
        if idx != len(audio_files) - 1:
            concatenated_audio += marker

    concatenated_audio.export(output_file, format="wav")

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

if __name__ == "__main__":
    output_file = input("Enter the name of the output file (e.g., output.wav): ").strip("'").strip('"')
    concatenate_audio_files(output_file)
