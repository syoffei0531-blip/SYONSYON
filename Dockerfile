FROM n8nio/n8n:2.43.5

USER root

RUN apk add --no-cache \
    python3 \
    py3-pip \
    ffmpeg \
    build-base \
    python3-dev \
    linux-headers \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    libpng-dev

RUN pip3 install --break-system-packages \
    moviepy \
    pillow \
    numpy \
    opencv-python-headless

USER node
