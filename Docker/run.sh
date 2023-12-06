#!/bin/bash

# Usage:
#
# ./run.sh PORT ADDRESS WIDTH HEIGHT
#
# Example 1:
#
# ./run.sh
#
# Example 2:
#
# ./run.sh 1071 localhost 256 256


# Run the container.
docker run -it \
  --rm \
  -e PORT=${1:-'1071'} \
  -e ADDRESS=${2:-'localhost'} \
  -e WIDTH=${3:-'256'} \
  -e HEIGHT=${4:-'256'} \
  --network host \
  alters/tdw:$(./tag.sh)