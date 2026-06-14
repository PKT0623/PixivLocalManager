# Pixiv Local Manager

Pixiv 작가 폴더를 로컬 환경에서 체계적으로 관리하기 위한 Windows 데스크탑 프로그램.

작가 정보, 작품 수, 평점, 메모, 업데이트 상태를 SQLite 데이터베이스에 저장하고,
Pixiv 최신 작품 여부를 확인하여 로컬 컬렉션을 효율적으로 관리하는 것을 목표로 한다.

---

# 주요 기능

## 대시보드

- 전체 작가 수 확인
- 전체 작품 수 확인
- 평균 평점 확인
- 업데이트 상태 요약
- 최근 등록 작가 확인
- 최근 스캔 일시 확인
- 추천 작가 표시
- 랜덤 작가 선택

## 폴더 스캔

- Pixiv 폴더 스캔
- 최대 3단계 하위 폴더 탐색
- 작가명 / Pixiv ID 자동 파싱
- 이미지 파일 자동 분석
- 신규 작가 등록
- 기존 작가 정보 갱신
- 진행률 표시
- 실시간 로그 출력

## 작가 관리

- 작가 검색
- 작가 정렬
- 상태별 정렬
- 평점 표시 방식 변경
- 작가 상세 정보 조회
- 평점 수정
- 메모 관리
- 폴더 경로 관리
- Pixiv 페이지 바로가기

## 업데이트 확인

- 다중 작가 선택
- Pixiv 최신 작품 조회
- 로컬 작품 수 비교
- 누락 작품 수 계산
- 업데이트 상태 자동 갱신
- 최근 확인 작가 제외
- 작업 취소 지원
- 요청 간격 자동 조절

## 설정

- 기본 Pixiv 폴더 설정
- Pixiv PHPSESSID 저장
- SQLite DB 백업
- SQLite DB 복원
- CSV 내보내기
- DB 폴더 열기

---

# 기술 스택

| 구분 | 기술 |
|--------|--------|
| Language | Python 3 |
| GUI | PySide6 |
| Database | SQLite |
| Architecture | Repository Pattern |
| Build | PyInstaller |
| Export | CSV |
| Network | Pixiv AJAX API |

---

# 아키텍처

```text
UI Layer
│
├─ Dashboard
├─ Scan
├─ Artists
├─ Artist Detail
└─ Settings
│
▼
Service Layer
│
├─ ArtistService
├─ ArtistScanService
├─ ArtistUpdateService
├─ PixivUpdateService
├─ FolderScanService
├─ SettingsService
├─ BackupService
└─ ExportService
│
▼
Repository Layer
│
├─ ArtistRepository
└─ AppSettingRepository
│
▼
SQLite Database
```

---

# 프로젝트 구조

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
├─ backups
├─ exports
├─ docs
├─ tests
│
├─ main.py
├─ requirements.txt
└─ README.md
```

---

# 문서

| 문서 | 설명 |
|--------|--------|
| 01_PROJECT_OVERVIEW | 프로젝트 개요 |
| 02_REQUIREMENTS | 요구사항 |
| 03_SYSTEM_FLOW | 시스템 흐름 |
| 04_DATABASE | 데이터베이스 설계 |
| 05_UI_DESIGN | UI 설계 |
| 06_CHANGELOG | 개발 이력 |
| 07_ARCHITECTURE | 시스템 아키텍처 |
| 08_SERVICES | 서비스 레이어 |
| 09_FILE_STRUCTURE | 프로젝트 구조 |
| 99_BACKLOG | 향후 개발 계획 |

---

# 현재 개발 상태

| 항목 | 상태 |
|--------|--------|
| 프로젝트 구조 설계 | 완료 |
| 데이터베이스 설계 | 완료 |
| 서비스 레이어 구현 | 완료 |
| UI 구현 | 완료 |
| 폴더 스캔 기능 | 완료 |
| 작가 관리 기능 | 완료 |
| 업데이트 확인 기능 | 완료 |
| 설정 기능 | 완료 |
| 테스트 작성 | 진행 중 |
| EXE 배포 | 예정 |

---

# 실행

## 가상환경 생성

```bash
python -m venv .venv
```

## 가상환경 활성화

```bash
.venv\Scripts\activate
```

## 패키지 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
python main.py
```

---

# 라이선스

개인 프로젝트