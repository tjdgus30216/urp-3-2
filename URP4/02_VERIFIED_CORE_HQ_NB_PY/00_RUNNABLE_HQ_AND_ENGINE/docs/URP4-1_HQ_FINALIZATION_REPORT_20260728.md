# URP4-1 HQ finalization report — 2026-07-28

## 1. 결론

`IMSTL-006-20260728-002` 완료를 선행 확인한 뒤, 기존 검증 모듈을 재작성하지 않고 하나의 실행 관제 노트북과 최소 Python 패키지로 연결했다.

- 산출물 루트: `URP4-1_DELIVERABLE/`
- 사용자 진입점: `URP4_1_HQ.ipynb`
- 유일한 사용자 편집 셀: Cell 1 `MASTER CONTROLLER`
- 최종 cell tree: Cell 0–12, 총 13개; input manifest·geometry QA·descriptor·slice QA·export·x-only readiness·training status를 분리 표시
- 실행 환경: `KMK312 / Python 3.12.12`
- 독립 통합 감사: `10/10 PASS`
- 빠른 smoke/guard: `9/9 PASS`
- Controller acceptance/rejection contract: `40/40 PASS`
- immutable source identity: `14/14 PASS`
- y 접근, x-y 분석, feature selection, fitting, prediction, inverse design: `0`
- NB-CURRENT, NB-ORIG, LEGACY-PY, 원본 Excel 수정: `0`

이번 결과는 **실행 가능한 HQ v0.1 통합본**이다. 모든 generator의 생산 정책이나 imported-STL의 universal/all58 정당성을 확정한 것은 아니다.

## 2. 기준 상태

선행 기준은 `RUN-336 / DEC-349 / CHG-334 / LAB-CHG-303 / R09-BB-1302`다.

- IMSTL-006 selected gate: B3/C1/L1/T1/T8/T9 통과, F1 보류.
- 통과한 6모델은 P1000/Z801 full extraction 완료.
- imported winding은 sampled B/C/L/T에서 operational evidence를 갖지만 F family와 all58은 미해결이다.
- 이 HQ 작업은 그 과학 상태를 완화하거나 승격하지 않았다.

## 3. 실제 통합 구조

```text
Cell 1 MASTER CONTROLLER
        ↓
Cell 2 validate → derive → freeze → config_sha256
        ↓
Cell 3 frozen settings table
        ↓
Cell 4 HQ engine
        ├─ generate: Lattice A / TPMS / Voxel
        └─ import: generated STL / imported STL / original STP
                 ↓
        explicit geometry route
        ├─ generated STL → native RUN-139 image pipeline
        ├─ imported STL → IMSTL oriented non-zero winding
        └─ original STP → strict/reference preflight; descriptor fail-closed
                 ↓
        PNG 생성 → PNG readback → pixel/component tables
                 ↓
        RUN-139 scalar service → 9 rows
                 ↓
        CSV + XLSX + QA + frozen config + run status
```

기존 `urp4/orchestration/v0_1`은 계약 검증 전용이므로 production HQ 엔진으로 재사용하지 않았다. 새 `urp4/hq/v0_1` 계층만 추가했다.

## 4. 경로 정책

### generated STL

`GEN-STL-NATIVE-CONTROLLED`를 유지한다. NB-CURRENT가 통제된 조건으로 만든 STL을 imported-STL 결함 경로와 섞지 않는다.

### imported STL

`IMP-STL-ORIENTED-NONZERO-SCREENING-L28`을 사용한다. 원시 triangle orientation과 multiplicity를 보존하고 signed non-zero winding으로 material을 판정한다. 자동 deduplication, hole fill, dilation, STL→STEP fallback은 하지 않는다.

### original STP

`IMP-STP-PERSOLID-REFERENCE`로 B-rep preflight만 수행한다. HQ v0.1에는 direct STP→RUN-139 descriptor adapter가 없으므로 descriptor 요청은 명시적으로 실패한다. 이는 미완성 기능을 STL proxy로 조용히 대체하지 않기 위한 잠금이다.

## 5. Controller 정책

Cell 1 외의 셀은 편집 대상이 아니다. Cell 2가 다음을 파생한다.

- `slice_count ↔ slice_spacing_mm`
- `pixel_resolution → pixel_size_mm → area_per_pixel_mm2`
- `lattice cells_per_axis ↔ cell_size_mm`
- route ID, formula/backend ID, imported algorithm revision, config hash

구조인자 실행은 현재 승인 프로필 `40 mm / P1000 / Z801 / 0.05 mm / CC8 / min 2 px`만 허용한다. 다른 설정은 geometry generation 또는 별도 DOE에서 검증한 뒤 승격해야 한다.

## 6. Generator 상태

| generator | HQ 실행 | 상태 | 제한 |
|---|---:|---|---|
| Lattice Type A | 가능 | likely/source-replay | 생산 mesh·printability 최종 승인 아님 |
| Lattice Type B | 차단 | unresolved | identity-locked `Variables.xlsx` 없음 |
| TPMS Multiwall | 가능 | likely/conditional | production VF·thickness·open-cell 정책 미확정 |
| Voxel | 가능 | likely/conditional | production grid·VF·printability 정책 미확정 |

## 7. Training 상태

박사님이 준 9개 notebook과 5개 method family는 SHA-256과 interface registry로 포함했다. Windows 장경로를 피하기 위해 바이트를 변경하지 않고 `reference_sources/training/`에 보존했다.

Training과 feature selection은 기본 OFF이며 HQ v0.1에서 실행 자체가 잠겨 있다. 공식 y와 modeling gate 없이 잘못된 학습이 시작되는 것을 막는다.

## 8. KMK312 검증

### 빠른 smoke/guard — 9/9 PASS

- Lattice Type A 생성
- TPMS 생성
- Voxel 생성
- imported L28 STL preflight
- original L28 STP preflight
- import/generate XOR 위반 차단
- y 없는 training 차단
- Type B 입력 없음 차단
- STP descriptor 요청 차단

### imported L28 full descriptor

L28 VF30 원본 STL을 P1000/Z801으로 두 번 독립 실행했다.

- slice rows: `801`
- overlay rows: `800`
- slice component rows: `44,849`
- overlay component rows: `43,966`
- PNG created/read: `1,601`
- PNG deleted: `1,601`
- remaining PNG: `0`
- readback mismatch: `0`
- scalar rows: `9`
- 두 완료 run의 descriptor 및 primitive table hashes: exact

### generated fixture와 실제 generator full descriptor

40 mm controlled generated fixture와 실제 Lattice Type A·TPMS·Voxel 출력을 native route로 실행했다.

| case | slice / overlay | scalar | PNG mismatch / remaining | result |
|---|---:|---:|---:|---|
| controlled fixture | 801 / 800 | 9 | 0 / 0 | PASS |
| Lattice Type A | 801 / 800 | 9 | 0 / 0 | PASS |
| TPMS | 801 / 800 | 9 | 0 / 0 | PASS |
| Voxel | 801 / 800 | 9 | 0 / 0 | PASS |

따라서 네 generated case 모두 생성→preflight→이미지 생성/readback→구조인자→manifest의 기술적 연결은 통과했다. 다만 실제 bbox extent는 Lattice `41.4074 mm`, TPMS `39.5 mm`, Voxel `38.0 mm`였고 Lattice/TPMS는 `topology_clean=false`였다. 이는 실행 실패가 아니라 **40 mm 생성 도메인·normalization·topology 생산 정책이 아직 미확정**임을 뜻하므로 scientific/production 승인으로 승격하지 않는다.

### 추가 디버깅과 휴대성 검증

- TPMS/Voxel이 호출자의 현재 작업 디렉터리에 의존하던 상대경로 해석 결함을 수정했다.
- L28 STL/STP 검증 fixture를 deliverable 내부에 동일 SHA-256으로 포함했다.
- 프로젝트 루트에서 직접 실행한 smoke도 `9/9 PASS`하여 deliverable 폴더 밖 CWD에서도 정상 작동함을 확인했다.
- Python 93개 AST parse, notebook 13-cell nbformat/AST 검증, 잠재 secret assignment scan 0건을 확인했다.

## 9. 보호 및 불변성

- deliverable 안 reference source는 등록 SHA와 `14/14` 일치한다.
- 원본 source notebook/geometry/Excel은 복사 또는 read-only audit만 수행했다.
- `NB-CURRENT`, `NB-ORIG`, `LEGACY-PY`, 원본 Excel을 수정하지 않았다.
- 결과는 hash+timestamp run 폴더에 저장하며 기존 run을 덮어쓰지 않는다.

## 10. 상태 라벨

- **confirmed**: single-controller freeze, explicit routing, generated fixture/Lattice A/TPMS/Voxel full technical chain, image readback trace, 9-scalar service, fail-closed guards, source identities.
- **likely**: imported STL screening route on L28 and sampled B/C/L/T; generator source-replay usability.
- **unresolved**: F1 resolution/pixel phase, all58 imported generalization, direct STP descriptor adapter, Type B workbook, generated-family 40 mm domain/normalization and topology policy, TPMS/Voxel production policy, official y/training gate.
- **rejected**: silent STL→STEP fallback, automatic feature selection/training, exact-STP/universal-import claim from this HQ work.

## 11. 다음 작업

박사님 로드맵 우선순위에서 다음 과학 작업은 그대로 `IMSTL-007_F1_SELECTED_SLICE_RESOLUTION_AND_PIXEL_PHASE_DIAGNOSIS_NO_Y`다. 병행 확인 사항은 generated Lattice/TPMS/Voxel의 40 mm domain 정의다. HQ v0.1 자체의 다음 개발은 direct STP descriptor adapter, Type B source workbook, 또는 공식 modeling gate가 확보될 때 별도 gate로 진행한다.
