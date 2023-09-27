FROM nvidia/opengl:1.1-glvnd-devel-ubuntu22.04

ARG TDW_VERSION
ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display
ENV DISPLAY=:0
ENV PORT=1071
ENV ADDRESS=localhost

RUN apt -qq update && apt -qq install -y sudo curl gconf-service libasound2 libc6 libcairo2 libcap2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libfreetype6 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libgl1-mesa-glx mesa-utils libglib2.0-0 libglu1-mesa libgtk2.0-0 libnspr4 libnss3 libpango1.0-0 libstdc++6 libx11-6 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6 zlib1g debconf npm xdg-utils lsb-release libpq5 x11-apps wget unzip  make pkg-config
RUN apt autoremove -y
RUN apt clean -y

# Download and untar TDW.
RUN wget https://github.com/threedworld-mit/tdw/releases/download/v${TDW_VERSION}/TDW_Linux.tar.gz --no-check-certificate
RUN tar -xzf TDW_Linux.tar.gz
RUN rm TDW_Linux.tar.gz

COPY entrypoint.sh entrypoint.sh

# Start Xserver and launch TDW.
ENTRYPOINT ./entrypoint.sh $DISPLAY $PORT $ADDRESS
