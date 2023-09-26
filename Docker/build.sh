#!/bin/bash

# Get the most recent version of TDW by checking the version.py script on Gitub.
TDW_VERSION=$(curl -s https://raw.githubusercontent.com/threedworld-mit/tdw/master/Python/tdw/version.py)
PATTERN='__version__ = \"(.*?)\"'
[[ "$TDW_VERSION" =~ $PATTERN ]] && TDW_VERSION="${BASH_REMATCH[1]}"

# Build the container.
docker build -t tdw/tdw:$TDW_VERSION --build-arg TDW_VERSION=$TDW_VERSION .
