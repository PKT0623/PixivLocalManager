# 프로젝트 구조 (File Structure)

## 개요

Pixiv Local Manager는 기능 단위 모듈 구조를 사용한다.

기존의 대형 파일 중심 구조에서 벗어나,

- Page 단위 분리
- Dialog 단위 분리
- Widget 단위 분리
- Service 단위 분리

를 적용하여 유지보수성을 높였다.

---

# 전체 구조

```text
PixivLocalManager
│
├─ app
│
├─ ui
│
├─ data
│
├─ backups
│
├─ exports
│
├─ docs
│
├─ tests
│
├─ main.py
├─ README.md
└─ requirements.txt
```

---

# app

비즈니스 로직 및 데이터 처리 계층.

```text
app
│
├─ database
│
├─ models
│
├─ services
│
└─ utils
```

---

# app/database

SQLite 접근 계층.

```text
database
│
├─ connection.py
├─ schema.py
│
├─ artist_repository.py
├─ app_setting_repository.py
│
└─ __init__.py
```

---

## 역할

| 파일 | 역할 |
|--------|--------|
| connection.py | SQLite 연결 관리 |
| schema.py | 테이블 생성 |
| artist_repository.py | 작가 데이터 CRUD |
| app_setting_repository.py | 설정 데이터 CRUD |

---

# app/models

데이터 모델 정의.

```text
models
│
├─ artist.py
├─ app_setting.py
│
└─ __init__.py
```

---

## 역할

| 파일 | 역할 |
|--------|--------|
| artist.py | Artist 모델 |
| app_setting.py | AppSetting 모델 |

---

# app/services

비즈니스 로직 계층.

```text
services
│
├─ artist_service.py
├─ folder_scan_service.py
├─ artist_scan_service.py
├─ artist_update_service.py
├─ pixiv_update_service.py
├─ artwork_status_service.py
├─ backup_service.py
├─ export_service.py
├─ settings_service.py
│
└─ __init__.py
```

---

## 역할

| 서비스 | 역할 |
|--------|--------|
| ArtistService | 작가 관리 |
| FolderScanService | 폴더 스캔 |
| ArtistScanService | 폴더 분석 |
| ArtistUpdateService | 업데이트 검사 |
| PixivUpdateService | Pixiv 통신 |
| ArtworkStatusService | 상태 계산 |
| BackupService | DB 백업 |
| ExportService | CSV 생성 |
| SettingsService | 설정 관리 |

---

# app/utils

공통 유틸리티.

```text
utils
│
├─ date_utils.py
├─ folder_parser.py
├─ path_utils.py
│
└─ __init__.py
```

---

## 역할

공통 함수 모음.

---

# ui

사용자 인터페이스 계층.

```text
ui
│
├─ dialogs
├─ pages
├─ widgets
│
├─ main_window.py
│
└─ __init__.py
```

---

# ui/pages

메인 화면 구성.

```text
pages
│
├─ dashboard
├─ scan
├─ artists
├─ artist_detail
├─ settings
│
└─ __init__.py
```

---

# Dashboard

대시보드 화면.

```text
dashboard
│
├─ page.py
├─ actions.py
├─ summary_section.py
├─ recent_section.py
├─ recommendation_section.py
│
└─ __init__.py
```

---

## 역할

- 통계 표시
- 최근 등록 작가
- 최근 스캔 정보
- 추천 작가
- 랜덤 작가

---

# Scan

폴더 스캔 화면.

```text
scan
│
├─ page.py
├─ actions.py
├─ worker.py
├─ log_table.py
│
└─ __init__.py
```

---

## 역할

- 폴더 선택
- 스캔 시작
- 진행률 표시
- 로그 출력

---

# Artists

작가 목록 화면.

```text
artists
│
├─ page.py
├─ actions.py
│
└─ __init__.py
```

---

## 역할

- 작가 검색
- 정렬
- 상태 정렬
- 업데이트 확인

---

# Artist Detail

작가 상세 화면.

```text
artist_detail
│
├─ page.py
├─ actions.py
├─ info_section.py
├─ utils.py
│
└─ __init__.py
```

---

## 역할

- 작가 정보 표시
- 작가 수정
- 평점 수정
- 메모 수정

---

# Settings

설정 화면.

```text
settings
│
├─ page.py
├─ actions.py
│
└─ __init__.py
```

---

## 역할

- PHPSESSID 관리
- 기본 폴더 관리
- DB 백업
- DB 복원
- CSV 내보내기

---

# ui/dialogs

보조 다이얼로그 모음.

```text
dialogs
│
└─ update_check
```

---

# Update Check Dialog

Pixiv 업데이트 확인.

```text
update_check
│
├─ dialog.py
├─ actions.py
├─ worker.py
├─ artist_table.py
├─ log_table.py
├─ selection_actions.py
├─ utils.py
│
└─ __init__.py
```

---

## 역할

- 다중 작가 선택
- 업데이트 검사
- 진행률 표시
- 결과 로그 출력

---

# ui/widgets

재사용 가능한 UI 컴포넌트.

```text
widgets
│
├─ artist_table
├─ sidebar.py
├─ status_badge.py
│
└─ __init__.py
```

---

# Artist Table

작가 목록 테이블.

```text
artist_table
│
├─ table.py
├─ actions.py
├─ row_renderer.py
├─ formatters.py
├─ columns.py
├─ cell_widgets.py
│
└─ __init__.py
```

---

## 역할

- 테이블 출력
- 정렬 이벤트
- Pixiv 버튼
- 상태 배지
- 평점 표시

---

# Sidebar

```text
sidebar.py
```

역할

- 페이지 이동
- 현재 페이지 표시

---

# Status Badge

```text
status_badge.py
```

역할

- 상태 표시 전용 UI 컴포넌트

---

# data

프로그램 데이터 저장.

```text
data
│
├─ pixiv_manager.db
│
└─ ...
```

---

# backups

백업 파일 저장.

```text
backups
│
└─ *.db
```

---

# exports

CSV 내보내기 파일 저장.

```text
exports
│
└─ *.csv
```

---

# docs

프로젝트 문서.

```text
docs
│
├─ 01_PROJECT_OVERVIEW.md
├─ 02_REQUIREMENTS.md
├─ 03_SYSTEM_FLOW.md
├─ 04_DATABASE.md
├─ 05_UI_DESIGN.md
├─ 06_CHANGELOG.md
├─ 07_ARCHITECTURE.md
├─ 08_SERVICES.md
├─ 09_FILE_STRUCTURE.md
│
└─ 99_BACKLOG.md
```

---

# 테스트 구조

```text
tests
│
├─ test_database.py
├─ test_services.py
│
└─ ...
```

---

# 설계 원칙

| 원칙 | 설명 |
|--------|--------|
| 기능 단위 분리 | 기능별 폴더 구성 |
| 단일 책임 원칙 | 파일당 하나의 책임 |
| 계층 분리 | UI / Service / Repository |
| 재사용성 | Widget 공통화 |
| 유지보수성 | 대형 파일 최소화 |
| 확장성 | 신규 기능 추가 용이 |

---

# 리팩토링 결과

## 이전

```text
artist_table.py
artist_detail_page.py
update_check_dialog.py
```

대형 파일 구조

---

## 현재

```text
artist_table/
artist_detail/
update_check/
```

모듈형 구조

---

# 향후 확장 예정

```text
artworks/
tags/
thumbnails/
recommendations/
plugins/
```

V2 이후 추가 예정