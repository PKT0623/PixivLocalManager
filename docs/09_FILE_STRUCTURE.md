# 프로젝트 구조

## 개요

Pixiv Local Manager는 기능 단위 모듈 구조를 사용한다.

초기에는 단일 파일 중심 구조였으나, 기능 증가와 리팩토링을 거치면서 Page, Dialog, Widget, Service, Repository 단위로 분리하였다.

현재 구조는 V2 개발 및 v0.10.0 2차 리팩토링 기준 구조이며, 향후 V3 작품 관리 및 뷰어 기능 확장을 고려하여 설계되었다.

---

# 전체 구조

```text
PixivLocalManager
│
├─ app
│  ├─ database
│  ├─ models
│  └─ services
│
├─ ui
│  ├─ dialogs
│  ├─ pages
│  └─ widgets
│
├─ data
├─ docs
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
├─ models
├─ services
└─ __init__.py
```

---

# app/database

SQLite 접근 계층.

```text
database
│
├─ artist
│  ├─ repository.py
│  ├─ update_repository.py
│  ├─ restore_repository.py
│  ├─ columns.py
│  └─ __init__.py
│
├─ connection.py
├─ app_setting_repository.py
├─ migrations.py
├─ schema.py
├─ table_definitions.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>역할</th>
</tr>

<tr>
    <td>connection.py</td>
    <td>SQLite 연결 및 데이터 폴더 관리</td>
</tr>

<tr>
    <td>schema.py</td>
    <td>데이터베이스 초기화</td>
</tr>

<tr>
    <td>table_definitions.py</td>
    <td>테이블 생성 SQL 정의</td>
</tr>

<tr>
    <td>migrations.py</td>
    <td>스키마 마이그레이션</td>
</tr>

<tr>
    <td>artist/repository.py</td>
    <td>작가 기본 CRUD</td>
</tr>

<tr>
    <td>artist/update_repository.py</td>
    <td>작가 정보 갱신 전용 처리</td>
</tr>

<tr>
    <td>artist/restore_repository.py</td>
    <td>삭제 작가 복구 처리</td>
</tr>

<tr>
    <td>app_setting_repository.py</td>
    <td>프로그램 설정 CRUD</td>
</tr>

</table>

---

# app/models

데이터 모델 정의.

```text
models
│
├─ artist.py
├─ app_setting.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>역할</th>
</tr>

<tr>
    <td>artist.py</td>
    <td>Artist 데이터 모델</td>
</tr>

<tr>
    <td>app_setting.py</td>
    <td>AppSetting 데이터 모델</td>
</tr>

</table>

---

# app/services

비즈니스 로직 계층.

```text
services
│
├─ artist
│  ├─ service.py
│  ├─ metadata_service.py
│  ├─ folder_service.py
│  ├─ delete_service.py
│  ├─ validation.py
│  └─ __init__.py
│
├─ backup
│  ├─ service.py
│  ├─ deleted_artist_backup_service.py
│  ├─ json_utils.py
│  └─ __init__.py
│
├─ scan
│  ├─ folder_scan_service.py
│  ├─ artist_scan_service.py
│  ├─ rescan_service.py
│  ├─ scan_builder.py
│  ├─ scan_compare.py
│  └─ __init__.py
│
├─ update
│  ├─ artist_update_service.py
│  ├─ bulk_update_service.py
│  ├─ update_utils.py
│  └─ __init__.py
│
├─ artwork_status_service.py
├─ export_service.py
├─ pixiv_update_service.py
├─ settings_service.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>서비스</th>
    <th>역할</th>
</tr>

<tr>
    <td>ArtistService</td>
    <td>작가 데이터 관리 진입점</td>
</tr>

<tr>
    <td>FolderScanService</td>
    <td>폴더 분석 및 메타데이터 추출</td>
</tr>

<tr>
    <td>ArtistScanService</td>
    <td>스캔 결과 등록 및 갱신</td>
</tr>

<tr>
    <td>RescanService</td>
    <td>기존 작가 재스캔</td>
</tr>

<tr>
    <td>ArtistUpdateService</td>
    <td>업데이트 정보 저장</td>
</tr>

<tr>
    <td>BulkUpdateService</td>
    <td>일괄 업데이트 처리</td>
</tr>

<tr>
    <td>PixivUpdateService</td>
    <td>Pixiv 최신 작품 조회</td>
</tr>

<tr>
    <td>ArtworkStatusService</td>
    <td>작품 상태 계산</td>
</tr>

<tr>
    <td>BackupService</td>
    <td>백업 및 복구 처리</td>
</tr>

<tr>
    <td>ExportService</td>
    <td>CSV 내보내기</td>
</tr>

<tr>
    <td>SettingsService</td>
    <td>프로그램 설정 관리</td>
</tr>

</table>

---

# ui

사용자 인터페이스 계층.

```text id="xfbqxa"
ui
│
├─ dialogs
├─ pages
├─ widgets
│
├─ main_window.py
└─ __init__.py
```

---

# ui/dialogs

독립 실행형 팝업 창.

```text id="msjl07"
dialogs
│
└─ update_check
```

---

# ui/dialogs/update_check

업데이트 확인 창.

```text id="jk8m7i"
update_check
│
├─ dialog.py
├─ dialog_styles.py
├─ worker.py
├─ worker_config.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>역할</th>
</tr>

<tr>
    <td>dialog.py</td>
    <td>업데이트 확인 UI</td>
</tr>

<tr>
    <td>dialog_styles.py</td>
    <td>스타일 정의</td>
</tr>

<tr>
    <td>worker.py</td>
    <td>백그라운드 처리</td>
</tr>

<tr>
    <td>worker_config.py</td>
    <td>설정 및 공통 상수</td>
</tr>

</table>

---

# ui/pages

프로그램 메인 페이지.

```text id="ytd4pd"
pages
│
├─ dashboard
├─ scan
├─ artists
├─ artist_detail
└─ settings
```

---

# dashboard

대시보드 페이지.

```text id="oh4yhn"
dashboard
│
├─ page.py
├─ actions.py
│
├─ dashboard_metrics.py
├─ dashboard_styles.py
│
├─ summary_section.py
├─ recent_artists_section.py
├─ recent_scan_section.py
├─ random_artist_section.py
│
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>역할</th>
</tr>

<tr>
    <td>page.py</td>
    <td>대시보드 페이지</td>
</tr>

<tr>
    <td>actions.py</td>
    <td>이벤트 처리</td>
</tr>

<tr>
    <td>dashboard_metrics.py</td>
    <td>통계 계산</td>
</tr>

<tr>
    <td>dashboard_styles.py</td>
    <td>스타일 정의</td>
</tr>

<tr>
    <td>summary_section.py</td>
    <td>요약 카드 영역</td>
</tr>

<tr>
    <td>recent_artists_section.py</td>
    <td>최근 등록 작가</td>
</tr>

<tr>
    <td>recent_scan_section.py</td>
    <td>최근 스캔 정보</td>
</tr>

<tr>
    <td>random_artist_section.py</td>
    <td>추천 작가</td>
</tr>

</table>

---

# scan

스캔 페이지.

```text id="ufx8mq"
scan
│
├─ action_parts
│  ├─ folder_actions.py
│  ├─ worker_actions.py
│  ├─ filter_actions.py
│  ├─ result_actions.py
│  └─ __init__.py
│
├─ preview_table_parts
│  ├─ filter_logic.py
│  ├─ row_renderer.py
│  ├─ summary.py
│  └─ __init__.py
│
├─ progress_parts
│  ├─ history_formatter.py
│  ├─ statistics_formatter.py
│  └─ __init__.py
│
├─ worker_parts
│  ├─ validation.py
│  ├─ preview_builder.py
│  ├─ result_builder.py
│  ├─ statistics.py
│  ├─ runtime_utils.py
│  └─ __init__.py
│
├─ page.py
├─ actions.py
├─ worker.py
│
├─ scan_styles.py
│
├─ folder_scanner.py
├─ folder_section.py
│
├─ preview_table.py
├─ progress_section.py
│
├─ log_table.py
├─ log_utils.py
│
└─ __init__.py
```

## 구조 설명

<table>
<tr>
    <th>구성</th>
    <th>역할</th>
</tr>

<tr>
    <td>page.py</td>
    <td>스캔 페이지</td>
</tr>

<tr>
    <td>actions.py</td>
    <td>스캔 액션 진입점</td>
</tr>

<tr>
    <td>action_parts</td>
    <td>기능별 액션 분리</td>
</tr>

<tr>
    <td>worker.py</td>
    <td>스캔 워커 본체</td>
</tr>

<tr>
    <td>worker_parts</td>
    <td>검증, 통계, 결과 생성 분리</td>
</tr>

<tr>
    <td>preview_table.py</td>
    <td>미리보기 테이블</td>
</tr>

<tr>
    <td>preview_table_parts</td>
    <td>필터 및 렌더링 분리</td>
</tr>

<tr>
    <td>progress_section.py</td>
    <td>진행 정보 표시</td>
</tr>

<tr>
    <td>progress_parts</td>
    <td>포맷팅 로직 분리</td>
</tr>

</table>

---

# artists

작가 목록 페이지.

```text id="2ak8jg"
artists
│
├─ action_parts
│  ├─ bulk_actions.py
│  ├─ data_actions.py
│  ├─ dialog_actions.py
│  └─ __init__.py
│
├─ page.py
├─ actions.py
├─ filters.py
├─ toolbar.py
│
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>역할</th>
</tr>

<tr>
    <td>page.py</td>
    <td>작가 목록 페이지</td>
</tr>

<tr>
    <td>actions.py</td>
    <td>액션 진입점</td>
</tr>

<tr>
    <td>action_parts</td>
    <td>기능별 액션 분리</td>
</tr>

<tr>
    <td>filters.py</td>
    <td>검색 및 필터</td>
</tr>

<tr>
    <td>toolbar.py</td>
    <td>도구 모음</td>
</tr>

</table>

---

# artist_detail

작가 상세 페이지.

```text id="c7v4e6"
artist_detail
│
├─ action_parts
│  ├─ artwork_actions.py
│  ├─ data_actions.py
│  ├─ dialog_actions.py
│  ├─ tag_actions.py
│  └─ __init__.py
│
├─ page.py
├─ actions.py
├─ styles.py
│
├─ info_section.py
├─ utils.py
│
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>역할</th>
</tr>

<tr>
    <td>page.py</td>
    <td>상세 페이지</td>
</tr>

<tr>
    <td>actions.py</td>
    <td>액션 진입점</td>
</tr>

<tr>
    <td>action_parts</td>
    <td>기능별 액션 분리</td>
</tr>

<tr>
    <td>styles.py</td>
    <td>상세 페이지 스타일</td>
</tr>

<tr>
    <td>info_section.py</td>
    <td>상세 정보 UI</td>
</tr>

<tr>
    <td>utils.py</td>
    <td>공통 유틸</td>
</tr>

</table>

---

# settings

설정 페이지.

```text
settings
│
├─ page.py
├─ actions.py
├─ settings_styles.py
│
├─ folder_section.py
├─ database_section.py
├─ pixiv_section.py
├─ app_info_section.py
│
├─ database_utils.py
│
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>역할</th>
</tr>

<tr>
    <td>page.py</td>
    <td>설정 페이지</td>
</tr>

<tr>
    <td>actions.py</td>
    <td>설정 저장 및 처리</td>
</tr>

<tr>
    <td>settings_styles.py</td>
    <td>설정 페이지 스타일</td>
</tr>

<tr>
    <td>folder_section.py</td>
    <td>폴더 설정</td>
</tr>

<tr>
    <td>database_section.py</td>
    <td>데이터베이스 관리</td>
</tr>

<tr>
    <td>pixiv_section.py</td>
    <td>Pixiv 관련 설정</td>
</tr>

<tr>
    <td>app_info_section.py</td>
    <td>프로그램 정보</td>
</tr>

<tr>
    <td>database_utils.py</td>
    <td>DB 유틸리티</td>
</tr>

</table>

---

# ui/widgets

프로그램 전체에서 재사용하는 공통 위젯.

```text
widgets
│
├─ artist_table
│  ├─ table.py
│  ├─ row_renderer.py
│  ├─ actions.py
│  ├─ columns.py
│  ├─ formatters.py
│  ├─ cell_widgets.py
│  └─ __init__.py
│
├─ sidebar.py
├─ status_badge.py
│
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>위젯</th>
    <th>역할</th>
</tr>

<tr>
    <td>ArtistTable</td>
    <td>작가 목록 테이블</td>
</tr>

<tr>
    <td>Sidebar</td>
    <td>메인 메뉴</td>
</tr>

<tr>
    <td>StatusBadge</td>
    <td>상태 표시 배지</td>
</tr>

</table>

---

# data

프로그램 데이터 저장 폴더.

```text
data
│
├─ pixiv_manager.db
└─ settings.ini
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>설명</th>
</tr>

<tr>
    <td>pixiv_manager.db</td>
    <td>SQLite 데이터베이스</td>
</tr>

<tr>
    <td>settings.ini</td>
    <td>프로그램 설정</td>
</tr>

</table>

---

# backups

백업 데이터 저장 폴더.

```text
backups
│
└─ deleted_artists
```

삭제된 작가 백업 파일을 저장한다.

---

# exports

내보내기 데이터 저장 폴더.

```text
exports
```

CSV 및 기타 내보내기 파일을 저장한다.

---

# thumbnails

썸네일 저장 폴더.

```text
thumbnails
```

향후 썸네일 캐시 저장에 사용된다.

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
└─ 99_BACKLOG.md
```

---

# tests

테스트 코드.

```text
tests
│
├─ test_database.py
├─ test_services.py
└─ __init__.py
```

---

# 구조 설계 원칙

## 1. Page 중심 구조

각 화면은 독립된 Page 단위로 구성한다.

```text
Page
 ├─ Actions
 ├─ Sections
 ├─ Styles
 └─ Utils
```

---

## 2. 기능별 분리

파일 길이가 증가하면 기능 단위로 분리한다.

예시:

```text
actions.py
↓

action_parts
├─ data_actions.py
├─ dialog_actions.py
└─ bulk_actions.py
```

---

## 3. Worker 분리

대형 Worker는 실행 흐름과 보조 기능을 분리한다.

```text
worker.py
↓

worker_parts
├─ validation.py
├─ statistics.py
├─ result_builder.py
├─ preview_builder.py
└─ runtime_utils.py
```

---

## 4. Style 분리

페이지 스타일은 별도 파일로 분리한다.

```text
page.py
↓

styles.py
```

또는

```text
dashboard_styles.py
settings_styles.py
scan_styles.py
```

형태를 사용한다.

---

## 5. Import 단순화

가능한 경우 **init**.py를 사용하여 import 경로를 단순화한다.

예시:

```python
from ui.pages.scan import ScanPage
from app.services.artist import ArtistService
```

---

# 향후 확장 구조

V3 이후 다음 구조가 추가될 수 있다.

```text
ui
│
├─ pages
│  ├─ viewer
│  ├─ artwork_manager
│  └─ statistics
│
├─ dialogs
│  ├─ artwork_preview
│  └─ tag_manager
│
└─ widgets
   ├─ thumbnail_grid
   ├─ artwork_card
   └─ artwork_viewer
```

---

# 버전 기준

본 문서는 v0.10.0 (2차 리팩토링 완료) 기준으로 작성되었다.
