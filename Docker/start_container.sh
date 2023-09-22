#!/bin/bash

# Usage:
#
# ./start_container.sh DISPLAY PORT ADDRESS
# 
# Example 1:
#
# ./start_container.sh
#
# Example 2:
#
# ./start_container.sh :0 1071 localhost

# Get the most recent version of TDW by checking the version.py script on Gitub.
TDW_VERSION=$(curl -s https://raw.githubusercontent.com/threedworld-mit/tdw/master/Python/tdw/version.py)
[[ "$TDW_VERSION" =~ "__version__ = \"(.*?)\"" ]] && TDW_VERSION="${BASH_REMATCH[1]}"

# Run the container.
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=${0:-':0'} \
  -e PORT=${1:-'1071'} \
  -e ADDRESS=${2:-'localhost'} \
  --network host \
  tdw/tdw:$TDW_VERSION
