#!/bin/bash

echo $DISPLAY
cd TDW
echo $2:$1
DISPLAY=$DISPLAY ./TDW.x86_64 -port=$1 -address=$2 -logFile /home/alters/tdw.txt
cat /home/alters/tdw.txt