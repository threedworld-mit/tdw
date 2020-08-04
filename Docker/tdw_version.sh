#!/bin/bash

# Get the version of TDW installed on this machine.
echo $(pip3 show tdw | grep 'Version:' | cut -d' ' -f2 | rev | cut -d. -f 2- | rev)
