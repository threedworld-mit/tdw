#!/bin/bash

cd TDW
echo Port $1, Address $2, $3x$4
xvfb-run --auto-servernum --server-args="-screen 0 $3x$4x24" \
    ./TDW.x86_64 -port=$1 -address=$2 -logFile /home/container/tdw.txt
cat /home/container/tdw.txt