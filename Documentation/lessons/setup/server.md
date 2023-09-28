###### Setup

# Setup TDW on a Linux server

## Requirements

- A Linux server. Typically, this is Ubuntu 20 or newer
- Python 3.8+
- An NVIDIA GPU
- **Up-to-date NVIDIA drivers** Check online for which package to install.
- **Xorg and an active X server** `sudo apt install -y gcc make pkg-config xorg`
- The server must have 8 or less GPUs. If there are more, you can temporarily disable them by editing xorg.conf. This is a Unity bug that they have told us they won't fix.

## You need to use sudo to install TDW 

Installing TDW on a server requires some admin privileges.

TDW runs on Unity3D, a video game engine. Unity3D requires a valid display buffer *even if it is not rendering.* Unity3D does offer a "headless" mode but because TDW *often* renders, it can't use headless mode. **Therefore, TDW needs an active X server, which requires sudo to start.**

Unity's rendering looks more photorealistic if the computer has a GPU. Without a GPU, Unity *cannot* render as realistically and rendering will be slower. Unity also offloads many physics calculations to the GPU; without a GPU, Unity's physics will be slower. **The server must therefore physically have a GPU, and the GPU must have up-to-date drivers, which requires sudo to install.**

The xorg.conf file will tell X displays to use a GPU. Without a valid xorg.conf file, TDW can't run with a GPU. **Generating an xorg.conf file requires sudo.**

If you want to run TDW in a Docker container, you still need sudo because the Docker container requires an active X server and NVIDIA drivers.


## With Docker

TODO

## Without Docker

