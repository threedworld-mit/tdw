## General usage errors

**Can't launch the simulation in a Docker container**

- **Cause:** Either there is a problem with your Docker image or you have `launch_build=True` in the `Controller` constructor.
- **Solution:** [TDW Docker image](../setup/install.md). Set `launch_build=False` in the `Controller` constructor.

**Images are grainy / very dark / obviously glitchy**

- **Cause:** [Check the player log.](https://docs.unity3d.com/Manual/LogFiles.html) If there are thousands of repeating errors about OpenGL, this is a known issue when running TDW on certain Linux machines.

- **Solution:** Run the build in OpenGL 4.2:

  ```bash
  ./TDW.x86_64 -force-glcore42
  ```

**On a Linux server, nothing happens after launching a minimal controller + build**

- **Cause:** [Check the player log.](https://docs.unity3d.com/Manual/LogFiles.html) If you see `Desktop is 0 x 0 @ 0 Hz`, this means that your xorg isn't set up correctly.
- **Solution:**  [Read the install guide](../setup/install.md) for how to launch the build on a headless server; note that there must be a valid virtual display.

**The simulation hangs indefinitely**

- **Cause:** This is usually because another process (such as another instance of a  TDW build) that is using the same port and received a message intended  for the TDW build.
- **Solution:** Kill all controller processes and build processes.

**The simulation behaves differently on different machines / Physics aren't deterministic**

- **Cause:** This is how the Unity physics engine works.
- **Solution:** Differences in behavior between machines should be *very* minor. Because the issue is intrinsic to PhysX, we can *reduce* determinism problems but we can't totally *fix* them.

## Errors in the Python (controller) console

**`zmq.error.ZMQError: Address in use`**

- **Cause:** There is another controller process using this socket.
- **Solution:** Kill all controller processes and build processes. Launch each controller + build on a separate port.

**`requests.exceptions.ConnectionError: HTTPSConnectionPool(host='github.com', port=443): Max retries exceeded with url:`**

- **Cause:** You tried launching the build. Your build is out of date. The controller tried to get the latest version of TDW but failed due to an internet connection error.
- **Solution:** Kill the controller process. Kill the build process. Either enable your Internet connection or set `launch_build=False` in the constructor. Note that if you don't have an Internet connection, you won't be able to add any objects to the scene.

**`The build quit due to an error. Check the build log for more info.`**

- **Cause:** The build quit due to an error.
- **Solution:** [Check the player log.](https://docs.unity3d.com/Manual/LogFiles.html) See below for possible causes.

## Errors in the Player (build) log

**`NullReferenceException`**

- **Cause:** This usually means that one or more fields in your commands is  incorrect (i.e. you're sending the ID of an object that doesn't exist in the scene).
- **Solution:** Proofread your commands. If problems still persist, add a GitHub Issue.

**`WARNING: Shader Unsupported`**

This warning is harmless; you can ignore it.

**`The referenced script on this Behaviour (Game Object '<NAME>') is missing!`**

This warning is harmless; you can ignore it.

**Segfault (Linux only)**

- **Cause:** Segfaults are rare and relatively hard to debug. Below is a solution to the most common segfault; if that doesn't work, please post a GitHub Issue.

- **Solution:** Make sure that unzip didn't fail and that the executable (`TDW.x86_64`) is in the same directory as `TDW_Data`:

  ```
  TDW/
  ....TDW_Data/
  ....TDW.x86_64
  ```

**`The code execution cannot proceed because UnityPlayer.dll was not found. Reinstalling the program may fix this problem.`**

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

**`Class not found: <type> [SerializationBinder]`**

- **Cause:** You sent a command that doesn't exist.
- **Solution:** Check the spelling of your commands.

**`Newtonsoft.Json.JsonSerializationException`**

- **Cause:** At least one of your commands is invalid. Common mistakes:
  - A command name is spelled wrong.
  - You sent an array such as `[0, 0, 0]` instead of a dictionary such as `{"x": 0, "y": 0, "z": 0}`.
  - You sent the wrong type of parameter, such as sending a dictionary when the API expects a float.
- **Solution:** Read the message carefully; it includes the last message sent to the build and indicates where in the string the error is.

