# 시스템 흐름도 (System Flow)

## 전체 시스템 흐름

```mermaid
flowchart LR

START[프로그램 실행]

START --> INIT[DB 초기화]

INIT --> MAIN[메인 윈도우]

MAIN --> DASHBOARD[대시보드]
MAIN --> SCAN[폴더 스캔]
MAIN --> ARTISTS[작가 목록]
MAIN --> SETTINGS[설정]

ARTISTS --> DETAIL[작가 상세]
ARTISTS --> UPDATE[업데이트 확인]
```

---

## 프로그램 구조

```mermaid
flowchart LR

UI[UI Layer]

SERVICE[Service Layer]

REPO[Repository Layer]

DB[(SQLite)]

UI --> SERVICE
SERVICE --> REPO
REPO --> DB
```

---

## 폴더 스캔 흐름

```mermaid
flowchart LR

A[루트 폴더 선택]

A --> B[하위 폴더 탐색]

B --> C[이미지 포함 폴더 확인]

C --> D[작가명 / Pixiv ID 파싱]

D --> E{기존 등록 여부}

E -- 신규 --> F[작가 등록]

E -- 기존 --> G[작가 정보 갱신]

F --> H[DB 저장]
G --> H

H --> I[스캔 로그 출력]

I --> J[작가 목록 갱신]
```

---

## 작가 목록 흐름

```mermaid
flowchart LR

A[작가 목록 조회]

A --> B[검색]

A --> C[정렬]

A --> D[상태 정렬]

A --> E[평점 표시 변경]

A --> F[작가 선택]

F --> G[작가 상세 이동]
```

---

## 작가 상세 흐름

```mermaid
flowchart LR

A[작가 선택]

A --> B[상세 정보 표시]

B --> C[작가명 수정]

B --> D[평점 수정]

B --> E[메모 수정]

B --> F[폴더 경로 수정]

C --> G[저장]
D --> G
E --> G
F --> G

G --> H[DB 업데이트]

H --> I[작가 목록 갱신]
```

---

## Pixiv 업데이트 확인 흐름

```mermaid
flowchart LR

A[업데이트 확인]

A --> B[작가 선택]

B --> C[최근 확인 작가 제외]

C --> D[업데이트 작업 시작]

D --> E[Pixiv API 요청]

E --> F[작품 수 조회]

F --> G[로컬 작품 수 비교]

G --> H{최신 여부}

H -- 최신 --> I[up_to_date]

H -- 차이 있음 --> J[need_update]

I --> K[DB 저장]
J --> K

K --> L[로그 출력]

L --> M[다음 작가]
```

---

## 업데이트 작업 흐름

```mermaid
flowchart LR

START[작업 시작]

START --> CHECK[작가 처리]

CHECK --> WAIT[5~10초 대기]

WAIT --> CHECK

CHECK --> REST{20명 처리}

REST -- 예 --> BREAK[3~5분 휴식]

BREAK --> CHECK

REST -- 아니오 --> NEXT[다음 작가]

NEXT --> CHECK
```

---

## 설정 저장 흐름

```mermaid
flowchart LR

A[설정 화면]

A --> B[기본 Pixiv 폴더]

A --> C[PHPSESSID]

B --> D[설정 저장]
C --> D

D --> E[AppSetting 저장]
```

---

## DB 백업 흐름

```mermaid
flowchart LR

A[DB 백업]

A --> B[SQLite DB 확인]

B --> C[무결성 검사]

C --> D[백업 폴더 선택]

D --> E[DB 파일 복사]

E --> F[백업 완료]
```

---

## DB 복원 흐름

```mermaid
flowchart LR

A[DB 복원]

A --> B[복원 파일 선택]

B --> C[SQLite 검증]

C --> D[안전 백업 생성]

D --> E[DB 파일 복원]

E --> F[프로그램 재시작]
```

---

## CSV 내보내기 흐름

```mermaid
flowchart LR

A[CSV 내보내기]

A --> B[저장 위치 선택]

B --> C[작가 데이터 조회]

C --> D[CSV 생성]

D --> E[파일 저장]

E --> F[완료]
```

---

## 화면 이동 구조

```mermaid
flowchart TD

MAIN[MainWindow]

MAIN --> DASHBOARD[Dashboard]

MAIN --> SCAN[Scan]

MAIN --> ARTISTS[Artists]

MAIN --> SETTINGS[Settings]

ARTISTS --> DETAIL[Artist Detail]

ARTISTS --> UPDATE[Update Check Dialog]
```

---

## 데이터 흐름

```mermaid
flowchart LR

FOLDER[Pixiv 폴더]

FOLDER --> SCAN[Folder Scan Service]

SCAN --> DB[(SQLite)]

DB --> REPO[Repository]

REPO --> SERVICE[Service Layer]

SERVICE --> UI[UI Layer]

UI --> CSV[CSV Export]

UI --> BACKUP[DB Backup]
```