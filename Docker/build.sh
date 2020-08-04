#!/bin/bash

# Build the container.

TAG=$(./tdw_version.sh)
docker build -t tdw:$TAG --build-arg TDW_VERSION=$TAG .
