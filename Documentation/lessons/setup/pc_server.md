###### Setup

# Setup TDW on a PC (Linux, MacOS, Windows) and a server

It is possible to run your controller on a PC and your build on a remote server. This is often the slowest way to run TDW. If possible, you should run your controller *and* your build on the same remote server.

1. [Install the `tdw` module on your PC.](pc.md)
2. [Install the TDW build on your server.](server.md)

When you run a controller, you must set `launch_build=False`. For more information, [read this](../core_concepts/launch_build.md).

When you run a build, you must set the address and port:

```bash
DISPLAY=:0.0 ./TDW.x86_64 -port=1071 -address=replace_with_the_controller_address
```

The controller address is the network address of your PC.