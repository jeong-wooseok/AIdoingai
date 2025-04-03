from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str:
    """YouTube URL에서 비디오 ID를 추출합니다."""
    try:
        parsed_url = urlparse(url)
        
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            if parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            if parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
        
        raise ValueError('올바른 YouTube URL이 아닙니다.')
    except Exception as e:
        raise ValueError(f'URL 파싱 중 오류 발생: {str(e)}')

async def get_video_transcript(url: str) -> str:
    """YouTube 영상의 자막을 추출합니다."""
    try:
        video_id = extract_video_id(url)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 자막 추출 시도 순서: 한국어 -> 영어 -> 자동 생성된 자막
        try:
            # 1. 한국어 자막 시도
            transcript = transcript_list.find_transcript(['ko'])
        except:
            try:
                # 2. 영어 자막 시도 후 한국어로 번역
                transcript = transcript_list.find_transcript(['en'])
                transcript = transcript.translate('ko')
            except:
                # 3. 자동 생성된 자막 시도
                available_transcripts = transcript_list.manual_transcripts
                if not available_transcripts:
                    available_transcripts = transcript_list.generated_transcripts
                
                if not available_transcripts:
                    raise Exception("이 영상에는 자막이 없습니다.")
                
                # 사용 가능한 첫 번째 자막을 한국어로 번역
                first_lang = list(available_transcripts.keys())[0]
                transcript = transcript_list.find_transcript([first_lang])
                transcript = transcript.translate('ko')
        
        transcript_parts = transcript.fetch()
        
        # 자막 텍스트 결합
        full_transcript = ""
        for part in transcript_parts:
            text = part["text"].strip()
            if text:
                full_transcript += f"{text} "
        
        return full_transcript.strip()
    
    except Exception as e:
        raise Exception(f"자막을 가져오는 중 오류가 발생했습니다: {str(e)}") 