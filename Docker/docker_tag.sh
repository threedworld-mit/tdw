#!/bin/bash

# Get the tag of the Docker image installed on this machine.
echo $(docker images tdw | grep tdw | column -t | cut -d' ' -f3)
