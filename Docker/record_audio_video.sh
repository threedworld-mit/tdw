#!/bin/bash

pulseaudio -D
echo $1
echo $2
# Run ffmpeg
FILE_ID=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13 ; echo '')
FILE_ID=$FILE_ID.nut
echo $FILE_ID
ffmpeg -y -video_size 320x320 -framerate 25 -f x11grab -draw_mouse 0 -i $DISPLAY+1152,672 -f alsa -ac 2 -i pulse -c:v ffv1 audio_data/$FILE_ID </dev/null >/dev/null 2>/audio_data/ffmpeg.log & 
./TDW/TDW.x86_64 -address=$1 -port=$2
