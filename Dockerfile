FROM n8nio/n8n:latest

USER root

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages \
    moviepy \
    pillow \
    numpy \
    opencv-python-headless

USER node
