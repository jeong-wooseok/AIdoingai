<%*
// ==========================================================
// Voice Record STT (Speech-to-Text) Template
// OpenAI Whisper API를 사용하여 오디오 파일을 텍스트로 변환합니다.
// 임시파일생성 → STT → Summary → Title → Properties → 파일명변경
// ==========================================================

// [설정] API 키 가져오기
const API_KEY = tp.user.secret();
const MODEL_NAME = "gpt-4o-mini";

try {
    // ============================================
    // STEP 0: 작업용 임시 파일 먼저 생성
    // ============================================
    new Notice("작업 파일 생성 중...");
    console.log("Step 0: 임시 파일 생성");

    const targetFolder = "5.Work/5-3.회의록/Recorded";
    const tempFileName = `_temp_stt_${Date.now()}.md`;
    const tempPath = `${targetFolder}/${tempFileName}`;

    // 임시 파일 생성
    const workFile = await app.vault.create(tempPath, "처리 중...");
    console.log("임시 파일 생성 완료:", tempPath);

    // 생성한 파일 열기
    await app.workspace.getLeaf().openFile(workFile);
    await new Promise(resolve => setTimeout(resolve, 200));

    // ============================================
    // STEP 1: 오디오 파일 선택
    // ============================================
    new Notice("오디오 파일 선택 중...");
    console.log("Step 1: 오디오 파일 선택");

    // 지원하는 오디오 파일 형식 정의
    const supportedFileTypes = ["wav", "webm", "m4a", "mp3", "mp4", "flac", "ogg"];

    // Vault에서 오디오 파일 목록 가져오기 (생성일 기준 정렬)
    const audioFiles = this.app.vault.getFiles()
        .filter((item) => supportedFileTypes.indexOf(item.extension) >= 0)
        .sort((a, b) => b.stat.ctime - a.stat.ctime); // 최신 파일이 먼저 나오도록

    // 오디오 파일이 없으면 중단
    if (!audioFiles || audioFiles.length === 0) {
        await app.vault.delete(workFile);
        new Notice("변환할 오디오 파일이 없습니다.");
        return;
    }

    // 사용자가 변환할 오디오 파일 선택 (파일 크기 포함)
    const target = await tp.system.suggester(
        (item) => {
            const sizeMB = (item.stat.size / (1024 * 1024)).toFixed(1);
            const dateStr = new Date(item.stat.ctime).toLocaleDateString('ko-KR').replace(/\. /g, '').replace('.', '');
            return `${sizeMB}mb_${item.basename}_${dateStr}`;
        },
        audioFiles,
        true
    );

    // 파일 선택을 취소한 경우
    if (!target) {
        await app.vault.delete(workFile);
        new Notice("파일 선택이 취소되었습니다.");
        return;
    }

    console.log("선택된 오디오 파일:", target.basename);

    // ============================================
    // STEP 1: STT 변환
    // ============================================
    new Notice(`1/4 STT 변환 중... (${target.basename})`);
    console.log("Step 1: STT 시작");

    const root = tp.file.path().replace(tp.file.path(true), "").replace("\/", "\\");
    const inputFile = root + target.path.replace(/\//g, "\\");
    const scriptPath = root + "8.Template\\Scripts\\whisper_api.py";

    const cmd_text = `chcp 65001 >nul && py "${scriptPath}" "${API_KEY}" "${inputFile}" ko`;
    const sttResult = await tp.user.cmd_exec({Cmd: cmd_text});

    console.log("STT 결과 길이:", sttResult ? sttResult.length : 0);

    // 결과 확인
    if (!sttResult || sttResult.trim().length === 0) {
        new Notice("STT 변환 결과가 비어있습니다.");
        return;
    }

    if (sttResult.includes("Error:")) {
        new Notice("API 호출 중 오류 발생");
        return;
    }

    console.log("Step 1 완료: STT 성공");

    // ============================================
    // STEP 2: Summary 생성
    // ============================================
    new Notice(`2/4 요약 생성 중...`);
    console.log("Step 2: Summary 시작");

    let summary = "";

    try {
        const summaryPrompt = `당신은 정보 요약 전문가입니다. 아래 지침에 따라 텍스트를 요약해주세요.

[지침]
제공된 텍스트를 바탕으로 연구자 및 전문가를 위한 핵심 정보 요약을 작성합니다.

- **핵심 정보:** 주요 연구 결과, 핵심 주장과 근거, 연구 방법론, 주요 통계 포함
- **스타일:** 200단어 내외의 명확하고 간결한 보고서체 (개인적 의견 제외)
- **형식:** 가독성을 위해 불릿 포인트 등을 적절히 사용`;

        const summaryResponse = await requestUrl({
            url: "https://api.openai.com/v1/chat/completions",
            method: "POST",
            headers: {
                "Authorization": `Bearer ${API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                model: MODEL_NAME,
                messages: [
                    { role: "system", content: summaryPrompt },
                    { role: "user", content: sttResult }
                ],
                temperature: 0.3
            })
        });

        if (summaryResponse.status === 200) {
            const summaryContent = summaryResponse.json.choices[0].message.content;
            summary = summaryContent.replace(/\n/g, "\n> ");
            console.log("Step 2 완료: Summary 생성 성공");
        } else {
            console.error("Summary API 오류:", summaryResponse.status);
        }
    } catch (summaryError) {
        console.error("Summary 생성 실패:", summaryError);
    }

    // ============================================
    // STEP 3: 파일명 생성
    // ============================================
    new Notice(`3/4 파일명 생성 중...`);
    console.log("Step 3: Title 시작");

    let newTitle = "STT 변환 결과";

    try {
        const titlePrompt = `제공된 텍스트의 핵심 내용을 한 문장(20자 이내)으로 요약하여 파일명으로 사용할 수 있는 제목을 만들어주세요.
특수문자(:, /, \\, *, ?, ", <, >, |)는 사용하지 마세요.
제목만 출력하고 다른 설명은 추가하지 마세요.`;

        const titleResponse = await requestUrl({
            url: "https://api.openai.com/v1/chat/completions",
            method: "POST",
            headers: {
                "Authorization": `Bearer ${API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                model: MODEL_NAME,
                messages: [
                    { role: "system", content: titlePrompt },
                    { role: "user", content: sttResult }
                ],
                temperature: 0.3,
                max_tokens: 50
            })
        });

        if (titleResponse.status === 200) {
            newTitle = titleResponse.json.choices[0].message.content.trim().replace(/[:/\\*?"<>|]/g, '');

            // 오디오 파일명에서 날짜(YYYYMMDD) 추출
            const dateMatch = target.basename.match(/(\d{8})/);
            if (dateMatch) {
                const fullDate = dateMatch[1]; // YYYYMMDD
                const shortDate = fullDate.substring(2); // YYMMDD (앞 2자리 제거)
                newTitle = shortDate + "_" + newTitle;
                console.log("날짜 추가됨:", shortDate);
            }

            console.log("Step 3 완료: Title 생성 성공 -", newTitle);
        } else {
            console.error("Title API 오류:", titleResponse.status);
        }
    } catch (titleError) {
        console.error("Title 생성 실패:", titleError);
    }

    // ============================================
    // STEP 4: Properties 생성
    // ============================================
    new Notice("4/4 속성 생성 중...");
    console.log("Step 4: Properties 시작");

    let properties = "";

    try {
        const propertiesPrompt = `당신은 옵시디안 노트의 속성값(metadata) 생성 전문가입니다. 제공된 텍스트를 분석하여 가장 적절한 속성값을 추천해주세요.

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

        const propertiesResponse = await requestUrl({
            url: "https://api.openai.com/v1/chat/completions",
            method: "POST",
            headers: {
                "Authorization": `Bearer ${API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                model: MODEL_NAME,
                messages: [
                    { role: "system", content: propertiesPrompt },
                    { role: "user", content: sttResult }
                ],
                temperature: 0.3
            })
        });

        if (propertiesResponse.status === 200) {
            properties = propertiesResponse.json.choices[0].message.content.trim();
            console.log("Step 4 완료: Properties 생성 성공");
        } else {
            console.error("Properties API 오류:", propertiesResponse.status);
        }
    } catch (propError) {
        console.error("Properties 생성 실패:", propError);
    }

    // ============================================
    // STEP 5: 최종 내용 조합 및 파일에 작성
    // ============================================
    new Notice("5/6 파일 작성 중...");
    console.log("Step 5: 파일 작성 시작");

    // 최종 내용 조합
    const finalContent = `${properties}

> [!summary] AI 요약 보고서
> ${summary}

## STT 변환 원본
![[${target.path}]]
> [!info] STT 변환 정보
> **오디오 파일:** ${target.path}
> **변환 시간:** ${new Date().toLocaleString()}
> **모델:** OpenAI Whisper-1

${sttResult}

`;

    console.log("최종 내용 길이:", finalContent.length);

    // 생성한 임시 파일에 내용 작성
    await app.vault.modify(workFile, finalContent);
    console.log("파일 작성 완료:", workFile.path);

    // 파일 시스템 동기화 대기
    await new Promise(resolve => setTimeout(resolve, 300));

    // 작성 확인
    const writtenContent = await app.vault.read(workFile);
    console.log("작성 확인 - 파일 내용 길이:", writtenContent.length);

    if (writtenContent.length === 0 || writtenContent === "처리 중...") {
        console.error("내용이 제대로 작성되지 않음! 재시도");
        await app.vault.modify(workFile, finalContent);
        await new Promise(resolve => setTimeout(resolve, 300));
        console.log("재작성 완료");
    }

    // ============================================
    // STEP 6: 파일 이름 변경
    // ============================================
    new Notice("6/6 파일 이름 변경 중...");
    console.log("Step 6: 파일 이름 변경 시작");

    let finalPath = `${targetFolder}/${newTitle}.md`;

    // 파일명 중복 확인 및 타임스탬프 추가
    if (app.vault.getAbstractFileByPath(finalPath)) {
        const timestamp = new Date().toLocaleString('ko-KR', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).replace(/\. /g, '').replace('.', '').replace(/:/g, '').replace(/ /g, '_');
        finalPath = `${targetFolder}/${newTitle}_${timestamp}.md`;
        console.log("파일명 중복, 타임스탬프 추가:", finalPath);
    }

    console.log("파일 이름 변경:", workFile.path, "->", finalPath);

    try {
        // 파일 이름 변경
        await app.fileManager.renameFile(workFile, finalPath);
        console.log("파일 이름 변경 완료");

        // 변경 후 잠시 대기
        await new Promise(resolve => setTimeout(resolve, 200));

        // 최종 파일 확인
        const finalFile = app.vault.getAbstractFileByPath(finalPath);
        if (finalFile) {
            console.log("최종 파일 확인:", finalFile.path);

            // 내용 확인
            const finalFileContent = await app.vault.read(finalFile);
            console.log("최종 파일 내용 길이:", finalFileContent.length);

            // 모든 열려있는 리프(탭) 가져오기
            const leaves = app.workspace.getLeavesOfType("markdown");

            // 템플릿 파일이나 임시 파일이 열려있으면 닫기
            const templateFile = tp.config.target_file;
            for (const leaf of leaves) {
                const file = leaf.view.file;
                if (file && (file.path === templateFile?.path || file.path === tempPath)) {
                    console.log("불필요한 탭 닫기:", file.path);
                    leaf.detach();
                }
            }

            await new Promise(resolve => setTimeout(resolve, 100));

            // 최종 파일을 새 탭에서 열기
            const newLeaf = app.workspace.getLeaf('tab');
            await newLeaf.openFile(finalFile);
            console.log("파일 열기 완료");
        }

        new Notice(`✅ 완료! 파일: ${newTitle}`);
        console.log("전체 작업 완료");

        // 템플릿 파일 삭제 (있는 경우)
        const templateFile = tp.config.target_file;
        if (templateFile && templateFile.path !== finalPath) {
            try {
                // 파일이 닫힌 후 삭제
                await new Promise(resolve => setTimeout(resolve, 100));
                await app.vault.delete(templateFile);
                console.log("템플릿 파일 삭제 완료");
            } catch (deleteError) {
                console.log("템플릿 파일 삭제 실패 (무시):", deleteError.message);
            }
        }

    } catch (renameError) {
        console.error("파일 이름 변경 오류:", renameError);
        new Notice("❌ 파일 이름 변경 실패");
    }

} catch (error) {
    new Notice("STT 변환 중 오류 발생");
    console.error("STT Error:", error);
    console.error("Error stack:", error.stack);
}
%>