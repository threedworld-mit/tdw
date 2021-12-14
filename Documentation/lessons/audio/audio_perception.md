##### Audio

# Audio perception

Because audio data isn't directly returned by the build, it is difficult to have an agent in TDW respond at runtime to audio events in the scene.

There are several workarounds for this:

1. You could read audio directly off the soundcard using a module such as [PyAudio](https://pypi.org/project/PyAudio/). This hasn't yet been extensively tested by the TDW development team; the main challenge will likely be syncing audio data to TDW output data (including image data).
2. You can pre-process audio. This is how the [Multimodal Challenge](https://github.com/alters-mit/multimodal_challenge) works. One controller generates a dataset of audio trials. In each audio trial, an object falls and generates audio using PyImpact. The audio is saved to a .wav file and the positions and rotations of each object are saved to a .json file. Then, a second controller can load a dataset trial. The second controller has a Magnebot agent. Effectively, the agent trial begins with the object having just fallen and the Magnebot having just "heard" the noise. Note that the Multimodal Challenge uses TDW v1.8.29 and an earlier version of PyImpact.

***

**This is the last document in the "Audio" tutorial.**

[Return to the README](../../../README.md)