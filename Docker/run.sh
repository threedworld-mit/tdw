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
PATTERN='__version__ = \"(.*?)\"'
[[ "$TDW_VERSION" =~ $PATTERN ]] && TDW_VERSION="${BASH_REMATCH[1]}"

xhost local:docker

# Run the container.
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --user="$(id --user):$(id --group)" \
  -e DISPLAY=${1:-':0'} \
  -e PORT=${2:-'1071'} \
  -e ADDRESS=${3:-'localhost'} \
  --network host \
  alters/tdw:$TDW_VERSION
