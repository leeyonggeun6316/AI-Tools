# 🌐 Google Workspace Manager (구글 워크스페이스 통합 매니저 스킬)

자연어 요청 한 줄로 Google Drive 상에 **스프레드시트(Sheets), 문서(Docs), 슬라이드(Slides)**를 실시간 자동 생성하고 편집하는 Antigravity 전용 스킬입니다.

---

## 📌 주요 기능
1. **📊 구글 스프레드시트 (Google Sheets)**
   - 다중 탭(시트) 자동 생성 및 일괄 데이터 주입
   - 1행 다크 네이비 헤더, 틀 고정(Freeze Rows), 자동 줄바꿈(WRAP), 컴팩트 열 너비 자동 최적화
2. **📄 구글 독스 문서 (Google Docs)**
   - 대제목, 제미나이 블루 소제목, 안내/주의 콜아웃 박스 서식 적용
3. **📑 구글 슬라이드 발표자료 (Google Slides)**
   - 16:9 와이드스크린 규격, 상단 액션 타이틀, 2~3단 카드 그리드 레이아웃 자동 렌더링
4. **🔒 영구 무소음 자동 인증**
   - 1회 브라우저 로그인 후 `token.json`이 자동 저장되어 이후 명령부터는 추가 인증 없이 완전 자동 실행

---

## 🛠️ [필독] 초기 세팅 5단계 완벽 가이드
Google API 보안 정책상 최초 1회 Google Cloud Console에서 데스크톱 OAuth 키 발급이 필요합니다. 아래 순서대로 3분이면 완료됩니다.

### 1단계: Google Cloud Console 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속 및 로그인
2. 상단 프로젝트 선택 드롭다운 ➔ **[새 프로젝트]** 클릭
3. 프로젝트 이름 입력 (예: `Workspace-Assistant` / ⚠️ `Google` 단어 포함 불가) ➔ **[만들기]**

### 2단계: OAuth 동의 화면 구성 (가장 중요!)
1. 좌측 메뉴 ➔ **[API 및 서비스]** ➔ **[OAuth 동의 화면]** 클릭
2. 사용자 유형: **[외부(External)]** 선택 후 [만들기]
3. 앱 정보 입력:
   - 앱 이름: `Workspace Assistant`
   - 사용자 지원 이메일: 본인 이메일
   - 개발자 연락처 정보: 본인 이메일 ➔ [저장 후 계속]
4. **[테스트 사용자] 단계 (★필수★)**:
   - **[+ ADD USERS]** 클릭 ➔ 본인의 구글 계정 이메일 입력 ➔ [저장]

### 3단계: 필수 Google API 4종 1초 활성화
아래 4개 링크를 차례로 열어 파란색 **[사용]** 버튼을 클릭합니다:
- 👉 [Google Drive API 활성화](https://console.cloud.google.com/apis/library/drive.googleapis.com)
- 👉 [Google Sheets API 활성화](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
- 👉 [Google Docs API 활성화](https://console.cloud.google.com/apis/library/docs.googleapis.com)
- 👉 [Google Slides API 활성화](https://console.cloud.google.com/apis/library/slides.googleapis.com)

### 4단계: 데스크톱 클라이언트 OAuth 키 다운로드
1. 좌측 메뉴 ➔ **[사용자 인증 정보]** ➔ 상단 **[+ 사용자 인증 정보 만들기]** ➔ **[OAuth 클라이언트 ID]** 선택
2. 애플리케이션 유형: **[데스크톱 앱(Desktop App)]** 선택 ➔ [만들기]
3. 생성 완료 팝업에서 **[JSON 다운로드]** 클릭
4. 다운로드된 파일의 이름을 **`credentials.json`**으로 변경하여 이 스킬 폴더(`google-workspace-manager/`) 안에 배치합니다.

### 5단계: 최초 1회 인증 실행
1. 터미널에서 스크립트 1회 실행:
   ```bash
   python scripts/auth_helper.py
   ```
2. 콘솔에 출력되는 **인증 링크를 클릭**하여 구글 계정 로그인 및 [허용] 클릭
3. `scripts/token.json` 파일이 자동 생성되며 모든 세팅이 완료됩니다!

---

## 🚀 원클릭 단독 설치 프롬프트 (Copy & Paste)
이 스킬만 본인의 Antigravity에 설치하고 싶다면 아래 프롬프트를 Antigravity 채팅창에 복사해 넣으세요:

```markdown
다음 저장소 경로에 있는 google-workspace-manager 스킬을 내 공식 전역 스킬 경로(C:\Users\<사용자명>\.gemini\config\skills\)에 설치해줘.
1. requirements.txt의 패키지 설치
2. 스킬 폴더 복사
3. 초기 세팅(credentials.json 배치 여부 확인 및 1회 인증)을 단계별로 대화형으로 안내해줘.
```
