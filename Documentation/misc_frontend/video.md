# Audio and Video Capture in TDW

There are several ways capture audio or video data in TDW.

## "I want to capture only video (without audio)"

Be sure to include `{"$type": "set_target_framerate", "framerate": 30}` or else the video might be too fast.

#### Option A: Use image data

1. Write a controller that receives and saves an image every frame, like the following minimal example:

```python
# Create the avatar.
c = Controller()
c.start()

# Create the scene, the avatar, and request images.
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      {"$type": "create_avatar",
                       "type": "A_Img_Caps_Kinematic",
                       "id": "a"},
                      {"$type": "set_target_framerate",
                       "framerate": 30},
                      {"$type": "set_pass_masks",
                       "avatar_id": "a",
                       "pass_masks": ["_img"]},
                      {"$type": "send_images",
                       "frequency": "always"}])

for i in range(num_frames): # You will need to define num_frames.
    # Save the image from the previous frame.
    images = Images(resp[0])
    TDWUtils.save_images(images, filename="filename", output_directory="path/to/output/directory")
    
    commands = get_commands() # Your code here.
    
    resp = c.communicate(commands)
```

2. After running the controller, stitch the frames together with **ffmpeg**.

#### Option B: Record a video with ffmpeg

##### Linux:

- Make sure that xpra isn't running.
- Use **x11grab** (run this outside of a Docker container):

```bash
DISPLAY=:0 ffmpeg -video_size 256x256 -f x11grab -i :0.0+0,0 output.mp4
```

- `DISPLAY` must have a valid display number.
- `-video_size` must be the display size.
- The TDW screen size must be less than or equal to the display size.
- `:0.0+0,0` is the display number (which should match `DISPLAY`) and `+(x,y)` pixel offset. You can get the coordinates of the window with:

```bash
xwininfo -tree -root
```

##### Windows:

```bash
ffmpeg -f dshow -i video="screen-capture-recorder" output.mkv
```

##### OS X:

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

## "I want to capture audio (and maybe video too)"

Important guidelines when recording audio:

- Audio capture requires audio drivers (not all headless servers have these installed).
- Audio capture does _not_ sync with TDW's send-receive pattern; playback is always in realtime. This is a limitation of the Unity Engine. To ensure that the visual frames align with the audio, send [`set_target_framerate`](../api/command_api.md#set_target_framerate) and set the target to a reasonable video framerate (typically 60).

## "I want to capture video and audio"

Be sure to include `{"$type": "set_target_framerate", "framerate": 30}` or else the video might be too fast.

To record audio and video, you need to use an external program.

#### On a headless Linux server

1. See [Docker documentation](../Docker/docker.md) for Docker requirements.
2. [Build this container.](https://github.com/threedworld-mit/tdw/blob/master/Docker/Dockerfile_audio)
3. Run `start_container_audio_video.sh`. You may need to adjust the `-video_size` and pixel offset (`$DISPLAY+1152,672`) parameters.
4. To stop recording, you will need to stop the Docker container.
5. After recording, you will need to re-encode the video:

```bash
ffmpeg -i <.nut file generated above> -c:v libx264 -vf format=yuv420p -crf 18 -strict -2 <output file>.mp4
```

#### On a personal computer

See above for instructions for how to use ffmpeg with x11grab. If you are using Linux, you can probably skip step 1.

You can also use [OBS](https://obsproject.com), which has limited command-line functionality. After installing OBS, you'll need to configure it yourself to get the audio-visual setup you need (there's a lot of documentation and tutorials for OBS online).

If you start OBS with the `--startrecording` flag, OBS will begin recording as soon as it is opened.

If you kill the OBS process, it will stop recording video (OBS continuously saves video while recording).

So, a reliable (albeit somewhat hack-y) approach to video capture would be:

```python
from subprocess import call, Popen
from tdw.controller import Controller
from os import getcwd, chdir

c = Controller()
c.load_streamed_scene(scene="tdw_room")

cwd = getcwd()
# Required for running OBS correctly!
chdir("C:/Program Files (x86)/obs-studio/bin/64bit/")
# Open OBS and start recording.
obs = Popen(["C:/Program Files (x86)/obs-studio/bin/64bit/obs64.exe", "--startrecording"])
# Return to the current working directory.
chdir(cwd)

# More TDW controller code here.

# Close OBS and stop recording.
call(['taskkill', '/F', '/T', '/PID', str(obs.pid)])
```

## "I want to capture only audio (without video)"

We recommend using our [`AudioUtils`](../python/tdw_utils.md#AudioUtils) class to record audio; see API for a usage example.

Note that `AudioUtils` requires [fmedia](https://stsaz.github.io/fmedia/), which has simpler syntax than ffmpeg for recording audio.

For an example of how to generate an audio-only dataset, see: `tdw/Python/example_controllers/minimal_audio_dataset.py` For more information regarding PyImpact (which is used in the controller), [read this](impact_sounds.md).
