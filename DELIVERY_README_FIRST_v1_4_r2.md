# URP4-1 박사님 전달 파일 안내

박사님께 보내는 최종 연구 인수인계본은 아래 ZIP 하나입니다.

## 1. 최종 ZIP

- 파일명: `URP4-1_DOCTOR_HANDOFF_20260802_v1_4_r2.zip`
- Google Drive: https://drive.google.com/file/d/1VX2VdeuIBRDSOb07dpDpWAxSXu8vySUH/view?usp=drivesdk
- SHA-256: `8c3d5b0c706abcc57eab36cc7070a1d07ad94177c8fc72d4c55b4c1ad99d958e`
- 연구 상태 cutoff: `HANDOFF-CUTOFF-20260802-002`
- 프로젝트 schema: `PROJECT_SCHEMA v1.3`

이 ZIP에는 박사님이 요청한 **수정·구축 알고리즘, 간단한 파일 설명, 알고리즘 활용 결과 데이터**가 들어 있습니다.

## 2. ZIP을 연 뒤 읽는 순서

```text
URP4/
├─ 00_READ_ME_FIRST/README_FIRST.md
│  └─ 한국어 전체 안내와 ID·alias 풀이
├─ 00_READ_ME_FIRST/README_ALL_FILES_TREE_AND_DESCRIPTION_KO.md
│  └─ ZIP 안 모든 파일의 상대경로 트리와 개별 설명
├─ 01_PROJECT_MAP_AND_LEDGER/URP4_1_HQ_PROJECT_MAP.html
│  └─ 전체 파이프라인·현재 상태·근거 파일 지도
├─ 01_PROJECT_MAP_AND_LEDGER/URP4_1_MASTER_HANDOFF_LEDGER.xlsx
│  └─ 작업·상태·근거·다음 gate를 검색하는 종합 원장
└─ 02_VERIFIED_CORE_HQ_NB_PY/00_RUNNABLE_HQ_AND_ENGINE/URP4_1_HQ.ipynb
   └─ 전체 pipeline을 실행·제어하는 메인 Notebook(HQ)
```

`XREG-v2.7` 같은 ID·alias는 기존 코드·로그와의 역추적을 위해 유지하되 README에서 바로 뜻을 설명합니다. 예: `XREG-v2.7 구조인자 후보은행(기존 구조인자 + 새로 추가한 구조인자 후보 542개)`.

과거 경로명 `PROFESSOR_GENERATORS`, `PROFESSOR_TRAINING`은 파일 provenance를 깨지 않기 위해 남긴 역사적 alias입니다. 실제 파일 제공자와 제출 수신자는 모두 박사님이며, 새 제출본 이름과 현재 설명은 `박사님/DOCTOR`를 사용합니다.

## 3. 별도 대형 자산

- 전체 전달 폴더: https://drive.google.com/drive/folders/1ofJz1N5ycdijVTuNtpeGn0xben08WWV0
- geometry 67파일 archive: https://drive.google.com/file/d/19yIGDRtUWQPRmaV3WyQvBa5S-QZgxpYh/view?usp=drivesdk
- 압축시험 원본 Excel 11개 폴더: https://drive.google.com/drive/folders/1XR1xMdQC9ePp_aWe-wsZB-kfYuGJRcmg

대형 geometry와 원본 압축 Excel은 중복을 막기 위해 ZIP 안에 다시 넣지 않고, manifest·SHA와 Drive 위치만 연결했습니다.

## 4. 검증 상태

- ZIP CRC/testzip: PASS
- ZIP member: 1,147개
- package manifest: 1,146/1,146 PASS
- 모든 파일 개별 설명: 1,147/1,147 PASS, 누락 0, 중복 0
- Python AST: 259/259 PASS
- 재개 코드 index: 161/161 경로·SHA PASS
- frozen raw table archive: 469/469 PASS
- read-only resume verifier: PASS
- 최종 판정: `FINAL_HANDOFF_RELEASE_READY_V1_4_R2`

## 5. 과학적 범위

이 제출본은 후속 계산을 재개할 수 있는 기술 인수인계본입니다. imported STL 전체 production 검증, Training 9개 전체 numerical parity, 최적 feature/model, 성능이 검증된 `y* → x* → θ*` 역설계 성공을 주장하지 않습니다.

## 6. 공유 권한

현재 Drive 파일은 공개 링크가 아닙니다. 전달 전에 Chuck이 박사님 Google 계정에 **Viewer 권한**을 부여해야 합니다.
