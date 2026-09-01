# URP4-1 HQ 실행 안내

`URP4_1_HQ.ipynb`의 **Cell 1 MASTER CONTROLLER만 수정**합니다. Cell 2가 모든 파생값과 잠금값을 검증·동결하고, 이후 셀은 그 동결본만 전달받습니다.

## 실행 환경

- 커널: `KMK312 (Python 3.12.12)`
- 이 폴더를 작업 디렉터리로 열고 위에서 아래로 실행합니다.
- 기존 결과는 덮어쓰지 않고 `outputs/HQ-<config hash>_<timestamp>/`에 새 run으로 저장됩니다.

## 라우팅 원칙

| 입력 | route | 현재 상태 |
|---|---|---|
| NB-CURRENT가 생성한 STL | `GEN-STL-NATIVE-CONTROLLED` | native slicing + RUN-139 구조인자 |
| 외부에서 가져온 STL | `IMP-STL-ORIENTED-NONZERO-SCREENING-L28` | IMSTL-005 winding + PNG readback + RUN-139 구조인자 |
| 원본 STP/STEP | `IMP-STP-PERSOLID-REFERENCE` | strict/reference preflight만; 구조인자는 v0.1에서 fail-closed |

STL→STEP proxy는 기본 경로가 아니며 자동 fallback이 없습니다.

## 현재 잠금

- 구조인자 실행 설정은 `40 mm / 1000×1000 / 801 slices / 0.05 mm / CC8 / min 2 px`만 승인합니다.
- Feature selection과 Training은 인터페이스만 표시하며 기본 OFF입니다.
- Batch와 아직 검증되지 않은 point/surface/lattice/candidate descriptor scope도
  Controller에 보이지만 v0.1에서는 fail-closed OFF입니다.
- Training 원본은 SHA-256을 유지한 채 Windows 장경로 오류를 피하도록
  `reference_sources/training/`에 보존했습니다. 실행은 여전히 잠겨 있습니다.
- y가 없거나 공식 modeling gate가 열리지 않으면 학습은 실행되지 않습니다.
- Lattice Type B는 identity-locked `Variables.xlsx`가 없으면 실패하도록 고정했습니다.
- TPMS와 Voxel은 검증된 source-replay plugin이지만 생산 VF/printability 정책의 최종 승인을 뜻하지 않습니다.
- TPMS는 현재 source-replay 검증 범위인 `target_vf=0.45~0.55`만 허용합니다. Cell 1의 기본 `0.30`은 Lattice/Voxel용이며 TPMS 선택 시 함께 변경해야 합니다.
- 실제 full-chain smoke에서 생성 STL bbox extent는 Lattice Type A `41.4074 mm`, TPMS `39.5 mm`, Voxel `38.0 mm`였습니다. 모두 기술 실행은 통과했지만 40 mm domain/normalization·topology 생산 정책은 아직 미확정이므로 연구 결과 확정에 바로 사용하지 않습니다.

## 이미지 저장 정책

- `STREAMING_TEMP_PNG`: 이미지 생성 → PNG readback → CSV 저장 → 즉시 삭제
- `KEEP_ALL`: 모든 mask/overlay 유지
- `KEEP_FLAGGED`: imported STL에서 이상 단면만 유지; generated STL v0.1에서는 지원하지 않아 fail-closed

## 빠른 사용

1. `import_geometry=True`, `generate_geometry=False`로 설정합니다.
2. `input_geometry`, `model_id`, `source_type`을 지정합니다.
3. Cell 2의 frozen settings 표와 route를 확인합니다.
4. Cell 4 이후를 실행하고 `run_manifest.json`, `input_geometry_manifest.json`,
   `run_status.json`, `output_manifest.csv`, `geometry_preflight.json`,
   `descriptor_result.csv/.xlsx`를 확인합니다.

## 제출 전 자체 검증

아래 명령은 반드시 `KMK312` Python으로 실행합니다. 테스트 fixture는 이 폴더 안에 있으며 원본 L28과 SHA-256이 같습니다.

```powershell
..\tools\envs\KMK312\python.exe tests\controller_contract.py
..\tools\envs\KMK312\python.exe tests\smoke_hq.py
..\tools\envs\KMK312\python.exe tests\audit_deliverable.py
```

- Controller contract: `40/40 PASS`
- 빠른 route/guard smoke: `9/9 PASS`
- 통합 감사: `10/10 PASS`
- immutable source identity: `14/14 PASS`

`tests/full_descriptor_smoke.py`는 P1000/Z801 전체 체인을 다시 계산하므로 약 25분 이상 걸릴 수 있습니다. 기존 검증에서는 imported L28 2회 exact 재현과 generated fixture/Lattice A/TPMS/Voxel 전부 통과했습니다.
