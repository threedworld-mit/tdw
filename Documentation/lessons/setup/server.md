###### Setup

# Setup TDW on a Linux server

## Requirements

- A Linux server. Typically, this is Ubuntu 20 or newer
- Python 3.8+
- An NVIDIA GPU
- **Server: Up-to-date NVIDIA drivers on the** Check online for which package to install.
- **Server: Xorg and an active X server** `sudo apt install -y gcc make pkg-config xorg`
- The server must have 8 or less GPUs. If there are more, you can temporarily disable them by editing xorg.conf. This is a Unity bug that they have told us they won't fix.
- Optional: Docker

## You need to use sudo to install TDW 

Installing TDW on a server requires some admin privileges.

TDW runs on Unity3D, a video game engine. Unity3D requires a valid display buffer *even if it is not rendering.* Unity3D does offer a "headless" mode but because TDW *often* renders, it can't use headless mode. **Therefore, TDW needs an active X server, which requires sudo to start.**

Unity's rendering looks more photorealistic if the computer has a GPU. Without a GPU, Unity *cannot* render as realistically and rendering will be slower. Unity also offloads many physics calculations to the GPU; without a GPU, Unity's physics will be slower. **The server must therefore physically have a GPU, and the GPU must have up-to-date drivers, which requires sudo to install.**

The xorg.conf file will tell X displays to use a GPU. Without a valid xorg.conf file, TDW can't run with a GPU. **Generating an xorg.conf file requires sudo.**

**If you want to run TDW in a Docker container, you still need sudo** because the Docker container requires an active X server and NVIDIA drivers.

## Create an xorg.conf file

The xorg.conf file tells Xorg that the computer has displays and that they can be run on GPUs.

1. Run `nvidia-xconfig --query-gpu-info`. This will list all the GPUs and their bus ids
2. Run `nvidia-xconfig --no-xinerama --probe-all-gpus --use-display-device=none`. This will generate xorg.conf (/etc/X11/xorg.conf) file
3. Make *n* copies of this file for *n* GPUs. You can name each file as xorg-1.conf, xorg-2.conf ... xorg-n.conf
4. Edit each file:
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
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
EndSection
```
...to...

```
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
Section "Device"
    Identifier     "Device1"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
EndSection
```

...to...

```
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

## Install TDW

1. ssh into the server
2. `pip install tdw`
3. Download [the latest build of TDW](https://github.com/threedworld-mit/tdw/releases/latest/) and extract the zip file.
4. Create this Python script and run it:

```python
from tdw.controller import Controller

port = 1071
c = Controller(launch_build=False, port=port)
print("Hello world!")
c.communicate({"$type": "terminate"})
```

In another shell:

1. ssh into the server
2. `cd` to wherever you downloaded the build.
3. `DISPLAY=:0 ./TDW.x86_64 -port 1071` Replace `:0`  with a valid display value.

**Result:** The terminal window will print messages about downloading a build. Then, it will launch a windowed application, print `Hello world!`, kill the windowed application process, and exit.

Test image capture by repeating the same steps but with this controller:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

camera = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                           avatar_id="a",
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("image_capture")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)

c = Controller(launch_build=False)
c.add_ons.extend([camera, capture])
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(c.get_add_physics_object(model_name="iron_box",
                                         position={"x": 0, "y": 0, "z": 0},
                                         object_id=object_id))
c.communicate(commands)
c.communicate({"$type": "terminate"})
```

Result:

![](images/box.jpg)

## Always set `launch_build=False`

On Linux servers, always set `launch_build=False` in your controllers. For more information, [read this](../core_concepts/launch_build.md).

## Docker

**The requirements for Docker are the same as those for non-Docker setups.** The host computer have a GPU + drivers, xorg.conf file, and must be running Xorg. In the future, we hope to make it possible to run Xorg from within a Docker file with its own internal xorg.conf file.

To build our Docker container, first clone this repo and then:

```bash
cd tdw/Docker
./install.sh
./build.sh
```

To pull from Dockerhub instead:

```bash
cd tdw/Docker
./pull.sh
```

To run the TDW Docker container:

```bash
cd tdw/Docker 
./run.sh DISPLAY PORT ADDRESS
```

For example: `./run.sh :0 1071 localhost`\

##  Troubleshooting

See [this list of common problems](../troubleshooting/common_errors.md). If you don't see your problem on the list, let us know by opening a GitHub Issue.
