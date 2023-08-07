##### Audio

# Overview

**Audio** in TDW is handled internally by the Unity physics engine. Via the TDW command API, you can send .wav data to the build. Once the build receives the .wav data, it will automatically start to play it.

Audio data is very different than [image](../visual_perception/overview.md) or [physics](../physx/overview.md) data in some key respects:

- Unlike all other data in TDW, audio output is strictly in realtime. It isn't possible for the underlying Unity engine to process audio at a faster rate.
- Strictly speaking, it isn't possible to directly capture audio data from the build. It must be recorded with an external program. TDW includes several useful wrapper functions to make this easy and reliable.

In this tutorial, you'll learn how to initialize audio, play pre-recorded audio, and how to record audio.

## Physically-derived audio (Clatter)

It is possible in TDW to generate and play audio from physical properties of two objects and the properties of a collision between them. This is handled via the C# Clatter library and the Python `Clatter` add-on. [Read this for more information.](../clatter/overview.md)

***

**Next: [Initialize audio and play .wav files](initialize_audio.md)**

[Return to the README](../../../README.md)