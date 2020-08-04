
VERSION=$(./tdw_version.sh)

nvidia-docker run --network host --env="DISPLAY=":$DISPLAY" \
        --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
        -e NVIDIA_DRIVER_CAPABILITIES=all \
        --volume "${1}:/audio_data"  \
        "tdw:${VERSION} sh record_audio_video.sh ${2} ${3}"
