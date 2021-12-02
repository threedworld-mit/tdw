##### Misc. remote server topics

# Remote rendering with xpra

It is desirable while debugging to be able to view a remote rendering process. In order to forward the X server to your local screen, we recommend [Xpra](https://www.xpra.org/trac/wiki/Download) in combination with [VirtualGL](https://sourceforge.net/projects/virtualgl/files).
# Installation instructions
1. Install Xpra on both client and server
2. Install VirtualGL on server. Note: if using Docker, this is already included in the Docker image

# Usage instructions

On server: 

1. Start xpra
```bash
xpra start :80
```
2. Start TDW using VirtualGL
```bash
DISPLAY=:80 vlgrun -d :0 ./tdw.x86_64
```
On client:

3. 
```bash
xpra attach --ssh=ssh ssh/server_hostname/80
```

See `tdw/Docker/start_container_xpra.sh` for an example script that executes the server side steps.

Note, if using Docker, xhost +local:root needs to be set for the virtual display (xpra) and the X server used to run VirtualGL

```bash
DISPLAY=:0 
xhost +local:root

DISPLAY=:80
xhost +local:root
```

Notes:
On newer Nvidia driver versions (>440), applications may be locked at 1 fps. For the fix, see [here](https://wiki.archlinux.org/index.php/VirtualGL#Problem:_All_applications_run_with_1_frame_per_second).

***

**This is the last document in the "Misc. remote server topics" tutorial.**

[Return to the README](../../../README.md)

