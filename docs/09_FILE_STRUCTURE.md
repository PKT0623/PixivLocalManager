# 파일 구조

## 개요

Pixiv Local Manager는 기능별 책임을 분리하기 위해 `app`과 `ui`를 중심으로 구성한다.

```text
PixivLocalManager
│
├─ app
├─ ui
├─ docs
├─ tests
├─ data
├─ backups
├─ exports
├─ thumbnails
│
├─ main.py
├─ requirements.txt
└─ README.md
```

## 주요 역할

| 경로               | 역할                         |
| ---------------- | -------------------------- |
| app              | 비즈니스 로직, 데이터 모델, 데이터베이스 처리 |
| ui               | PySide6 기반 사용자 인터페이스       |
| docs             | 프로젝트 문서                    |
| tests            | 테스트 코드                     |
| data             | SQLite DB 및 앱 데이터 저장       |
| backups          | 백업 파일 저장                   |
| exports          | CSV 등 내보내기 파일 저장           |
| thumbnails       | 썸네일 캐시 저장 예정               |
| main.py          | 프로그램 실행 진입점                |
| requirements.txt | Python 패키지 의존성             |
| README.md        | 프로젝트 소개 문서                 |

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

## 역할

| 항목          | 역할                         |
| ----------- | -------------------------- |
| database    | SQLite 연결, 스키마, Repository |
| models      | 데이터 모델 정의                  |
| services    | 비즈니스 로직 처리                 |
| **init**.py | app 패키지 초기화                |

---

# app/database

데이터베이스 연결, 스키마, Repository 계층.

```text
database
│
├─ artist
├─ bookmark
├─ follow
│
├─ app_setting_repository.py
├─ bookmark_artwork_repository.py
├─ connection.py
├─ follow_user_repository.py
├─ migrations.py
├─ schema.py
├─ table_definitions.py
├─ update_history_repository.py
├─ update_history_utils.py
└─ __init__.py
```

## 역할

| 파일                             | 역할                             |
| ------------------------------ | ------------------------------ |
| app_setting_repository.py      | 프로그램 설정 저장 및 조회                |
| bookmark_artwork_repository.py | 북마크 작품 Repository export 호환 모듈 |
| connection.py                  | SQLite 연결 생성                   |
| follow_user_repository.py      | 팔로우 유저 Repository export 호환 모듈 |
| migrations.py                  | DB 마이그레이션 처리                   |
| schema.py                      | DB 초기화 및 스키마 적용                |
| table_definitions.py           | 테이블 생성 SQL 정의                  |
| update_history_repository.py   | 업데이트 확인 이력 저장 및 조회             |
| update_history_utils.py        | 업데이트 이력 관련 유틸                  |
| **init**.py                    | database 패키지 export            |

---

## app/database/artist

작가 데이터 Repository 그룹.

```text
artist
│
├─ columns.py
├─ repository.py
├─ restore_repository.py
├─ update_repository.py
└─ __init__.py
```

### 역할

| 파일                    | 역할                            |
| --------------------- | ----------------------------- |
| columns.py            | artists 테이블 컬럼 정의             |
| repository.py         | 작가 조회, 등록, 삭제 등 기본 Repository |
| restore_repository.py | 삭제 작가 복구 및 백업 복원용 Repository  |
| update_repository.py  | 작가 정보 갱신 전용 Repository        |
| **init**.py           | artist Repository export      |

---

## app/database/bookmark

북마크 작품 Repository 그룹.

```text
bookmark
│
├─ normalize.py
├─ repository.py
├─ update_repository.py
└─ __init__.py
```

### 역할

| 파일                   | 역할                         |
| -------------------- | -------------------------- |
| normalize.py         | 북마크 작품 DB 저장값 정규화          |
| repository.py        | 북마크 작품 조회, 저장, 삭제          |
| update_repository.py | 북마크 작품 메타데이터 갱신            |
| **init**.py          | bookmark Repository export |

---

## app/database/follow

팔로우 유저 Repository 그룹.

```text
follow
│
├─ normalize.py
├─ repository.py
├─ update_repository.py
└─ __init__.py
```

### 역할

| 파일                   | 역할                       |
| -------------------- | ------------------------ |
| normalize.py         | 팔로우 유저 DB 저장값 정규화        |
| repository.py        | 팔로우 유저 조회, 저장, 삭제        |
| update_repository.py | 팔로우 유저 메타데이터 갱신          |
| **init**.py          | follow Repository export |

---

# app/models

데이터 모델 정의.

```text
models
│
├─ app_setting.py
├─ artist.py
├─ bookmark_artwork.py
├─ follow_user.py
└─ __init__.py
```

Service와 Repository 사이에서 사용되는 데이터 객체를 정의한다.

## 역할

| 파일                  | 역할         |
| ------------------- | ---------- |
| app_setting.py      | 프로그램 설정 모델 |
| artist.py           | 작가 데이터 모델  |
| bookmark_artwork.py | 북마크 작품 모델  |
| follow_user.py      | 팔로우 유저 모델  |
| **init**.py         | 모델 export  |

---

# app/services

비즈니스 로직 계층.

```text
services
│
├─ artist
├─ backup
├─ bookmark
├─ follow
├─ pixiv
├─ scan
├─ statistics
├─ tag
├─ update
│
├─ artwork_status_service.py
├─ database_info_service.py
├─ database_integrity_service.py
├─ database_maintenance_service.py
├─ export_service.py
├─ log_management_service.py
├─ pixiv_update_service.py
├─ settings_backup_service.py
├─ settings_service.py
└─ __init__.py
```

UI와 Repository 사이에서 주요 기능 로직을 처리한다.

UI는 Service를 통해 데이터를 요청하고, Service는 필요한 Repository와 유틸리티를 조합해 기능을 수행한다.

## 역할

| 파일                              | 역할                                  |
| ------------------------------- | ----------------------------------- |
| artwork_status_service.py       | 로컬 작품 ID와 Pixiv 작품 ID 기반 업데이트 상태 계산 |
| database_info_service.py        | DB 경로, 크기, 통계 정보 조회                 |
| database_integrity_service.py   | 중복 ID, 폴더 오류, 상태 오류 등 무결성 검사        |
| database_maintenance_service.py | SQLite VACUUM, ANALYZE 등 DB 유지보수    |
| export_service.py               | 작가 데이터 및 결과 CSV 내보내기                |
| log_management_service.py       | 실행 로그, 업데이트 로그, 동기화 로그 관리           |
| pixiv_update_service.py         | Pixiv 최신 작품 조회 및 업데이트 확인 공통 처리      |
| settings_backup_service.py      | 설정 JSON 백업 및 복원                     |
| settings_service.py             | 설정값 저장, 조회, 초기화                     |
| **init**.py                     | services 패키지 export                 |

---

# app/services/artist

작가 관리 서비스.

```text
artist
│
├─ delete_service.py
├─ folder_service.py
├─ metadata_service.py
├─ service.py
├─ validation.py
└─ __init__.py
```

## 역할

| 파일                  | 역할                               |
| ------------------- | -------------------------------- |
| delete_service.py   | 작가 삭제 및 삭제 작가 복구 처리              |
| folder_service.py   | 작가 폴더 경로 변경 및 폴더 기반 재스캔 처리       |
| metadata_service.py | 작가명, Pixiv ID, 태그, 메모 등 메타데이터 처리 |
| service.py          | ArtistService 진입점                |
| validation.py       | 작가 입력값 검증                        |
| **init**.py         | artist 서비스 export                |

---

# app/services/backup

백업 및 복구 서비스.

```text
backup
│
├─ database_backup_service.py
├─ deleted_artist_backup_service.py
├─ json_utils.py
├─ service.py
└─ __init__.py
```

## 역할

| 파일                               | 역할                    |
| -------------------------------- | --------------------- |
| database_backup_service.py       | DB 백업, 복원, 자동 백업 관리   |
| deleted_artist_backup_service.py | 삭제 작가 JSON 백업 및 복구 처리 |
| json_utils.py                    | JSON 저장 및 로드 공통 유틸    |
| service.py                       | BackupService 진입점     |
| **init**.py                      | backup 서비스 export     |

---

# app/services/bookmark

Pixiv 북마크 작품 관리 서비스.

```text
bookmark
│
├─ importer.py
├─ matcher.py
├─ service.py
└─ __init__.py
```

## 역할

| 파일          | 역할                           |
| ----------- | ---------------------------- |
| importer.py | TXT / CSV 북마크 작품 ID 파싱       |
| matcher.py  | 북마크 작품의 작가 ID 기준 로컬 작가 자동 매칭 |
| service.py  | 북마크 작품 저장, 조회, 통계 처리         |
| **init**.py | bookmark 서비스 export          |

---

# app/services/follow

Pixiv 팔로우 유저 관리 서비스.

```text
follow
│
├─ importer.py
├─ matcher.py
├─ service.py
└─ __init__.py
```

## 역할

| 파일          | 역할                      |
| ----------- | ----------------------- |
| importer.py | TXT / CSV 팔로우 유저 ID 파싱  |
| matcher.py  | Pixiv ID 기준 로컬 작가 자동 매칭 |
| service.py  | 팔로우 유저 저장, 조회, 통계 처리    |
| **init**.py | follow 서비스 export       |

---

# app/services/pixiv

Pixiv 연동 서비스.

```text
pixiv
│
├─ metadata_parts
├─ sync_parts
│
├─ client.py
├─ metadata_service.py
├─ rate_limit.py
├─ session_service.py
├─ sync_service.py
└─ __init__.py
```

## 역할

| 파일                  | 역할                   |
| ------------------- | -------------------- |
| client.py           | Pixiv API 요청 클라이언트   |
| metadata_service.py | Pixiv 메타데이터 수집 진입점   |
| rate_limit.py       | 요청 간격, 배치 휴식, 재시도 제어 |
| session_service.py  | PHPSESSID 세션 검증      |
| sync_service.py     | 팔로우 / 북마크 동기화 진입점    |
| **init**.py         | pixiv 서비스 export     |

## metadata_parts

```text
metadata_parts
│
├─ models.py
├─ response_parser.py
├─ tag_parser.py
└─ __init__.py
```

### 역할

| 파일                 | 역할                     |
| ------------------ | ---------------------- |
| models.py          | Pixiv 유저 / 작품 메타데이터 모델 |
| response_parser.py | Pixiv API 응답 파싱        |
| tag_parser.py      | Pixiv 태그 통계 및 번역 태그 파싱 |
| **init**.py        | metadata_parts export  |

## sync_parts

```text
sync_parts
│
├─ bookmark_sync.py
├─ constants.py
├─ follow_sync.py
├─ helpers.py
└─ __init__.py
```

### 역할

| 파일               | 역할                |
| ---------------- | ----------------- |
| bookmark_sync.py | 북마크 작품 동기화 처리     |
| constants.py     | 동기화 상태 및 공통 상수    |
| follow_sync.py   | 팔로우 유저 동기화 처리     |
| helpers.py       | 동기화 공통 헬퍼         |
| **init**.py      | sync_parts export |

---

# app/services/scan

폴더 스캔 및 재스캔 서비스.

```text
scan
│
├─ artist_scan_service.py
├─ folder_scan_service.py
├─ non_artwork_file_collector.py
├─ non_artwork_file_exporter.py
├─ rescan_service.py
├─ scan_builder.py
├─ scan_compare.py
└─ __init__.py
```

## 역할

| 파일                            | 역할                       |
| ----------------------------- | ------------------------ |
| artist_scan_service.py        | 신규 등록 및 기존 작가 갱신 처리      |
| folder_scan_service.py        | 폴더 분석, 작품 수, 파일 수, 용량 계산 |
| non_artwork_file_collector.py | 비작품 파일 수집                |
| non_artwork_file_exporter.py  | 비작품 파일 CSV 저장            |
| rescan_service.py             | 특정 작가 재스캔 처리             |
| scan_builder.py               | 스캔 결과 데이터 생성             |
| scan_compare.py               | 기존 정보와 신규 스캔 결과 비교       |
| **init**.py                   | scan 서비스 export          |

---

# app/services/statistics

통계 분석 서비스.

```text
statistics
│
├─ favorite_service.py
├─ pixiv_management_service.py
├─ quality_service.py
├─ ranking_service.py
├─ rating_service.py
├─ service.py
├─ status_service.py
├─ tag_service.py
├─ trend_service.py
└─ __init__.py
```

## 역할

| 파일                          | 역할                    |
| --------------------------- | --------------------- |
| favorite_service.py         | 즐겨찾기 통계               |
| pixiv_management_service.py | 팔로우 및 북마크 통계          |
| quality_service.py          | 데이터 품질 분석             |
| ranking_service.py          | 작품 수, 파일 수, 저장 용량 TOP |
| rating_service.py           | 평점 분포 분석              |
| service.py                  | StatisticsService 진입점 |
| status_service.py           | 업데이트 상태 분포 분석         |
| tag_service.py              | 태그 사용 분석              |
| trend_service.py            | 주간 변화 분석              |
| **init**.py                 | statistics 서비스 export |

---

# app/services/tag

태그 처리 서비스.

```text
tag
│
├─ models.py
├─ parser.py
├─ service.py
└─ __init__.py
```

## 역할

| 파일          | 역할                 |
| ----------- | ------------------ |
| models.py   | TagData 모델         |
| parser.py   | 태그 파싱 및 검증         |
| service.py  | 태그 병합, 직렬화, 표시명 생성 |
| **init**.py | tag 서비스 export     |

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

| 파일                       | 역할                |
| ------------------------ | ----------------- |
| artist_update_service.py | 단일 작가 업데이트 확인     |
| bulk_update_service.py   | 다중 작가 업데이트 확인     |
| update_utils.py          | 업데이트 공통 유틸        |
| **init**.py              | update 서비스 export |

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

## 역할

| 파일             | 역할                      |
| -------------- | ----------------------- |
| main_window.py | 메인 윈도우, 사이드바, 페이지 전환 관리 |
| pages          | 주요 기능 페이지               |
| widgets        | 공통 위젯                   |
| **init**.py    | ui 패키지 export           |

---

# ui/pages

프로그램의 주요 기능 페이지.

```text
pages
│
├─ artists
├─ artist_detail
├─ dashboard
├─ pixiv_manager
├─ scan
├─ settings
├─ statistics
├─ update_check
└─ __init__.py
```

## 역할

| 파일            | 역할               |
| ------------- | ---------------- |
| artists       | 작가 목록 관리 페이지     |
| artist_detail | 작가 상세 페이지        |
| dashboard     | 대시보드 페이지         |
| pixiv_manager | Pixiv 관리 페이지     |
| scan          | 스캔 페이지           |
| settings      | 설정 페이지           |
| statistics    | 통계 분석 페이지        |
| update_check  | 업데이트 확인 페이지      |
| **init**.py   | pages 패키지 export |

---

# ui/pages/artists

작가 목록 관리 페이지.

```text
artists
│
├─ action_parts
│
├─ actions.py
├─ filters.py
├─ page.py
├─ toolbar.py
└─ __init__.py
```

## 역할

| 파일          | 역할                 |
| ----------- | ------------------ |
| actions.py  | ArtistsActions 진입점 |
| filters.py  | 검색, 필터, 정렬 로직      |
| page.py     | 작가 목록 페이지 UI       |
| toolbar.py  | 검색창, 필터, 관리 버튼 영역  |
| **init**.py | artists 페이지 export |

## action_parts

작가 목록 페이지의 기능별 액션 모듈.

```text
action_parts
│
├─ bulk_actions.py
├─ data_actions.py
├─ dialog_actions.py
└─ __init__.py
```

### 역할

| 파일                | 역할                            |
| ----------------- | ----------------------------- |
| bulk_actions.py   | 선택 작가 평점 변경, 즐겨찾기, 삭제 등 일괄 작업 |
| data_actions.py   | 작가 목록 로드, 필터, 정렬, 표시 갱신       |
| dialog_actions.py | 삭제, 복구, 입력 등 대화상자 기반 작업       |
| **init**.py       | action_parts export           |

---

# ui/pages/artist_detail

작가 상세 페이지.

```text
artist_detail
│
├─ action_parts
├─ info_parts
│
├─ actions.py
├─ info_section.py
├─ page.py
├─ styles.py
├─ utils.py
└─ __init__.py
```

## 역할

| 파일              | 역할                       |
| --------------- | ------------------------ |
| actions.py      | ArtistDetailActions 진입점  |
| info_section.py | 상세 정보 전체 영역              |
| page.py         | 작가 상세 페이지                |
| styles.py       | 상세 페이지 스타일               |
| utils.py        | 상세 페이지 공통 유틸             |
| **init**.py     | artist_detail 페이지 export |

## action_parts

작가 상세 페이지의 기능별 액션 모듈.

```text
action_parts
│
├─ data_actions_parts
│
├─ artwork_actions.py
├─ data_actions.py
├─ dialog_actions.py
├─ tag_actions.py
└─ __init__.py
```

### 역할

| 파일                 | 역할                                |
| ------------------ | --------------------------------- |
| artwork_actions.py | 최근 로컬 작품, 누락 작품, Pixiv 작품 바로가기 처리 |
| data_actions.py    | ArtistDataActions 진입점             |
| dialog_actions.py  | 폴더 선택, 복사, 알림 등 대화상자 작업           |
| tag_actions.py     | 태그 추가, 삭제, 정리, 수집                 |
| **init**.py        | action_parts export               |

## data_actions_parts

작가 상세 페이지 데이터 액션의 세부 모듈.

```text
data_actions_parts
│
├─ artist_load.py
├─ artist_operations.py
├─ artist_save.py
├─ update_history.py
└─ __init__.py
```

### 역할

| 파일                   | 역할                        |
| -------------------- | ------------------------- |
| artist_load.py       | 작가 데이터 로드 및 화면 반영         |
| artist_operations.py | 현재 작가 재스캔, 업데이트 확인        |
| artist_save.py       | 작가 정보 저장                  |
| update_history.py    | 업데이트 이력 테이블 데이터 처리        |
| **init**.py          | data_actions_parts export |

## info_parts

작가 상세 정보 UI 세부 모듈.

```text
info_parts
│
├─ artwork_section.py
├─ basic_info.py
├─ memo_section.py
├─ update_history.py
└─ __init__.py
```

### 역할

| 파일                 | 역할                     |
| ------------------ | ---------------------- |
| artwork_section.py | 최근 로컬 작품 및 누락 작품 UI    |
| basic_info.py      | 기본 정보, 폴더 정보, 상태 정보 UI |
| memo_section.py    | 메모, 참고 링크, 다운로드 메모 UI  |
| update_history.py  | 업데이트 이력 UI             |
| **init**.py        | info_parts export      |

---

# ui/pages/dashboard

대시보드 페이지.

```text
dashboard
│
├─ recent_activity_parts
│
├─ actions.py
├─ dashboard_metrics.py
├─ dashboard_styles.py
├─ page.py
├─ random_artist_section.py
├─ recent_activity_section.py
├─ recent_artists_section.py
├─ recommendation_card.py
├─ recommendation_section.py
├─ scan_statistics_section.py
├─ summary_card.py
├─ summary_section.py
├─ top_ranking_section.py
├─ top_ranking_utils.py
├─ update_status_section.py
├─ utils.py
└─ __init__.py
```

## 역할

| 파일                         | 역할                   |
| -------------------------- | -------------------- |
| actions.py                 | 대시보드 데이터 로드 및 화면 갱신  |
| dashboard_metrics.py       | 대시보드 통계 계산           |
| dashboard_styles.py        | 대시보드 스타일             |
| page.py                    | 대시보드 페이지             |
| random_artist_section.py   | 랜덤 작가 영역             |
| recent_activity_section.py | 최근 활동 영역             |
| recent_artists_section.py  | 최근 등록 작가 영역          |
| recommendation_card.py     | 추천 작가 카드             |
| recommendation_section.py  | 추천 작가 영역             |
| scan_statistics_section.py | 최근 스캔 통계 영역          |
| summary_card.py            | 요약 카드 위젯             |
| summary_section.py         | 상단 요약 통계 영역          |
| top_ranking_section.py     | TOP 랭킹 영역            |
| top_ranking_utils.py       | TOP 랭킹 공통 유틸         |
| update_status_section.py   | 업데이트 현황 영역           |
| utils.py                   | 대시보드 공통 유틸           |
| **init**.py                | dashboard 페이지 export |

## recent_activity_parts

최근 활동 영역 구성 모듈.

```text
recent_activity_parts
│
├─ row_utils.py
├─ table_factory.py
├─ table_updaters.py
└─ __init__.py
```

### 역할

| 파일                | 역할                            |
| ----------------- | ----------------------------- |
| row_utils.py      | 최근 활동 테이블 행 생성 및 상세 페이지 이동 처리 |
| table_factory.py  | 최근 활동 탭 및 테이블 생성              |
| table_updaters.py | 최근 활동 데이터 갱신                  |
| **init**.py       | recent_activity_parts export  |

---

# ui/pages/pixiv_manager

Pixiv 관리 페이지.

```text
pixiv_manager
│
├─ action_parts
├─ bookmark_table_parts
├─ follow_table_parts
├─ table_common
├─ worker_parts
│
├─ actions.py
├─ bookmark_table.py
├─ follow_table.py
├─ log_table.py
├─ page.py
├─ styles.py
├─ summary_section.py
├─ worker.py
└─ __init__.py
```

## 역할

| 파일                 | 역할                              |
| ------------------ | ------------------------------- |
| actions.py         | PixivManagerActions 진입점         |
| bookmark_table.py  | BookmarkArtworkTable export 진입점 |
| follow_table.py    | FollowUserTable export 진입점      |
| log_table.py       | Pixiv 관리 로그 테이블                 |
| page.py            | Pixiv 관리 페이지                    |
| styles.py          | Pixiv 관리 페이지 스타일                |
| summary_section.py | 팔로우 / 북마크 요약 카드                 |
| worker.py          | Pixiv 가져오기 / 동기화 워커 진입점         |
| **init**.py        | pixiv_manager 페이지 export        |

## action_parts

Pixiv 관리 페이지 액션 모듈.

```text
action_parts
│
├─ data_actions.py
├─ delete_actions.py
├─ import_actions.py
├─ log_actions.py
├─ pagination_actions.py
├─ selection_actions.py
├─ worker_actions.py
└─ __init__.py
```

### 역할

| 파일                    | 역할                    |
| --------------------- | --------------------- |
| data_actions.py       | 팔로우 / 북마크 데이터 로드 및 갱신 |
| delete_actions.py     | 선택 항목 삭제 처리           |
| import_actions.py     | txt / csv 가져오기 처리     |
| log_actions.py        | 작업 로그 처리              |
| pagination_actions.py | 페이지 이동 및 페이지 크기 처리    |
| selection_actions.py  | 테이블 선택 처리             |
| worker_actions.py     | 가져오기 / 동기화 워커 실행 처리   |
| **init**.py           | action_parts export   |

## bookmark_table_parts

북마크 작품 테이블 구성 모듈.

```text
bookmark_table_parts
│
├─ constants.py
├─ model.py
├─ table.py
└─ __init__.py
```

### 역할

| 파일           | 역할                          |
| ------------ | --------------------------- |
| constants.py | 북마크 테이블 컬럼 상수               |
| model.py     | 북마크 테이블 모델                  |
| table.py     | 북마크 테이블 위젯                  |
| **init**.py  | bookmark_table_parts export |

## follow_table_parts

팔로우 유저 테이블 구성 모듈.

```text
follow_table_parts
│
├─ constants.py
├─ model.py
├─ table.py
└─ __init__.py
```

### 역할

| 파일           | 역할                        |
| ------------ | ------------------------- |
| constants.py | 팔로우 테이블 컬럼 상수             |
| model.py     | 팔로우 테이블 모델                |
| table.py     | 팔로우 테이블 위젯                |
| **init**.py  | follow_table_parts export |

## table_common

공통 테이블 모듈.

```text
table_common
│
├─ base_model.py
├─ base_table.py
├─ checkbox_delegate.py
├─ formatters.py
└─ __init__.py
```

### 역할

| 파일                   | 역할                  |
| -------------------- | ------------------- |
| base_model.py        | Pixiv 관리 테이블 공통 모델  |
| base_table.py        | Pixiv 관리 테이블 공통 기능  |
| checkbox_delegate.py | 체크박스 셀 delegate     |
| formatters.py        | 테이블 표시값 포맷          |
| **init**.py          | table_common export |

## worker_parts

Pixiv 가져오기 및 동기화 워커 모듈.

```text
worker_parts
│
├─ file_import.py
├─ pixiv_sync.py
├─ progress.py
├─ result_builder.py
└─ __init__.py
```

### 역할

| 파일                | 역할                  |
| ----------------- | ------------------- |
| file_import.py    | 파일 가져오기 처리          |
| pixiv_sync.py     | Pixiv 메타데이터 동기화 처리  |
| progress.py       | 진행률 계산 및 전달         |
| result_builder.py | 가져오기 / 동기화 결과 생성    |
| **init**.py       | worker_parts export |

---

# ui/pages/scan

스캔 페이지.

```text
scan
│
├─ action_parts
├─ page_parts
├─ preview_table_parts
├─ progress_parts
├─ worker_parts
│
├─ actions.py
├─ folder_scanner.py
├─ folder_section.py
├─ log_table.py
├─ log_utils.py
├─ page.py
├─ preview_table.py
├─ progress_section.py
├─ scan_styles.py
├─ worker.py
└─ __init__.py
```

## 역할

| 파일                  | 역할              |
| ------------------- | --------------- |
| actions.py          | ScanActions 진입점 |
| folder_scanner.py   | 폴더 탐색 보조        |
| folder_section.py   | 폴더 선택 UI        |
| log_table.py        | 스캔 로그 테이블       |
| log_utils.py        | 로그 표시 유틸        |
| page.py             | 스캔 페이지          |
| preview_table.py    | 미리보기 테이블 진입점    |
| progress_section.py | 진행률 / 통계 표시 영역  |
| scan_styles.py      | 스캔 페이지 스타일      |
| worker.py           | ScanWorker 진입점  |
| **init**.py         | scan 페이지 export |

## action_parts

스캔 페이지 액션 모듈.

```text
action_parts
│
├─ worker_actions
│
├─ filter_actions.py
├─ folder_actions.py
├─ result_actions.py
└─ __init__.py
```

### 역할

| 파일                | 역할                         |
| ----------------- | -------------------------- |
| filter_actions.py | 스캔 결과 필터 처리                |
| folder_actions.py | 스캔 폴더 선택 및 경로 처리           |
| result_actions.py | 스캔 결과 저장, CSV 내보내기, 실패 재시도 |
| **init**.py       | action_parts export        |

### worker_actions

스캔 워커 제어 모듈.

```text
worker_actions
│
├─ control_actions.py
├─ handler_actions.py
├─ start_actions.py
├─ state_actions.py
└─ __init__.py
```

#### 역할

| 파일                 | 역할                       |
| ------------------ | ------------------------ |
| control_actions.py | 스캔 중지 / 일시정지 / 재개 제어     |
| handler_actions.py | 워커 시그널 결과 처리             |
| start_actions.py   | 스캔 및 미리보기 시작 처리          |
| state_actions.py   | 버튼 상태 및 진행 상태 관리         |
| **init**.py        | ScanWorkerActions export |

## page_parts

스캔 페이지 UI 구성 모듈.

```text
page_parts
│
├─ log_header.py
├─ preview_header.py
├─ signal_connector.py
└─ __init__.py
```

### 역할

| 파일                  | 역할                |
| ------------------- | ----------------- |
| log_header.py       | 로그 영역 헤더 UI       |
| preview_header.py   | 미리보기 영역 헤더 UI     |
| signal_connector.py | 페이지 시그널 연결        |
| **init**.py         | page_parts export |

## preview_table_parts

미리보기 테이블 구성 모듈.

```text
preview_table_parts
│
├─ filter_logic.py
├─ row_renderer.py
├─ summary.py
└─ __init__.py
```

### 역할

| 파일              | 역할                         |
| --------------- | -------------------------- |
| filter_logic.py | 미리보기 테이블 필터 로직             |
| row_renderer.py | 미리보기 테이블 행 렌더링             |
| summary.py      | 미리보기 요약 계산                 |
| **init**.py     | preview_table_parts export |

## progress_parts

진행률 표시 모듈.

```text
progress_parts
│
├─ history_formatter.py
├─ statistics_formatter.py
└─ __init__.py
```

### 역할

| 파일                      | 역할                    |
| ----------------------- | --------------------- |
| history_formatter.py    | 스캔 이력 표시 포맷           |
| statistics_formatter.py | 스캔 통계 표시 포맷           |
| **init**.py             | progress_parts export |

## worker_parts

스캔 워커 모듈.

```text
worker_parts
│
├─ validation
│
├─ control_handler.py
├─ preview_builder.py
├─ preview_runner.py
├─ result_builder.py
├─ runtime_utils.py
├─ scan_runner.py
├─ state_manager.py
├─ statistics.py
└─ __init__.py
```

### 역할

| 파일                 | 역할                  |
| ------------------ | ------------------- |
| control_handler.py | 워커 제어 요청 처리         |
| preview_builder.py | 미리보기 결과 생성          |
| preview_runner.py  | 미리보기 실행             |
| result_builder.py  | 스캔 결과 생성            |
| runtime_utils.py   | 실행 시간, 속도 등 런타임 유틸  |
| scan_runner.py     | 실제 스캔 실행            |
| state_manager.py   | 워커 상태 관리            |
| statistics.py      | 스캔 통계 계산            |
| **init**.py        | worker_parts export |

### validation

스캔 검증 모듈.

```text
validation
│
├─ existing_maps.py
├─ folder_validation.py
├─ validation_mixin.py
└─ __init__.py
```

#### 역할

| 파일                   | 역할                       |
| -------------------- | ------------------------ |
| existing_maps.py     | 기존 등록 작가 / Pixiv ID 맵 생성 |
| folder_validation.py | 폴더명 및 경로 검증              |
| validation_mixin.py  | 검증 믹스인                   |
| **init**.py          | validation export        |

---

# ui/pages/settings

설정 페이지.

```text
settings
│
├─ action_parts
│
├─ actions.py
├─ app_info_section.py
├─ database_section.py
├─ database_utils.py
├─ folder_section.py
├─ log_section.py
├─ page.py
├─ pixiv_section.py
├─ settings_management_section.py
├─ settings_styles.py
└─ __init__.py
```

## 역할

| 파일                             | 역할                  |
| ------------------------------ | ------------------- |
| actions.py                     | SettingsActions 진입점 |
| app_info_section.py            | 프로그램 정보 영역          |
| database_section.py            | DB 관리 영역            |
| database_utils.py              | DB 표시용 유틸           |
| folder_section.py              | Pixiv 루트 폴더 설정 영역   |
| log_section.py                 | 로그 관리 영역            |
| page.py                        | 설정 페이지              |
| pixiv_section.py               | Pixiv 세션 설정 영역      |
| settings_management_section.py | 설정 백업 / 복원 영역       |
| settings_styles.py             | 설정 페이지 스타일          |
| **init**.py                    | settings 페이지 export |

## action_parts

설정 페이지 액션 모듈.

```text
action_parts
│
├─ backup_actions.py
├─ common.py
├─ database_actions.py
├─ environment_actions.py
├─ load_actions.py
├─ log_actions.py
├─ pixiv_actions.py
├─ request_actions.py
└─ __init__.py
```

### 역할

| 파일                     | 역할                     |
| ---------------------- | ---------------------- |
| backup_actions.py      | DB 백업, 복원, 백업 목록 처리    |
| common.py              | 설정 액션 공통 유틸            |
| database_actions.py    | DB 무결성 검사 및 최적화 처리     |
| environment_actions.py | 창 크기, 위치 등 환경 설정 처리    |
| load_actions.py        | 설정값 로드 및 화면 반영         |
| log_actions.py         | 로그 조회, 삭제, 로그 폴더 열기 처리 |
| pixiv_actions.py       | PHPSESSID 저장 및 검증      |
| request_actions.py     | Pixiv / 업데이트 요청 설정 저장  |
| **init**.py            | action_parts export    |

---

# ui/pages/statistics

통계 분석 페이지.

```text
statistics
│
├─ actions.py
├─ formatters.py
├─ page.py
├─ quality_section.py
├─ ranking_section.py
├─ rating_section.py
├─ status_section.py
├─ styles.py
├─ summary_card.py
├─ summary_section.py
├─ tag_section.py
├─ trend_section.py
└─ __init__.py
```

## 역할

| 파일                 | 역할                       |
| ------------------ | ------------------------ |
| actions.py         | 통계 데이터 로드 및 화면 갱신        |
| formatters.py      | 통계 수치 공통 포맷              |
| page.py            | 통계 페이지                   |
| quality_section.py | 데이터 품질 분석                |
| ranking_section.py | 작품 수, 파일 수, 저장 용량 TOP 랭킹 |
| rating_section.py  | 평점 분포                    |
| status_section.py  | 상태 분포                    |
| styles.py          | 통계 페이지 스타일               |
| summary_card.py    | 요약 카드 위젯                 |
| summary_section.py | 요약 통계 카드 영역              |
| tag_section.py     | 태그 통계                    |
| trend_section.py   | 주간 변화                    |
| **init**.py        | statistics 페이지 export    |

---

# ui/pages/update_check

업데이트 확인 페이지.

```text
update_check
│
├─ action_parts
├─ page_parts
├─ worker_parts
│
├─ actions.py
├─ artist_table.py
├─ log_table.py
├─ page.py
├─ selection_actions.py
├─ styles.py
├─ utils.py
├─ worker.py
├─ worker_config.py
└─ __init__.py
```

## 역할

| 파일                   | 역할                      |
| -------------------- | ----------------------- |
| actions.py           | UpdateCheckActions 진입점  |
| artist_table.py      | 업데이트 대상 작가 테이블          |
| log_table.py         | 로그 테이블                  |
| page.py              | 업데이트 확인 페이지             |
| selection_actions.py | 선택 작가 처리                |
| styles.py            | 페이지 스타일                 |
| utils.py             | 공통 유틸                   |
| worker.py            | UpdateCheckWorker 진입점   |
| worker_config.py     | 워커 설정                   |
| **init**.py          | update_check 페이지 export |

## action_parts

업데이트 확인 액션 모듈.

```text
action_parts
│
├─ control_actions.py
├─ start_actions.py
├─ ui_state_actions.py
├─ utility_actions.py
├─ worker_handlers.py
└─ __init__.py
```

### 역할

| 파일                  | 역할                  |
| ------------------- | ------------------- |
| control_actions.py  | 중지, 일시정지, 재개 처리     |
| start_actions.py    | 업데이트 확인 시작          |
| ui_state_actions.py | 버튼 및 화면 상태 관리       |
| utility_actions.py  | 공통 유틸 작업            |
| worker_handlers.py  | 워커 시그널 처리           |
| **init**.py         | action_parts export |

## page_parts

업데이트 확인 페이지 UI 모듈.

```text
page_parts
│
├─ data_actions.py
├─ log_frame.py
├─ option_frame.py
├─ progress_frame.py
├─ settings_actions.py
├─ summary_frame.py
├─ table_frame.py
└─ __init__.py
```

### 역할

| 파일                  | 역할                |
| ------------------- | ----------------- |
| data_actions.py     | 페이지 데이터 로드        |
| log_frame.py        | 로그 영역 UI          |
| option_frame.py     | 옵션 영역 UI          |
| progress_frame.py   | 진행률 영역 UI         |
| settings_actions.py | 설정값 적용            |
| summary_frame.py    | 결과 요약 영역          |
| table_frame.py      | 작가 테이블 영역         |
| **init**.py         | page_parts export |

## worker_parts

업데이트 확인 워커 모듈.

```text
worker_parts
│
├─ log_utils.py
├─ pause_cancel.py
├─ run_logic.py
├─ sleep_utils.py
├─ summary.py
└─ __init__.py
```

### 역할

| 파일              | 역할                  |
| --------------- | ------------------- |
| log_utils.py    | 로그 생성 유틸            |
| pause_cancel.py | 일시정지, 중단 처리         |
| run_logic.py    | 업데이트 실행 로직          |
| sleep_utils.py  | 요청 간 대기 처리          |
| summary.py      | 결과 요약 생성            |
| **init**.py     | worker_parts export |

---

# ui/widgets

프로그램 전역에서 사용하는 공통 위젯.

```text
widgets
│
├─ artist_table
│
├─ sidebar.py
├─ status_badge.py
└─ __init__.py
```

## 역할

| 파일              | 역할             |
| --------------- | -------------- |
| sidebar.py      | 사이드바 메뉴        |
| status_badge.py | 업데이트 상태 배지     |
| **init**.py     | widgets export |

## artist_table

작가 목록 공통 테이블.

```text
artist_table
│
├─ actions.py
├─ cell_widgets.py
├─ columns.py
├─ formatters.py
├─ row_renderer.py
├─ table.py
└─ __init__.py
```

### 역할

| 파일              | 역할                  |
| --------------- | ------------------- |
| actions.py      | 테이블 액션 처리           |
| cell_widgets.py | 별점, 버튼 등 셀 위젯       |
| columns.py      | 컬럼 정의               |
| formatters.py   | 표시값 포맷              |
| row_renderer.py | 행 렌더링               |
| table.py        | ArtistTable         |
| **init**.py     | artist_table export |

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

## 역할

| 파일                     | 역할          |
| ---------------------- | ----------- |
| 01_PROJECT_OVERVIEW.md | 프로젝트 소개     |
| 02_REQUIREMENTS.md     | 기능 요구사항     |
| 03_SYSTEM_FLOW.md      | 시스템 흐름      |
| 04_DATABASE.md         | 데이터베이스 설계   |
| 05_UI_DESIGN.md        | UI 설계       |
| 06_CHANGELOG.md        | 변경 이력       |
| 07_ARCHITECTURE.md     | 시스템 아키텍처    |
| 08_SERVICES.md         | 서비스 구조      |
| 09_FILE_STRUCTURE.md   | 파일 구조       |
| 99_BACKLOG.md          | 향후 개발 예정 기능 |

---

# tests

테스트 코드.

```text
tests
│
├─ services
│
├─ conftest.py
└─ __init__.py
```

## 역할

| 파일          | 역할           |
| ----------- | ------------ |
| services    | 서비스 단위 테스트   |
| conftest.py | pytest 공통 설정 |
| **init**.py | tests 패키지    |

---

# data

프로그램 데이터 저장 폴더.

```text
data
│
├─ app.db
├─ settings.json
└─ logs
```

## 역할

| 파일            | 역할            |
| ------------- | ------------- |
| app.db        | SQLite 데이터베이스 |
| settings.json | 프로그램 설정       |
| logs          | 프로그램 로그       |

---

# backups

백업 파일 저장 폴더.

```text
backups
│
├─ database
├─ deleted_artists
└─ settings
```

## 역할

| 폴더              | 역할       |
| --------------- | -------- |
| database        | DB 백업    |
| deleted_artists | 삭제 작가 백업 |
| settings        | 설정 백업    |

---

# exports

내보내기 파일 저장 폴더.

```text
exports
│
├─ artists
├─ scans
├─ updates
└─ non_artwork_files
```

## 역할

| 폴더                | 역할          |
| ----------------- | ----------- |
| artists           | 작가 목록 CSV   |
| scans             | 스캔 결과 CSV   |
| updates           | 업데이트 결과 CSV |
| non_artwork_files | 비작품 파일 CSV  |

---

# 설계 원칙

## 1. 페이지 단위 분리

```text
Dashboard
Scan
Update Check
Artists
Artist Detail
Pixiv Manager
Statistics
Settings
```

각 기능은 독립적인 페이지로 구성한다.

---

## 2. Action 계층 분리

```text
Page
→ Actions
→ Action Parts
```

페이지 이벤트와 비즈니스 로직 연결을 분리한다.

---

## 3. UI 영역 분리

```text
Page
→ Section
```

복잡한 화면은 기능 단위 Section으로 분리한다.

---

## 4. Worker 분리

```text
Page
→ Worker
→ Worker Parts
```

장시간 작업은 UI 스레드와 분리한다.

---

## 5. Service Layer 사용

```text
UI
→ Service
→ Repository
→ Database
```

UI는 직접 데이터베이스에 접근하지 않는다.

---

## 6. 공통 위젯 사용

```text
Sidebar
StatusBadge
ArtistTable
```

재사용 가능한 UI는 공통 Widget으로 관리한다.

---

## 7. 기능 단위 패키지 구성

```text
artist
scan
update
pixiv
statistics
backup
```

도메인 중심 구조를 유지한다.

---

# 버전 기준

본 문서는 v0.17.0 (추가 기능 개발 완료) 기준으로 작성되었다.

Pixiv 관리 시스템, Pixiv 메타데이터 동기화, 태그 관리, 통계 분석, 주간 변화 분석 기능이 포함된 현재 파일 구조를 설명한다.
