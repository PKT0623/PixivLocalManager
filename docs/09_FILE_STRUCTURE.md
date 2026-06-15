# 프로젝트 구조

## 개요

Pixiv Local Manager는 기능 단위 모듈 구조를 사용한다.

초기에는 단일 파일 중심 구조였으나, 기능 증가에 따라 Page, Dialog, Widget, Service 단위로 분리하였다.

---

# 전체 구조

```text
PixivLocalManager
│
├─ app
│  ├─ database
│  ├─ models
│  ├─ services
│  └─ utils
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
├─ artist_repository.py
├─ app_setting_repository.py
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
    <td>테이블 생성 및 마이그레이션</td>
</tr>

<tr>
    <td>artist_repository.py</td>
    <td>작가 데이터 CRUD, 일괄 수정, 삭제 복구용 삽입</td>
</tr>

<tr>
    <td>app_setting_repository.py</td>
    <td>설정 데이터 CRUD</td>
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
    <td>Artist 모델</td>
</tr>

<tr>
    <td>app_setting.py</td>
    <td>AppSetting 모델</td>
</tr>

</table>

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
    <td>작가 관리, 일괄 작업, 폴더 변경, 삭제 복구</td>
</tr>

<tr>
    <td>FolderScanService</td>
    <td>폴더 분석, 작품 수 계산, 파일 수 계산, Pixiv ID 추출</td>
</tr>

<tr>
    <td>ArtistScanService</td>
    <td>스캔 결과 기반 작가 등록 및 갱신</td>
</tr>

<tr>
    <td>ArtistUpdateService</td>
    <td>Pixiv 업데이트 확인 결과 저장</td>
</tr>

<tr>
    <td>PixivUpdateService</td>
    <td>Pixiv 최신 작품 정보 조회</td>
</tr>

<tr>
    <td>ArtworkStatusService</td>
    <td>로컬 / Pixiv 작품 ID 비교 및 업데이트 상태 계산</td>
</tr>

<tr>
    <td>BackupService</td>
    <td>DB 백업, 삭제 작가 백업, 삭제 작가 복구</td>
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

```text
ui
│
├─ dialogs
├─ pages
├─ widgets
├─ main_window.py
└─ __init__.py
```

---

# ui/pages

메인 페이지 구성.

```text
pages
│
├─ dashboard
├─ scan
├─ artists
├─ artist_detail
├─ settings
└─ __init__.py
```

---

# dashboard

대시보드 화면.

```text
dashboard
│
├─ page.py
├─ actions.py
├─ summary_section.py
├─ recent_section.py
├─ recommendation_section.py
└─ __init__.py
```

## 역할

* 전체 통계 표시
* 최근 등록 작가 표시
* 최근 스캔 정보 표시
* 추천 작가 표시
* 랜덤 작가 표시

---

# scan

폴더 스캔 화면.

```text
scan
│
├─ page.py
├─ actions.py
├─ worker.py
├─ log_table.py
└─ __init__.py
```

## 역할

* 폴더 선택
* 스캔 시작
* 진행률 표시
* 스캔 로그 출력

---

# artists

작가 목록 화면.

```text
artists
│
├─ page.py
├─ actions.py
├─ filters.py
├─ toolbar.py
└─ __init__.py
```

## 역할

* 작가 목록 조회
* 검색
* 필터
* 정렬
* 다중 선택
* 일괄 작업
* 작가 삭제
* 삭제 작가 복구
* 업데이트 확인 다이얼로그 실행

---

# artist_detail

작가 상세 화면.

```text
artist_detail
│
├─ page.py
├─ actions.py
├─ info_section.py
├─ utils.py
└─ __init__.py
```

## 역할

* 작가 정보 표시
* 작가명 수정
* 평점 수정
* 즐겨찾기 설정
* 숨김 설정
* 태그 관리
* 메모 관리
* 폴더 경로 변경
* 폴더 변경 후 재스캔

---

# settings

설정 화면.

```text
settings
│
├─ page.py
├─ actions.py
└─ __init__.py
```

## 역할

* PHPSESSID 관리
* 기본 폴더 관리
* DB 백업
* DB 복원
* CSV 내보내기
* DB 폴더 열기

---

# ui/dialogs

보조 다이얼로그.

```text
dialogs
│
└─ update_check
```

---

# update_check

Pixiv 업데이트 확인 다이얼로그.

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
    <td>업데이트 확인 다이얼로그 UI 구성</td>
</tr>

<tr>
    <td>actions.py</td>
    <td>시작, 취소, 완료 처리</td>
</tr>

<tr>
    <td>worker.py</td>
    <td>백그라운드 업데이트 확인 작업</td>
</tr>

<tr>
    <td>artist_table.py</td>
    <td>업데이트 대상 작가 선택 테이블</td>
</tr>

<tr>
    <td>log_table.py</td>
    <td>업데이트 결과 로그 테이블</td>
</tr>

<tr>
    <td>selection_actions.py</td>
    <td>전체 선택, 미확인 선택, 업데이트 필요 선택</td>
</tr>

<tr>
    <td>utils.py</td>
    <td>업데이트 확인 관련 유틸리티</td>
</tr>

</table>

---

# ui/widgets

재사용 가능한 UI 컴포넌트.

```text
widgets
│
├─ artist_table
├─ sidebar.py
├─ status_badge.py
└─ __init__.py
```

---

# artist_table

작가 목록 테이블 위젯.

```text
artist_table
│
├─ table.py
├─ actions.py
├─ row_renderer.py
├─ formatters.py
├─ columns.py
├─ cell_widgets.py
└─ __init__.py
```

## 역할

<table>
<tr>
    <th>파일</th>
    <th>역할</th>
</tr>

<tr>
    <td>table.py</td>
    <td>작가 테이블 본체</td>
</tr>

<tr>
    <td>actions.py</td>
    <td>셀 클릭, 더블클릭, 정렬, 바로가기 처리</td>
</tr>

<tr>
    <td>row_renderer.py</td>
    <td>작가 행 렌더링</td>
</tr>

<tr>
    <td>formatters.py</td>
    <td>테이블 표시값 포맷</td>
</tr>

<tr>
    <td>columns.py</td>
    <td>컬럼 정의 및 정렬 필드 정의</td>
</tr>

<tr>
    <td>cell_widgets.py</td>
    <td>즐겨찾기 버튼, 상태 배지, 바로가기 버튼 생성</td>
</tr>

</table>

---

# data

프로그램 데이터 저장 위치.

```text
data
│
├─ pixiv_manager.db
│
├─ backups
│  └─ deleted_artists
│
└─ exports
```

## 역할

<table>
<tr>
    <th>경로</th>
    <th>역할</th>
</tr>

<tr>
    <td>pixiv_manager.db</td>
    <td>SQLite 데이터베이스</td>
</tr>

<tr>
    <td>backups/deleted_artists</td>
    <td>삭제 작가 자동 백업 JSON 저장</td>
</tr>

<tr>
    <td>exports</td>
    <td>CSV 내보내기 파일 저장</td>
</tr>

</table>

---

# docs

문서 저장 위치.

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

테스트 코드 저장 위치.

```text
tests
│
├─ test_database.py
├─ test_services.py
└─ ...
```

---

# 설계 원칙

<table>
<tr>
    <th>원칙</th>
    <th>설명</th>
</tr>

<tr>
    <td>기능 단위 분리</td>
    <td>화면, 서비스, 위젯을 기능 단위로 분리</td>
</tr>

<tr>
    <td>단일 책임 원칙</td>
    <td>파일 하나가 하나의 주요 역할만 담당</td>
</tr>

<tr>
    <td>계층 분리</td>
    <td>UI / Service / Repository / Database 역할 분리</td>
</tr>

<tr>
    <td>재사용성</td>
    <td>공통 UI 요소는 widgets로 분리</td>
</tr>

<tr>
    <td>유지보수성</td>
    <td>대형 파일을 작은 파일로 분리</td>
</tr>

<tr>
    <td>확장성</td>
    <td>V2, V3 기능 확장을 고려한 구조 유지</td>
</tr>

</table>

---

# 향후 확장 예정 구조

```text
ui/pages/artworks
ui/pages/statistics
ui/widgets/artwork_table
ui/widgets/thumbnail_grid

app/services/artwork_service.py
app/services/statistics_service.py
app/services/viewer_service.py

app/database/artwork_repository.py
app/database/update_history_repository.py
```
