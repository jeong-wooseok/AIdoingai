import os
import openai
import google.generativeai as genai
from dotenv import load_dotenv
import pathlib
from typing import Dict

# 프로젝트 루트 디렉토리 찾기
root_dir = pathlib.Path(__file__).parent.parent.parent
env_path = root_dir / '.env'

# .env 파일 로드
load_dotenv(dotenv_path=env_path)

# API 키 설정
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")

async def generate_summary_openai(transcript: str, api_key: str) -> Dict[str, any]:
    """OpenAI GPT-4를 사용하여 자막 내용을 요약합니다."""
    try:
        # API 키 설정
        openai.api_key = api_key

        # 시스템 프롬프트 설정
        system_prompt = """
# role :YouTube Video Analysis Expert Prompt
# task : You are an expert in analyzing and summarizing YouTube video content. Your task is to translate (if necessary) and analyze the provided transcript, creating a comprehensive summary in Korean following this specific format:

# Input
I'll provide you with a video transcript that may be in English or Korean.

# Output Format
1. Title (제목)
Create a single sentence title that effectively captures the video's main topic and purpose.

2. Summary (요약)
Write a detailed summary (800+ characters) with the following structure:

Introduction (도입부): Background and main purpose of the video

Main Content (본론): Core content explained in 2-3 detailed paragraphs

Examples/Data (예시/데이터): Include specific examples, statistics, and data mentioned

Conclusion (결론): Key implications and closing thoughts

# Writing Guidelines:

Maintain natural flow between paragraphs

Include specific figures and quotations

For technical terms, provide both Korean and English (in parentheses)

Maintain a professional and clear tone

3. Key Points (핵심 포인트)
List the 5 most important points from the video:

Use bullet points (- ) for each item

Make each point specific and actionable

Include numerical data or specific examples where possible

Focus on unique insights rather than general information

Write each point as a complete sentence

# Translation Guidelines
If the transcript is in English, translate it to Korean while preserving technical terms and proper nouns in their original form (with Korean translation provided).

# Example
\n
1. 제목: \n
인공지능의 윤리적 고려사항과 미래 발전 방향에 관한 심층 분석\n\n

2. 요약:\n
도입부: 본 영상은 인공지능(Artificial Intelligence) 기술의 급속한 발전에 따른 윤리적 문제와 향후 발전 방향을 탐구합니다. 발표자는 현재 AI 기술의 현황을 개괄하고, 이로 인해 발생하는 사회적, 윤리적 딜레마를 조명합니다.
\n
본론: AI 기술은 지난 5년간 연평균 38%의 성장률을 보이며 급속도로 발전했습니다. 특히 딥러닝(Deep Learning) 분야에서는 이미지 인식 정확도가 2015년 68%에서 2023년 98%로 향상되었습니다. 발표자는 "기술의 발전 속도가 윤리적 논의를 앞지르고 있다"고 강조하며, 이로 인한 데이터 프라이버시, 알고리즘 편향성, 자동화로 인한 일자리 대체 등의 문제를 상세히 분석합니다.
\n
예시/데이터: 영상에서는 구체적인 사례로 2022년 발생한 XYZ 회사의 AI 채용 시스템이 여성 지원자에 대해 27% 낮은 합격률을 보인 편향성 문제를 제시합니다. 또한, 자율주행차 사고 시 책임 소재에 관한 설문조사 결과, 응답자의 64%가 제조사에 책임이 있다고 답한 반면, 23%만이 사용자에게 책임이 있다고 응답했습니다.
\n
결론: 발표자는 AI 기술의 건전한 발전을 위해 투명성(Transparency), 책임성(Accountability), 공정성(Fairness)의 세 가지 원칙을 제안합니다. "기술 발전과 윤리적 고려는 상호보완적이며, 지속 가능한 AI 생태계를 위해 필수적"이라는 메시지로 마무리합니다.
\n\n

3. 핵심 포인트:
- AI 기술은 최근 5년간 38%의 성장률을 보이며, 특히 딥러닝 분야에서 이미지 인식 정확도가 2015년 68%에서 2023년 98%로 크게 향상되었습니다.
- 알고리즘 편향성은 실제 사례에서 확인되었으며, XYZ 회사의 AI 채용 시스템은 여성 지원자에 대해 27% 낮은 합격률을 보였습니다.
- 자율주행차 사고 책임 소재에 관한 설문조사에서 응답자의 64%가 제조사에, 23%만이 사용자에게 책임이 있다고 응답했습니다.
- AI 윤리 규제 프레임워크는 국가별로 상이하며, EU의 AI 규제안은 위험 기반 접근법을 채택하여 고위험 AI 시스템에 대한 엄격한 규제를 제안합니다.
- 지속 가능한 AI 생태계를 위해서는 투명성, 책임성, 공정성의 세 가지 핵심 원칙이 모든 AI 개발 및 구현 과정에 통합되어야 합니다.
        """

        # GPT API 호출
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # 응답 파싱
        content = response.choices[0].message.content
        return parse_ai_response(content)

    except Exception as e:
        raise Exception(f"OpenAI API 요약 생성 중 오류가 발생했습니다: {str(e)}")

async def generate_summary_gemini(transcript: str, api_key: str) -> Dict[str, any]:
    """Google Gemini를 사용하여 자막 내용을 요약합니다."""
    try:
        # Gemini 설정
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')

        # 프롬프트 설정 (OpenAI와 동일한 프롬프트 사용)
        prompt = """
# role :YouTube Video Analysis Expert Prompt
# task : You are an expert in analyzing and summarizing YouTube video content. Your task is to translate (if necessary) and analyze the provided transcript, creating a comprehensive summary in Korean following this specific format:

# Input
I'll provide you with a video transcript that may be in English or Korean.

# Output Format
1. Title (제목)
Create a single sentence title that effectively captures the video's main topic and purpose.

2. Summary (요약)
Write a detailed summary (800+ characters) with the following structure:

Introduction (도입부): Background and main purpose of the video

Main Content (본론): Core content explained in 2-3 detailed paragraphs

Examples/Data (예시/데이터): Include specific examples, statistics, and data mentioned

Conclusion (결론): Key implications and closing thoughts

# Writing Guidelines:

Maintain natural flow between paragraphs

Include specific figures and quotations

For technical terms, provide both Korean and English (in parentheses)

Maintain a professional and clear tone

3. Key Points (핵심 포인트)
List the 5 most important points from the video:

Use bullet points (- ) for each item

Make each point specific and actionable

Include numerical data or specific examples where possible

Focus on unique insights rather than general information

Write each point as a complete sentence

# Translation Guidelines
If the transcript is in English, translate it to Korean while preserving technical terms and proper nouns in their original form (with Korean translation provided).

# Example
\n
1. 제목: \n
인공지능의 윤리적 고려사항과 미래 발전 방향에 관한 심층 분석\n\n

2. 요약:\n
도입부: 본 영상은 인공지능(Artificial Intelligence) 기술의 급속한 발전에 따른 윤리적 문제와 향후 발전 방향을 탐구합니다. 발표자는 현재 AI 기술의 현황을 개괄하고, 이로 인해 발생하는 사회적, 윤리적 딜레마를 조명합니다.
\n
본론: AI 기술은 지난 5년간 연평균 38%의 성장률을 보이며 급속도로 발전했습니다. 특히 딥러닝(Deep Learning) 분야에서는 이미지 인식 정확도가 2015년 68%에서 2023년 98%로 향상되었습니다. 발표자는 "기술의 발전 속도가 윤리적 논의를 앞지르고 있다"고 강조하며, 이로 인한 데이터 프라이버시, 알고리즘 편향성, 자동화로 인한 일자리 대체 등의 문제를 상세히 분석합니다.
\n
예시/데이터: 영상에서는 구체적인 사례로 2022년 발생한 XYZ 회사의 AI 채용 시스템이 여성 지원자에 대해 27% 낮은 합격률을 보인 편향성 문제를 제시합니다. 또한, 자율주행차 사고 시 책임 소재에 관한 설문조사 결과, 응답자의 64%가 제조사에 책임이 있다고 답한 반면, 23%만이 사용자에게 책임이 있다고 응답했습니다.
\n
결론: 발표자는 AI 기술의 건전한 발전을 위해 투명성(Transparency), 책임성(Accountability), 공정성(Fairness)의 세 가지 원칙을 제안합니다. "기술 발전과 윤리적 고려는 상호보완적이며, 지속 가능한 AI 생태계를 위해 필수적"이라는 메시지로 마무리합니다.
\n\n

3. 핵심 포인트:
- AI 기술은 최근 5년간 38%의 성장률을 보이며, 특히 딥러닝 분야에서 이미지 인식 정확도가 2015년 68%에서 2023년 98%로 크게 향상되었습니다.
- 알고리즘 편향성은 실제 사례에서 확인되었으며, XYZ 회사의 AI 채용 시스템은 여성 지원자에 대해 27% 낮은 합격률을 보였습니다.
- 자율주행차 사고 책임 소재에 관한 설문조사에서 응답자의 64%가 제조사에, 23%만이 사용자에게 책임이 있다고 응답했습니다.
- AI 윤리 규제 프레임워크는 국가별로 상이하며, EU의 AI 규제안은 위험 기반 접근법을 채택하여 고위험 AI 시스템에 대한 엄격한 규제를 제안합니다.
- 지속 가능한 AI 생태계를 위해서는 투명성, 책임성, 공정성의 세 가지 핵심 원칙이 모든 AI 개발 및 구현 과정에 통합되어야 합니다.

자막 내용:
{transcript}
        """

        # Gemini API 호출
        response = await model.generate_content_async(prompt.format(transcript=transcript))
        content = response.text
        return parse_ai_response(content)

    except Exception as e:
        raise Exception(f"Gemini API 요약 생성 중 오류가 발생했습니다: {str(e)}")

def parse_ai_response(content: str) -> Dict[str, any]:
    """AI 모델의 응답을 파싱하여 구조화된 형식으로 변환합니다."""
    lines = content.split("\n")
    title = ""
    summary = ""
    key_points = []
    
    current_section = ""
    for line in lines:
        line = line.strip()
        if "제목:" in line:
            title = line.split("제목:")[1].strip()
            current_section = "title"
        elif "요약:" in line:
            current_section = "summary"
        elif "핵심 포인트:" in line:
            current_section = "key_points"
        elif line and current_section == "summary" and not line.startswith("-"):
            summary += line + " "
        elif line.startswith("-"):
            point = line[1:].strip()
            if point:
                key_points.append(point)

    return {
        "title": title,
        "summary": summary.strip(),
        "key_points": key_points
    } 