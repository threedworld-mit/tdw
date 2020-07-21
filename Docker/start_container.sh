# Build the container
docker build -t tdw:v1.6.0 .

# Allow x server to accept local connections
xhost +local:root

# Run the container
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --network host \
  tdw:1.6.0 \
  ./TDW/TDW.x86_64
