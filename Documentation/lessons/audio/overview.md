##### Audio

# Overview

**Audio** in TDW is handled internally by the Unity physics engine. Via the TDW command API, you can send .wav data to the build. Once the build receives the .wav data, it will automatically start to play it.

## Setup for playing audio

Most personal computers are already set up to play audio. If you can listen to music on your computer, you'll be able to play audio in TDW.

On a Linux server, you need to install:

- `pulseaudio`
- `socat`
- `alsa-utils`

[This Docker file](https://github.com/threedworld-mit/tdw/blob/master/Docker/Dockerfile_audio) creates a container that can play audio.

## Pre-recorded vs. generated audio

It is possible to play pre-recorded audio in the build by sending it .wav data. It is also possible to generate sounds from physics data using [`PyImpact`](py_impact.md), i.e. generate a sound from the collision of two metal objects hitting each other at a particular velocity vector, contact area, etc.

Ultimately, both means of playing audio are handled identically within the command API; either way, the controller will send the build audio data which the build will then play. It's just a question of whether the audio data is a file or if it is created at runtime.

## Unique properties of audio output data

Audio data is very different than [image](../visual_perception/overview.md) or [physics](../physx/overview.md) data in some key respects:

- Unlike all other data in TDW, audio output is strictly in realtime. It isn't possible for the underlying Unity engine. to process audio at a faster rate.
- Strictly speaking, it isn't possible to directly capture audio data from the build. It must be recorded with an external program. TDW includes several useful wrapper functions to make this easy and reliable.

***

**Next: [Initialize audio and play .wav files](initialize_audio.md)**

[Return to the README](../../../README.md)