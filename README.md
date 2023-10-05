# M8_KitCreator

A simple sliced audio file maker that creates files that are compatible with the M8. You select your files, and the script puts them into one file, with markers (slices) at the start of each sample. It also throws out extra silence.

The idea here is to be able to take a selection of wav files and mash them into a sliced kit that the M8 likes.

To use, grab the last version that's out there. You'll need to have python installed. As well as the pydub https://pypi.org/project/pydub/

This is a python script with a couple dependencies, but nothing weird.
The biggest issue right now is that it needs to make the files mono to put the slices in the right spot. Not too sure why. Seems like a small price to pay, and maybe someone smarter can fix it. Or I'll take a swing at it. V13 is the version that doesn't make the files mono.

![OceanAudio](/images/OceanShot.png)



