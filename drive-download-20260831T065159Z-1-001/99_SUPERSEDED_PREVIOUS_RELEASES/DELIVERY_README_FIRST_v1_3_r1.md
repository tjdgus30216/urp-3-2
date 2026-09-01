# URP4-1 교수님 전달본 v1.3-r1

## 교수님께 보낼 파일

- `URP4-1_PROFESSOR_HANDOFF_20260802_v1_3_r1.zip`
- Drive: https://drive.google.com/file/d/1gsQf33MDYchw8VxAxoMk7fuSzPnExyAh/view?usp=drivesdk
- SHA-256: `dd9e4bf7961e5dbdfa05af1d4b8c0a671dbb01c46672b7ac119fc9864b6e0a34`
- Cutoff/schema: `HANDOFF-CUTOFF-20260802-002 / PROJECT_SCHEMA v1.3`

## 이 버전의 목적

박사님 요청인 `수정/구축한 알고리즘 모두 + 간단한 파일 설명 + 알고리즘 활용 결과 데이터`를, 후속 담당자가 실제 계산을 재개할 수 있는 범위로 선별한 제출본이다. 과거 실패본·superseded 중간본·cache·중복 대형 파일은 제외했다.

압축을 푼 뒤 다음 순서로 읽는다.

1. `URP4/00_READ_ME_FIRST/README_FIRST.md`
2. `URP4/00_READ_ME_FIRST/ALGORITHM_AND_RESULT_GUIDE_KO.txt`
3. `URP4/00_READ_ME_FIRST/ALGORITHM_PIPELINE_INDEX.csv`
4. `URP4/02_VERIFIED_CORE_HQ_NB_PY/00_RUNNABLE_HQ_AND_ENGINE/README_RUN.md`
5. `URP4/02_VERIFIED_CORE_HQ_NB_PY/03_RESUMABLE_PROJECT_SNAPSHOT/RESUME_RUNBOOK.md`

## 현재 안내서와 역사 보존 문서의 구분

현재 v1.3 기준 안내서는 위의 다섯 파일과 다음 두 index다.

- `URP4/00_READ_ME_FIRST/ALGORITHM_FILE_INDEX.csv`
- `URP4/01_PROJECT_MAP_AND_LEDGER/URP4_1_MASTER_HANDOFF_LEDGER.xlsx`

`SOURCE_CUTOFF_SNAPSHOT/`, `10_MANIFEST_SHA256_AND_QA/attempts/`, 파일명이 `R2_` 또는 `PACKAGE_REVISION_v1_1/v1_2`인 문서는 이전 cutoff와 감사 과정을 증거로 보존한 자료다. 그 안의 v1.1/v1.2, running, pending 표기를 현재 상태로 해석하지 않는다.

## 내부 디렉터리 구조

```text
URP4/
├─ 00_READ_ME_FIRST/                     현재 설명과 알고리즘 index
├─ 01_PROJECT_MAP_AND_LEDGER/             프로젝트 지도·원장·근거 index
├─ 02_VERIFIED_CORE_HQ_NB_PY/             실행 HQ·Python 엔진·재개 snapshot
├─ 03_CONFIG_RUNTIME_AND_COMMANDS/        KMK312 환경·명령·portable 설정
├─ 04_REFERENCE_INPUTS/                   참조 Excel·geometry pointer
├─ 05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE/ 구조인자·geometry 검증 근거
├─ 06_TRAINING_EVIDENCE/                  Training 원본·adapter·차단 근거
├─ 07_COMPRESSION_DATA_AND_PILOT/         AI Lattice·B/C/L·Voronoi 코드와 결과
├─ 08_OPTIONAL_UI_DEMO/                   검증 범위를 분리한 선택적 UI demo
├─ 09_LIMITATIONS_AND_RESUME/             미완료 gate와 재개 경계
├─ 10_MANIFEST_SHA256_AND_QA/             해시·manifest·패키지 QA
└─ SOURCE_CUTOFF_SNAPSHOT/                과거 cutoff read-only 증거
```

## 핵심 포함 범위

- HQ/NB 및 Python 엔진
- C1 direct STEP 계산·QA
- imported STL/STEP route 검증 코드와 근거
- SLICE-004/XREG 후보 생성·QA 파이프라인과 검증된 raw table archive
- resolution/slice optimization 파이프라인
- Training 원본·adapter·parity 근거
- AI Lattice, B/C/L, Voronoi 압축 데이터 intake·grouped pilot 코드와 결과
- manifest, SHA-256, config, runtime, 재개 검증기

## 해석 경계

이 파일은 재현 가능한 기술 인수인계본이다. imported STL 전체 production qualification, Training 전체 numerical parity, 최적 feature/model, 검증된 inverse design 완료를 주장하지 않는다.

## 별도 Drive 자산

- geometry archive: https://drive.google.com/file/d/19yIGDRtUWQPRmaV3WyQvBa5S-QZgxpYh/view?usp=drivesdk
- compression source 11 workbooks: https://drive.google.com/drive/folders/1XR1xMdQC9ePp_aWe-wsZB-kfYuGJRcmg

현재 공유 상태는 `not_shared`다. Chuck이 교수님의 검증된 Google 계정을 Viewer로 추가해야 한다.
