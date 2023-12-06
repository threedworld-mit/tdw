##### Setup

# Installing TDW

TDW is two applications that communicate with each other over a TCP/IP socket. You need to have both to run TDW. They can be on the same machine or on separate machines (such as a laptop and a remote server).

- **The build** is the 3D simulation environment. It is a windowed application that requires a display and a GPU.
- **The controller** is a Python script that communicates with the build. You write your own controller script (though this repo contains many examples).

These documents will explain how to install both the build executable and the Python code required to write TDW controller scripts.

- [Install TDW on a PC (Linux, MacOS, Windows)](pc.md) We recommend always starting with this.
- [Install TDW on a server](server.md)
- [Install TDW on a server in a Docker container](docker.md)
- [Install TDW on a PC and a server](pc_server.md)

***

**Next: [Upgrading TDW](upgrade.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [hello_world.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/setup/hello_world.py)
