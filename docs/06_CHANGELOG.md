# 변경 이력 (Changelog)

프로젝트 진행 과정에서 수행된 주요 변경 사항을 기록한다.

---

# v0.1.0

## 프로젝트 초기 구성

### 추가

- 프로젝트 저장소 생성
- 기본 폴더 구조 구성
- 문서 작성 시작

### 문서

- 01_PROJECT_OVERVIEW 작성
- 02_REQUIREMENTS 작성
- 03_SYSTEM_FLOW 작성
- 04_DATABASE 작성
- 05_UI_DESIGN 작성

---

# v0.2.0

## 데이터베이스 설계

### 추가

- SQLite 데이터베이스 구조 설계
- artists 테이블 설계
- app_settings 테이블 설계

### 구현

- Database Connection 모듈 작성
- ArtistRepository 작성
- AppSettingRepository 작성

---

# v0.3.0

## 서비스 레이어 구축

### 추가

- ArtistService
- FolderScanService
- ArtistScanService
- ArtistUpdateService
- PixivUpdateService
- ArtworkStatusService
- BackupService
- ExportService
- SettingsService

### 변경

- UI에서 DB 직접 접근 제거
- Service Layer 중심 구조로 변경

---

# v0.4.0

## GUI 구현

### 추가

#### Main Window

- Sidebar
- Page Navigation

#### Dashboard

- 통계 카드
- 최근 등록 작가
- 최근 스캔 정보
- 추천 작가
- 랜덤 작가

#### Scan

- 폴더 선택
- 진행률 표시
- 로그 출력

#### Artists

- 작가 검색
- 정렬
- 상태 정렬
- 평점 표시 전환

#### Artist Detail

- 작가 정보 수정
- 평점 수정
- 메모 수정
- Pixiv 열기
- 폴더 열기

#### Settings

- PHPSESSID 관리
- 기본 Pixiv 폴더 관리
- DB 백업
- DB 복원
- CSV 내보내기

---

# v0.5.0

## Pixiv 업데이트 확인 기능

### 추가

- UpdateCheckDialog
- 다중 작가 선택
- Pixiv 작품 수 조회
- 업데이트 상태 갱신
- 누락 작품 수 계산
- 작업 로그 출력

### 추가 보호 기능

- 요청 간 랜덤 대기
- 배치 처리 후 휴식
- 최근 확인 작가 제외
- 작업 취소 지원

---

# v0.6.0

## 1차 리팩토링

### 목표

- 대형 파일 분리
- 유지보수성 향상
- 역할 분리

### 변경

#### Artist Table 분리

기존

```text
ArtistTable
```

변경 후

```text
artist_table/
├─ table.py
├─ actions.py
├─ row_renderer.py
├─ formatters.py
├─ columns.py
└─ cell_widgets.py
```

#### Artist Detail 분리

기존

```text
artist_detail_page.py
```

변경 후

```text
artist_detail/
├─ page.py
├─ actions.py
├─ info_section.py
└─ utils.py
```

#### Update Dialog 분리

기존

```text
update_check_dialog.py
```

변경 후

```text
update_check/
├─ dialog.py
├─ actions.py
├─ worker.py
├─ artist_table.py
├─ log_table.py
├─ selection_actions.py
└─ utils.py
```

### 결과

- 파일 크기 감소
- 가독성 향상
- 기능별 책임 분리
- 유지보수성 향상

---

# 향후 예정

## v0.7.0

예정 기능

- 테스트 코드 확장
- 예외 처리 강화
- UI 개선

---

## v1.0.0

목표

- EXE 빌드
- 배포 준비
- 문서 정리 완료
- 안정화

---