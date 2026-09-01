# COMP-FACTORY-001 AI Lattice intake handoff

status: passed
run_id: COMP-FACTORY-001-AI-LATTICE-20260731-142459
scope: intake, normalization, registry, exact x-y join, QA

## 결과

- 성능 원본의 canonical AI Lattice 행: 149
- `Structural_Factors_All.xlsx`의 AI Lattice 구조인자 행: 150
- 분석 가능 exact join: 149
- 전체 trace registry: 150
- 구조인자만 있고 성능값이 없는 모델: AI092
- 성능 후보 열: 17
  - 완전 finite: 16
  - 전부 결측으로 hold: `POST-UCS-PEAK`
- 구조인자 열: 45
- 원본에서 제외한 비모델/보조 행: 37
- producer QA: PASS
- independent QA: 22/22 PASS
- feature selection, 모델 학습, 예측: 미실행

## AI092 처리

`Ai-Lattice_(51-100)_summary.xlsx`에는 `CP_Lattice_92.csv`가 없고 그 위치에 비정상 `42.csv` 행이 있다. 해당 행은 스프레드시트 오류값을 포함하므로 AI092로 추정·대체하지 않았다. AI092는 `x_only_missing_target`으로 보존한다.

## 재사용 전략

B/C/L 및 Voronoi summary가 입고되면 같은 공장의 다음 단계를 재사용한다.

1. 원본 hash와 workbook/sheet inventory
2. group별 model-ID/replicate/direction 규칙 감사
3. 성능 y 정규화
4. `Structural_Factors_All.xlsx`에서 해당 source의 구조인자 x 추출
5. exact crosswalk와 결측/중복 격리
6. producer QA와 KMK312 independent QA
7. 세 group을 묶는 compression dataset manifest 생성

기존 FS4 feature-selection/training 엔진은 폐기하지 않는다. 다만 target 의미·단위·목표방향과 leakage-safe group split 정책을 사전등록한 뒤에만 새 dataset manifest를 연결한다.

## 현재 게이트

- `confirmed`: AI Lattice intake/normalization/exact join 기술 계약
- `confirmed`: AI092 성능 결측
- `confirmed`: 16개 finite 성능 후보와 45개 구조인자 열 보존
- `unresolved`: 각 성능 열의 단위와 maximize/minimize 방향
- `unresolved`: AI 생성 batch/geometry lineage를 고려한 leakage-safe split group
- `hold`: feature selection, training, prediction, inverse design
