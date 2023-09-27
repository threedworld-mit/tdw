#!/bin/bash

cd TDW
echo Display $1, Port $2, Address $3
DISPLAY=$0 ./TDW.x86_64 -port=$1 -address=$2
