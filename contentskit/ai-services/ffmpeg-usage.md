# n8n에서 FFmpeg 활용 가이드

이 가이드는 n8n 워크플로우에서 FFmpeg를 사용하여 다양한 미디어 파일을 변환하고 처리하는 방법을 설명합니다.

## 개요

[FFmpeg](https://ffmpeg.org/)는 오디오 및 비디오를 처리하기 위한 강력한 명령줄 도구입니다. 이 도구는 n8n 컨테이너에 이미 설치되어 있으며, Execute Command 노드를 통해 쉽게 사용할 수 있습니다.

## 기본 FFmpeg 명령어

### 오디오 변환 (MPEG에서 MP3로)

```bash
ffmpeg -i input.mpeg -vn -ar 44100 -ac 2 -b:a 192k output.mp3
```

매개변수 설명:
- `-i input.mpeg`: 입력 파일 경로
- `-vn`: 비디오 스트림 제거 (오디오만 추출)
- `-ar 44100`: 오디오 샘플링 레이트를 44.1kHz로 설정
- `-ac 2`: 오디오 채널 수 (스테레오 = 2)
- `-b:a 192k`: 오디오 비트레이트를 192kbps로 설정
- `output.mp3`: 출력 파일 경로

### 비디오 형식 변환 (MP4에서 WebM으로)

```bash
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm
```

### 비디오 크기 조정

```bash
ffmpeg -i input.mp4 -vf "scale=1280:720" -c:a copy output.mp4
```

### 비디오 트림 (특정 구간 추출)

```bash
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:02:30 -c copy output.mp4
```

## n8n 워크플로우 설정

### MPEG에서 MP3로 변환 워크플로우

1. **트리거**: 파일 감시자(Files Watcher) 노드 사용
   - 감시 경로: `/data/videos`
   - 파일 확장자: `mpeg`

2. **파일 경로 설정**: Set 노드 사용
   - 입력 파일: `{{$json.path}}`
   - 출력 파일: `{{$json.path.replace('.mpeg', '.mp3')}}`

3. **FFmpeg 명령 실행**: Execute Command 노드 사용
   - 명령어: 
   ```
   ffmpeg -i "{{$node["파일 경로 설정"].json["inputFile"]}}" -vn -ar 44100 -ac 2 -b:a 192k "{{$node["파일 경로 설정"].json["outputFile"]}}" -y
   ```

4. **결과 처리**: If 노드를 사용하여 성공/실패 조건 분기
   - 성공 조건: `{{$json.exitCode}} === 0`

### 일괄 변환 워크플로우 설정

여러 파일을 일괄 처리하려면:

1. **파일 목록 조회**: Execute Command 노드
   - 명령어: `find /data/videos -name "*.mpeg" -type f`

2. **목록 분할**: Split In Batches 노드
   - 구분자로 줄바꿈 사용

3. **각 파일 처리**: 각 파일에 대해 FFmpeg 명령 실행

## 고급 FFmpeg 명령어

### 오디오 정규화

```bash
ffmpeg -i input.mp3 -filter:a loudnorm output.mp3
```

### 워터마크 추가

```bash
ffmpeg -i input.mp4 -i watermark.png -filter_complex "overlay=10:10" output.mp4
```

### 2개 이상의 오디오 파일 합치기

```bash
ffmpeg -i input1.mp3 -i input2.mp3 -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1[out]" -map "[out]" output.mp3
```

### 자막 추가

```bash
ffmpeg -i input.mp4 -vf subtitles=subtitles.srt output.mp4
```

## 문제 해결

- **메모리 부족**: 대용량 파일을 처리할 때 메모리 부족 오류가 발생할 수 있습니다. 이 경우 Docker 컨테이너에 더 많은 메모리를 할당하세요.
- **처리 시간 초과**: Execute Command 노드의 `executeTimeout` 값을 0(무제한) 또는 충분히 큰 값으로 설정하세요.
- **파일 권한**: 입력 및 출력 디렉토리에 대한 읽기/쓰기 권한이 있는지 확인하세요.

## 참고 자료

- [FFmpeg 공식 문서](https://ffmpeg.org/documentation.html)
- [FFmpeg 위키](https://trac.ffmpeg.org/wiki)
- [FFmpeg 명령어 가이드](https://ffmpeg.org/ffmpeg.html) 