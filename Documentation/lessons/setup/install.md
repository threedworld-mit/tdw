##### Setup

# Installing TDW

TDW is two applications that communicate with each other over a TCP/IP socket. You need to have both to run TDW. They can be on the same machine or on separate machines (such as a laptop and a remote server).

- **The build** is the 3D simulation environment. It is a windowed application that requires a display and a GPU.
- **The controller** is a Python script that communicates with the build. You write your own controller script (though this repo contains many examples).

This document will explain how to install both the build executable and the Python code required to write TDW controller scripts.

## System Requirements

- Windows, OS X, or Linux (we've tested TDW on Ubuntu 16, 18, and 20)
- Python 3.6+
- A GPU, the faster the better, with up-to-date drivers. It is possible to run TDW without a GPU but you will lose some speed and photorealism.
- For [audio simulations](../audio/overview.md), you will need an audio driver.
- [Flex](../flex/flex.md) has complicated requirements; please refer to the linked document.
- **Additional Linux server requirements:**
  - An active X server
  - nvidia graphics card
  - nvidia drivers (> 418.xx)
  - The server must have 8 or less GPUs. (If there are more, you can temporarily disable them by editing xorg.conf)
- **Additional Docker container requirements:**
  - Set Docker to run as a user in the Docker group. See this [link](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04).
  - Please test your nvidia-docker setup prior to starting TDW with Docker. The following command should execute succesfully: `docker run --gpus all nvidia/cuda:9.0-base nvidia-smi`
  - [nvidia-container-toolkit](https://github.com/NVIDIA/nvidia-docker)

## Install TDW on a personal computer

**We recommend installing TDW on a personal computer before attempting to install TDW on a remote server.** Installing on a personal computer is easier and it may help you understand the fundamentals of TDW.

1. OS X and Linux: **`sudo pip3 install tdw`** Windows: **`pip3 install tdw --user`** 
2. Create this Python script and run it:

```python
from tdw.controller import Controller

c = Controller()
print("Hello world!")
c.communicate({"$type": "terminate"})
```

**Result:** The terminal window will print messages about downloading a build. Then, it will launch a windowed application, print `Hello world!`, kill the windowed application process, and exit.

## Install TDW on a remote Linux server

#### Install NVIDIA and X on your server

1. Download and install latest NVIDIA drivers for the machine
2. Install xorg and dependencies `sudo apt-get install -y gcc make pkg-config xorg`
3. Run `nvidia-xconfig --query-gpu-info`. This will list all the GPUs and their bus ids
4. Run `nvidia-xconfig --no-xinerama --probe-all-gpus --use-display-device=none`. This will generate xorg.conf (/etc/X11/xorg.conf) file
5. Make *n* copies of this file for *n* GPUs. You can name each file as xorg-1.conf, xorg-2.conf ... xorg-n.conf
6. Edit each file:
   1. Remove ServerLayout and Screen section
   2. Edit Device section to include the BusID and BoardName field of the corresponding GPU. You can get GPU list by running `nvidia-xconfig --query-gpu-info`

For example if `nvidia-xconfig --query-gpu-info` outputs two GPUs:

```
Number of GPUs: 2

GPU #0:
  Name      : Tesla V100-PCIE-16GB
  UUID      : GPU-bbf6c915-de29-6e08-90e6-0da7981a590b
  PCI BusID : PCI:0:7:0

  Number of Display Devices: 0


GPU #1:
  Name      : Tesla V100-PCIE-16GB
  UUID      : GPU-2a69c672-c895-5671-00ba-14ac43a9ec39
  PCI BusID : PCI:0:8:0

  Number of Display Devices: 0
```

Then create two xorg.conf files and edit the device section for first file:

```
This ->
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
EndSection
To ->
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "Tesla V100-PCIE-16GB"
    BusID          "PCI:0:7:0"
EndSection
```

And

```
This ->
Section "Device"
    Identifier     "Device1"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
EndSection
To ->
Section "Device"
    Identifier     "Device1"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "Tesla V100-PCIE-16GB"
    BusID          "PCI:0:8:0"
EndSection
```

7. Run x-server. For each xorg configuration file run `sudo nohup Xorg :<Display server name> -config <configuration file name> & `:

```
sudo nohup Xorg :1 -config /etc/X11/xorg-1.conf & 
```

```
sudo nohup Xorg :2 -config /etc/X11/xorg-2.conf &
```

8. When successfully done, running `nvidia-smi` should show the x-server proccess with corresponding GPU version

#### Install TDW

1. `sudo pip3 install tdw`
2. Download [the latest build of TDW](https://github.com/threedworld-mit/tdw/releases/latest/) and extract the zip file.
3. Verify that you can run TDW by running a minimal example. Create this Python script and save it as `my_controlller.py`:

```python
from tdw.controller import Controller

port = 1071  # This is the default port. You can change this.
c = Controller(launch_build=False, port=port) 
print("Hello world!")
c.communicate({"$type": "terminate"})
```

4. In one shell window, run the controller: `python3 my_controller.py`
5. Open another shell window.
6. In the second shell window, `cd` to the location of the build (`TDW.x86.64`)
7. In the second window, launch the build. Include the `DISPLAY` environment variable. This should match the display number of the virtual display (see "Install", above):

```bash
DISPLAY=:0.0 ./TDW.x86_64 -port=1071
```

## Install TDW in a Docker container

1. Follow the above instructions for installing X on your server.
2. Install Docker and nvidia-docker. [Read this for more information.](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)
3. Allow the X server to accept local connections:

```bash
xhost +local:root
```

4. Pull a Docker container that matches your version of TDW:

```bash
cd tdw/Docker
```


```bash
./pull.sh
```

5. Verify that you can run TDW by running a minimal example. Create this Python script and save it as `my_controlller.py`:

```python
from tdw.controller import Controller

port = 1071  # This is the default port. You can change this.
c = Controller(launch_build=False, port=port) 
print("Hello world!")
c.communicate({"$type": "terminate"})
```

6. Run your controller.
7. Launch the container. [This is an example launch script.](https://github.com/threedworld-mit/tdw/blob/master/Docker/start_container.sh) You can also [use xpra for remote rendering](https://github.com/threedworld-mit/tdw/blob/master/Docker/start_container_xpra.sh).

We have [many other useful Docker scripts](https://github.com/threedworld-mit/tdw/tree/master/Docker).

It's also possible to run Docker within Docker (such as a Tensorflow container). Pass these to your Docker initialization options:

```bash
-v /var/run/docker.sock:/var/run/docker.sock
-v /usr/bin/docker:/bin/docker
```

## Install TDW on a personal computer and a remote Linux server

1. Follow directions for installing TDW on your personal computer.
2. Follow instructions for installing X on your Linux server.
3. On the Linux server, download [the latest build of TDW](https://github.com/threedworld-mit/tdw/releases/latest/) and extract the zip file.
4. On the Linux server,  `cd` to the location of the build (`TDW.x86.64`)
5. On the Linux server, launch the build. Include:
   - The `DISPLAY` environment variable, which should match the display number of the virtual display (see "Install", above)
   - The `-port` parameter (which should match the port of the controller)
   - The `-address` parameter (which should match the network address of the controller)

```bash
DISPLAY=:0.0 ./TDW.x86_64 -port=1071 -address=replace_with_the_controller_address
```

***

**Next: [Upgrading TDW](upgrade.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [hello_world.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/setup/hello_world.py)
