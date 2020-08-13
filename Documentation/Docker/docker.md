# Dockerized TDW

The TDW Dockerfile builds an Nvidia container with the following:

- OpenGL (Due to limitations in the hypervisor, it is not possible to run OpenGL within a container on macOS. The image can be built and launched directly from within a TDW controller (see docker_controller.py).
- Cuda 8.0
- pulseaudio

## Requirements

* Linux (Debian, Ubuntu, RHEL, CentOS, Fedora, etc.)
* Docker
	* Set Docker to run as a user in the Docker group. See this [link](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04).
	* Please test your nvidia-docker setup prior to starting TDW with Docker. The following command should execute succesfully: `docker run --gpus all nvidia/cuda:9.0-base nvidia-smi`
* nvidia graphics card
* [nvidia-container-toolkit](https://github.com/NVIDIA/nvidia-docker)
* nvidia drivers (> 418.xx)
* An active X server

## Usage

1. Allow the X server to accept local connections

```bash
xhost +local:root
```

2. Pull a Docker container that matches [your version of TDW](../python/tdw.md):

```bash
cd tdw/Docker
```


```bash
./pull.sh
```

4. Start your controller.
5. Launch the container. Below is an example, but we have other bash scripts:

```bash
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --network host \
  tdw:1.6.0 \
  ./TDW.TDW.x86_64
```

## Bash scripts

All Docker-related bash scripts are in [`tdw/Docker`](https://github.com/threedworld-mit/tdw/tree/master/Docker):

### Scripts that launch a container

| Script                                                       | Arguments                                                    | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [`start_container.sh`](https://github.com/threedworld-mit/tdw/tree/master/Docker/start_container.sh) |                                                              | Start the container and run TDW.                             |
| [`start_container_xpra.sh`](https://github.com/threedworld-mit/tdw/tree/master/Docker/start_container_xpra.sh) |                                                              | Start the container with [Xpra](../misc_frontend/xpra.md) and run TDW. |
| [`start_container_audio_video.sh VOLUME IPADDRESS PORT`](https://github.com/threedworld-mit/tdw/tree/master/Docker/start_container_audio_video.sh) | `VOLUME` Save audio to this volume<br>`IPADDRESS` The address of the build.<br>`PORT` The port of the build. | [Record audio and video](../misc_frontend/video.md) from TDW. |

### Other scripts

| Script                                                       | Arguments                                                    | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [`pull.sh`](https://github.com/threedworld-mit/tdw/tree/master/Docker/pull.sh) |                                                              | Try to download a Docker container from DockerHub with a tag that matches the version of TDW on this machine. |
| [`docker_tag.sh`](https://github.com/threedworld-mit/tdw/tree/master/Docker/docker_tag.sh) |                                                              | Get the tag of the TDW Docker image.                         |
| [`tdw_version.py`](https://github.com/threedworld-mit/tdw/tree/master/Docker/tdw_version.py) |                                                              | Get the version of TDW on this machine.                      |
| [`record_audio_video.sh ADDRESS PORT WIDTH HEIGHT`](https://github.com/threedworld-mit/tdw/tree/master/Docker/record_audio_video.sh) | `ADDRESS` The network address of the build.<br>`PORT` The network port of the build<br> `WIDTH` The desired width of the video in pixels.<br>`HEIGHT` The desired height of the video in pixels. | Launch TDW and begin recording audio.                        |


## Docker within Docker

1. To launch a TDW docker container within another container (such as the Tensorflow container), pass:
```
-v /var/run/docker.sock:/var/run/docker.sock
-v /usr/bin/docker:/bin/docker
```
to your docker initialization options. 
