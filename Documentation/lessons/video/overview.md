##### Video Recording

# Overview

It is possible to record video in TDW in one of two ways: Internally, using a standard controller + build setup, and with an external video recording application. This tutorial will cover both of these options.

If you haven't done so already, we recommend  you read the documentation for [visual perception](../visual_perception/overview.md) and [camera controls](../camera/overview.md).

## How to install ffmpeg

Most video capture techniques involve using [ffmpeg](https://ffmpeg.org/). To install:

- Ubuntu: `sudo apt install ffmpeg`
- OS X: `sudo brew install ffmpeg`
- Windows: [download the latest build of ffmpeg](https://www.gyan.dev/ffmpeg/builds/). Then, [add ffmpeg to the path environment variable](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/).

To verify that ffmpeg is installed, open a terminal, type `ffmpeg`, and press enter.

***

**Next: [Image-only video](images.md)**

[Return to the README](../../../README.md)

