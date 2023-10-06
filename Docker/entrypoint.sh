#!/bin/bash

cd TDW
echo Port $1, Address $2
./TDW.x86_64 -port=$1 -address=$2 -logFile /home/alters/tdw.txt
cat /home/alters/tdw.txt