FROM ubuntu:22.04

ARG TDW_VERSION

ENV PORT=1071
ENV ADDRESS=localhost
ENV WIDTH=256
ENV HEIGHT=256

# Update all packages.
RUN apt -qq update

# Install everything we need for TDW.
RUN apt install -y xvfb alsa-base wget

# Cleanup.
RUN apt autoremove --purge -y
RUN apt clean
RUN apt -qq update

# Download and untar TDW.
RUN wget https://github.com/threedworld-mit/tdw/releases/download/v${TDW_VERSION}/TDW_Linux.tar.gz --no-check-certificate
RUN tar -xzf TDW_Linux.tar.gz
RUN rm TDW_Linux.tar.gz

COPY internal/entrypoint.sh entrypoint.sh

# HOME
RUN mkdir -p /home/container && chmod 777 /home/container
ENV HOME=/home/container

# Start xvfb and launch TDW.
ENTRYPOINT ./entrypoint.sh ${PORT} ${ADDRESS} ${WIDTH} ${HEIGHT}
