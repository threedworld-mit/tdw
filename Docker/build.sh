#!/bin/bash

# Get the most recent version of TDW by checking the version.py script on Gitub.
tdw_version=$(curl -s https://raw.githubusercontent.com/threedworld-mit/tdw/master/Python/tdw/version.py)
pattern="__version__ = \"(.*?)\""
[[ "$tdw_version" =~ $pattern ]] && tdw_version="${BASH_REMATCH[1]}"

# Get this computer's NVIDIA version.
# Source: https://github.com/mviereck/x11docker/wiki/NVIDIA-driver-support-for-docker-container#nvidia-driver-base-image
nvidia_version="$(head -n1 </proc/driver/nvidia/version | awk '{ print $8 }')"

# Build the container.
docker build -t tdw/tdw:$VERSION --build-arg TDW_VERSION=$tdw_version NVIDIA_VERSION=$nvidia_version .