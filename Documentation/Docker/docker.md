# Dockerized TDW

The TDW Dockerfile builds an Nvidia container with support for OpenGL and Cuda 8.0. Due to limitations in the hypervisor, it is not possible to run OpenGL within a container on macOS. The image can be built and launched directly from within a TDW controller (see docker_controller.py).

### Requirements

* Linux (Debian, Ubuntu, RHEL, CentOS, Fedora, etc.)
* Docker
	* Set Docker to run as a user in the Docker group. See this [link](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04).
	* Please test your nvidia-docker setup prior to starting TDW with Docker. The following command should execute succesfully: `docker run --gpus all nvidia/cuda:9.0-base nvidia-smi`

* nvidia graphics card
* [nvidia-container-toolkit](https://github.com/NVIDIA/nvidia-docker)
* nvidia drivers (> 418.xx)
* An active X server

### Usage

1. Add a GitHub [personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line) (with repo access) to gh-release.sh in the Docker folder

2. Allow the X server to accept local connections


```bash
xhost +local:root
```

3. Build the container, specifying the desired TDW version


```bash
docker build -t tdw:v.1.6.0
```

4. Launch the container

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

5.  Start controller

Note: `start_container.sh` automates steps 2, 3, and 4 of this process


### Docker within Docker

1. To launch a TDW docker container within another container (such as the Tensorflow container), pass:
```
-v /var/run/docker.sock:/var/run/docker.sock
-v /usr/bin/docker:/bin/docker
```
to your docker initialization options. 
