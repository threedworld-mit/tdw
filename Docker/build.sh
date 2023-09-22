#!/bin/bash

# Get the most recent version of TDW by checking the version.py script on Gitub.
TDW_VERSION=$(curl -s https://raw.githubusercontent.com/threedworld-mit/tdw/master/Python/tdw/version.py)
[[ "$TDW_VERSION" =~ "__version__ = \"(.*?)\"" ]] && TDW_VERSION="${BASH_REMATCH[1]}"

# Get this computer's NVIDIA version.
# Source: https://github.com/mviereck/x11docker/wiki/NVIDIA-driver-support-for-docker-container#nvidia-driver-base-image
NVIDIA_VERSION="$(head -n1 </proc/driver/nvidia/version | awk '{ print $8 }')"

# Build the container.
docker build -t tdw/tdw:$VERSION --build-arg TDW_VERSION=$TDW_VERSION --build-arg NVIDIA_VERSION=$NVIDIA_VERSION .