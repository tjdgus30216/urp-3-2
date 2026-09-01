# URP4-1 HQ v0.3 — 21셀 개발 통합본

## 파일 역할

- 실행 노트북: `URP4_1_HQ_v0_3_21CELL_DEV.ipynb`
- 단계 엔진: `urp4/hq/v0_3/stage_runtime.py`
- 노트북 생성 원본: `../tools/build_hq_v03_21cell_dev_notebook.py`
- smoke 검증: `tests/smoke_hq_v03_21cell.py`

이 개발본은 제출된 13셀 HQ v0.1의 실제 geometry/pixel/descriptor 엔진을
재사용하되, 한 번의 `run_hq()` 호출에 숨겨진 흐름을 21개의 순차 셀로 나눠
보인다. 기존 `URP4_1_HQ.ipynb`, `urp4/hq/v0_1/`, v0.2 개발본,
NB-CURRENT/ORIG, LEGACY-PY, 원본 Excel·geometry는 수정하지 않는다.

## 실제 구현 경로

1. `generated_stl`: v0.1 generator → image/mask → PNG readback →
   pixel/component → direct descriptor.
2. `imported_stl`: immutable STL import → winding 기반 image/mask →
   PNG readback → pixel/component → direct descriptor.
3. `FROZEN_REPLAY`: 기존 slice/overlay/component CSV를 읽어 direct
   descriptor만 재계산한다. 새 image/geometry 계산은 하지 않는다.

`STRICT`는 P1000/Z801/N40의 v0.1 계약을 재검증하여 쓴다. 물리 설정을
바꾸면 `EXPLORATORY`로만 실행하며, 실제 image/pixel 계산을 하더라도
`exploratory_not_parity`로 표시한다.

## 의도적으로 차단한 단계

- `original_step_stp`: inventory/preflight 외 direct descriptor는 미구현이라 fail-closed.
- XREG-v2.7 후보은행: 별도 공장은 있지만 검증된 HQ 실행 API가 없어 Cell 11에서 fail-closed.
- y intake, feature selection, Training 1–5, ensemble, forward/inverse:
  현재 HQ 엔진으로 구현되지 않아 Cell 14–19에서 fail-closed.
- Cell 13은 F001–F008에 해당하는 direct scalar 9행만 export하며 full XREG export가 아니다.

## v0.2 감사 결과

`v0_2/control.py`와 `direct_aggregation.py`의 실제 config validation,
Frozen replay, exploratory direct aggregation을 재사용한다.
`v0_2/models.py`와 `runtime.py`는 상태-only Blueprint로 실제 extraction
engine이 아니므로 수정하거나 v0.3 실행 경로에 병합하지 않았다. 이 workspace는
Git repository가 아니어서 VCS 변경 이력 대신 실제 source 내용과 SHA만 감사했다.

## Smoke 산출물의 지위

`outputs/hq_v02_smoke/`, `outputs/hq_v02_experimental_smoke/`,
`outputs/hq_v03_smoke/`는 코드 검증·디버깅 산출물이다. 과학적 parity나
박사님 제출 근거로 승격하지 않는다.

## 실행 환경

프로젝트 로컬 KMK312만 사용한다.

```powershell
& .\tools\envs\KMK312\python.exe .\tools\build_hq_v03_21cell_dev_notebook.py
Push-Location .\URP4-1_DELIVERABLE
& ..\tools\envs\KMK312\python.exe .\tests\smoke_hq_v03_21cell.py
Pop-Location
```

