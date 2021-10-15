FROM nvidia/opengl:1.1-glvnd-devel-ubuntu18.04

ARG TDW_VERSION
ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display

RUN apt-get -qq update && apt-get -qq install -y sudo curl

RUN apt-get -qq update && apt-get -qq install sudo gconf-service 


RUN apt-get -qq update && apt-get -qq install -y sudo lib32gcc1 lib32stdc++6 libasound2 libc6 libc6-i386 

RUN apt-get -qq update && apt-get -qq install -y  sudo libcairo2 libcap2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libfreetype6 libgcc1 libgconf-2-4 

RUN apt-get -qq update && apt-get -qq install -y  sudo libgdk-pixbuf2.0-0 libgl1-mesa-glx mesa-utils libglib2.0-0 libglu1-mesa libgtk2.0-0 libnspr4 libnss3 libpango1.0-0 libstdc++6 libx11-6 libxcomposite1 libxcursor1 libxdamage1 libxext6 

RUN apt-get -qq update && apt-get -qq install -y sudo libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6 zlib1g debconf npm xdg-utils lsb-release libpq5 xvfb x11-apps  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip


RUN wget https://github.com/threedworld-mit/tdw/releases/download/v${TDW_VERSION}/TDW_Linux.tar.gz
RUN tar -xzf TDW_Linux.tar.gz
