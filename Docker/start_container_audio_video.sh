
VERSION=$(python3 ./tdw_version.py)

docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --network host \
  --volume "${1}:/audio_data"  \
  alters/tdw:$VERSION\
  "sh record_audio_video.sh ${2} ${3} ${4} ${5}"
