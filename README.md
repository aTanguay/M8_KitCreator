# M8_KitCreator

A simple sliced audio file maker that creates files that are compatible with the M8. The idea here is to be able to take a selection of wav files and mash them into a sliced kit that the M8 likes.

You'll need to have python installed and you'll need these two libraries if you don't have them:

<b>customtkinter (or its abbreviation ctk)

pydub</b>

Install them with <i>"pip (or pip3 if that doesn't work) install pydub customtkinter"</i>

Run the newest M8_KitBasher_0.24.py file.

To use: You select your files, and the script puts them into one file, with markers (slices) at the start of each sample. It also throws out extra silence.

![interface](/images/app_022.png)

To install, grab the last version that's out there. Getting things set up is not my strong suit, but I'll try and add more install tips, as well as try and get it packed up into a Mac app. I got close, but not quite yet.

This is a python script with a couple dependencies, but nothing weird.

**New in v0.24:** Code quality improvements and validation!
- Input validation: Files are checked before processing to ensure they're valid WAV files
- Better error messages: Clear feedback when files can't be loaded or processed
- Constants extracted: All magic numbers moved to named constants at top of file
- Cleaner code: Duplicate variable names fixed, better documentation, proper docstrings
- Improved error handling: Specific error messages for different failure scenarios

**New in v0.23:** Stereo support! The app now preserves stereo files correctly. Previous versions forced mono conversion because the cue point calculation was using sample positions instead of frame positions. This has been fixed - cue points now use the correct frame-based positioning that works with any channel configuration (mono, stereo, or multi-channel). 

Here's the output:
![OceanAudio](/images/OceanShot.png)



