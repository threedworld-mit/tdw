#!/bin/bash

# Set render target for virtualgl
DISPLAY=":${1}"

# Make sure we have the right image.
$(./pull.sh)
VERSION=$(./tdw_version.sh)


# Allow x server to accept local connections
xhost +local:root

# Start virtual display for xpra
xpra start :80

# Set render target of virtual display (xpra) 
DISPLAY=:80

# Allow xpra x server to accept local connections
xhost +local:root

# Run the container
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$1 \
  --network host \
  vglrun -d :0 \
  tdw:$VERSION \
  ./TDW/TDW.x86_64
