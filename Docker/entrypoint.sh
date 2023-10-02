#!/bin/bash

cd TDW
echo Display $1, Port $2, Address $3
DISPLAY=$1 ./TDW.x86_64 -port=$2 -address=$3
