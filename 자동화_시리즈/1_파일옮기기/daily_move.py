import os
import shutil
# 하위 경로의 모든 파일 가져오기
import datetime

# 오늘 날짜 가져오기
today = datetime.date.today().strftime("%Y%m")

# 기존 경로와 새로운 경로 지정
old_path = "C:/Users/masta/Downloads/"
new_path = "Z:/SynObs/1.Fleet_Notes/1-1.inbox/1-1-1.Clipping/"

# 기존 경로에 오늘 날짜의 폴더가 있는지 확인
if os.path.exists(os.path.join(old_path, today)):
    # 오늘 날짜의 폴더가 있으면 새로운 경로에 동일한 이름의 폴더 생성
    os.makedirs(os.path.join(new_path, today), exist_ok=True)

    # 기존 경로의 오늘 날짜 폴더에서 파일 이동
    for file in os.listdir(os.path.join(old_path, today)):
        shutil.move(os.path.join(old_path, today, file), os.path.join(new_path, today, file))