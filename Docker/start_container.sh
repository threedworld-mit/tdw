#!/bin/bash

VERSION=$(python3 ./tdw_version.py)

# Allow x server to accept local connections
xhost +local:root

# Run the container
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --network host \
  alters/tdw:$VERSION \
  ./TDW/TDW.x86_64
