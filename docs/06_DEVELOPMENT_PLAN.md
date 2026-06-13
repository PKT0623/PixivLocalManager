# 개발 계획 (Development Plan)

## 개발 전략

<table>
<tr>
    <th>항목</th>
    <th>내용</th>
</tr>
<tr>
    <td>개발 방식</td>
    <td>기능 단위 순차 개발</td>
</tr>
<tr>
    <td>우선순위</td>
    <td>데이터 → 기능 → UI → 편의 기능</td>
</tr>
<tr>
    <td>목표</td>
    <td>V1 완성 후 V2 진행</td>
</tr>
<tr>
    <td>원칙</td>
    <td>작동하는 기능부터 구현</td>
</tr>
</table>

---

## 전체 개발 흐름

```mermaid
flowchart LR

PLAN[설계]

PLAN --> DATABASE[DB 구축]

DATABASE --> CORE[핵심 기능]

CORE --> UI[UI 구현]

UI --> TEST[테스트]

TEST --> RELEASE[V1 완료]
```

---

## Phase 1 - 프로젝트 기반 구축

<table>
<tr>
    <th>ID</th>
    <th>작업</th>
    <th>상태</th>
</tr>

<tr>
    <td>P1-01</td>
    <td>프로젝트 구조 생성</td>
    <td>완료</td>
</tr>

<tr>
    <td>P1-02</td>
    <td>Git 저장소 구성</td>
    <td>완료</td>
</tr>

<tr>
    <td>P1-03</td>
    <td>가상환경 구성</td>
    <td>완료</td>
</tr>

<tr>
    <td>P1-04</td>
    <td>문서 작성</td>
    <td>진행중</td>
</tr>

</table>

---

## Phase 2 - 데이터 계층

<table>
<tr>
    <th>ID</th>
    <th>작업</th>
    <th>상태</th>
</tr>

<tr>
    <td>P2-01</td>
    <td>SQLite 연결</td>
    <td>예정</td>
</tr>

<tr>
    <td>P2-02</td>
    <td>DB 초기화 코드 작성</td>
    <td>예정</td>
</tr>

<tr>
    <td>P2-03</td>
    <td>artists 테이블 생성</td>
    <td>예정</td>
</tr>

<tr>
    <td>P2-04</td>
    <td>app_settings 테이블 생성</td>
    <td>예정</td>
</tr>

<tr>
    <td>P2-05</td>
    <td>DB CRUD 구현</td>
    <td>예정</td>
</tr>

</table>

---

## Phase 3 - 작가 관리

<table>
<tr>
    <th>ID</th>
    <th>작업</th>
    <th>상태</th>
</tr>

<tr>
    <td>P3-01</td>
    <td>폴더 선택 기능</td>
    <td>예정</td>
</tr>

<tr>
    <td>P3-02</td>
    <td>폴더 스캔 기능</td>
    <td>예정</td>
</tr>

<tr>
    <td>P3-03</td>
    <td>작가명-ID 파싱</td>
    <td>예정</td>
</tr>

<tr>
    <td>P3-04</td>
    <td>작가 등록 기능</td>
    <td>예정</td>
</tr>

<tr>
    <td>P3-05</td>
    <td>작가 수정 기능</td>
    <td>예정</td>
</tr>

<tr>
    <td>P3-06</td>
    <td>작가 삭제 기능</td>
    <td>예정</td>
</tr>

</table>

---

## Phase 4 - 작품 관리

<table>
<tr>
    <th>ID</th>
    <th>작업</th>
    <th>상태</th>
</tr>

<tr>
    <td>P4-01</td>
    <td>최신 작품 ID 계산</td>
    <td>예정</td>
</tr>

<tr>
    <td>P4-02</td>
    <td>Pixiv 최신 작품 입력</td>
    <td>예정</td>
</tr>

<tr>
    <td>P4-03</td>
    <td>업데이트 상태 계산</td>
    <td>예정</td>
</tr>

<tr>
    <td>P4-04</td>
    <td>작품 링크 열기</td>
    <td>예정</td>
</tr>

</table>

---

## Phase 5 - 데이터 관리

<table>
<tr>
    <th>ID</th>
    <th>작업</th>
    <th>상태</th>
</tr>

<tr>
    <td>P5-01</td>
    <td>CSV 내보내기</td>
    <td>예정</td>
</tr>

<tr>
    <td>P5-02</td>
    <td>JSON 백업</td>
    <td>예정</td>
</tr>

<tr>
    <td>P5-03</td>
    <td>JSON 복원</td>
    <td>예정</td>
</tr>

</table>

---

## Phase 6 - UI 구현

<table>
<tr>
    <th>ID</th>
    <th>작업</th>
    <th>상태</th>
</tr>

<tr>
    <td>P6-01</td>
    <td>메인 창 구성</td>
    <td>예정</td>
</tr>

<tr>
    <td>P6-02</td>
    <td>사이드바 구성</td>
    <td>예정</td>
</tr>

<tr>
    <td>P6-03</td>
    <td>대시보드 구현</td>
    <td>예정</td>
</tr>

<tr>
    <td>P6-04</td>
    <td>작가 목록 화면</td>
    <td>예정</td>
</tr>

<tr>
    <td>P6-05</td>
    <td>작가 상세 화면</td>
    <td>예정</td>
</tr>

<tr>
    <td>P6-06</td>
    <td>설정 화면</td>
    <td>예정</td>
</tr>

</table>

---

## Phase 7 - 테스트

<table>
<tr>
    <th>ID</th>
    <th>작업</th>
    <th>상태</th>
</tr>

<tr>
    <td>P7-01</td>
    <td>대량 폴더 테스트</td>
    <td>예정</td>
</tr>

<tr>
    <td>P7-02</td>
    <td>DB 테스트</td>
    <td>예정</td>
</tr>

<tr>
    <td>P7-03</td>
    <td>UI 테스트</td>
    <td>예정</td>
</tr>

<tr>
    <td>P7-04</td>
    <td>백업 복원 테스트</td>
    <td>예정</td>
</tr>

</table>

---

## V1 완료 조건

<table>
<tr>
    <th>항목</th>
    <th>조건</th>
</tr>

<tr>
    <td>작가 등록</td>
    <td>정상 동작</td>
</tr>

<tr>
    <td>작가 검색</td>
    <td>정상 동작</td>
</tr>

<tr>
    <td>최신 작품 확인</td>
    <td>정상 동작</td>
</tr>

<tr>
    <td>CSV 내보내기</td>
    <td>정상 동작</td>
</tr>

<tr>
    <td>JSON 백업 및 복원</td>
    <td>정상 동작</td>
</tr>

<tr>
    <td>EXE 빌드</td>
    <td>정상 실행</td>
</tr>

</table>

---

## 현재 진행 상태

<table>
<tr>
    <th>문서</th>
    <th>상태</th>
</tr>

<tr>
    <td>01_PROJECT_OVERVIEW</td>
    <td>완료</td>
</tr>

<tr>
    <td>02_REQUIREMENTS</td>
    <td>완료</td>
</tr>

<tr>
    <td>03_SYSTEM_FLOW</td>
    <td>완료</td>
</tr>

<tr>
    <td>04_DATABASE</td>
    <td>완료</td>
</tr>

<tr>
    <td>05_UI_DESIGN</td>
    <td>완료</td>
</tr>

<tr>
    <td>06_DEVELOPMENT_PLAN</td>
    <td>작성중</td>
</tr>

</table>
