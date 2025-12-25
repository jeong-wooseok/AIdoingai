<%*
// ==========================================================
// [설정] 별도 파일(secret.js)에서 API 키를 불러옵니다.
// 파일명이 secret.js라면 tp.user.secret()을 호출합니다.
const API_KEY = tp.user.secret(); 

// [설정] 모델명
const MODEL_NAME = "gpt-4o-mini"; 
// ==========================================================

// 1. 요약할 대상 텍스트 가져오기
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
    new Notice("요약할 텍스트가 없습니다.");
    return;
}

// 2. 프롬프트 정의
const systemPrompt = `
당신은 학술 논문 및 정보 요약 전문가입니다. 아래 지침에 따라 텍스트를 요약해주세요.

[지침]
> [!summary] 요약
> 제공된 텍스트를 바탕으로 연구자 및 전문가를 위한 핵심 정보 요약을 작성합니다.
>
> - **핵심 정보:** 주요 연구 결과, 핵심 주장과 근거, 연구 방법론, 주요 통계 포함
> - **스타일:** 200단어 내외의 명확하고 간결한 보고서체 (개인적 의견 제외)
> - **형식:** 가독성을 위해 불릿 포인트 등을 적절히 사용
`;

new Notice(`AI 요약 생성 중... (${MODEL_NAME})`);

try {
    // 3. OpenAI API 호출
    const response = await requestUrl({
        url: "https://api.openai.com/v1/chat/completions",
        method: "POST",
        headers: {
            "Authorization": `Bearer ${API_KEY}`, // 불러온 키 사용
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
        
        const formattedResult = `\n\n> [!summary] AI 요약 보고서\n> ${result.replace(/\n/g, "\n> ")}\n`;
        
        tp.file.cursor_append(formattedResult);
        
        new Notice("요약이 완료되었습니다!");
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