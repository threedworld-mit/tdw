##### Audio

# Overview

**Audio** in TDW is handled internally by the Unity physics engine. Via the TDW command API, you can send .wav data to the build. Once the build receives the .wav data, it will automatically start to play it.

Audio data is very different than [image](../visual_perception/overview.md) or [physics](../physx/overview.md) data in some key respects:

- Unlike all other data in TDW, audio output is strictly in realtime. It isn't possible for the underlying Unity engine to process audio at a faster rate.
- Strictly speaking, it isn't possible to directly capture audio data from the build. It must be recorded with an external program. TDW includes several useful wrapper functions to make this easy and reliable.

In this tutorial, you'll learn how to initialize audio, play pre-recorded audio, generate dynamic audio from physics collision events, and how to record audio.

## High-Level API: Multimodal Challenge

The  [Multimodal Challenge](https://github.com/alters-mit/multimodal_challenge) combines a [Magnebot](https://github.com/alters-mit/magnebot) with an audio simulation; the Magnebot can both [visually perceive objects](../visual_perception/overview.md) and "listen" to a pre-processed physics audio event. The Multimodal Challenge includes a controller with an agent that can respond to the audio event, an a separate controller for generating a dataset of pre-processed trial data (including audio data).

***

**Next: [Initialize audio and play .wav files](initialize_audio.md)**

[Return to the README](../../../README.md)