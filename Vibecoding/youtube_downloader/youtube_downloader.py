import streamlit as st
# from pytube import YouTube  # pytube 관련 제거
# from pytube.exceptions import PytubeError, RegexMatchError # pytube 관련 제거
import os
import re
import subprocess # subprocess 모듈 추가
import locale # 인코딩 감지를 위해 추가
from dotenv import load_dotenv # dotenv 추가

load_dotenv() # .env 파일 로드 시도

# 시스템 기본 인코딩 가져오기 (오류 발생 시 utf-8 사용)
try:
    preferred_encoding = locale.getpreferredencoding()
except locale.Error:
    preferred_encoding = "utf-8"

def sanitize_filename(filename):
    """ 파일명으로 사용할 수 없는 문자를 제거하거나 대체합니다. """
    # 제거할 문자 패턴 (Windows 및 일반적인 경우)
    sanitized = re.sub(r'[\\/*?:".<>|]', "", filename)
    # Windows 예약 파일 이름 방지 (CON, PRN, AUX, NUL 등)
    reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
    if sanitized.upper() in reserved_names:
        sanitized = "_" + sanitized
    # 파일명 길이 제한 (선택 사항, Windows 최대 255자 고려)
    # sanitized = sanitized[:200]
    return sanitized

def download_video(url, save_path='.'):
    """
    유튜브 URL을 받아 yt-dlp를 사용하여 동영상을 지정된 경로에 다운로드합니다.

    Args:
        url (str): 다운로드할 유튜브 동영상 URL.
        save_path (str): 동영상을 저장할 경로.

    Returns:
        tuple: (success: bool, message: str, downloaded_file_path: str or None)
               다운로드 성공 여부, 결과 메시지 (로그 또는 에러), 다운로드된 파일 경로.
    """
    try:
        # 저장 경로 미리 생성하는 로직 제거
        # if not os.path.exists(save_path):
        #     try:
        #         os.makedirs(save_path)
        #         st.sidebar.info(f"지정된 경로가 없어 생성했습니다: {save_path}")
        #     except OSError as e:
        #         return False, f"다운로드 경로 생성 실패: {e}", None

        # yt-dlp 명령어 구성 (프리미어 호환 코덱 우선)
        output_template = os.path.join(save_path, "%(title)s.%(ext)s")

        command = [
            "yt-dlp",
            url,
            # H.264(AVC) 비디오 + AAC 오디오 우선, 없으면 차선책
            # vcodec^=avc : 비디오 코덱이 avc로 시작하는 것
            # acodec^=aac : 오디오 코덱이 aac로 시작하는 것
            "-f", "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a][acodec^=aac]/best[ext=mp4][vcodec^=avc][acodec^=aac]/best[ext=mp4]",
            "-o", output_template,
            "--remux-video", "mp4", # 최종 컨테이너 MP4 보장
            # "--print", "filename", # 로그 파싱으로 대체
            # "--force-overwrites", # 필요시 주석 해제
            "-v"
        ]
        st.code(" ".join(command))

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            check=False,
            encoding=preferred_encoding,
            errors='replace',
            stderr=subprocess.STDOUT
        )

        output_log = result.stdout
        downloaded_file_path = None
        log_message = f"yt-dlp 종료 코드: {result.returncode}\n\n로그/오류:\n{output_log}"

        if result.returncode == 0:
            # 파일 존재 확인 로직 수정: -o 템플릿 기반으로 예상 경로 생성 및 확인
            # 주의: 실제 파일명과 약간 다를 수 있음 (yt-dlp 내부 처리)
            # 우선 stdout에서 파일명 관련 정보를 찾아보자.
            potential_filename = None
            for line in output_log.split('\n'):
                # '[download] Destination: ...' 또는 '[Merger] Merging formats into ...' 에서 파일명 추출 시도
                match_dest = re.search(r"Destination:\s*(.*)", line)
                match_merge = re.search(r"Merging formats into \"(.*)\"", line)
                if match_merge:
                    potential_filename = match_merge.group(1).strip()
                    break # 병합된 파일명이 더 최종적임
                elif match_dest:
                    potential_filename = match_dest.group(1).strip()
                    # 병합 가능성 있으므로 계속 탐색

            predicted_path = None
            if potential_filename:
                 # yt-dlp는 -o 템플릿의 경로를 기준으로 출력하므로, save_path를 다시 붙일 필요 없음
                 predicted_path = os.path.abspath(potential_filename)
                 print(f"[Debug] Predicted path from log: {predicted_path}")
            else:
                 # 로그에서 못찾으면 -o 템플릿으로 예측 (덜 정확)
                 # 예측을 위해서는 title 정보가 필요하나 현재 없음. 일단 실패 처리 강화.
                 print("[Debug] Could not predict filename from log.")

            if predicted_path and os.path.exists(predicted_path):
                downloaded_file_path = predicted_path
                print(f"[Debug] File found at predicted path: {downloaded_file_path}")
                message = f"다운로드 완료! 파일 경로: {downloaded_file_path}"
                return True, message + "\n\n" + log_message, downloaded_file_path
            else:
                message = f"다운로드 성공 (종료 코드 0) 했으나 최종 파일 확인에 실패했습니다."
                if predicted_path:
                     message += f" 예상 경로({predicted_path})에 파일이 생성되지 않았습니다. 권한, 디스크 공간, 보안 설정을 확인하세요."
                else:
                     message += f" 로그에서 최종 파일명을 예측할 수 없었습니다. 저장 경로({save_path})를 직접 확인하세요."
                return True, message + "\n\n" + log_message, None
        else:
            # 실패 시 오류 메시지
            error_message = f"yt-dlp 다운로드 실패"
            if "ffmpeg" in output_log.lower() or "ffprobe" in output_log.lower():
                 error_message += "\n\n경고: 오류 메시지에 'ffmpeg' 또는 'ffprobe'가 포함되어 있습니다."
            return False, error_message + "\n\n" + log_message, None

    except FileNotFoundError:
        return False, "오류: 'yt-dlp' 명령어를 찾을 수 없습니다. 가상 환경이 활성화되었는지, yt-dlp가 올바르게 설치되었는지 확인하세요.", None
    except Exception as e:
        return False, f"subprocess 실행 중 알 수 없는 오류 발생: {e}", None

# --- Streamlit App UI ---

# 세션 상태 초기화
if 'download_status' not in st.session_state:
    st.session_state.download_status = None # None, 'processing', 'success', 'error'
if 'video_url' not in st.session_state:
    st.session_state.video_url = ""
if 'last_stdout' not in st.session_state:
    st.session_state.last_stdout = None
if 'last_stderr' not in st.session_state:
    st.session_state.last_stderr = None
if 'clear_url_on_next_run' not in st.session_state: # 초기화 플래그 추가
    st.session_state.clear_url_on_next_run = False
if 'save_path' not in st.session_state:
    # 다운로드 경로 설정 (앱 시작 시 한 번만)
    try:
        download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        st.session_state.save_path = download_folder
    except Exception:
        st.warning("Downloads 폴더를 찾거나 생성할 수 없습니다. 현재 디렉토리에 저장합니다.")
        st.session_state.save_path = '.'

# 다음 실행 시 URL 초기화 로직
if st.session_state.clear_url_on_next_run:
    st.session_state.video_url = ""
    st.session_state.clear_url_on_next_run = False # 플래그 리셋

st.set_page_config(layout="wide") # 넓은 레이아웃 사용

st.title("유튜브 동영상 다운로더")

# --- 사이드바 (입력) ---
st.sidebar.header("입력 설정")

# URL 입력
url_input = st.sidebar.text_input("유튜브 URL", value=st.session_state.get("video_url", ""))

# 다운로드 경로 설정 (환경 변수 또는 기본값)
def get_default_download_path():
    user_profile_name = os.getenv("USER_PROFILE_NAME")
    if user_profile_name:
        # 환경 변수에 사용자 이름이 있으면 해당 경로 사용 시도
        path = os.path.join("C:\\Users", user_profile_name, "Downloads")
    else:
        # 없으면 현재 사용자 홈 디렉토리 사용
        path = os.path.join(os.path.expanduser("~"), "Downloads")
    return path

default_save_path = st.session_state.get("save_path", get_default_download_path())
save_path_input = st.sidebar.text_input("저장 경로", value=default_save_path)

# 다운로드 버튼
if st.sidebar.button("다운로드 시작"):
    if url_input:
        # 입력값 세션 상태에 저장 (실행 전)
        st.session_state.video_url = url_input
        st.session_state.save_path = save_path_input
        st.session_state.download_status = 'processing'
        st.session_state.result_message = None
        st.session_state.downloaded_file = None
        st.rerun() # 상태 저장 후 재실행하여 스피너 표시
    else:
        st.sidebar.warning("유튜브 URL을 입력해주세요.")

# --- 메인 영역 (출력) ---
st.header("다운로드 결과")

# 다운로드 실행 및 결과 처리 (상태가 processing일 때)
if st.session_state.get("download_status") == 'processing':
    with st.spinner("다운로드 진행 중... yt-dlp 실행 중"):
        success, message, file_path = download_video(st.session_state.video_url, st.session_state.save_path)
        st.session_state.result_message = message
        st.session_state.downloaded_file = file_path
        st.session_state.download_status = 'success' if success else 'error'
        st.session_state.video_url = "" # 입력 필드 초기화를 위해 URL 상태 비움
        st.rerun() # 결과 표시를 위해 재실행

# 결과 메시지 표시
if st.session_state.get("download_status") == 'success':
    st.success("다운로드 성공!")
    downloaded_file = st.session_state.get('downloaded_file')
    save_path = st.session_state.get('save_path')

    if downloaded_file:
        st.info(f"다운로드된 파일: {downloaded_file}")
    else:
        st.warning("다운로드 성공(종료 코드 0)했으나, 최종 파일 경로를 확인하지 못했습니다.")

    if save_path and os.path.exists(save_path):
        if st.button("저장 폴더 열기"):
            print(f"[Debug] Attempting to open folder: {save_path}")
            try:
                process = subprocess.Popen(['explorer', save_path])
                print(f"[Debug] Explorer process started: {process}")
            except FileNotFoundError:
                 st.warning("'explorer' 명령을 찾을 수 없습니다. Windows 환경이 맞는지 확인하세요.")
            except AttributeError:
                st.warning("현재 운영체제에서는 폴더 열기 기능을 지원하지 않습니다.")
            except Exception as e:
                st.error(f"폴더를 여는 중 오류 발생: {e}")
                print(f"[Error] Failed to open folder: {e}")

    with st.expander("상세 로그 보기"):
        st.code(st.session_state.get("result_message", ""))
    st.balloons()
    # 상태 초기화 제거 (다음 상호작용 전까지 유지)
    # st.session_state.download_status = None
    # st.session_state.result_message = None
    # st.session_state.downloaded_file = None

elif st.session_state.get("download_status") == 'error':
    st.error("다운로드 실패")
    with st.expander("오류 및 로그 보기"):
        st.code(st.session_state.get("result_message", ""))
    # 상태 초기화 제거
    # st.session_state.download_status = None
    # st.session_state.result_message = None
    # st.session_state.downloaded_file = None
else:
    st.info("사이드바에서 URL과 저장 경로를 입력하고 '다운로드 시작' 버튼을 누르세요.") 