# 시스템 흐름

## 전체 흐름

```mermaid
flowchart LR

START[프로그램 시작]

START --> DASHBOARD[대시보드]
START --> SCAN[폴더 스캔]
START --> ARTISTS[작가 관리]
START --> UPDATE[업데이트 확인]
START --> SETTINGS[설정]

ARTISTS --> DETAIL[작가 상세]
DETAIL --> UPDATE
DETAIL --> SETTINGS
```

---

# 폴더 스캔 흐름

```mermaid
flowchart LR

A[폴더 선택]

A --> B[하위 폴더 탐색]
B --> C[작가명 추출]
C --> D[Pixiv ID 추출]
D --> E[작품 수 계산]
E --> F[파일 수 계산]
F --> G[작품 ID 수집]

G --> H{기존 작가 존재}

H -->|없음| I[신규 등록]
H -->|있음| J[정보 갱신]

I --> K[스캔 완료]
J --> K
```

---

# 작가 조회 흐름

```mermaid
flowchart LR

A[작가 목록]

A --> B[검색]
A --> C[필터]
A --> D[정렬]

B --> E[결과 표시]
C --> E
D --> E

E --> F[상세 페이지 이동]
```

---

# 작가 상세 조회 흐름

```mermaid
flowchart LR

A[작가 선택]

A --> B[기본 정보 표시]
A --> C[평점 표시]
A --> D[태그 표시]
A --> E[메모 표시]
A --> F[파일 수 표시]
A --> G[업데이트 상태 표시]
A --> H[최근 로컬 작품 표시]
A --> I[누락 작품 표시]
A --> J[참고 링크 표시]
A --> K[다운로드 메모 표시]

B --> L[수정]
C --> L
D --> L
E --> L
J --> L
K --> L

L --> M[저장]
```

---

# 작가 폴더 변경 흐름

```mermaid
flowchart LR

A[폴더 변경]

A --> B[새 폴더 선택]
B --> C[Pixiv ID 파싱]

C --> D{중복 Pixiv ID 존재}

D -->|예| E[저장 취소]
D -->|아니오| F[경로 저장]

F --> G[재스캔]
G --> H[작가명 갱신]
H --> I[작품 수 갱신]
I --> J[파일 수 갱신]
J --> K[작품 ID 갱신]
K --> L[업데이트 상태 갱신]

L --> M[완료]
```

---

# 누락 작품 생성 흐름

```mermaid
flowchart LR

A[작가 상세 페이지]

A --> B[Pixiv 최신 작품 ID]
A --> C[로컬 작품 ID]

B --> D[비교]
C --> D

D --> E[누락 작품 목록 생성]

E --> F[상세 페이지 표시]
```

---

# 업데이트 확인 흐름

```mermaid
flowchart LR

A[작가 선택]

A --> B[Pixiv 접속]
B --> C[최신 작품 조회]
C --> D[작품 ID 수집]

D --> E[로컬 작품 ID 비교]

E --> F{누락 존재}

F -->|예| G[업데이트 필요]
F -->|아니오| H[최신 상태]

G --> I[상태 저장]
H --> I

I --> J[결과 표시]
```

---

# 다중 업데이트 확인 흐름

```mermaid
flowchart LR

A[작가 다중 선택]

A --> B[업데이트 확인 시작]

B --> C[작가 반복 처리]

C --> D[최신 작품 조회]
D --> E[작품 ID 비교]
E --> F[상태 저장]

F --> G{다음 작가 존재}

G -->|예| C
G -->|아니오| H[결과 요약]

H --> I[완료]
```

---

# 작가 삭제 흐름

```mermaid
flowchart LR

A[작가 선택]

A --> B[삭제 실행]
B --> C[삭제 확인]

C --> D[삭제 백업 생성]

D --> E[작가 삭제]

E --> F[완료]
```

---

# 삭제 작가 복구 흐름

```mermaid id="u1s3xa"
flowchart LR

A[복구 실행]

A --> B[백업 파일 선택]
B --> C[백업 데이터 읽기]

C --> D[작가 반복 처리]

D --> E{동일 Pixiv ID 존재}

E -->|예| F[중복 작가 - 복구 제외]
E -->|아니오| G[작가 복구]

F --> H{다음 작가}
G --> H

H -->|있음| D
H -->|없음| I[결과 요약]

I --> J[백업 파일 삭제]

J --> K[완료]
```

---

# DB 백업 흐름

```mermaid id="cqkxvw"
flowchart LR

A[DB 백업 실행]

A --> B[SQLite DB 확인]
B --> C[백업 파일 생성]

C --> D[백업 폴더 저장]

D --> E[완료]
```

---

# DB 복원 흐름

```mermaid id="w5kxxz"
flowchart LR

A[DB 복원 실행]

A --> B[백업 파일 선택]
B --> C[DB 교체]

C --> D[설정 재로드]

D --> E[완료]
```

---

# CSV 내보내기 흐름

```mermaid id="3jzv5v"
flowchart LR

A[CSV 내보내기]

A --> B[작가 데이터 조회]
B --> C[CSV 생성]

C --> D[파일 저장]

D --> E[완료]
```

---

# 평점 일괄 변경 흐름

```mermaid id="psh5oe"
flowchart LR

A[작가 다중 선택]

A --> B[평점 지정]

B --> C[선택 작가 반복 처리]

C --> D[평점 저장]

D --> E{다음 작가 존재}

E -->|예| C
E -->|아니오| F[완료]
```

---

# 즐겨찾기 일괄 변경 흐름

```mermaid id="kuzq5z"
flowchart LR

A[작가 다중 선택]

A --> B[즐겨찾기 설정 또는 해제]

B --> C[선택 작가 반복 처리]

C --> D[상태 저장]

D --> E{다음 작가 존재}

E -->|예| C
E -->|아니오| F[완료]
```

---

# 숨김 일괄 변경 흐름

```mermaid id="3ru3x8"
flowchart LR

A[작가 다중 선택]

A --> B[숨김 설정 또는 해제]

B --> C[선택 작가 반복 처리]

C --> D[상태 저장]

D --> E{다음 작가 존재}

E -->|예| C
E -->|아니오| F[완료]
```

---

# 태그 정리 흐름

```mermaid id="22c65i"
flowchart LR

A[태그 정리 실행]

A --> B[태그 목록 조회]

B --> C[중복 태그 병합]
C --> D[빈 태그 제거]

D --> E[작품 수 기준 정렬]

E --> F[저장]
```

---

# 프로그램 종료 흐름

```mermaid id="9aq0pz"
flowchart LR

A[프로그램 종료]

A --> B[설정 저장]
B --> C[DB 연결 종료]

C --> D[종료]
```

---

# 주요 데이터 흐름

## 작가 등록

```text
폴더 스캔
→ ArtistScanService
→ ArtistRepository
→ SQLite 저장
```

---

## 작가 수정

```text
Artist Detail
→ ArtistService
→ ArtistRepository
→ SQLite 저장
```

---

## 업데이트 확인

```text
Update Dialog
→ PixivUpdateService
→ ArtworkStatusService
→ ArtistUpdateService
→ ArtistRepository
→ SQLite 저장
```

---

## 삭제 작가 복구

```text
복구 실행
→ BackupService
→ ArtistRepository
→ SQLite 저장
```

---

## 폴더 변경

```text
폴더 변경
→ FolderScanService
→ ArtworkStatusService
→ ArtistRepository
→ SQLite 저장
```

---

# 향후 확장 예정

## V2

```text
업데이트 이력
오류 이력
통계 생성
대시보드 고도화
설정 관리 고도화
```

---

## V3

```text
작품 관리
작품 상세 정보
카드 보기
썸네일 보기
자체 뷰어
자동 업데이트
```

---
