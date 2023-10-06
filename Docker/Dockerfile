FROM ubuntu:22.04

ARG TDW_VERSION
ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display
ENV PORT=1071
ENV ADDRESS=localhost

# Update all packages.
RUN apt -qq update

# Add deb-src. Source: https://askubuntu.com/a/857433
RUN cp /etc/apt/sources.list /etc/apt/sources.list~
RUN sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list
RUN apt -qq update

# Source: https://github.com/mviereck/dockerfile-x11docker-xserver/blob/main/Dockerfile
# Install nxagent.
RUN apt install -y nxagent
# Cleanup.
COPY clean.sh clean.sh
RUN ./clean.sh
# X servers.
RUN apt install -y --no-install-recommends \
        kwin-wayland \
        kwin-wayland-backend-drm \
        kwin-wayland-backend-wayland \
        kwin-wayland-backend-x11 \
        weston \
        xserver-xephyr \
        xserver-xorg \
        xserver-xorg-legacy \
        xvfb \
        xwayland \
        xpra \
        openbox
# Disable openbox's context menu.
RUN sed -i /ShowMenu/d         /etc/xdg/openbox/rc.xml
RUN sed -i s/NLIMC/NLMC/       /etc/xdg/openbox/rc.xml
# Cleanup.
RUN ./clean.sh
# Compile fake MIT-SHM library.
COPY XlibNoSHM.c /XlibNoSHM.c
RUN apt-get install -y --no-install-recommends gcc libc6-dev libx11-dev
RUN gcc -shared -o /XlibNoSHM.so /XlibNoSHM.c
RUN  apt remove --purge -y gcc libc6-dev libx11-dev
RUN ./clean.sh
# Tools.
RUN apt-get install -y --no-install-recommends \
        catatonit \
        procps \
        psmisc \
        psutils \
        socat \
        vainfo \
        vdpauinfo \
        virgl-server \
        wl-clipboard \
        wmctrl \
        x11-utils \
        x11-xkb-utils \
        x11-xserver-utils \
        xauth \
        xbindkeys \
        xclip \
        xdotool \
        xfishtank \
        xinit
RUN ./clean.sh
# Configure Xorg wrapper.
RUN echo 'allowed_users=anybody' >/etc/X11/Xwrapper.config
RUN echo 'needs_root_rights=yes' >>/etc/X11/Xwrapper.config
# Wrapper to run weston either on console or within DISPLAY or WAYLAND_DISPLAY.
# Note: includes setuid for agetty to allow it for unprivileged users.
RUN echo '#! /bin/bash \n\
case "$DISPLAY$WAYLAND_DISPLAY" in \n\
  "") \n\
    [ -e /dev/tty$XDG_VTNR ] && [ -n "$XDG_VTNR" ] || { \n\
      echo "ERROR: No display and no tty found. XDG_VTNR is empty." >&2 \n\
      exit 1 \n\
    } \n\
    exec agetty --login-options "-v -- $* --log=/x11docker/compositor.log " --autologin $(id -un) --login-program /usr/bin/weston-launch --noclear tty$XDG_VTNR \n\
  ;; \n\
  *) \n\
    exec /usr/bin/weston "$@" \n\
  ;; \n\
esac \n\
' >/usr/local/bin/weston && \
    chmod +x /usr/local/bin/weston && \
    ln /usr/local/bin/weston /usr/local/bin/weston-launch
# HOME
RUN mkdir -p /home/container && chmod 777 /home/container
ENV HOME=/home/container
LABEL version='1.10'
LABEL options='--kwin --weston --weston-xwayland --xephyr --xpra --xpra-xwayland --xpra2 --xpra2-xwayland --xorg --xvfb --xwayland'
LABEL tools='catatonit cvt glxinfo iceauth setxkbmap socat \
             vainfo vdpauinfo virgl wl-copy wl-paste wmctrl \
             xauth xbindkeys xclip xdotool xdpyinfo xdriinfo xev \
             xfishtank xhost xinit xkbcomp xkill xlsclients xmessage \
             xmodmap xprop xrandr xrefresh xset xsetroot xvinfo xwininfo'
LABEL options_console='--kwin --weston --weston-xwayland --xorg'
LABEL gpu='MESA'
LABEL windowmanager='openbox'

# Install TDW requirements.
RUN apt -qq install -y alsa-base wget
RUN ./clean.sh

# Download and untar TDW.
RUN wget https://github.com/threedworld-mit/tdw/releases/download/v${TDW_VERSION}/TDW_Linux.tar.gz --no-check-certificate
RUN tar -xzf TDW_Linux.tar.gz
RUN rm TDW_Linux.tar.gz

COPY entrypoint.sh entrypoint.sh

# Start Xserver and launch TDW.
ENTRYPOINT ./entrypoint.sh $PORT $ADDRESS
