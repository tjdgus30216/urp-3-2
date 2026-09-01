# URP4-1 박사님 제출·인수인계 파일 안내 — 이 문서부터 읽어주세요

## 0. 이 파일은 무엇인가

이 ZIP은 박사님이 요청한 아래 두 항목을 전달하기 위한 **재현 가능한 연구 인수인계 패키지**입니다.

```text
4. 김우진
├─ 수정·구축한 알고리즘 모두
│  └─ 간단한 파일 설명 텍스트 추가
└─ 알고리즘 활용 결과 데이터
```

새 연구 계산을 추가한 최종 제품이 아니라, **현재까지 구현·검증한 코드와 결과, 한계, 재개 방법을 함께 묶은 제출본**입니다.

박사님이 먼저 열 파일은 아래 세 개입니다.

```text
URP4/
├─ 00_READ_ME_FIRST/README_FIRST.md
│  └─ 지금 읽고 있는 한국어 안내문
├─ 01_PROJECT_MAP_AND_LEDGER/URP4_1_HQ_PROJECT_MAP.html
│  └─ 전체 파이프라인·현재 상태·근거 파일을 연결한 프로젝트 지도
└─ 02_VERIFIED_CORE_HQ_NB_PY/00_RUNNABLE_HQ_AND_ENGINE/URP4_1_HQ.ipynb
   └─ 전체 파이프라인을 실행·제어하는 메인 Notebook(HQ)
```

ZIP 안의 **모든 파일 상대경로와 개별 설명**은 다음 부록에 있습니다.

- `00_READ_ME_FIRST/README_ALL_FILES_TREE_AND_DESCRIPTION_KO.md`
- `00_READ_ME_FIRST/ALL_FILES_DESCRIPTION_INDEX_KO.csv`
- `00_READ_ME_FIRST/ALL_FILES_DESCRIPTION_QA.json`

첫 번째는 사람이 읽는 트리, 두 번째는 검색·필터용 표, 세 번째는 누락·중복이 없는지 검사한 결과입니다.

---

## 1. ID·alias 읽는 법

아래 ID와 alias는 기존 연구 기록·코드·경로를 역추적하기 위해 **이름을 유지**했습니다. 처음 나올 때는 뜻을 괄호로 함께 적었습니다.

| ID / alias | 이 패키지에서의 뜻 |
|---|---|
| `HQ` | 전체 파이프라인을 실행·제어하는 메인 Notebook과 Python 엔진 |
| `LEGACY-PY` | 박사님·조교님이 원래 사용하던 검증 레거시 Python 코드 |
| `NB-ORIG` | 처음 받은 원본 통합 Notebook |
| `NB-CURRENT` | `LEGACY-PY`를 통합한 박사님 승인 기준 Notebook |
| `NB-DEV` | Import route controller를 개발·검증한 versioned development Notebook |
| `R09-SCRIPT` | 구조인자 검증·포렌식·실험을 위해 제작한 Python 스크립트군 |
| `XREG-v2.7` | 구조인자 후보은행(기존 구조인자 + 새로 추가한 구조인자 후보 542개) |
| `Training 1–5` | 박사님이 전달한 5가지 Feature Selection·Training 방법군 |
| `generated STL` | `NB-CURRENT` 또는 `HQ`가 직접 생성한 STL |
| `imported STL` | 외부에서 가져와 실제 실험 성능값 `y`와 연결하는 STL |
| `direct STEP` | 원본 STEP/STP B-rep 형상을 직접 slicing하는 경로 |
| `STRICT-STEP` | 원본 STEP direct 경로의 실행·검증 작업군 |
| `ROUTE-VALID` | STEP·controlled tessellation·imported STL 경로를 비교하고 정책을 검증한 작업군 |
| `COMP-FACTORY` | 압축시험 데이터 인입·x-y 결합·Feature Selection 파일럿 계산 파이프라인 |
| `FS4` | 네 가지 Feature Selection 방법을 동일한 계약에서 비교한 technical pilot |
| `OOF` | 학습에 사용하지 않은 fold에서 만든 out-of-fold 예측값 |
| `QA` | 결과·경로·해시·계약을 독립적으로 재검사한 품질검증 |
| `manifest` | 어떤 입력·설정·출력 파일을 사용했는지 고정한 목록과 SHA-256 기록 |
| `cutoff` | 이 제출본이 반영한 연구 상태의 기준 시점 |
| `schema` | 프로젝트 상태를 기계가 읽을 수 있게 정리한 데이터 구조 버전 |

역사적 경로명 `PROFESSOR_GENERATORS`, `PROFESSOR_TRAINING`, `06_PROFESSOR_DECISIONS_NEEDED`는 과거 패키지에서 만든 alias라 추적성을 위해 유지했습니다. **여기서 `PROFESSOR`는 교수님이 아니라 실제로 파일을 제공하고 이 제출물을 받는 박사님을 뜻하는 과거 내부 명칭**입니다. 새 설명문과 새 제출 파일명에서는 `박사님/DOCTOR`를 사용합니다.

---

## 2. 전체 연구 흐름과 현재 가능한 범위

```text
생성 파라미터 θ
→ Lattice / TPMS / Voxel geometry 생성
→ generated STL 사용 또는 STL/STP Import
→ slicing
→ pixel / connected component 분석
→ 구조인자 x 계산·저장
→ Feature Selection / Training 실험
→ 목표 성능 y*에서 구조를 찾는 역설계
```

| 기능 | 현재 상태 | 대표 파일 |
|---|---|---|
| Lattice / TPMS / Voxel 생성 | 기술 구현·실행 가능 | `02_VERIFIED_CORE_HQ_NB_PY/00_RUNNABLE_HQ_AND_ENGINE/URP4_1_HQ.ipynb` |
| generated STL 처리 | 실행 가능 | `02_VERIFIED_CORE_HQ_NB_PY/00_RUNNABLE_HQ_AND_ENGINE/urp4/` |
| imported STL 처리 | fail-closed 개발 경로 구현; 전체 production 검증 미완료 | `05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE/NB-INTEGRATE-001/` |
| direct STEP 처리 | C1에서 801 slices·800 overlays·구조인자 40개 완료 | `05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE/STRICT-STEP-026/` |
| LEGACY 구조인자 계산 | `LEGACY-PY` 기반 계산·검증 자료 포함 | `02_VERIFIED_CORE_HQ_NB_PY/02_PROTECTED_REFERENCES_READ_ONLY/LEGACY-PY/` |
| 구조인자 후보 확장 | `XREG-v2.7`(기존 + 신규 구조인자 후보 542개), no-y·unselected | `05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE/XREG-v2.7/` |
| Feature Selection / Training | 원본 9개 audit; 일부 replay·technical pilot 완료 | `06_TRAINING_EVIDENCE/` |
| 압축 데이터 활용 | AI Lattice·B/C/L·Voronoi x-y 결합과 기술 파일럿 완료 | `07_COMPRESSION_DATA_AND_PILOT/` |
| 전체 역설계 `y* → x* → θ*` | 아직 과학적으로 검증되지 않음 | `09_LIMITATIONS_AND_RESUME/KNOWN_LIMITATIONS_AND_BLOCKERS.md` |

따라서 이 패키지는 **후속 계산을 그대로 재개하는 기술 인수인계본**이며, 성능이 검증된 최종 역설계 제품은 아닙니다.

---

## 3. 메인 Notebook과 Python 코드의 관계

```text
02_VERIFIED_CORE_HQ_NB_PY/
├─ 00_RUNNABLE_HQ_AND_ENGINE/
│  ├─ URP4_1_HQ.ipynb
│  │  └─ 메인 실행 Notebook(HQ): 설정·단계·실행 순서를 제어
│  ├─ URP4_1_HQ_BLUEPRINT_v0_2.ipynb
│  │  └─ 향후 21-cell 전체 구조 설계
│  ├─ urp4/
│  │  └─ geometry·Import·slicing·구조인자 계산을 수행하는 Python 엔진
│  ├─ config/ · configs/
│  │  └─ 실행 설정과 frozen contract
│  ├─ tests/
│  │  └─ contract·smoke·회귀검증
│  └─ README_RUN.md
│     └─ 실제 실행 순서
│
├─ 01_EXPERIMENTAL_TRAINING_ADAPTER/
│  └─ Training 원본 수치 branch를 이식한 실험 adapter; production 통합 아님
│
├─ 02_PROTECTED_REFERENCES_READ_ONLY/
│  ├─ LEGACY-PY/             ─ 검증 레거시 Python 코드
│  ├─ NB-ORIG/               ─ 처음 받은 원본 통합 Notebook
│  ├─ NB-CURRENT/            ─ 박사님 승인 기준 Notebook
│  ├─ NB-DEV/                ─ Import route controller 개발 Notebook
│  ├─ PROFESSOR_GENERATORS/  ─ 박사님 제공 generator Notebook(과거 alias 유지)
│  └─ PROFESSOR_TRAINING/    ─ 박사님 제공 Training 1–5 원본(과거 alias 유지)
│
└─ 03_RESUMABLE_PROJECT_SNAPSHOT/
   └─ 후속 담당자가 실제 계산을 재개하는 코드·설정·최소 입력·runbook
```

`URP4_1_HQ.ipynb`가 실행을 조직하고 실제 계산은 주로 `urp4/`의 `.py`가 수행합니다. 다만 패키지의 모든 `.py`가 HQ에서 자동 실행되는 것은 아닙니다. `R09-SCRIPT`, `STRICT-STEP`, `ROUTE-VALID`, `IMSTL`, `PRM`, Training 관련 스크립트는 검증·포렌식·별도 계산용이며, 정확한 역할은 전수 파일 설명 부록과 `ALGORITHM_FILE_INDEX.csv`에 있습니다.

---

## 4. 박사님이 10분 안에 보는 순서

1. `00_READ_ME_FIRST/README_FIRST.md`
2. `01_PROJECT_MAP_AND_LEDGER/URP4_1_HQ_PROJECT_MAP.html`
3. `01_PROJECT_MAP_AND_LEDGER/URP4_1_MASTER_HANDOFF_LEDGER.xlsx`
4. `02_VERIFIED_CORE_HQ_NB_PY/00_RUNNABLE_HQ_AND_ENGINE/URP4_1_HQ.ipynb`
5. 관심 결과만 아래 폴더에서 확인

```text
URP4/
├─ 05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE/
│  ├─ STRICT-STEP-026/       ─ C1 direct STEP 계산·검증
│  ├─ NB-INTEGRATE-001/      ─ imported STL route controller 근거
│  ├─ ROUTE-VALID-003/       ─ 세 경로 비교 근거
│  ├─ ROUTE-VALID-004/       ─ source type별 route 정책
│  ├─ XREG-v2.7/             ─ 구조인자 후보은행(기존 + 신규 후보)
│  └─ L28-DESCVAL/           ─ L28 구조인자 검증
├─ 06_TRAINING_EVIDENCE/
│  ├─ TRAIN-AUDIT-001/       ─ Training 원본 9개 구조 감사
│  ├─ TRAIN-REPLAY-001/      ─ 원본 Notebook replay
│  └─ TRAIN-PARITY-001~004/  ─ adapter·parity 검증과 native crash 근거
└─ 07_COMPRESSION_DATA_AND_PILOT/
   ├─ COMP-FACTORY-001/      ─ AI Lattice 압축 데이터 인입
   ├─ COMP-FACTORY-002/      ─ AI Lattice 4-method pilot
   ├─ COMP-FACTORY-004_BCL/  ─ B/C/L grouped pilot
   ├─ COMP-FACTORY-004_VORONOI/ ─ Voronoi grouped pilot
   └─ COMP-FACTORY-004_PIPELINE_SOURCE/ ─ 압축 데이터 계산 재개용 Python 코드
```

대표 결과:

- `STRICT-STEP-026`(C1 원본 STEP direct 구조인자 계산): 801/801 slices, 800/800 overlays, `LEGACY-PY` 구조인자 40개, 독립 QA 9/9 PASS.
- `XREG-v2.7`(기존 + 신규 구조인자 후보은행): 후보 542개, no-y·unselected.
- `Training 1–5`(박사님 제공 Feature Selection·Training 방법군): 원본 9개 audit 9/9, replay 1/9; 수치 parity는 native crash로 `blocked_with_evidence`.
- `AI Lattice` 압축 데이터: exact x-y join 149개, technical pilot 완료, feature/model 승격 없음.
- `B/C/L + Voronoi` 압축 데이터: exact x-y join 167개, grouped OOF 10,688개, QA-v2 `PASS_WITH_WARNINGS`, feature/model 승격 없음.

---

## 5. 후속 담당자가 계산을 재개하는 순서

1. ZIP을 `C:\URP4_RESUME\` 같은 짧은 경로에 압축 해제합니다.
2. `02_VERIFIED_CORE_HQ_NB_PY/03_RESUMABLE_PROJECT_SNAPSHOT/RESUME_RUNBOOK.md`를 읽습니다.
3. `03_CONFIG_RUNTIME_AND_COMMANDS/README_PORTABLE_REPRODUCTION.md`를 읽습니다.
4. `KMK312`(Python 3.12.12) 환경을 연결합니다.
5. 다음 read-only 검증기를 먼저 실행합니다.

```text
02_VERIFIED_CORE_HQ_NB_PY/
└─ 03_RESUMABLE_PROJECT_SNAPSHOT/
   └─ 00_VERIFY_RESUMABLE_HANDOFF.py
```

검증 통과 후 새 `run_id`와 새 결과 폴더에서만 계산을 재개합니다. 기존 결과는 덮어쓰지 않습니다.

---

## 6. 최상위 폴더 구조

```text
URP4/
├─ 00_READ_ME_FIRST/                     ─ 시작 안내·alias 풀이·모든 파일 설명
├─ 01_PROJECT_MAP_AND_LEDGER/            ─ 전체 지도·상태·근거·파일 원장
├─ 02_VERIFIED_CORE_HQ_NB_PY/            ─ HQ·Python 엔진·원본 Notebook·재개 snapshot
├─ 03_CONFIG_RUNTIME_AND_COMMANDS/       ─ KMK312·Python·실행 명령·환경 설정
├─ 04_REFERENCE_INPUTS/                  ─ 참조 Excel·압축시험 입력·geometry Drive 위치
├─ 05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE/ ─ geometry·slicing·구조인자 결과와 QA
├─ 06_TRAINING_EVIDENCE/                 ─ Training audit·replay·parity 결과
├─ 07_COMPRESSION_DATA_AND_PILOT/        ─ 압축 데이터 코드·결과·QA
├─ 08_OPTIONAL_UI_DEMO/                  ─ 선택 사항인 UI demo; 과학적 역설계 검증 아님
├─ 09_LIMITATIONS_AND_RESUME/            ─ 미완료·차단·다음 gate·과거 연구 로그
├─ 10_MANIFEST_SHA256_AND_QA/            ─ 파일 무결성·SHA-256·패키지 QA
└─ SOURCE_CUTOFF_SNAPSHOT/               ─ 과거 cutoff 보존본; 현재 상태가 아님
```

현재 상태를 볼 때 사용하는 authority:

- 기계가 읽는 현재 상태: `01_PROJECT_MAP_AND_LEDGER/PROJECT_SCHEMA.json`
- 사람이 보는 전체 상태: `01_PROJECT_MAP_AND_LEDGER/URP4_1_HQ_PROJECT_MAP.html`
- 작업·근거 원장: `01_PROJECT_MAP_AND_LEDGER/URP4_1_MASTER_HANDOFF_LEDGER.xlsx`
- 미완료·차단 사항: `09_LIMITATIONS_AND_RESUME/KNOWN_LIMITATIONS_AND_BLOCKERS.md`
- 모든 파일 설명: `00_READ_ME_FIRST/README_ALL_FILES_TREE_AND_DESCRIPTION_KO.md`
- 파일 무결성: `10_MANIFEST_SHA256_AND_QA/PACKAGE_CONTENT_SHA256.csv`

`SOURCE_CUTOFF_SNAPSHOT/`, `10_MANIFEST_SHA256_AND_QA/attempts/`, 과거 `PACKAGE_REVISION_*` 파일은 현재 상태가 아니라 과거 판단·실패·수정 이력을 보존한 근거입니다.

---

## 7. 박사님 요구사항과 대응 위치

| 박사님 요구 | 패키지 내 위치 |
|---|---|
| 수정·구축한 알고리즘 모두 | `02_VERIFIED_CORE_HQ_NB_PY/` 및 `07_COMPRESSION_DATA_AND_PILOT/COMP-FACTORY-004_PIPELINE_SOURCE/` |
| 알고리즘 간단 설명 | `00_READ_ME_FIRST/ALGORITHM_AND_RESULT_GUIDE_KO.txt` |
| 코드별 파일 목록·SHA | `00_READ_ME_FIRST/ALGORITHM_FILE_INDEX.csv` |
| 파이프라인 입력·출력·재개점 | `00_READ_ME_FIRST/ALGORITHM_PIPELINE_INDEX.csv` |
| 모든 파일의 상대경로·개별 설명 | `00_READ_ME_FIRST/README_ALL_FILES_TREE_AND_DESCRIPTION_KO.md` |
| 모든 파일 설명 검색표 | `00_READ_ME_FIRST/ALL_FILES_DESCRIPTION_INDEX_KO.csv` |
| 알고리즘 활용 결과 | `05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE/`, `06_TRAINING_EVIDENCE/`, `07_COMPRESSION_DATA_AND_PILOT/` |
| 전체 상태·근거 연결 | `01_PROJECT_MAP_AND_LEDGER/URP4_1_HQ_PROJECT_MAP.html` |

---

## 8. 버전·검증 범위·금지 주장

- 현재 박사님 제출본: `URP4-1_DOCTOR_HANDOFF_20260802_v1_4_r2`
- 연구 상태 cutoff: `HANDOFF-CUTOFF-20260802-002`
- 프로젝트 schema: `PROJECT_SCHEMA v1.3`
- `v1.4-r2`는 alias 풀이·전수 파일 설명·박사님 용어와 QA 버전 표기를 정비한 packaging revision입니다. 새 연구 계산이나 과학 결론은 추가하지 않았습니다.

아직 확정되지 않은 항목:

- imported STL 전체 58모델 production qualification
- F1 z400 원인 해결
- Training 전체 9개 numerical parity
- 최적 feature·최적 model 확정
- 성능이 검증된 최적 구조 생성
- 전체 `y* → x* → θ*` 역설계 성공

이 한계는 실패를 숨긴 것이 아니라, 다음 작업의 정확한 시작점을 남기기 위해 그대로 기록했습니다.
