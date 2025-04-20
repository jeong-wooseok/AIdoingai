FROM n8nio/n8n:1.88.0

USER root

# Alpine 패키지 매니저 사용하여 Python과 필요 도구 설치
RUN apk add --no-cache \
    python3 \
    python3-dev \
    py3-pip \
    ffmpeg \
    ffmpeg-dev \
    build-base \
    pkgconf \
    cython \
    jpeg-dev \
    zlib-dev \
    bash \
    git \
    gcc \
    musl-dev \
    linux-headers

# 가상환경 생성 및 패키지 설치
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install wheel setuptools-rust && \
    /opt/venv/bin/pip install yt-dlp && \
    /opt/venv/bin/pip install numpy moviepy

# 가상환경의 바이너리를 PATH에 추가
ENV PATH="/opt/venv/bin:$PATH"

# Create necessary directories and scripts
RUN mkdir -p /data/videos /usr/local/bin

USER node

CMD ["/usr/local/bin/n8n", "start"]
