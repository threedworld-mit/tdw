# Installation

## System Requirements

- Windows, OS X, or Linux (we've tested TDW on Ubuntu 16 and 18)
- Python 3.6+
- A GPU, the faster the better, with up-to-date drivers. It is possible to run TDW without a GPU but you will lose some speed and photorealism.
- For [audio/video recording](misc_frontend/video.md), you will need an audio driver.
- [Flex](misc_frontend/flex.md) has complicated requirements; please refer to the linked document.
- **Additional Linux server requirements:**
  - The build requires X
  - The server must have 8 or less GPUs. (If there are more, you can temporarily disable them by editing xorg.conf)

## Install TDW

### On a Linux server

1. `sudo pip3 install tdw`
2. Set up a virtual display. (Not all of these commands will be applicable to every server. The `:0` is the display number, which might vary between servers.)

```bash
sudo service lightdm stop
sudo killall Xorg
sudo nvidia-xconfig -a --use-display-device=None --virtual=256x256
sudo /usr/bin/X :0&
```

3. Download [the latest build of TDW](https://github.com/threedworld-mit/tdw/releases/latest/) and extract the zip file.

### On a personal computer

1. OS X and Linux: `sudo pip3 install tdw` Windows: `pip3 install tdw --user` 

## Run a minimal example of TDW

### On a Linux server

1. Create this Python script and save it as `my_controlller.py`:

```python
from tdw.controller import Controller

c = Controller(launch_build=False, port=1071) # This is the default port.
print("Everything is OK!")
c.communicate({"$type": "terminate"})
```

2. In one shell window, run the controller: `python3 my_controller.py`
3. Open another shell window.
4. In the second shell window, `cd` to the location of the build (TDW.x86.64)
5. In the second window, launch the build. Include the `DISPLAY` environment variable. This should match the display number of the virtual display (see "Install", above):

```bash
DISPLAY=:0.0 ./TDW.x86_64 -port=1071
```

### In a Docker container

**[Read this](https://github.com/threedworld-mit/tdw/blob/v1.6.1/Documentation/Docker/docker.md).** We recommend first trying TDW on a personal computer to familiarize yourself with the basic setup.

### On a personal computer

1. Create this Python script and save it as `my_controller.py`:

```python
from tdw.controller import Controller

c = Controller()
print("Everything is OK!")
c.communicate({"$type": "terminate"})
```

2. Run the controller:
   - OS X and Linux: `python3 my_controller.py`
   - Windows: `py -3 my_controller.py`

When you launch run this script, the `Controller` will download the **build**, the binary executable application that runs the simulation environment and then launch the build. The controller will also check to see if your version of TDW is the most recent. For more information on what happens when you start a controller, read [this](misc_frontend/releases.md#Updates).

### From a personal computer to a remote Linux server

1. On your personal computer, create this Python script and save it as `my_controlller.py`:

```python
from tdw.controller import Controller

c = Controller(launch_build=False, port=1071) # This is the default port.
print("Everything is OK!")
c.communicate({"$type": "terminate"})
```

2. On the Linux server, download [the latest build of TDW](https://github.com/threedworld-mit/tdw/releases/latest/) and extract the zip file.
3. Run the controller:
   - OS X and Linux: `python3 my_controller.py`
   - Windows: `py -3 my_controller.py`
4. On the Linux server,  `cd` to the location of the build (TDW.x86.64)
5. On the Linux server, launch the build. Include:
   - The `DISPLAY` environment variable, which should match the display number of the virtual display (see "Install", above)
   - The `-port` parameter (which should match the port of the controller)
   - The `-address` parameter (which should match the network address of the controller)

```bash
DISPLAY=:0.0 ./TDW.x86_64 -port=1071 -address=replace_with_the_controller_address
```

***

Next: [Getting started with TDW](getting_started.md)

[Return to the README](../../README.md)
