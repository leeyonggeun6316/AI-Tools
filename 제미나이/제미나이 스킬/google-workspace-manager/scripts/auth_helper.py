# -*- coding: utf-8 -*-
import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/drive',           # 드라이브 내 모든 폴더 탐색 및 파일 생성/수정
    'https://www.googleapis.com/auth/spreadsheets',    # 구글 시트
    'https://www.googleapis.com/auth/documents',       # 구글 독스
    'https://www.googleapis.com/auth/presentations'    # 구글 슬라이드
]

def get_credentials(credentials_path=None, token_path=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if credentials_path is None:
        for candidate in ["credentials.json", os.path.join(script_dir, "credentials.json"), os.path.join(script_dir, "..", "credentials.json")]:
            if os.path.exists(candidate):
                credentials_path = candidate
                break
        if credentials_path is None:
            credentials_path = os.path.join(script_dir, "credentials.json")
    if token_path is None:
        token_path = os.path.join(script_dir, "token.json")

    creds = None

    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"[AUTH] Could not load token.json: {e}", flush=True)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("[AUTH] 만료된 구글 액세스 토큰을 자동 갱신합니다...", flush=True)
                creds.refresh(Request())
            except Exception as e:
                print(f"[AUTH] 토큰 갱신 실패 (재인증 필요): {e}", flush=True)
                creds = None

        if not creds:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"\n[오류] credentials.json 인증 키 파일이 없습니다!\n"
                    f"파일 위치: '{credentials_path}' 에 Google Cloud 데스크톱 OAuth 키를 넣어주세요."
                )

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            auth_msg = (
                "\n==================================================================\n"
                "🔑 [Google Workspace 계정 인증 안내]\n"
                "웹 브라우저가 자동으로 열립니다. 만약 브라우저가 열리지 않거나\n"
                "계정 선택 화면이 나타나지 않으면 아래 링크를 직접 복사하여 브라우저에서 열어주세요:\n\n"
                "{url}\n"
                "==================================================================\n"
            )
            creds = flow.run_local_server(
                port=0,
                open_browser=True,
                authorization_prompt_message=auth_msg
            )

        with open(token_path, 'w', encoding='utf-8') as token_file:
            token_file.write(creds.to_json())
        print("[AUTH] 인증 성공! 1회용 토큰(token.json)이 저장되었습니다.", flush=True)

    return creds

if __name__ == '__main__':
    creds = get_credentials()
