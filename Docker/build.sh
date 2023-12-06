#!/bin/bash

# Usage: ./build.sh VERSION
#
# Example: ./build.sh 1.12.13

docker build -t alters/tdw:$1 --build-arg TDW_VERSION=$1 .
