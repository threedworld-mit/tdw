###### Setup

# Setup TDW on a PC (Linux, MacOS, Windows) and a server

It is possible to run your controller on a PC and your build on a remote server. This is often the slowest way to run TDW. If possible, you should run your controller *and* your build on the same remote server.

1. [Install the `tdw` module on your PC.](pc.md)
2. Install the TDW build on your server [outside a Docker container](server.md) or [inside a Docker container](docker.md).

When you run a controller, you must set `launch_build=False`. For more information, [read this](../core_concepts/launch_build.md).

When you run a build, you must set the address and port.

If you're running TDW [outside a Docker container](server.md):

```bash
DISPLAY=:0.0 ./TDW.x86_64 -port=1071 -address=the_controller_address
```

If you're running TDW [inside a Docker container](docker.md):

```bash
./run.sh 1071 the_controller_address 256 256
```

Replace `the_controller_address` with the actual network address of your PC.