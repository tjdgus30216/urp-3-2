# 다음 담당자용 — HQ v0.3 21셀 개발 통합본

## 먼저 읽을 파일

1. HQ_V0_3_21CELL_DEV_README_KO.md
2. HQ-INTEGRATE-003_21CELL_VERSIONED_DEV_20260803/REPORT.md
3. URP4_1_HQ_v0_3_21CELL_DEV.ipynb
4. urp4/hq/v0_3/stage_runtime.py
5. tests/smoke_hq_v03_21cell.py

## 이 파일이 하는 일

기존 HQ v0.1의 실제 STL → image → pixel/component → direct descriptor 계산을
21개 cell로 나눠, 각 단계의 입력·출력·현재 구현 상태를 보이게 한다.

- 실제 실행: generated/imported STL, ARTIFACT_FULL, STREAMING, FROZEN_REPLAY, direct 9 scalar
- 차단: original STEP/STP direct descriptor, XREG HQ API, y/feature selection/Training/model/forward/inverse
- 모든 차단은 없는 계산을 대체하지 않기 위한 fail-closed다.

## 절대 주의

- URP4_1_HQ.ipynb는 기존 제출 HQ이고 수정하지 않는다.
- outputs/hq_v02_smoke/와 outputs/hq_v03_smoke/는 코드 smoke 결과다. 과학적 결과나 제출물로 쓰지 않는다.
- Python은 반드시 tools/envs/KMK312/python.exe로 실행한다.

