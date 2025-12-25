<%*
// ==========================================================
// [설정] 별도 파일(secret.js)에서 API 키를 불러옵니다.
// 파일명이 secret.js라면 tp.user.secret()을 호출합니다.
const API_KEY = tp.user.secret(); 

// [설정] 모델명
const MODEL_NAME = "gpt-4o-mini"; 
// ==========================================================

// 템플릿 출력을 완전히 제어하기 위해 tR 초기화
tR = "";

// 1. 분석할 대상 텍스트 가져오기
let content = tp.file.selection();

if (!content) {
    const editor = app.workspace.activeLeaf?.view?.editor;
    if (editor) {
        content = editor.getValue();
    } else {
        content = await tp.file.content;
    }
}

// 내용이 없으면 중단
if (!content || content.trim().length === 0) {
    new Notice("분석할 텍스트가 없습니다.");
    return;
}

// 2. 프롬프트 정의
const systemPrompt = `당신은 옵시디안 노트의 속성값(metadata) 생성 전문가입니다. 제공된 텍스트를 분석하여 가장 적절한 속성값을 추천해주세요.

[지침]
- **tags**: 텍스트의 핵심 주제와 관련된 태그를 5-10개 추천합니다.
  * 영문 태그: 소문자로, 공백 없이 (예: promptengineering, llms, chainofthought)
  * 한글 태그: 의미 있는 단어로 (예: 프롬프트, AI추론, 제로샷COT)
  * 기술 용어와 일반 용어를 적절히 섞어주세요

- **status**: 콘텐츠의 상태를 하나만 선택하세요.
  * "🟩 완료" - 완성된 정보, 최종 결과물
  * "🟧 예정" - 처리해야 할 정보, 계획 중인 내용
  * "🟦 진행중" - 현재 작업 중인 내용
  * "🟥 보류" - 임시 중단된 내용

- **source**: 소스 URL이 텍스트에 포함되어 있다면 추출하고, 없다면 빈 문자열로 남겨주세요.

- **created**: 오늘 날짜를 YYYY-MM-DD 형식으로 제공하세요.

- **Rating**: 1-5 사이의 숫자로 콘텐츠의 유용성을 평가하세요. 평가가 어렵다면 빈 문자열로 남겨주세요.

[출력 형식]
반드시 아래 YAML 형식으로만 출력하세요. 다른 설명이나 텍스트를 추가하지 마세요:

---
tags:
  - 태그1
  - 태그2
  - 태그3
status: 상태값
source: URL 또는 빈 문자열
created: YYYY-MM-DD
Rating: 숫자 또는 빈 문자열
---`;

new Notice(`속성값 생성 중... (${MODEL_NAME})`);

try {
    // 3. OpenAI API 호출
    const response = await requestUrl({
        url: "https://api.openai.com/v1/chat/completions",
        method: "POST",
        headers: {
            "Authorization": `Bearer ${API_KEY}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            model: MODEL_NAME,
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: content }
            ],
            temperature: 0.3
        })
    });

    // 4. 응답 처리 및 삽입
    if (response.status === 200) {
        const result = response.json.choices[0].message.content;
        
        // 기존 frontmatter가 있는지 확인
        const fileContent = await tp.file.content;
        const frontmatterRegex = /^---\n[\s\S]*?\n---/;
        
        if (frontmatterRegex.test(fileContent)) {
            // 기존 frontmatter가 있으면 교체
            const newContent = fileContent.replace(frontmatterRegex, result.trim());
            // 파일 내용을 교체하기 위해 editor 사용
            const editor = app.workspace.activeLeaf?.view?.editor;
            if (editor) {
                editor.setValue(newContent);
                new Notice("기존 속성값이 업데이트되었습니다!");
            } else {
                // editor가 없으면 커서 위치에 삽입
                tp.file.cursor_append(result.trim() + "\n\n");
                new Notice("속성값이 추가되었습니다!");
            }
        } else {
            // 기존 frontmatter가 없으면 맨 앞에 추가
            const newContent = result.trim() + "\n\n" + fileContent;
            const editor = app.workspace.activeLeaf?.view?.editor;
            if (editor) {
                editor.setValue(newContent);
                new Notice("새로운 속성값이 추가되었습니다!");
            } else {
                // editor가 없으면 커서 위치에 삽입
                tp.file.cursor_append(result.trim() + "\n\n");
                new Notice("속성값이 추가되었습니다!");
            }
        }
    } else {
        const errorMsg = `오류 발생: ${response.status}`;
        new Notice(errorMsg);
        console.error("OpenAI Error:", response);
        tp.file.cursor_append(`\n> [!failure] API 오류 발생\n> 상태 코드: ${response.status}\n> 개발자 도구(Ctrl+Shift+I)를 확인하세요.`);
    }
} catch (error) {
    new Notice("스크립트 실행 중 치명적 오류 발생");
    console.error("Script Error:", error);
    tp.file.cursor_append(`\n> [!failure] 스크립트 오류\n> ${error.message}`);
}
%>
