# Auto-launching the TDW build

By default, a TDW controller will automatically launch a build when it runs. It will also automatically update the TDW build if it detects an out of date version:

```python
from tdw.controller import Controller

c = Controller()
```

To kill the build process, add a `terminate` command:

```python
from tdw.controller import Controller

c = Controller()
c.communicate({"$type": "terminate"})
```

**However, the build won't work if auto-launched on a Linux server.** This is because it's too difficult to automatically predict the display settings of a server. If you try running the previous example controller snippets on a Linux server, they won't work.

Instead, you must set the `launch_build` parameter to `False`:

```python
from tdw.controller import Controller

c = Controller(launch_build=False)
c.communicate({"$type": "terminate"})
```

Then, download an extract the [latest version of the build](https://github.com/threedworld-mit/tdw/releases/latest/). If you are using OS X, you'll need to run the shellscript located in the same directory as TDW.app the before running TDW for the first time (this is handled automatically if `launch_build=True`).

You can set `launch_build=False` on a personal computer as well (in which case you'll need to download the build manually; see the previous link).

All of the code snippets in these tutorials are set up to automatically launch the build. If you want to try running them on a Linux server, just remember to add `launch_build=False` to the controller constructor.

If you've already launched the build automatically via `Controller()`, the location of the build is always `~/tdw_build` where `~` is your home directory.

***

Next: [Upgrading TDW](upgrade.md)

[Return to the README](../../README.md)