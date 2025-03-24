# n8n에서 auto-editor 사용 가이드

이 가이드는 n8n 워크플로우에서 auto-editor를 사용하여 동영상을 자동으로 편집하는 방법을 설명합니다.

## 개요

[auto-editor](https://auto-editor.com/)는 조용한 부분이나 움직임이 없는 부분을 자동으로 감지하여 불필요한 부분을 제거하는 동영상 편집 도구입니다. 이 도구는 강의, 튜토리얼, 스트리밍 녹화본 등을 효과적으로 편집하는 데 유용합니다.

## 설정 방법

이 프로젝트는 n8n 컨테이너 내에 auto-editor와 필요한 의존성을 모두 설치합니다. 별도의 설정 없이 바로 사용할 수 있습니다.

## 사용 방법

### 1. 동영상 파일 준비

편집할 동영상 파일을 `ai-services/videos` 디렉토리에 업로드합니다. 이 디렉토리는 n8n 컨테이너 내부의 `/data/videos` 경로에 마운트됩니다.

### 2. n8n 워크플로우 생성

n8n에서 다음 노드를 사용하여 auto-editor 워크플로우를 생성합니다:

1. **트리거 노드**: 워크플로우를 시작할 방법 선택 (수동, 스케줄, 웹훅 등)
2. **Set 노드**: 파일 경로 설정
   - `filePath`: `/data/videos/your_video.mp4`
3. **Execute Command 노드**: auto-editor 명령 실행
   - 명령어: `auto-editor {{$node["Set"].json["filePath"]}} --export_to_mp4 --no_open`
   - 작업 디렉토리: `/data/videos`

### 3. 예제 명령어

```bash
# 기본 편집 (무음 부분 제거)
auto-editor /data/videos/video.mp4 --export_to_mp4 --no_open

# 무음 기준값 조정 (0.03 = 더 많은 부분 남김, 0.1 = 더 많은 부분 제거)
auto-editor /data/videos/video.mp4 --silent_threshold 0.03 --export_to_mp4 --no_open

# 컷 전후로 여백 추가 (0.3초)
auto-editor /data/videos/video.mp4 --margin 0.3 --export_to_mp4 --no_open

# 최소 클립 길이 설정 (0.5초 미만 클립 제거)
auto-editor /data/videos/video.mp4 --min_clip 0.5 --export_to_mp4 --no_open

# 최대 컷 길이 설정 (5초 이상 무음은 최대 5초만 유지)
auto-editor /data/videos/video.mp4 --max_cut 5 --export_to_mp4 --no_open
```

### 4. 결과 확인

처리된 파일은 입력 파일과 동일한 디렉토리에 `[원본 파일명]_ALTERED.mp4` 형식으로 저장됩니다.

## 예제 워크플로우

예제 워크플로우 파일(`auto-editor-workflow.json`)을 n8n으로 가져와서 사용할 수 있습니다:

1. n8n 인터페이스에서 **워크플로우** 메뉴 선택
2. **가져오기 버튼** 클릭
3. `auto-editor-workflow.json` 파일 선택
4. 필요에 맞게 편집 후 저장

## 문제 해결

- **명령 실행 시간 초과**: Execute Command 노드의 `executeTimeout` 값을 0(무제한) 또는 충분히 큰 값으로 설정
- **메모리 부족**: 대용량 파일 처리 시 Docker 컨테이너에 충분한 메모리 할당
- **출력 파일 오류**: 볼륨 마운트와 권한 설정 확인

## 고급 사용법

auto-editor는 다양한 옵션을 제공합니다. 자세한 내용은 [공식 문서](https://auto-editor.com)를 참조하세요.

```bash
# 모든 옵션 확인
auto-editor --help

# 비디오와 오디오 모두 분석하여 편집
auto-editor /data/videos/video.mp4 --edit audio video --export_to_mp4 --no_open

# 특정 시간 범위만 처리
auto-editor /data/videos/video.mp4 --cut_out from 00:01:00 to 00:02:00 --export_to_mp4 --no_open
``` 