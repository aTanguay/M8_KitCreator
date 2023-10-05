# M8_KitCreator

A simple sliced audio file maker that creates files that are compatible with the M8. The idea here is to be able to take a selection of wav files and mash them into a sliced kit that the M8 likes.

To use: You select your files, and the script puts them into one file, with markers (slices) at the start of each sample. It also throws out extra silence.

To install, grab the last version that's out there. You'll need to have python installed. As well as the pydub https://pypi.org/project/pydub/
Getting things set up is not my strong suit, but I'll try and add more install tips.

This is a python script with a couple dependencies, but nothing weird.
The biggest issue right now is that it needs to make the files mono to put the slices in the right spot. Not too sure why. Seems like a small price to pay, and maybe someone smarter can fix it. Or I'll take a swing at it. V13 is the version that doesn't make the files mono but puts the markers in the wrong spot. 

Here's the output:
![OceanAudio](/images/OceanShot.png)



