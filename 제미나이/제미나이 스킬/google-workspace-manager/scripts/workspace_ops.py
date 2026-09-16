# -*- coding: utf-8 -*-
"""
==============================================================================
[workspace_ops.py] Google Workspace 산출물 생성 및 사내 디자인 규칙 일괄 적용 엔진
==============================================================================
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import argparse
from googleapiclient.discovery import build
from auth_helper import get_credentials

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return {
        "red": int(hex_code[0:2], 16) / 255.0,
        "green": int(hex_code[2:4], 16) / 255.0,
        "blue": int(hex_code[4:6], 16) / 255.0
    }

def pt_to_emu(pt):
    return int(pt * 12700)

def create_drive_file(drive_service, title, folder_id, mime_type):
    file_metadata = {
        'name': title,
        'mimeType': mime_type
    }
    if folder_id and folder_id != 'root':
        file_metadata['parents'] = [folder_id]

    try:
        file = drive_service.files().create(body=file_metadata, fields='id, webViewLink', supportsAllDrives=True).execute()
    except Exception as e:
        if 'notFound' in str(e) or 'File not found' in str(e):
            print(f"[알림] 대상 폴더({folder_id})를 찾을 수 없어 '내 드라이브(루트)'에 생성합니다...", flush=True)
            file_metadata.pop('parents', None)
            file = drive_service.files().create(body=file_metadata, fields='id, webViewLink', supportsAllDrives=True).execute()
        else:
            raise e
    return file.get('id'), file.get('webViewLink')

# ==============================================================================
# 1. 📊 구글 스프레드시트 생성 및 서식 엔진 (rules/design/sheets.md 규격)
# ==============================================================================
def process_sheet(drive_service, sheets_service, folder_id, title, data):
    mime = 'application/vnd.google-apps.spreadsheet'
    ss_id, link = create_drive_file(drive_service, title, folder_id, mime)
    print(f"[생성 완료] 구글 시트 파일 생성됨: {link}", flush=True)

    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=ss_id).execute()
    existing_sheets = spreadsheet.get('sheets', [])
    first_sheet_id = existing_sheets[0]['properties']['sheetId'] if existing_sheets else 0

    structure_requests = []
    style_requests = []
    values_batch = []

    sheets_to_process = data.get('sheets', [])
    if not sheets_to_process and 'headers' in data:
        sheets_to_process = [data]

    DEFAULT_WIDTHS = [140, 170, 260, 230, 200, 180, 180]

    for idx, sheet_info in enumerate(sheets_to_process):
        sheet_title = sheet_info.get('title', f"Sheet{idx+1}")
        headers = sheet_info.get('headers', [])
        rows = sheet_info.get('rows', [])

        if idx == 0:
            current_sheet_id = first_sheet_id
            structure_requests.append({
                "updateSheetProperties": {
                    "properties": {"sheetId": current_sheet_id, "title": sheet_title},
                    "fields": "title"
                }
            })
        else:
            current_sheet_id = 1000 + idx
            structure_requests.append({
                "addSheet": {
                    "properties": {"sheetId": current_sheet_id, "title": sheet_title}
                }
            })

        all_rows = [headers] + rows
        values_batch.append({
            'range': f"'{sheet_title}'!A1",
            'values': all_rows
        })

        col_count = len(headers)
        row_count = len(all_rows)

        # 1행 틀 고정
        style_requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": current_sheet_id,
                    "gridProperties": {"frozenRowCount": 1}
                },
                "fields": "gridProperties.frozenRowCount"
            }
        })

        # 자동 줄바꿈 및 세로 정중앙
        style_requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": current_sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": col_count
                },
                "cell": {
                    "userEnteredFormat": {
                        "wrapStrategy": "WRAP",
                        "verticalAlignment": "MIDDLE",
                        "textFormat": {
                            "fontFamily": "Noto Sans",
                            "fontSize": 10
                        }
                    }
                },
                "fields": "userEnteredFormat(wrapStrategy,verticalAlignment,textFormat.fontFamily,textFormat.fontSize)"
            }
        })

        # 1행 다크 네이비 헤더
        header_bg = hex_to_rgb("#1A365D")
        style_requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": current_sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": col_count
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": header_bg,
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                            "bold": True,
                            "fontSize": 11,
                            "fontFamily": "Noto Sans"
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        })

        # 1행 헤더 행 높이 38px
        style_requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": current_sheet_id,
                    "dimension": "ROWS",
                    "startIndex": 0,
                    "endIndex": 1
                },
                "properties": {
                    "pixelSize": 38
                },
                "fields": "pixelSize"
            }
        })

        # Zebra 줄무늬 패턴
        style_requests.append({
            "addBanding": {
                "bandedRange": {
                    "range": {
                        "sheetId": current_sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": row_count,
                        "startColumnIndex": 0,
                        "endColumnIndex": col_count
                    },
                    "rowProperties": {
                        "headerColor": header_bg,
                        "firstBandColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                        "secondBandColor": hex_to_rgb("#F1F5F9")
                    }
                }
            }
        })

        # 컴팩트 열 너비
        for c_idx in range(col_count):
            target_width = DEFAULT_WIDTHS[c_idx] if c_idx < len(DEFAULT_WIDTHS) else 180
            style_requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": current_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": c_idx,
                        "endIndex": c_idx + 1
                    },
                    "properties": {
                        "pixelSize": target_width
                    },
                    "fields": "pixelSize"
                }
            })

    if structure_requests:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=ss_id,
            body={"requests": structure_requests}
        ).execute()

    if values_batch:
        sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=ss_id,
            body={"valueInputOption": "USER_ENTERED", "data": values_batch}
        ).execute()

    if style_requests:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=ss_id,
            body={"requests": style_requests}
        ).execute()

    return link

# ==============================================================================
# 2. 📄 구글 독스(Docs) 문서 생성 및 서식 엔진 (rules/design/docs.md 규격)
# ==============================================================================
def process_doc(drive_service, docs_service, folder_id, title, data):
    mime = 'application/vnd.google-apps.document'
    doc_id, link = create_drive_file(drive_service, title, folder_id, mime)
    print(f"[생성 완료] 구글 독스 문서 생성됨: {link}", flush=True)

    content_text = f"{title}\n\n"
    sections = data.get('sections', [])
    for sec in sections:
        sec_title = sec.get('heading', '')
        sec_body = sec.get('body', '')
        if sec_title:
            content_text += f"{sec_title}\n"
        if sec_body:
            content_text += f"{sec_body}\n\n"

    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': content_text
            }
        }
    ]

    docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    return link

# ==============================================================================
# 3. 📑 구글 슬라이드(Slides) 생성 및 서식 엔진 (rules/design/slides.md 규격)
# ==============================================================================
def process_slide(drive_service, slides_service, folder_id, title, data):
    mime = 'application/vnd.google-apps.presentation'
    pres_id, link = create_drive_file(drive_service, title, folder_id, mime)
    print(f"[생성 완료] 구글 슬라이드 발표자료 생성됨: {link}", flush=True)

    # 1. 기존 슬라이드 정보 확인 (기본 빈 슬라이드 1장 존재)
    presentation = slides_service.presentations().get(presentationId=pres_id).execute()
    existing_slides = presentation.get('slides', [])
    initial_slide_id = existing_slides[0]['objectId'] if existing_slides else None

    requests = []
    slides_data = data.get('slides', [])

    # 색상 정의 (안티그래비티 테마)
    COLOR_PRIMARY = hex_to_rgb("#1A365D")   # 다크 네이비
    COLOR_ACCENT = hex_to_rgb("#2563EB")    # 제미나이 블루
    COLOR_MUTED = hex_to_rgb("#475569")     # 슬레이트 그레이
    COLOR_BG_CARD = hex_to_rgb("#F8FAFC")   # 카드 배경
    COLOR_BORDER = hex_to_rgb("#CBD5E1")    # 테두리

    created_slide_ids = []

    # 슬라이드 페이지 생성
    for idx, slide_info in enumerate(slides_data):
        slide_id = f"slide_page_{idx+1}"
        created_slide_ids.append(slide_id)
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'insertionIndex': idx,
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK' # 완전 백지 레이아웃으로 커스텀 디자인 배치
                }
            }
        })

    # 초기 기본 슬라이드 삭제
    if initial_slide_id:
        requests.append({
            'deleteObject': {'objectId': initial_slide_id}
        })

    # 1단계: 슬라이드 구조 생성
    slides_service.presentations().batchUpdate(presentationId=pres_id, body={'requests': requests}).execute()

    # 2단계: 각 슬라이드별 디자인 및 텍스트 박스 주입
    content_requests = []

    for idx, slide_info in enumerate(slides_data):
        slide_id = created_slide_ids[idx]
        stype = slide_info.get('type', 'content')
        stitle = slide_info.get('title', '')

        if stype == 'title' or idx == 0:
            # [표지 슬라이드]
            subtitle = slide_info.get('subtitle', '')
            title_box_id = f"title_box_{idx}"
            sub_box_id = f"sub_box_{idx}"

            # 제목 박스 (다크네이비 볼드 32pt)
            content_requests.append({
                'createShape': {
                    'objectId': title_box_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {'width': {'magnitude': pt_to_emu(620), 'unit': 'EMU'}, 'height': {'magnitude': pt_to_emu(80), 'unit': 'EMU'}},
                        'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': pt_to_emu(50), 'translateY': pt_to_emu(110), 'unit': 'EMU'}
                    }
                }
            })
            content_requests.append({'insertText': {'objectId': title_box_id, 'text': stitle}})
            content_requests.append({
                'updateTextStyle': {
                    'objectId': title_box_id,
                    'style': {
                        'foregroundColor': {'opaqueColor': {'rgbColor': COLOR_PRIMARY}},
                        'bold': True,
                        'fontSize': {'magnitude': 32, 'unit': 'PT'},
                        'fontFamily': 'Noto Sans'
                    },
                    'fields': 'foregroundColor,bold,fontSize,fontFamily'
                }
            })

            # 부제목 박스 (그레이 16pt)
            if subtitle:
                content_requests.append({
                    'createShape': {
                        'objectId': sub_box_id,
                        'shapeType': 'TEXT_BOX',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {'width': {'magnitude': pt_to_emu(620), 'unit': 'EMU'}, 'height': {'magnitude': pt_to_emu(50), 'unit': 'EMU'}},
                            'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': pt_to_emu(50), 'translateY': pt_to_emu(195), 'unit': 'EMU'}
                        }
                    }
                })
                content_requests.append({'insertText': {'objectId': sub_box_id, 'text': subtitle}})
                content_requests.append({
                    'updateTextStyle': {
                        'objectId': sub_box_id,
                        'style': {
                            'foregroundColor': {'opaqueColor': {'rgbColor': COLOR_MUTED}},
                            'fontSize': {'magnitude': 16, 'unit': 'PT'},
                            'fontFamily': 'Noto Sans'
                        },
                        'fields': 'foregroundColor,fontSize,fontFamily'
                    }
                })

        else:
            # [본문 슬라이드]
            # 1. 상단 액션 타이틀 (20pt 볼드 다크네이비)
            header_box_id = f"header_box_{idx}"
            content_requests.append({
                'createShape': {
                    'objectId': header_box_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {'width': {'magnitude': pt_to_emu(620), 'unit': 'EMU'}, 'height': {'magnitude': pt_to_emu(45), 'unit': 'EMU'}},
                        'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': pt_to_emu(50), 'translateY': pt_to_emu(35), 'unit': 'EMU'}
                    }
                }
            })
            content_requests.append({'insertText': {'objectId': header_box_id, 'text': stitle}})
            content_requests.append({
                'updateTextStyle': {
                    'objectId': header_box_id,
                    'style': {
                        'foregroundColor': {'opaqueColor': {'rgbColor': COLOR_PRIMARY}},
                        'bold': True,
                        'fontSize': {'magnitude': 22, 'unit': 'PT'},
                        'fontFamily': 'Noto Sans'
                    },
                    'fields': 'foregroundColor,bold,fontSize,fontFamily'
                }
            })

            # 2. 카드 그리드 레이아웃 (포인트별 카드 박스 생성)
            points = slide_info.get('points', [])
            card_y_start = 95
            card_height = 80
            card_spacing = 15

            for p_idx, point_text in enumerate(points):
                card_shape_id = f"card_shape_{idx}_{p_idx}"
                card_y = card_y_start + p_idx * (card_height + card_spacing)

                # 카드 박스 (배경 + 테두리)
                content_requests.append({
                    'createShape': {
                        'objectId': card_shape_id,
                        'shapeType': 'ROUND_RECTANGLE',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {'width': {'magnitude': pt_to_emu(620), 'unit': 'EMU'}, 'height': {'magnitude': pt_to_emu(card_height), 'unit': 'EMU'}},
                            'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': pt_to_emu(50), 'translateY': pt_to_emu(card_y), 'unit': 'EMU'}
                        }
                    }
                })
                # 카드 배경 및 테두리 색상
                content_requests.append({
                    'updateShapeProperties': {
                        'objectId': card_shape_id,
                        'shapeProperties': {
                            'shapeBackgroundFill': {
                                'solidFill': {'color': {'rgbColor': COLOR_BG_CARD}}
                            },
                            'outline': {
                                'outlineFill': {'solidFill': {'color': {'rgbColor': COLOR_BORDER}}},
                                'weight': {'magnitude': pt_to_emu(1), 'unit': 'EMU'}
                            }
                        },
                        'fields': 'shapeBackgroundFill.solidFill.color,outline.outlineFill.solidFill.color,outline.weight'
                    }
                })
                # 카드 텍스트 삽입
                card_text_formatted = f"• {point_text}"
                content_requests.append({'insertText': {'objectId': card_shape_id, 'text': card_text_formatted}})
                content_requests.append({
                    'updateTextStyle': {
                        'objectId': card_shape_id,
                        'style': {
                            'foregroundColor': {'opaqueColor': {'rgbColor': {'red': 0.1, 'green': 0.15, 'blue': 0.25}}},
                            'bold': True,
                            'fontSize': {'magnitude': 14, 'unit': 'PT'},
                            'fontFamily': 'Noto Sans'
                        },
                        'fields': 'foregroundColor,bold,fontSize,fontFamily'
                    }
                })

    if content_requests:
        slides_service.presentations().batchUpdate(presentationId=pres_id, body={'requests': content_requests}).execute()

    return link

def main():
    parser = argparse.ArgumentParser(description="Google Workspace Operations Controller")
    parser.add_argument("--type", choices=['sheet', 'doc', 'slide'], required=True, help="산출물 유형(sheet, doc, slide)")
    parser.add_argument("--folder-id", required=True, help="대상 구글 드라이브 폴더 고유 ID")
    parser.add_argument("--title", default="Antigravity Workspace Item", help="문서 제목")
    parser.add_argument("--data-json", required=True, help="입력 데이터 JSON 파일 경로")

    args = parser.parse_args()

    with open(args.data_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    creds = get_credentials()
    drive_service = build('drive', 'v3', credentials=creds)

    if args.type == 'sheet':
        sheets_service = build('sheets', 'v4', credentials=creds)
        url = process_sheet(drive_service, sheets_service, args.folder_id, args.title, data)
    elif args.type == 'doc':
        docs_service = build('docs', 'v1', credentials=creds)
        url = process_doc(drive_service, docs_service, args.folder_id, args.title, data)
    elif args.type == 'slide':
        slides_service = build('slides', 'v1', credentials=creds)
        url = process_slide(drive_service, slides_service, args.folder_id, args.title, data)

    print(f"\n[최종 성공] 산출물 생성이 완료되었습니다: {url}", flush=True)

if __name__ == '__main__':
    main()
