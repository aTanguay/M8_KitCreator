# Stereo Cue Point Fix - Technical Analysis

## Problem Statement

The current code forces all audio to mono (line 136) because cue points are incorrectly positioned when using stereo files. The original author noted: "Can't seem to figure this one out."

## Root Cause Analysis

### The Issue

**Lines 128 & 142:**
```python
cue_positions = [len(marker.get_array_of_samples())]  # Initial position
cue_positions.append(len(concatenated_audio.get_array_of_samples()))  # Additional positions
```

### Understanding Audio Samples vs. Frames

**Key Concept:**
- **Sample**: A single audio value for one channel
- **Frame**: One sample for EACH channel at the same point in time

**Example (1 second at 44100 Hz):**

| Format | Frames | Samples | Array Length |
|--------|--------|---------|--------------|
| Mono | 44,100 | 44,100 | 44,100 |
| Stereo | 44,100 | 88,200 | 88,200 |
| 5.1 Surround | 44,100 | 264,600 | 264,600 |

### What pydub Returns

`AudioSegment.get_array_of_samples()` returns an array with **one value per sample per channel** (interleaved):

**Mono:**
```
[S1, S2, S3, S4, ...]
```

**Stereo:**
```
[L1, R1, L2, R2, L3, R3, L4, R4, ...]
```

### What WAV Cue Chunks Expect

According to the [WAV specification](http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html), cue points reference **sample frame positions**, not individual sample positions.

**From the spec:**
```
Cue Point:
  dwIdentifier: Unique ID
  dwPosition: Sample frame position (not sample position)
  fccChunk: 'data'
  dwChunkStart: Byte offset of data chunk
  dwBlockStart: Byte offset of block
  dwSampleOffset: Sample frame offset
```

### The Math

**Current code (broken for stereo):**
- Stereo file at 1 second (44100 Hz)
- `get_array_of_samples()` returns 88,200 values
- Cue point written as position 88,200
- **Should be:** 44,100 (frames)
- **Error:** 2x too large

**Why mono works:**
- Mono file at 1 second (44100 Hz)
- `get_array_of_samples()` returns 44,100 values
- Cue point written as position 44,100
- **Should be:** 44,100 (frames)
- **Result:** Correct by coincidence (1 channel = 1 sample per frame)

## The Fix

### Correct Calculation

```python
# Get total number of samples (includes all channels)
sample_count = len(concatenated_audio.get_array_of_samples())

# Get number of channels
num_channels = concatenated_audio.channels

# Calculate frame position (samples / channels)
frame_position = sample_count // num_channels

# Store frame position, not sample position
cue_positions.append(frame_position)
```

### Why This Works

- **Mono (1 channel):** 44,100 samples ÷ 1 = 44,100 frames ✓
- **Stereo (2 channels):** 88,200 samples ÷ 2 = 44,100 frames ✓
- **Surround (6 channels):** 264,600 samples ÷ 6 = 44,100 frames ✓

## Implementation

### Required Changes

**File:** `M8_KitBasher_0.22.py`

**Change 1 - Line 128:**
```python
# OLD (broken for stereo):
cue_positions = [len(marker.get_array_of_samples())]

# NEW (works for all channel counts):
marker_samples = len(marker.get_array_of_samples())
marker_channels = marker.channels
cue_positions = [marker_samples // marker_channels]
```

**Change 2 - Line 142:**
```python
# OLD (broken for stereo):
cue_positions.append(len(concatenated_audio.get_array_of_samples()))

# NEW (works for all channel counts):
sample_count = len(concatenated_audio.get_array_of_samples())
frame_position = sample_count // concatenated_audio.channels
cue_positions.append(frame_position)
```

**Change 3 - Line 136 (REMOVE mono conversion):**
```python
# OLD (forced mono):
audio = audio.set_channels(1)

# NEW (preserve original channels):
# Removed - no longer needed!
```

**Change 4 - Line 124-125 (ensure markers match audio channels):**
```python
# OLD (always mono markers):
marker = AudioSegment.silent(duration=marker_duration_ms)
retain_silence = AudioSegment.silent(duration=retained_silence)

# NEW (markers match audio channels - set after loading first file):
# Will be set dynamically based on first file
```

### Full Refactored Function

```python
def concatenate_audio_files(file_names, output_file, marker_duration_ms=1,
                           silence_thresh=-50.0, min_silence_len=10,
                           retained_silence=1, preserve_stereo=True):
    """
    Concatenate audio files with M8-compatible cue markers.

    Args:
        preserve_stereo: If True, preserve original channel count.
                        If False, convert to mono (legacy behavior)
    """
    concatenated_audio = AudioSegment.empty()
    cue_positions = []
    marker = None
    retain_silence = None
    target_channels = None

    for i, file in enumerate(file_names):
        audio = AudioSegment.from_wav(file)

        # On first file, determine target channel count and create markers
        if i == 0:
            target_channels = audio.channels if preserve_stereo else 1
            marker = AudioSegment.silent(duration=marker_duration_ms,
                                        frame_rate=audio.frame_rate)
            marker = marker.set_channels(target_channels)
            retain_silence = AudioSegment.silent(duration=retained_silence,
                                                frame_rate=audio.frame_rate)
            retain_silence = retain_silence.set_channels(target_channels)

            # Add initial marker and record position
            concatenated_audio += marker
            marker_samples = len(marker.get_array_of_samples())
            marker_frames = marker_samples // marker.channels
            cue_positions.append(marker_frames)

        # Convert to target channel count
        if audio.channels != target_channels:
            audio = audio.set_channels(target_channels)

        # Process silence
        chunks = split_on_silence(audio, silence_thresh=silence_thresh,
                                 min_silence_len=min_silence_len)
        processed_audio = sum([chunk + retain_silence for chunk in chunks],
                             AudioSegment.empty())[:-retained_silence]

        # Add processed audio
        concatenated_audio += processed_audio

        # Calculate and store frame position (not sample position!)
        sample_count = len(concatenated_audio.get_array_of_samples())
        frame_position = sample_count // concatenated_audio.channels
        cue_positions.append(frame_position)

        # Add marker
        concatenated_audio += marker

    # Export and add cue points (same as before)
    try:
        concatenated_audio.export(output_file, format="wav")
        print("Audio exported successfully!")
    except Exception as e:
        print(f"Error exporting audio: {e}")
        messagebox.showerror("Error", f"Failed to export audio: {e}")
        return False

    # Add cue points to WAV file
    with wave.open(output_file, 'rb') as wf:
        params = wf.getparams()
        num_frames = params.nframes
        data = wf.readframes(num_frames)

    cue_chunk_data = struct.pack('<L', len(cue_positions))
    for i, position in enumerate(cue_positions):
        cue_id = i + 1
        cue_chunk_data += struct.pack('<LL4sLLL', cue_id, position,
                                      b'data', 0, 0, position)

    cue_chunk = b'cue ' + struct.pack('<L', len(cue_chunk_data)) + cue_chunk_data

    with wave.open(output_file, 'wb') as wf:
        wf.setparams(params)
        wf.writeframes(data)
        wf._file.write(cue_chunk)

    print(f"Concatenated audio saved as {output_file}")
    print(f"Channel count: {target_channels} ({'stereo' if target_channels == 2 else 'mono'})")
    messagebox.showinfo("Success", "Files have been merged successfully.")
    return True
```

## Testing Plan

### Test Cases

1. **Mono files only** - Should work as before
2. **Stereo files only** - Should preserve stereo with correct cue points
3. **Mixed mono/stereo** - Should normalize to first file's channel count
4. **Verify cue points** - Open in audio editor, verify markers at correct positions
5. **M8 hardware test** - Import to M8, verify slices trigger correctly

### Test Files Needed

Create test WAV files:
- `mono_44100.wav` - 1 second, 44100Hz, mono
- `stereo_44100.wav` - 1 second, 44100Hz, stereo
- `test_kit_mono.wav` - 5 short mono samples
- `test_kit_stereo.wav` - 5 short stereo samples

### Verification Steps

1. Process test files with new code
2. Open output in Ocenaudio or Audacity
3. Verify cue markers appear at start of each sample
4. Calculate expected frame positions manually
5. Use `wave` module to read cue chunk and verify positions
6. Test on M8 hardware

## Benefits

### For Users

- ✓ **Preserve stereo information** - No more forced mono conversion
- ✓ **Better audio quality** - Stereo samples keep spatial information
- ✓ **Wider compatibility** - Works with any channel count (mono, stereo, surround)
- ✓ **Backward compatible** - Can add `force_mono=True` option if needed

### For Code Quality

- ✓ **Correct algorithm** - Follows WAV specification properly
- ✓ **Future-proof** - Works with any channel configuration
- ✓ **Documented** - Clear explanation of samples vs. frames
- ✓ **Testable** - Easy to verify with test files

## Backward Compatibility

To maintain compatibility with users who want mono:

```python
# Add checkbox to GUI
self.stereo_checkbox = ctk.CTkCheckBox(
    self,
    text="Preserve Stereo (recommended)",
    variable=self.preserve_stereo_var
)
```

Or default to mono with option to enable stereo:
```python
concatenate_audio_files(files, output, preserve_stereo=False)  # Default: mono (safe)
```

## Related Issues

This fix also resolves:
- Multi-channel audio support
- Future surround sound support (5.1, 7.1)
- Correct frame calculations for all WAV operations

## References

- [WAV File Format Specification](http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html)
- [Multimedia Programming Interface and Data Specifications 1.0](https://www.recordingblogs.com/wiki/cue-chunk-of-a-wave-file)
- [pydub Documentation](https://github.com/jiaaro/pydub)

---

**Analysis Date:** 2025-11-15
**Status:** Solution identified, ready for implementation
**Estimated Fix Time:** 1-2 hours
**Testing Time:** 1-2 hours
**Total:** 2-4 hours to fully resolve
