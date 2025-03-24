# 윈도우용

1. 파일 설치 : 가상환경에 설치하는 게 잘됨
```bash
conda create -n editor python=3.11
conda activate editor
pip install auto-editor
```

2. 동영상 자동편집 : 있는 경로에 동영상을 컷편집해 줍니다.
```bash
auto-editor 250316212309.mp4 --margin 0.1sec #동영상 자동편집 (앞뒤 마진붙임)
```

3. 한번에 많은동영상을 편집
```shell
cd E:\temp\clib
Get-ChildItem -Path "E:\temp\clib" -Filter *.mp4 | ForEach-Object { auto-editor $_.FullName --margin 0.5sec}
```

4.  출력경로 생성/지정 및 출력품질 개선  
```bash
# 출력 폴더가 없으면 생성
cd E:\temp\clib
if (-not (Test-Path -Path "E:\temp\clib\out")) {
    New-Item -Path "E:\temp\clib\out" -ItemType Directory
}

Get-ChildItem -Path "E:\temp\clib" -Filter *.mp4 | ForEach-Object {
    $outputPath = "E:\temp\clib\out\$($_.BaseName)_edited$($_.Extension)"
    auto-editor $_.FullName --margin 0.5sec --output-file $outputPath -b:v auto
}
```
