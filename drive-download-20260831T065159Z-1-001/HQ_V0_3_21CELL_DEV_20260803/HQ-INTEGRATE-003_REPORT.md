# HQ-INTEGRATE-003 — 21셀 HQ v0.3 개발 통합 감사

- 작업일: 2026-08-03 (KST)
- runtime: project-local tools/envs/KMK312/python.exe / Python 3.12.12
- 상태: development integration passed; scientific production qualification is not granted.
- 보호 대상: URP4_1_HQ.ipynb, urp4/hq/v0_1/, v0.2 기존 파일, NB-CURRENT/ORIG, LEGACY-PY, 원본 Excel·geometry를 수정하지 않았다.
- smoke 실행 산출물: URP4-1_DELIVERABLE/outputs/hq_v03_smoke/ — 코드 검증 격리물이며 제출·과학 근거가 아니다.

## 1. Source-level 감사 결론

| 대상 | 실제 역할 | v0.3 처리 |
|---|---|---|
| URP4_1_HQ.ipynb (13셀) | 기존 제출 HQ. Cell 4가 run_hq()로 전체 route 실행 | 수정하지 않음; 실제 v0.1 엔진 재사용 |
| urp4/hq/v0_1/controller.py | strict contract / control 정의 | 재사용 |
| urp4/hq/v0_1/engine.py | geometry, manifest, 전체 실행 엔진 | 필요한 실제 helper만 재사용 |
| urp4/hq/v0_1/imported_pipeline.py | imported STL winding image/pixel route | 재사용 |
| URP4_1_HQ_v0_2_CONTROLLED_DEV.ipynb (10셀) | Frozen replay, exploratory smoke 검증용 개발본 | 수정하지 않음; 최종 21셀 구조에는 부족 |
| urp4/hq/v0_2/control.py | 실제 v0.2 config validation / mode guard | 재사용 |
| urp4/hq/v0_2/direct_aggregation.py | exploratory direct scalar calculation | 재사용 |
| urp4/hq/v0_2/models.py, runtime.py | status-only Blueprint, actual image/descriptor engine 아님 | 충돌 방지를 위해 수정·병합하지 않음 |
| 새 urp4/hq/v0_3/stage_runtime.py | 각 HQ cell가 순차 호출하는 stage API | 새 versioned development implementation |
| 새 URP4_1_HQ_v0_3_21CELL_DEV.ipynb | 21 code cells, cell-by-cell visible route | 새 versioned development notebook |

Git repository metadata가 이 workspace에 없어 이전 commit 이력은 감사할 수 없었다. 판단은 실제 source 내용, notebook JSON, file SHA-256 및 KMK312 실행 결과에 근거한다.

## 2. 21셀 구현 지도

| Cell | 기능 | 실제 호출/결과 | 상태 |
|---|---|---|---|
| 01 | 사용자 설정 | URP4Controller + HQV02Controller | 입력 계약 |
| 02 | config freeze | HQStageSession.create, validate_v02 또는 STEP inventory contract | 구현 |
| 03 | stage/route 상태 | stage_route_status() | 구현 |
| 04 | source inventory | Frozen table hash / STL SHA / STEP inventory | 구현 |
| 05 | geometry generation/import | v0.1 generated geometry 또는 immutable STL import | STL만 구현 |
| 06 | normalization | imported winding normalization contract | imported route에서 Cell 08 실행 |
| 07 | geometry QA | inspect_source preflight | 구현 |
| 08 | slicing | 실제 image/mask/PNG readback extraction | STL만 구현 |
| 09 | pixel/component | 실제 primitive table status | STL만 구현 |
| 10 | LEGACY descriptor | direct XRV1-F001–F008, 9 scalar rows | 구현 |
| 11 | XREG candidate factory | XREG-v2.7 HQ API 부재 | fail-closed |
| 12 | descriptor QA | finite/direct/image QA | 구현 |
| 13 | full X export | direct 9-row export | partial; XREG blocked |
| 14–19 | y/FS/Training/model/forward/inverse | 검증된 HQ engine 없음 | fail-closed |
| 20 | export/manifest | current v0.3 run manifest | 구현 |
| 21 | final gate | development-only boundary 기록 | 구현; production release 아님 |

## 3. Validation

1. Frozen replay parity: 기존 primitive table에서 v0.3가 direct scalar를 재계산했다. 기존 v0.1 scalar와 maximum absolute error는 0.0이다.
2. ARTIFACT_FULL ↔ STREAMING parity: P128/Z9 exploratory smoke에서 slice pixel, overlay pixel, overlay component tables가 각각 exact equality이고 9 scalar maximum absolute error는 0.0이다.
3. STRICT existing regression: 동일 generated STL과 P1000/Z801 strict route를 실제 실행했다. 기존 v0.1 reference run과 9 scalar maximum absolute error는 0.0이다. 새 strict run은 약 515.6초가 걸렸다. 이 run은 code regression evidence이며 legacy/Excel scientific parity의 새로운 증거가 아니다.
4. Exploratory route: P128/Z9에서 실제 image/pixel/component extraction을 수행했고 output state가 experimental임을 확인했다.
5. STEP/STP: tests/fixtures/L28_UBCCz_VF30_original.stp를 inventory route로 만들고 Cell 04–06가 direct descriptor를 실행하지 않고 blocked 처리하는 것을 확인했다.
6. XREG/y/Training/forward/inverse: API 또는 검증된 engine 없이 실행되지 않고 fail-closed임을 확인했다.

## 4. 다음 담당자 재개 지점

- HQ 21셀의 구현 범위는 Cell 01–13, 20–21이며 direct 9-scalar lane까지만 실제 계산한다.
- XREG를 HQ에 넣으려면 XREG factory API contract와 parity/QA가 필요하다.
- y/Feature Selection/Training/forward/inverse는 source training code와 data contract를 검증한 뒤 Cell 14–19에 별도 stage engine으로 편입해야 한다.
- STEP/STP direct descriptor는 current route에서 구현하지 않는다. 별도 direct B-rep slicing qualification이 필요하다.
- outputs/hq_v02_smoke/와 outputs/hq_v03_smoke/를 submission/scientific evidence로 편입하지 않는다.

## 5. 제출 적합성 판정

v0.3은 제출된 HQ v0.1을 대체하는 박사님 제출본이 아니다. 그러나 코드·config·route 상태를 순차적으로 보여 주는 다음 개발 담당자용 handoff로는 적합하다. 기존 제출 ZIP은 재패키징하지 않았다.

