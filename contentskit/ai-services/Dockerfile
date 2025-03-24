FROM n8nio/n8n:latest

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
    git

# 가상환경 생성 및 패키지 설치
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install wheel setuptools-rust && \
    /opt/venv/bin/pip install yt-dlp && \
    /opt/venv/bin/pip install numpy moviepy && \
    /opt/venv/bin/pip install av==14.1.0 && \
    /opt/venv/bin/pip install auto-editor==24.31.1 || \
    /opt/venv/bin/pip install auto-editor==23.46.1 || \
    /opt/venv/bin/pip install git+https://github.com/WyattBlue/auto-editor.git@v24.31.1 || \
    echo "auto-editor 설치 실패, 백업 스크립트 사용"

# 가상환경의 바이너리를 PATH에 추가
ENV PATH="/opt/venv/bin:$PATH"

# ffmpeg 기반 비디오 자동 편집 스크립트 생성 (백업용)
RUN mkdir -p /usr/local/bin && \
    echo '#!/bin/bash\n\
input="$1"\n\
output="$2"\n\
volume_threshold="${3:-0.1}"\n\
\n\
# 소리가 있는 구간 감지\n\
ffmpeg -i "$input" -af "silencedetect=noise=${volume_threshold}:d=0.5" -f null - 2>&1 | grep "silence_end\|silence_start" > /tmp/silence_log.txt\n\
\n\
# 소리가 있는 구간만 추출해서 연결\n\
ffmpeg -i "$input" -filter_complex "silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=${volume_threshold}" "$output"\n\
\n\
echo "편집 완료: $output"\n\
' > /usr/local/bin/auto-edit.sh && \
    chmod +x /usr/local/bin/auto-edit.sh

# n8n에서 사용할 Python 스크립트 생성
RUN echo '#!/opt/venv/bin/python3\n\
import sys\n\
import subprocess\n\
\n\
if __name__ == "__main__":\n\
    if len(sys.argv) < 3:\n\
        print("사용법: python3 auto_edit.py 입력파일 출력파일")\n\
        sys.exit(1)\n\
\n\
    input_file = sys.argv[1]\n\
    output_file = sys.argv[2]\n\
\n\
    try:\n\
        # auto-editor 명령어 실행 시도\n\
        cmd = ["auto-editor", input_file, "-o", output_file]\n\
        subprocess.run(cmd, check=True)\n\
        print(f"auto-editor로 편집 완료: {output_file}")\n\
    except (subprocess.SubprocessError, FileNotFoundError):\n\
        # 실패 시 백업 스크립트 사용\n\
        print("auto-editor 실행 실패, ffmpeg 스크립트 사용")\n\
        cmd = ["/usr/local/bin/auto-edit.sh", input_file, output_file]\n\
        subprocess.run(cmd, check=True)\n\
' > /usr/local/bin/auto_edit.py && \
    chmod +x /usr/local/bin/auto_edit.py

# Create directory for video processing
RUN mkdir -p /data/videos

# Make sure n8n user can access these directories
RUN chown -R node:node /data /opt/venv /usr/local/bin/auto-edit.sh /usr/local/bin/auto_edit.py && \
    chmod -R 755 /usr/bin/ffmpeg /usr/local/bin/auto-edit.sh /usr/local/bin/auto_edit.py

# # Switch back to node user
# USER node

# # Expose default n8n port
# EXPOSE 5678

# Start n8n (원래 명령으로 되돌림)
# ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]
# CMD ["n8n", "start"] 