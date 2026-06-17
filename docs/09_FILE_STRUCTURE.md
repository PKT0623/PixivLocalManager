# 프로젝트 구조

## 개요

Pixiv Local Manager는 기능 단위 모듈 구조를 사용한다.

초기에는 단일 파일 중심 구조였으나, 기능 증가와 리팩토링을 거치면서
Page, Widget, Service, Repository 단위로 분리하였다.

현재 구조는 V2 개발 및 v0.12.0 대시보드 고도화 완료 기준 구조이며,
향후 V3 작품 관리 및 뷰어 기능 확장을 고려하여 설계되었다.

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
│  ├─ pages
│  └─ widgets
│
├─ data
├─ backups
├─ exports
├─ thumbnails
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
├─ app_setting_repository.py
├─ update_history_repository.py
├─ connection.py
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
    <td>SQLite 연결 관리</td>
</tr>

<tr>
    <td>schema.py</td>
    <td>DB 초기화</td>
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
    <td>app_setting_repository.py</td>
    <td>프로그램 설정 CRUD</td>
</tr>

<tr>
    <td>update_history_repository.py</td>
    <td>업데이트 이력 저장 및 조회</td>
</tr>

<tr>
    <td>artist/repository.py</td>
    <td>작가 CRUD</td>
</tr>

<tr>
    <td>artist/update_repository.py</td>
    <td>작가 정보 갱신</td>
</tr>

<tr>
    <td>artist/restore_repository.py</td>
    <td>삭제 작가 복구</td>
</tr>

<tr>
    <td>artist/columns.py</td>
    <td>작가 컬럼 정의</td>
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
│
├─ backup
│
├─ scan
│
├─ update
│
├─ artwork_status_service.py
├─ export_service.py
├─ pixiv_update_service.py
├─ settings_service.py
│
└─ __init__.py
```

---

# app/services/artist

작가 관리 서비스.

```text
artist
│
├─ service.py
├─ metadata_service.py
├─ folder_service.py
├─ delete_service.py
├─ validation.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>서비스</th>
    <th>역할</th>
</tr>

<tr>
    <td>service.py</td>
    <td>ArtistService 메인 진입점</td>
</tr>

<tr>
    <td>metadata_service.py</td>
    <td>작가 메타데이터 처리</td>
</tr>

<tr>
    <td>folder_service.py</td>
    <td>폴더 관련 처리</td>
</tr>

<tr>
    <td>delete_service.py</td>
    <td>삭제 및 복구 처리</td>
</tr>

<tr>
    <td>validation.py</td>
    <td>입력 검증</td>
</tr>

</table>

---

# app/services/backup

백업 서비스.

```text
backup
│
├─ service.py
├─ deleted_artist_backup_service.py
├─ json_utils.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>서비스</th>
    <th>역할</th>
</tr>

<tr>
    <td>service.py</td>
    <td>BackupService</td>
</tr>

<tr>
    <td>deleted_artist_backup_service.py</td>
    <td>삭제 작가 백업 처리</td>
</tr>

<tr>
    <td>json_utils.py</td>
    <td>JSON 저장 유틸</td>
</tr>

</table>

---

# app/services/scan

스캔 관련 서비스.

```text
scan
│
├─ folder_scan_service.py
├─ artist_scan_service.py
├─ rescan_service.py
├─ scan_builder.py
├─ scan_compare.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>서비스</th>
    <th>역할</th>
</tr>

<tr>
    <td>folder_scan_service.py</td>
    <td>폴더 분석</td>
</tr>

<tr>
    <td>artist_scan_service.py</td>
    <td>작가 등록 및 갱신</td>
</tr>

<tr>
    <td>rescan_service.py</td>
    <td>기존 작가 재스캔</td>
</tr>

<tr>
    <td>scan_builder.py</td>
    <td>스캔 데이터 생성</td>
</tr>

<tr>
    <td>scan_compare.py</td>
    <td>스캔 결과 비교</td>
</tr>

</table>

---

# app/services/update

업데이트 확인 서비스.

```text
update
│
├─ artist_update_service.py
├─ bulk_update_service.py
├─ update_utils.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>서비스</th>
    <th>역할</th>
</tr>

<tr>
    <td>artist_update_service.py</td>
    <td>작가 업데이트 저장</td>
</tr>

<tr>
    <td>bulk_update_service.py</td>
    <td>일괄 업데이트 처리</td>
</tr>

<tr>
    <td>update_utils.py</td>
    <td>업데이트 공통 유틸</td>
</tr>

</table>

---

# 공통 서비스

<table>
<tr>
    <th>서비스</th>
    <th>역할</th>
</tr>

<tr>
    <td>pixiv_update_service.py</td>
    <td>Pixiv 최신 작품 조회</td>
</tr>

<tr>
    <td>artwork_status_service.py</td>
    <td>작품 상태 계산</td>
</tr>

<tr>
    <td>export_service.py</td>
    <td>CSV 내보내기</td>
</tr>

<tr>
    <td>settings_service.py</td>
    <td>설정 관리</td>
</tr>

</table>

---

# ui

사용자 인터페이스 계층.

```text
ui
│
├─ pages
├─ widgets
│
├─ main_window.py
└─ __init__.py
```

---

# ui/pages

프로그램 메인 페이지.

```text
pages
│
├─ dashboard
├─ scan
├─ artists
├─ artist_detail
├─ update_check
├─ settings
└─ __init__.py
```

---

# dashboard

대시보드 페이지.

```text
dashboard
│
├─ page.py
├─ actions.py
│
├─ dashboard_metrics.py
├─ dashboard_styles.py
├─ utils.py
│
├─ summary_card.py
├─ summary_section.py
├─ update_status_section.py
├─ recent_activity_section.py
├─ scan_statistics_section.py
├─ top_ranking_section.py
│
├─ recommendation_card.py
├─ recommendation_section.py
├─ random_artist_section.py
│
├─ recent_artists_section.py
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
    <td>대시보드 데이터 로드 및 이벤트 처리</td>
</tr>

<tr>
    <td>dashboard_metrics.py</td>
    <td>대시보드 통계 계산</td>
</tr>

<tr>
    <td>summary_card.py</td>
    <td>요약 카드 위젯</td>
</tr>

<tr>
    <td>summary_section.py</td>
    <td>전체 통계 카드 영역</td>
</tr>

<tr>
    <td>update_status_section.py</td>
    <td>업데이트 현황 영역</td>
</tr>

<tr>
    <td>recent_activity_section.py</td>
    <td>최근 활동 영역</td>
</tr>

<tr>
    <td>scan_statistics_section.py</td>
    <td>최근 스캔 결과 영역</td>
</tr>

<tr>
    <td>top_ranking_section.py</td>
    <td>TOP 랭킹 영역</td>
</tr>

<tr>
    <td>recommendation_card.py</td>
    <td>추천 카드 UI</td>
</tr>

<tr>
    <td>recommendation_section.py</td>
    <td>추천 작가 영역</td>
</tr>

<tr>
    <td>random_artist_section.py</td>
    <td>랜덤 작가 영역</td>
</tr>

</table>

---

# scan

스캔 페이지.

```text
scan
│
├─ action_parts
├─ preview_table_parts
├─ progress_parts
├─ worker_parts
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
    <td>스캔 워커</td>
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
    <td>progress_section.py</td>
    <td>진행 상황 표시</td>
</tr>

<tr>
    <td>log_table.py</td>
    <td>결과 로그 표시</td>
</tr>

</table>

---

# artists

작가 목록 페이지.

```text
artists
│
├─ action_parts
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
    <td>작가 목록 액션 진입점</td>
</tr>

<tr>
    <td>filters.py</td>
    <td>검색 및 필터</td>
</tr>

<tr>
    <td>toolbar.py</td>
    <td>목록 도구 모음</td>
</tr>

<tr>
    <td>action_parts</td>
    <td>기능별 액션 분리</td>
</tr>

</table>

---

# artist_detail

작가 상세 페이지.

```text
artist_detail
│
├─ action_parts
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
    <td>상세 페이지 액션 진입점</td>
</tr>

<tr>
    <td>action_parts</td>
    <td>작품, 태그, 데이터 처리 분리</td>
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

# update_check

업데이트 확인 페이지.

```text
update_check
│
├─ page.py
├─ actions.py
│
├─ worker.py
├─ worker_config.py
│
├─ artist_table.py
├─ log_table.py
│
├─ selection_actions.py
├─ styles.py
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
    <td>업데이트 확인 페이지</td>
</tr>

<tr>
    <td>actions.py</td>
    <td>업데이트 실행 처리</td>
</tr>

<tr>
    <td>worker.py</td>
    <td>업데이트 워커</td>
</tr>

<tr>
    <td>worker_config.py</td>
    <td>설정 및 공통 상수</td>
</tr>

<tr>
    <td>artist_table.py</td>
    <td>대상 작가 목록</td>
</tr>

<tr>
    <td>log_table.py</td>
    <td>결과 로그</td>
</tr>

<tr>
    <td>selection_actions.py</td>
    <td>선택 관련 기능</td>
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

---

# ui/widgets

공통 위젯.

```text
widgets
│
├─ artist_table
│
├─ sidebar.py
├─ status_badge.py
│
└─ __init__.py
```

---

# artist_table

작가 목록 테이블 위젯.

```text
artist_table
│
├─ table.py
├─ row_renderer.py
├─ actions.py
├─ columns.py
├─ formatters.py
├─ cell_widgets.py
└─ __init__.py
```

---

# data

프로그램 데이터 저장 폴더.

```text
data
│
├─ pixiv_manager.db
├─ settings.ini
│
├─ scan_results
├─ update_history
└─ logs
```

---

# backups

백업 데이터 저장 폴더.

```text
backups
│
├─ database
└─ deleted_artists
```

---

# exports

내보내기 데이터 저장 폴더.

```text
exports
```

---

# thumbnails

썸네일 캐시 저장 폴더.

```text
thumbnails
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

```text
Page
 ├─ Actions
 ├─ Sections
 ├─ Styles
 └─ Utils
```

---

## 2. 기능별 분리

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

---

## 5. Import 단순화

```python
from ui.pages.scan import ScanPage
from app.services.artist import ArtistService
```

---

# 향후 확장 구조

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

본 문서는 v0.12.0 (대시보드 고도화 완료) 기준으로 작성되었다.
