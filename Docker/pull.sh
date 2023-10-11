#!/bin/bash

# Check if your Docker image matches your installed TDW version.
# If not, pull the correct image.

TDW_VERSION=$(curl -s https://raw.githubusercontent.com/threedworld-mit/tdw/master/Python/tdw/version.py)
PATTERN='__version__ = \"(.*?)\"'
[[ "$TDW_VERSION" =~ $PATTERN ]] && TDW_VERSION="${BASH_REMATCH[1]}"
DOCKER_TAG=$(./tag.sh)

if [ "$TDW_VERSION" != "$DOCKER_TAG" ]
  then
    echo "No Docker image found that matches TDW v${TDW_VERSION}. Trying to pull now..."
    docker pull alters/tdw:$TDW_VERSION
fi
