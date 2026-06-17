# 시스템 흐름

## 전체 흐름

```mermaid
flowchart LR

START[프로그램 시작]

START --> DASHBOARD[대시보드]
START --> SCAN[폴더 스캔]
START --> ARTISTS[작가 관리]
START --> UPDATE[업데이트 확인]
START --> STATISTICS[통계 분석]
START --> SETTINGS[설정]

DASHBOARD --> DETAIL[작가 상세]
ARTISTS --> DETAIL
SCAN --> DETAIL
UPDATE --> DETAIL
STATISTICS --> DETAIL

DETAIL --> DASHBOARD
DETAIL --> ARTISTS
DETAIL --> SCAN
DETAIL --> UPDATE
DETAIL --> STATISTICS
```

---

# 대시보드 흐름

```mermaid
flowchart LR

A[대시보드 진입]

A --> B[작가 데이터 조회]
A --> C[업데이트 이력 조회]

B --> D[통계 카드 계산]
B --> E[TOP 랭킹 계산]
B --> F[추천 작가 생성]
B --> G[랜덤 작가 생성]

C --> H[업데이트 현황 계산]
C --> I[최근 활동 생성]
C --> J[최근 스캔 결과 생성]
C --> K[누락 변화 계산]

D --> L[대시보드 표시]
E --> L
F --> L
G --> L
H --> L
I --> L
J --> L
K --> L
```

---

# 대시보드 상세 이동 흐름

```mermaid
flowchart LR

A[대시보드]

A --> B[최근 활동]
A --> C[TOP 랭킹]

B --> D[작가명 더블클릭]
C --> D

D --> E[작가 ID 확인]
E --> F[작가 상세 이동]

F --> G[돌아가기]
G --> H[대시보드 복귀]
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
F --> G[폴더 용량 계산]
G --> H[작품 ID 수집]

H --> I{기존 작가 존재}

I -->|없음| J[신규 등록]
I -->|있음| K[정보 갱신]

J --> L[스캔 결과 저장]
K --> L

L --> M[스캔 완료]
```

---

# 스캔 미리보기 흐름

```mermaid
flowchart LR

A[미리보기 실행]

A --> B[폴더 탐색]
B --> C[스캔 예상 결과 생성]

C --> D{예상 결과}

D -->|신규| E[신규 등록 예정]
D -->|기존| F[업데이트 예정]
D -->|동일| G[변경 없음 예정]
D -->|오류| H[오류 예상]

E --> I[미리보기 테이블 표시]
F --> I
G --> I
H --> I

I --> J[항목 선택]
J --> K[선택 항목 등록]
```

---

# 스캔 제어 흐름

```mermaid
flowchart LR

A[스캔 시작]

A --> B[작업 반복 처리]

B --> C{사용자 요청}

C -->|없음| D[다음 폴더 처리]
C -->|일시정지| E[현재 작업 완료 후 정지]
C -->|중지| F[스캔 중단]

E --> G[재개 대기]
G --> H[이어서 스캔]

H --> B
D --> B

B --> I{모든 작업 완료}
I -->|예| J[스캔 완료]
I -->|아니오| B
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
A --> C[작품 정보 표시]
A --> D[평점 표시]
A --> E[태그 표시]
A --> F[메모 표시]
A --> G[최근 로컬 작품 표시]
A --> H[누락 작품 표시]
A --> I[업데이트 이력 표시]
A --> J[참고 링크 표시]
A --> K[다운로드 메모 표시]

B --> L[수정]
C --> L
D --> L
E --> L
F --> L
J --> L
K --> L

L --> M[저장]
```

---

# 작가 상세 돌아가기 흐름

```mermaid
flowchart LR

A[작가 상세 진입]

A --> B[진입 전 페이지 저장]

B --> C{진입 경로}

C -->|대시보드| D[대시보드로 복귀]
C -->|작가 목록| E[작가 목록으로 복귀]
C -->|스캔| F[스캔으로 복귀]
C -->|업데이트 확인| G[업데이트 확인으로 복귀]
C -->|통계 분석| H[통계 분석으로 복귀]
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
J --> K[폴더 용량 갱신]
K --> L[작품 ID 갱신]
L --> M[업데이트 상태 갱신]

M --> N[완료]
```

---

# 누락 작품 생성 흐름

```mermaid
flowchart LR

A[업데이트 확인 결과]

A --> B[Pixiv 작품 ID]
A --> C[로컬 작품 ID]

B --> D[작품 ID 비교]
C --> D

D --> E[누락 작품 목록 생성]
E --> F[누락 작품 수 계산]
F --> G[상태 저장]
G --> H[상세 페이지 및 대시보드 표시]
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

G --> I[결과 저장]
H --> I

I --> J[업데이트 이력 저장]
J --> K[직전 결과 비교]
K --> L[신규 누락 계산]
K --> M[해결 작품 계산]

L --> N[결과 표시]
M --> N
```

---

# 다중 업데이트 확인 흐름

```mermaid id="k4xv9m"
flowchart LR

A[작가 다중 선택]

A --> B[업데이트 확인 시작]

B --> C[작가 반복 처리]

C --> D[최신 작품 조회]
D --> E[작품 ID 비교]
E --> F[상태 저장]
F --> G[이력 저장]
G --> H[결과 비교]

H --> I{다음 작가 존재}

I -->|예| C
I -->|아니오| J[결과 요약]

J --> K[완료]
```

---

# 업데이트 일시정지 / 재개 흐름

```mermaid id="j8r0sa"
flowchart LR

A[업데이트 확인 시작]

A --> B[작가 반복 처리]

B --> C{사용자 요청}

C -->|없음| D[다음 작가 확인]
C -->|일시정지| E[현재 작가 확인 완료 후 정지]
C -->|중단| F[업데이트 중단]

E --> G[재개 대기]
G --> H[이어서 확인]

H --> B
D --> B

B --> I{모든 작가 완료}
I -->|예| J[결과 요약]
I -->|아니오| B
```

---

# 업데이트 이력 비교 흐름

```mermaid id="m4zc5u"
flowchart LR

A[현재 업데이트 결과]

A --> B[직전 업데이트 결과 조회]

B --> C[누락 ID 비교]

C --> D[신규 누락 ID 계산]
C --> E[해결 ID 계산]
C --> F[누락 수 변화량 계산]

D --> G[이력 저장]
E --> G
F --> G

G --> H[상세 페이지 표시]
G --> I[대시보드 반영]
```

---

# 통계 분석 흐름

```mermaid id="3kk1nm"
flowchart LR

A[통계 페이지 진입]

A --> B[작가 데이터 조회]

B --> C[상태 분석]
B --> D[평점 분석]
B --> E[랭킹 분석]
B --> F[태그 분석]
B --> G[데이터 품질 분석]
B --> H[즐겨찾기 분석]

C --> I[통계 데이터 생성]
D --> I
E --> I
F --> I
G --> I
H --> I

I --> J[통계 페이지 표시]
```

---

# 상태 분포 분석 흐름

```mermaid id="1udk7g"
flowchart LR

A[작가 데이터 조회]

A --> B[업데이트 미확인]
A --> C[최신 상태]
A --> D[업데이트 필요]
A --> E[확인 실패]
A --> F[업데이트 완료]

B --> G[상태 집계]
C --> G
D --> G
E --> G
F --> G

G --> H[상태 분포 표시]
```

---

# 평점 분포 분석 흐름

```mermaid id="6prm9q"
flowchart LR

A[평점 데이터 조회]

A --> B[1~2점]
A --> C[3~4점]
A --> D[5~6점]
A --> E[7~8점]
A --> F[9~10점]

B --> G[분포 계산]
C --> G
D --> G
E --> G
F --> G

G --> H[평점 분포 표시]
```

---

# 랭킹 분석 흐름

```mermaid id="j7h3mt"
flowchart LR

A[작가 데이터 조회]

A --> B[작품 수 정렬]
A --> C[파일 수 정렬]
A --> D[저장 용량 정렬]

B --> E[작품 수 TOP]
C --> F[파일 수 TOP]
D --> G[저장 용량 TOP]

E --> H[통계 페이지 표시]
F --> H
G --> H
```

---

# 태그 분석 흐름

```mermaid id="p5ttmr"
flowchart LR

A[태그 데이터 조회]

A --> B[태그 수집]
B --> C[사용 횟수 계산]

C --> D[상위 태그 정렬]

D --> E[태그 분석 표시]
```

---

# 데이터 품질 분석 흐름

```mermaid id="q7ewpw"
flowchart LR

A[작가 데이터 조회]

A --> B[평점 설정 여부]
A --> C[태그 작성 여부]
A --> D[메모 작성 여부]
A --> E[폴더 오류 여부]

B --> F[비율 계산]
C --> F
D --> F
E --> F

F --> G[품질 통계 표시]
```

---

# 설정 저장 흐름

```mermaid id="4gh4xz"
flowchart LR

A[설정 변경]

A --> B[입력값 검증]
B --> C[설정 저장]

C --> D[설정 적용]

D --> E[완료]
```

---

# 설정 백업 흐름

```mermaid id="n1bg5t"
flowchart LR

A[설정 백업]

A --> B[설정 데이터 조회]
B --> C[JSON 생성]

C --> D[파일 저장]

D --> E[완료]
```

---

# 설정 복원 흐름

```mermaid id="96i1n2"
flowchart LR

A[설정 복원]

A --> B[백업 파일 선택]
B --> C[JSON 검증]

C --> D[설정 적용]

D --> E[설정 재로드]

E --> F[완료]
```

---

# DB 무결성 검사 흐름

```mermaid id="l4z0mq"
flowchart LR

A[무결성 검사 실행]

A --> B[작가 데이터 조회]

B --> C[중복 Pixiv ID 검사]
B --> D[폴더 존재 여부 검사]
B --> E[빈 작가명 검사]
B --> F[평점 검사]
B --> G[상태값 검사]

C --> H[결과 생성]
D --> H
E --> H
F --> H
G --> H

H --> I[결과 표시]
```

---

# DB 최적화 흐름

```mermaid id="5t1n1z"
flowchart LR

A[DB 최적화 실행]

A --> B[현재 크기 측정]

B --> C[VACUUM]
C --> D[ANALYZE]

D --> E[최적화 후 크기 측정]

E --> F[절감 용량 계산]

F --> G[결과 표시]
```

---

# 작가 삭제 흐름

```mermaid id="vr8nca"
flowchart LR

A[작가 선택]

A --> B[삭제 실행]
B --> C[삭제 확인]

C --> D[삭제 백업 생성]

D --> E[작가 삭제]
E --> F[업데이트 이력 삭제]

F --> G[완료]
```

---

# 삭제 작가 복구 흐름

```mermaid id="sd95qn"
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

```mermaid id="0ll7jz"
flowchart LR

A[DB 백업 실행]

A --> B[SQLite DB 확인]
B --> C[백업 파일 생성]

C --> D[백업 폴더 저장]

D --> E[완료]
```

---

# DB 복원 흐름

```mermaid id="1yfcux"
flowchart LR

A[DB 복원 실행]

A --> B[백업 파일 선택]
B --> C[DB 교체]

C --> D[설정 재로드]

D --> E[완료]
```

---

# CSV 내보내기 흐름

```mermaid id="h5e5nn"
flowchart LR

A[CSV 내보내기]

A --> B[작가 데이터 조회]
B --> C[CSV 생성]

C --> D[파일 저장]

D --> E[완료]
```

---

# 평점 일괄 변경 흐름

```mermaid id="xhmpys"
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

```mermaid id="zd9lmv"
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

```mermaid id="yotf1o"
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

```mermaid id="4wafrt"
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

```mermaid id="c5j6he"
flowchart LR

A[프로그램 종료]

A --> B[진행 중 작업 확인]
B --> C[업데이트 워커 종료]
C --> D[DB 연결 종료]

D --> E[종료]
```

---

# 주요 데이터 흐름

## 대시보드

```text id="s5n9e2"
Dashboard
→ ArtistService
→ ArtistUpdateHistoryRepository
→ Dashboard Metrics
→ Dashboard UI
```

---

## 통계 분석

```text id="7h09p5"
Statistics Page
→ StatisticsService
→ StatisticsStatusService
→ StatisticsRatingService
→ StatisticsRankingService
→ StatisticsTagService
→ StatisticsQualityService
→ StatisticsFavoriteService
→ Statistics UI
```

---

## 작가 등록

```text id="r8q1v7"
폴더 스캔
→ ArtistScanService
→ ArtistRepository
→ SQLite 저장
```

---

## 작가 수정

```text id="2v4jaf"
Artist Detail
→ ArtistService
→ ArtistRepository
→ SQLite 저장
```

---

## 업데이트 확인

```text id="5xv8cz"
Update Check Page
→ PixivUpdateService
→ ArtworkStatusService
→ ArtistUpdateService
→ ArtistUpdateHistoryRepository
→ ArtistRepository
→ SQLite 저장
```

---

## 업데이트 결과 비교

```text id="i72juh"
Update Result
→ ArtistUpdateHistoryRepository
→ Previous History
→ Comparison
→ History Save
→ Dashboard / Artist Detail
```

---

## 삭제 작가 복구

```text id="4xy3x8"
복구 실행
→ BackupService
→ ArtistRepository
→ SQLite 저장
```

---

## 폴더 변경

```text id="d8b2pk"
폴더 변경
→ FolderScanService
→ ArtworkStatusService
→ ArtistRepository
→ SQLite 저장
```

---

## 설정 저장

```text id="kt5x6o"
Settings Page
→ SettingsService
→ AppSettingRepository
→ SQLite 저장
```

---

## 설정 백업

```text id="2t3wih"
Settings Backup
→ SettingsBackupService
→ JSON Export
→ Backup File
```

---

## DB 무결성 검사

```text id="2y2frl"
Settings Page
→ DatabaseIntegrityService
→ ArtistRepository
→ Validation Result
→ Settings UI
```

---

## DB 최적화

```text id="jb2j7t"
Settings Page
→ DatabaseMaintenanceService
→ VACUUM
→ ANALYZE
→ Result
```

---

# 향후 확장 예정

## V2

```text id="vfrwb3"
설정 관리 고도화 완료
통계 분석 시스템 완료
3차 리팩토링
Pixiv 팔로우 / 북마크 관리
누락 기능 및 신규 기능 추가
```

---

## V3

```text id="hnw4gi"
작품 관리
작품 상세 정보
카드 보기
썸네일 보기
자체 뷰어
자동 업데이트
다운로드 큐
```

---

# 설계 원칙

## 1. UI → Service → Repository 구조 유지

```text id="axp1wf"
UI
→ Service
→ Repository
→ Database
```

---

## 2. UI 직접 DB 접근 금지

모든 데이터 처리는 Service를 통해 수행한다.

---

## 3. 기능 단위 모듈 분리

```text id="lxxd5f"
Artist
Scan
Update
Statistics
Backup
Settings
```

---

## 4. 통계 계산 UI 분리

```text id="2nqfrr"
Statistics UI
→ StatisticsService
→ Statistics Modules
```

---

## 5. Dashboard 계산 분리

```text id="7fxp3u"
Dashboard UI
→ Dashboard Metrics
→ Service Layer
```

---

## 6. 확장 우선 설계

신규 기능 추가 시 기존 구조 변경을 최소화한다.

---

# 버전 기준

본 문서는 v0.14.0 (통계 분석 시스템 완료) 기준으로 작성되었다.
