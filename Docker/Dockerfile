FROM nvidia/opengl:1.1-glvnd-devel-ubuntu22.04

ARG TDW_VERSION
ARG NVIDIA_VERSION
ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display
ENV DISPLAY=:0
ENV PORT=1071
ENV ADDRESS=localhost

RUN apt -qq update && apt -qq install -y sudo curl gconf-service libasound2 libc6 libcairo2 libcap2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libfreetype6 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libgl1-mesa-glx mesa-utils libglib2.0-0 libglu1-mesa libgtk2.0-0 libnspr4 libnss3 libpango1.0-0 libstdc++6 libx11-6 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6 zlib1g debconf npm xdg-utils lsb-release libpq5 x11-apps wget unzip  make pkg-config

# Install xorg.
RUN apt -qq install -y xorg xserver-xorg-input-evdev  xserver-xorg-input-all

# Install NVIDIA drivers.
# Source: https://github.com/mviereck/x11docker/wiki/NVIDIA-driver-support-for-docker-container#nvidia-driver-base-image
RUN apt -qq install -y kmod xz-utils ca-certificates binutils 
RUN wget https://http.download.nvidia.com/XFree86/Linux-x86_64/${NVIDIA_VERSION}/NVIDIA-Linux-x86_64-${NVIDIA_VERSION}.run -O NVIDIA-installer.run
ENV NVIDIA_OPTIONS='--accept-license --no-runlevel-check --no-questions --no-backup --ui=none --no-kernel-module --no-nouveau-check'
RUN sh NVIDIA-installer.run -A | grep -q -- '--install-libglvnd'        && Nvidiaoptions="${NVIDIA_OPTIONS} --install-libglvnd"
RUN sh NVIDIA-installer.run -A | grep -q -- '--no-nvidia-modprobe'      && Nvidiaoptions="${NVIDIA_OPTIONS} --no-nvidia-modprobe"
RUN sh NVIDIA-installer.run -A | grep -q -- '--no-kernel-module-source' && Nvidiaoptions="${NVIDIA_OPTIONS} --no-kernel-module-source"
RUN sh NVIDIA-installer.run ${NVIDIA_OPTIONS}
RUN rm NVIDIA-installer.run
RUN apt -qq remove -y kmod xz-utils ca-certificates binutils

# Cleanup.
RUN apt-get autoremove -y 
RUN apt-get clean -y

# Configure xorg.conf
RUN nvidia-xconfig --no-xinerama --probe-all-gpus --use-display-device=none

# Download and untar TDW.
RUN wget https://github.com/threedworld-mit/tdw/releases/download/v${TDW_VERSION}/TDW_Linux.tar.gz
RUN tar -xzf TDW_Linux.tar.gz

# Start Xserver and launch TDW.
ENTRYPOINT sudo nohup Xorg ${DISPLAY} -config /etc/X11/xorg.conf &; cd TDW; DISPLAY=${DISPLAY} ./TDW.x86_64 -port=${PORT} -address=${ADDRESS}
