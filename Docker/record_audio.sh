#!/bin/bash
# Start pulse audio in background
pulseaudio -D
echo $1
echo $2
# Run ffmpeg
# Random file name
FILE_ID=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13 ; echo '')
FILE_ID=$FILE_ID.wav
echo $FILE_ID
#Run ffmpeg in background
ffmpeg -f pulse -i default audio_data/$FILE_ID </dev/null >/dev/null 2>/tmp/ffmpeg.log &
./TDW/TDW.x86_64 -address=$1 -port=$2
