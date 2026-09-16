---
name: google-workspace-manager
description: Automates creating, updating, and managing Google Sheets, Google Docs, and Google Slides inside Google Drive or local office files. Trigger whenever the user requests generating, updating, or organizing spreadsheets, documents, or presentation slides.
---

# Google Workspace Manager

## Goal
사용자의 자연어 요청과 데이터를 분석하여, Google Drive 상에 Google 스프레드시트(Sheets), 문서(Docs), 슬라이드(Slides) 또는 로컬 오피스 산출물을 안전하고 정확하게 자동 생성 및 관리한다.

## Instructions
1. **Determine Target & Platform (대상 매체 및 위치 확인)**
   - 구글 드라이브 폴더 링크/ID가 주어졌거나 구글 문서 요청인 경우 ➔ Google Cloud API 모드로 진행.
   - 로컬 파일(.xlsx, .docx, .pptx) 다운로드/생성 요청인 경우 ➔ Local File 모드로 진행.
   - 매체나 저장 위치가 모호할 경우 ➔ 사용자에게 확인 질문을 하거나 기본 '내 드라이브(루트)'를 대상으로 처리.

2. **Formulate Payload and Execute Script (데이터 구성 및 실행)**
   - 입력할 데이터(표, 텍스트, 슬라이드 항목)를 JSON 파일로 구성.
   - `scripts/workspace_ops.py` 스크립트를 `run_command`로 실행:
     - 시트: `python scripts/workspace_ops.py --type sheet --folder-id <FOLDER_ID> --title "<TITLE>" --data-json <JSON_PATH>`
     - 문서: `python scripts/workspace_ops.py --type doc --folder-id <FOLDER_ID> --title "<TITLE>" --data-json <JSON_PATH>`
     - 슬라이드: `python scripts/workspace_ops.py --type slide --folder-id <FOLDER_ID> --title "<TITLE>" --data-json <JSON_PATH>`

3. **Deliver URL Link (결과 링크 반환)**
   - 산출물 생성이 완료되면 사용자에게 생성된 웹 URL 링크(`https://docs.google.com/...`)를 제공.

## Constraints
- **CRITICAL**: 대상 구글 드라이브 폴더 ID가 유효하지 않거나 권한이 없을 경우 안전하게 대체 위치(내 드라이브 루트)에 생성하고 사용자에게 안내한다.
- 인증 오류 또는 API 미활성화 시 `credentials.json` 배치 또는 1회 웹 승인 링크를 안내한다.
- 불필요한 부가 작업 없이 오로지 Google Workspace 문서 생성 및 데이터 주입에만 집중한다.
