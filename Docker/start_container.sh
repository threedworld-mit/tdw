#!/bin/bash

DISPLAY=":${1}"

# Make sure we have the right image.
$(./pull.sh)
VERSION=$(./tdw_version.sh)

# Allow x server to accept local connections
xhost +local:root

# Run the container
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --network host \
  tdw:$VERSION \
  ./TDW/TDW.x86_64
