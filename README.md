# Pixiv Local Manager

Pixiv 작가 및 작품 폴더를 관리하기 위한 Windows 데스크탑 프로그램.

로컬 데이터 중심으로 작가, 작품, 평점, 메모, 업데이트 상태 등을 한 곳에서 관리하는 것을 목표로 한다.

---

## 주요 기능

* 작가 폴더 등록
* 작가명-ID 자동 파싱
* 작가 검색 및 정렬
* 평점 및 메모 관리
* Pixiv 작가 페이지 바로가기
* 로컬 폴더 바로가기
* 최신 작품 상태 관리
* CSV 내보내기
* JSON 백업 및 복원
* Pixiv 최신 작품 확인
* 다중 작가 업데이트 확인
* Pixiv PHPSESSID 연동
* DB 백업 및 복원

---

## 프로젝트 목표

* 빠른 속도
* 크롤링 최소화
* 로컬 데이터 중심
* EXE 단독 실행
* 간단하고 보기 좋은 UI

---

## 기술 스택

| 구분       | 기술          |
| -------- | ----------- |
| Language | Python      |
| GUI      | PySide6     |
| Database | SQLite      |
| Config   | INI         |
| Backup   | JSON        |
| Export   | CSV         |
| Build    | PyInstaller |

---

## 프로젝트 문서

| 문서                  | 설명      |
| ------------------- | ------- |
| 01_PROJECT_OVERVIEW | 프로젝트 개요 |
| 02_REQUIREMENTS     | 기능 요구사항 |
| 03_SYSTEM_FLOW      | 시스템 흐름도 |
| 04_DATABASE         | DB 설계   |
| 05_UI_DESIGN        | UI 설계   |
| 06_DEVELOPMENT_PLAN | 개발 계획   |
| 99_BACKLOG          | 향후 기능   |

---

## 프로젝트 구조

```text
PixivLocalManager
│
├─ app
├─ ui
├─ data
├─ backups
├─ exports
├─ thumbnails
│
├─ docs
│  ├─ 01_PROJECT_OVERVIEW.md
│  ├─ 02_REQUIREMENTS.md
│  ├─ 03_SYSTEM_FLOW.md
│  ├─ 04_DATABASE.md
│  ├─ 05_UI_DESIGN.md
│  ├─ 06_DEVELOPMENT_PLAN.md
│  └─ 99_BACKLOG.md
│
├─ README.md
├─ requirements.txt
└─ main.py
```

---

## 개발 상태

| 단계      | 상태    |
| ------- | ----- |
| 프로젝트 구조 | 완료    |
| 문서 작성   | 완료    |
| DB 설계   | 완료    |
| UI 설계   | 완료    |
| 실제 개발   | 진행 중 |

---

## 라이선스

개인 프로젝트
