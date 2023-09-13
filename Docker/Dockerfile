FROM nvidia/opengl:1.1-glvnd-devel-ubuntu22.04

ARG DISPLAY
ARG TDW_VERSION
ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display
ENV DISPLAY=$DISPLAY

RUN apt-get -qq update && apt-get -qq install -y sudo curl gconf-service libasound2 libc6 libcairo2 libcap2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libfreetype6 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libgl1-mesa-glx mesa-utils libglib2.0-0 libglu1-mesa libgtk2.0-0 libnspr4 libnss3 libpango1.0-0 libstdc++6 libx11-6 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6 zlib1g debconf npm xdg-utils lsb-release libpq5 xvfb x11-apps python3-pip wget unzip xserver-xorg-video-nvidia-535

RUN rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/threedworld-mit/tdw/releases/download/v${TDW_VERSION}/TDW_Linux.tar.gz
RUN tar -xzf TDW_Linux.tar.gz

RUN python3 -m pip install tdw

RUN nvidia-xconfig --use-display-device=None --allow-empty-initial-configuration --virtual=1920x1080 --mode=1920x1080 --no-use-edid-dpi -o /etc/X11/xorg.conf

CMD Xorg vt10 $DISPLAY &;cd TDW;./TDW.x86_64