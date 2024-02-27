##### Troubleshooting

# Common errors

This document is a list of common usage errors in TDW. This is not a comprehensive document. We are continuously expanding this document as our user base increases and we gain more information about beginner TDW users.

If after reading this document you're still unsure how to fix your error, [please report the bug as a GitHub Issue](issues.md).

## All Platforms

### 1. The build or controller quit with an error or crashed

- Make sure that your `tdw` Python module is at the latest release.
- Make sure that the version of the TDW build matches the version of the `tdw` Python module.
- **Check [the player log](https://docs.unity3d.com/Manual/LogFiles.html) for errors. See the next section below for a list of commonly logged problems.**
- Add a [logger](../read_write/logger.md) to your controller.

### 2. The simulation hangs indefinitely

- **Cause:** This is usually because another process (such as another instance of a  TDW build) that is using the same port and received a message intended  for the TDW build.
- **Solution:** Kill all controller processes and build processes.

### 3. `zmq.error.ZMQError: Address in use`

- **Cause:** There is another controller process using this socket.
- **Solution:** Kill all controller processes and build processes. Launch each controller + build on a separate port.

**`requests.exceptions.ConnectionError: HTTPSConnectionPool(host='github.com', port=443): Max retries exceeded with url:`**

- **Cause:** You tried launching the build. Your build is out of date. The controller tried to get the latest version of TDW but failed due to an internet connection error.
- **Solution:** Kill the controller process. Kill the build process. Either enable your Internet connection or set `launch_build=False` in the constructor. Note that if you don't have an Internet connection, you won't be able to add any objects to the scene.

### 4. The simulation behaves differently on different machines / Physics aren't deterministic

- **Cause:** This is how the Unity physics engine works.
- **Solution:** Differences in behavior between machines should be *very* minor. Because the issue is intrinsic to PhysX, we can *reduce* determinism problems but we can't totally *fix* them.

### 5. The simulation is slow

- **Cause:** There are two common causes:
  - You're running TDW without a GPU.
  - Your code isn't optimized.
- **Solution:**
  - On Linux servers, make sure that TDW is using a GPU.
  - [Read the documentation for performance optimizations](performance_optimizations.md).

### 6. There are no shadows in the scene / rendering quality is generally poor

- **Cause:** There are two common causes:
  - You're running TDW without a GPU or your GPU isn't powerful. Certain rendering steps won't occur if the GPU is incapable of doing them; some of the more obvious examples are shadows and reflections.
  - You're using a low render quality setting. Render quality settings can sometimes carry between build process instances; this appears to be a Unity Engine bug.
- **Solution:**
  - On Linux servers, make sure that TDW is using a GPU.
  - Send [`{"$type": "set_render_quality", "render_quality": 5}`](../../api/command_api.md#set_render_quality) to set the build to the maximum render quality level.

### 7. Images are upside-down

- **Cause:** This is caused by your computer/GPU's graphics API.
- **Solution**:  
  - If `launch_build=True`, you can add `--flip_images` to any controller that you run, for example: `python3 my_controller.py --flip_images`.
  - If `launch_build=False`, you can add `-flip_images` to your build's launch path, for example: `./TDW.x86_64 -flip_images`.


**[Linux:] Can't launch the simulation in a Docker container**

- **Cause:** Either there is a problem with your Docker image or you have `launch_build=True` in the `Controller` constructor.
- **Solution:** [TDW Docker image](../setup/install.md). Set `launch_build=False` in the `Controller` constructor.

## Linux

### 1. Images are grainy / very dark / obviously glitchy

- **Cause:** [Check the player log.](https://docs.unity3d.com/Manual/LogFiles.html) If there are thousands of repeating errors about OpenGL, this is a known issue when running TDW on certain Linux machines.

- **Solution:** 
  - Update all packages. This usually solves the problem.
  -  If `launch_build=True`, add `--force-glcore42` to any controller that you run, for example: `python3 my_controller.py --force_glcore42`. 
  -  If `launch_build=False`, add the `-force-glcore42` flag to the build launch path, for example: `./TDW.x86_64 -force-glcore42`

### 2. The build segfaults as soon as it runs

- **Cause:** Segfaults are rare and relatively hard to debug. Below is a solution to the most common segfault; if that doesn't work, please post a GitHub Issue.
- **Solution:** Make sure that unzip didn't fail and that the executable (`TDW.x86_64`) is in the same directory as `TDW_Data`:

  ```
  TDW/
  ....TDW_Data/
  ....TDW.x86_64
  ```

### 3. The build segfaults when an avatar/camera is added to the scene

- **Cause:** Unknown but it has something to do with an incorrect or obsolete graphics API. Check [the player log](https://docs.unity3d.com/Manual/LogFiles.html) for errors having to do with graphics. 
- **Solution** Follow all steps in 1. described above.

### 4. Nothing happens after launching a minimal controller + build

- **Cause:** [Check the player log.](https://docs.unity3d.com/Manual/LogFiles.html) If you see `Desktop is 0 x 0 @ 0 Hz`, this means that your xorg isn't set up correctly.
- **Solution:**  [Read the install guide](../setup/install.md) for how to launch the build on a headless server; note that there must be a valid virtual display.

## MacOS

### 1. I can't run TDW.app in the terminal

- **Cause:** There is a file within TDW.app that you need to launch in the terminal. 
- **Solution:**
  - You can launch TDW.app by double-clicking it.
  - To launch TDW.app in the terminal: Right-click on the TDW.app file. Click `Show Package Contents`. Find the executable in the MacOS folder (e.g.  “TDW_v1.12.11”) and drag that to your bash shell window.

### 2. When I double-click TDW.app I get an error: `TDW.app is damaged and can't be opened`

- **Cause:** The app is not damaged. This is a known bug caused by TDW not adhering to MacOS code signing protocols.
- **Solution:** Move the app and `setup.sh` out of Downloads (for example, into your home directory). Run `setup.sh` (located in the same directory as TDW.app). This will repair TDW.app; you only need to run `setup.sh` once.

## Errors in the Player (build) log

To find the Player log, [read this](https://docs.unity3d.com/Manual/LogFiles.html).

### 1. `NullReferenceException`

- **Cause:** This usually means that one or more fields in your commands is  incorrect (i.e. you're sending the ID of an object that doesn't exist in the scene).
- **Solution:** Proofread your commands. If problems still persist, add a GitHub Issue.

### 2. `WARNING: Shader Unsupported`

This warning is harmless; you can ignore it.

### 3. `The referenced script on this Behaviour (Game Object '<NAME>') is missing!`

This warning is harmless; you can ignore it.

### 4. `Class not found: <type> [SerializationBinder]`

- **Cause:** You sent a command that doesn't exist.
- **Solution:** Check the spelling of your commands.

### 5. `Newtonsoft.Json.JsonSerializationException`

- **Cause:** At least one of your commands is invalid. Common mistakes:
  - A command name is spelled wrong.
  - You sent an array such as `[0, 0, 0]` instead of a dictionary such as `{"x": 0, "y": 0, "z": 0}`.
  - You sent the wrong type of parameter, such as sending a dictionary when the API expects a float.
- **Solution:** Read the message carefully; it includes the last message sent to the build and indicates where in the string the error is.

### 6. `SocketException: Could not resolve host 'localhost'`

- **Cause:** `localhost` isn't a listed host.
- **Solution:** To add `localhost` to your computer's list of hosts, read [this](https://apple.stackexchange.com/a/307029).

### 7. `The code execution cannot proceed because UnityPlayer.dll was not found. Reinstalling the program may fix this problem.`

- **Cause:**  TDW.exe is in the wrong directory; it must be in the same directory as all of the other files from the .zip file.

- **Solution:** Make sure that the executable `TDW.exe` is in the same folder as the other unzipped files:

  ```
  TDW/
  ....MonoBleedingEdge/
  ....TDW_Data/
  ....UnityCrashHandler64.exe
  ....UnityPlayer.dll
  ....TDW.exe
  ```

***

**Next: [Performance optimizations](performance_optimizations.md)**

[Return to the README](../../../README.md)