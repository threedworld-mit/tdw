# Build the container
VERSION=$(pip3 show tdw | grep 'Version:' | cut -d' ' -f2 | rev | cut -d. -f 2- | rev)
echo $VERSION
docker build -t tdw:$VERSION --build-arg TDW_VERSION=v$VERSION .

# Allow x server to accept local connections
xhost +local:root

# Run the container
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --network host \
  tdw:$VERSION \
  ./TDW/TDW.x86_64
