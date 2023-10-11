#!/bin/bash

echo $(docker images alters/tdw | grep alters/tdw | column -t | cut -d' ' -f3)