##### How to run TDW on a Linux server

# X11 fowarding

Follow these steps to enable X11 forwarding from a local machine. 

## OS X

This has been tested on macOs13.3.1:

1. Install XQuartz
2. Open a terminal and run `ssh -X username@serverdomain`
3. In the same terminal, `echo $DISPLAY` to ensure that there is a valid display.
4. In the same terminal, open a tmux session on the server and launch the build: `./TDW.x86_64 -port=1071`, notice that you don’t need to specify the display number because it has been set automatically. You should be able to see a TDW window pops up on your local machine.
5. Open a second terminal and run `ssh -X username@serverdomain`
6. In the second terminal, open a tmux session on the server and run this example controller: 

```python
from tdw.controller import Controller

c = Controller(launch_build=False) 
print("Hello world!")
c.communicate({"$type": "terminate"})
```

Result: The console prints `Hello world!` and exits.

If you intend to spawn many jobs on the server,  this method is not ideal because it will span many windows on your local machine. [Try this instead.](https://stackoverflow.com/a/8961649)

## Windows

X11 forwarding hasn't been tested on Windows yet. If you know how to set up X11 forwarding on Windows, please let us know.

## Linux

X11 forwarding hasn't been tested on Linux yet. If you know how to set up X11 forwarding on Linux, please let us know.


***

**This is the last document in the "Misc. remote server topics" tutorial.**

[Return to the README](../../../README.md)