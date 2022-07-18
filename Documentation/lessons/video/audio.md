##### Video Recording

# Video with audio

The best way to record video with audio is to call TDW's video capture commands, which launch [ffmpeg](https://www.ffmpeg.org/). ffmpeg's screen capture parameters vary by OS and so there are three different commands for starting video capture. Read the following to learn more:

- [Video with audio (Linux)](screen_record_linux.md)
- [Video with audio (OS X)](screen_record_osx.md)
- [Video with audio (Windows)](screen_record_windows.md)

## Separate image capture and audio capture

It is possible, **but not recommended**, to record image data [as described in the previous document](images.md), [record audio with `AudioUtils`](../audio/overview.md), and combine the images and the audio with [ffmpeg](https://www.ffmpeg.org/). **However, it is *extremely* difficult to synchronize them into a video.** This is classic problem in audio/visual recording; we don't recommend attempting it!

## Record with OBS

[OBS](https://obsproject.com) is an excellent screen recorder for personal computers. Unfortunately, it has very limited command line options. If you want to automatically generate many videos, you should use ffmpeg as described above. OBS is best used for one-shot videos, especially if you want to fine-tune the input/output settings.

***

[Return to the README](../../../README.md)
