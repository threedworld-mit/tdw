#!/bin/bash

# Usage:
#
# ./start_container.sh PORT ADDRESS
#
# Example 1:
#
# ./start_container.sh
#
# Example 2:
#
# ./start_container.sh 1071 localhost

# Get the most recent version of TDW by checking the version.py script on Gitub.
TDW_VERSION=$(curl -s https://raw.githubusercontent.com/threedworld-mit/tdw/master/Python/tdw/version.py)
PATTERN='__version__ = \"(.*?)\"'
[[ "$TDW_VERSION" =~ $PATTERN ]] && TDW_VERSION="${BASH_REMATCH[1]}"

# Run the container.
x11docker \
  --gpu \
  --desktop \
  --runtime=nvidia \
  --env PORT=${1:-'1071'} \
  --env ADDRESS=${2:-'localhost'} \
  --network=host \
  --workdir / -- \
  alters/tdw:$TDW_VERSION
