# 동영상 자동 편집 디렉토리

이 디렉토리는 auto-editor로 처리할 동영상 파일을 저장하는 곳입니다.

## 사용 방법

1. 편집할 동영상 파일을 이 디렉토리에 업로드합니다.
2. n8n 워크플로우에서 auto-editor를 사용하여 동영상을 처리합니다.
3. 처리된 동영상은 동일한 디렉토리의 `[원본파일명]_ALTERED.mp4` 형식으로 저장됩니다.

## auto-editor 기본 명령어

n8n Execute Command 노드에서 다음과 같은 명령어를 사용할 수 있습니다:

```bash
auto-editor /data/videos/your_video.mp4 --export_to_mp4 --no_open
```

## 주요 옵션

auto-editor의 주요 옵션은 다음과 같습니다:

- `--silent_threshold [0-1]`: 소리 임계값 설정 (기본값: 0.04)
- `--video_threshold [0-1]`: 영상 움직임 임계값 설정 (기본값: 0.04)
- `--cut_out [true/false]`: 조용한 부분 제거 여부 (기본값: true)
- `--margin [초]`: 컷 주변 유지할 여백 시간 (기본값: 0.5초)
- `--min_clip [초]`: 남길 최소 클립 길이 (기본값: 0.1초)
- `--export_to_mp4`: MP4 포맷으로 출력
- `--no_open`: 처리 후 파일 열지 않음

자세한 옵션은 `auto-editor --help` 명령어로 확인하거나 [공식 문서](https://auto-editor.com)를 참조하세요. 