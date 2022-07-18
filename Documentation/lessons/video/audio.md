##### Video Recording

# Video with audio

The best way to record video with audio is to call TDW's video capture commands, which launch [ffmpeg](https://www.ffmpeg.org/). ffmpeg's screen capture parameters vary by OS and so there are three different commands for starting video capture. Read the following to learn more:

- [Video with audio (Linux)](screen_record_linux.md)
- [Video with audio (OS X)](screen_record_osx.md)
- [Video with audio (Windows)](screen_record_windows.md)

## Separate image capture and audio capture

It is possible, **but not recommended**, to record image data [as described in the previous document](images.md), [record audio with `AudioUtils`](../audio/overview.md), and combine the images and the audio with [ffmpeg](https://www.ffmpeg.org/). **However, it is *extremely* difficult to synchronize them into a video.** This is classic problem in audio/visual recording; we don't recommend attempting it!

## Linux server

1. See [install guide](../setup/install.md) for Docker requirements.
2. [Build this container.](https://github.com/threedworld-mit/tdw/blob/master/Docker/Dockerfile_audio)
3. Run [`start_container_audio_video.sh`](https://github.com/threedworld-mit/tdw/blob/master/Docker/start_container_audio_video.sh). You may need to adjust the `-video_size` and pixel offset (`$DISPLAY+1152,672`) parameters.
4. To stop recording, you will need to stop the Docker container.
5. After recording, you will need to re-encode the video:

```bash
ffmpeg -i <.nut file generated above> -c:v libx264 -vf format=yuv420p -crf 18 -strict -2 <output file>.mp4
```

## Personal computer (Windows, OS X, or Linux)

[See previous document for how to record with ffmpeg or OBS](images.md)

***

**This is the last document in the "Video Recording" tutorial.**

[Return to the README](../../../README.md)
