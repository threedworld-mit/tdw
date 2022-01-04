##### Video Recording

# Video with audio

*If you haven't done so already, please read the documentation for [audio in TDW](../audio/overview.md).*

It is possible to record audio in TDW while capturing image data. **However, it is *extremely* difficult to synchronize them into a video.** This is classic problem in audio/visual recording; we don't recommend attempting it!

Instead, we *strongly* recommend capturing video with audio using an external application.

In setting up your controller:

- You must still [initialize audio](../audio/initialize_audio.md) in TDW like you normally would; you should *not* [record audio](../audio/record_audio.md)
- You must still [render images, but you shouldn't save images to disk](../core_concepts/images.md).
- You should set the target framerate to 30 or 60 frames per second.

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
