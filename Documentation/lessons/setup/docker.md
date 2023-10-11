###### Setup

# Setup TDW in a Docker container

You can run the TDW build inside and outside a Docker container. There are advantages and disadvantages to either approach:

If you run TDW inside a Docker container, it can't use a GPU. This means that rendering will be slow and not as photorealistic. The Docker container is mainly suitable only for projects that don't require rendering or don't have sudo access.

If you run TDW outside a Docker container, it can use a GPU and run much faster. However, you need sudo access to configure the server.

This document describes how to run TDW inside a Docker container. To learn how to run TDW outside a Docker container, [read this](server.md).

## Requirements

- Python 3.8+ (optionally, conda)
- A Linux server. 
- Docker

## Install

### Pull the Docker image

1. `pip install tdw`
2. Clone this repo or download everything in [this folder](https://github.com/threedworld-mit/tdw/tree/master/Docker).
3. `cd tdw/Docker` or to the folder you downloadded the Docker files into.
4. Pull the Docker image by running `./pull.sh` The image is `alters/tdw:VERSION` where `VERSION` is the latest version of TDW.

If you want to build the image yourself, you can instead run `./build.sh`

## Run

In one shell, start running the Docker container:

1. `cd tdw/Docker` or to the folder you downloadded the Docker files into.
2. `./run.sh` to run the container. You can optionally set the port, network address, screen width, and screen height: `./run.sh 1071 localhost 256 256`

Write this controller:

```python
from tdw.controller import Controller

port = 1071
c = Controller(launch_build=False, port=port)
print("Hello world!")
c.communicate({"$type": "terminate"})
```

Make sure that `port` matches the port value used in `run.sh`

3. `python3 name_of_the_controller.py`

Result: The controller prints "Hello world!" and exits. The Docker container prints a log and exits.