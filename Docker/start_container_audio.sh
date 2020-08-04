# Make sure we have the right image.
$(./pull.sh)
VERSION=$(./tdw_version.sh)

nvidia-docker run --network host --env="DISPLAY=":${1}" \
        --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
        -e NVIDIA_DRIVER_CAPABILITIES=all \
        --volume "${2}:/audio_data"  \
        "tdw:${VERSION} sh record_audio.sh ${3} ${4}"
