##### Setup

# Auto-launching the TDW build

By default, a TDW controller will automatically launch a build when it runs. **However, the build won't work if auto-launched on a Linux server.** This is because it's too difficult to automatically predict the display settings of a server.

This will work if the build is running on a personal computer:

```python
from tdw.controller import Controller

c = Controller()
c.communicate({"$type": "terminate"})
```

On a Linux server, you must set the `launch_build` parameter of the Controller constructor to `False`:

```python
from tdw.controller import Controller

c = Controller(launch_build=False)
c.communicate({"$type": "terminate"})
```

Then, download, extract, and run the [latest version of the build](https://github.com/threedworld-mit/tdw/releases/latest/).

All of the code snippets in the TDW documentation are set up to automatically launch the build. If you want to try running them on a Linux server, just remember to add `launch_build=False` to the controller constructor.

## Desktop computers

You can set `launch_build=False` on a personal computer as well (in which case you'll need to [download the build manually](https://github.com/threedworld-mit/tdw/releases/latest/)).

**If you are using OS X, you'll need to run the shellscript located in the same directory as TDW.app before running TDW for the first time.** This is handled automatically if `launch_build=True`.

If you've already launched the build automatically via `Controller()`, the location of the build is always `~/tdw_build` where `~` is your home directory.

***

**Next: [Commands](commands.md)**

[Return to the README](../../../README.md)