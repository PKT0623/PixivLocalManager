# 시스템 흐름도 (System Flow)

## 전체 사용 흐름

```mermaid
flowchart LR

START[프로그램 실행]

START --> DASHBOARD[대시보드]

DASHBOARD --> REGISTER[폴더 등록]
DASHBOARD --> ARTISTS[작가 목록]
DASHBOARD --> SETTINGS[설정]

REGISTER --> SCAN[폴더 스캔]
SCAN --> PARSE[작가명-ID 파싱]
PARSE --> SAVE[DB 저장]

SAVE --> ARTISTS
```

---

## 작가 등록 흐름

```mermaid
flowchart LR

A[폴더 선택]

A --> B[폴더 스캔]

B --> C[작가명-ID 추출]

C --> D{중복 여부}

D -- 신규 --> E[등록]

D -- 기존 --> F[업데이트]

E --> G[DB 저장]
F --> G

G --> H[작가 목록 갱신]
```

---

## 작가 조회 흐름

```mermaid
flowchart LR

A[작가 목록]

A --> B[검색]

A --> C[정렬]

A --> D[작가 선택]

D --> E[상세 정보 표시]
```

---

## 작가 상세 흐름

```mermaid
flowchart LR

DETAIL[작가 상세]

DETAIL --> PIXIV[Pixiv 페이지 열기]

DETAIL --> FOLDER[로컬 폴더 열기]

DETAIL --> EDIT[정보 수정]

DETAIL --> INFO[폴더 정보 확인]

INFO --> SIZE[폴더 용량]

INFO --> FILES[파일 수]

INFO --> ARTWORKS[작품 수]

DETAIL --> UPDATE[최신 작품 상태 확인]
```

---

## 최신 작품 확인 흐름

```mermaid
flowchart LR

A[작가 선택]

A --> B[로컬 폴더 분석]

B --> C[작품 ID 추출]

C --> D[최신 작품 ID 3개 계산]

D --> E[폴더 용량 계산]

E --> F[파일 수 계산]

F --> G[작품 수 계산]

G --> H[DB 저장]

H --> I[Pixiv 최신 작품 ID 3개 입력]

I --> J{동일 여부}

J -- 동일 --> K[최신]

J -- 다름 --> L[업데이트 있음]
```

---

## CSV 내보내기 흐름

```mermaid
flowchart LR

A[내보내기]

A --> B[CSV 생성]

B --> C[파일 저장]

C --> D[완료]
```

---

## 백업 흐름

```mermaid
flowchart LR

A[백업]

A --> B[DB 읽기]

B --> C[JSON 생성]

C --> D[백업 저장]
```

---

## 복원 흐름

```mermaid
flowchart LR

A[복원]

A --> B[JSON 선택]

B --> C[데이터 검증]

C --> D[DB 복원]

D --> E[완료]
```

---

## 화면 이동 구조

```mermaid
flowchart TD

MAIN[메인 창]

MAIN --> DASHBOARD[대시보드]

MAIN --> REGISTER[폴더 등록]

MAIN --> ARTISTS[작가 목록]

MAIN --> SETTINGS[설정]

ARTISTS --> DETAIL[작가 상세]
```

---

## V1 데이터 흐름

```mermaid
flowchart LR

FOLDER[로컬 폴더]

FOLDER --> SCAN[폴더 스캔]

SCAN --> SQLITE[(SQLite)]

SQLITE --> UI[프로그램 UI]

UI --> CSV[CSV Export]

UI --> JSON[JSON Backup]
```
