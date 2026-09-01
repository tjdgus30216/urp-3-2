# COMP-FACTORY-002 AI Lattice compression pilot handoff

status: passed_with_scientific_caution
canonical_run: COMP-FACTORY-002-AI-LATTICE-PILOT-20260731-144749
runtime: project-local KMK312 / Python 3.12.12 / one thread

## 1. 수행 범위

- AI Lattice 149개 exact x-y join 사용
- AI092 제외: 구조인자 x만 있고 유효한 성능 y가 없음
- 성능 target 16개
- 구조인자 45열 중 수치·분산 조건을 통과한 37개 후보
- 1–50, 51–100, 101–150 원본 summary 파일을 각각 통째로 holdout하는 3-fold 평가
- 모든 구조인자 선택은 각 outer training fold 내부에서만 수행
- fold당 최대 8개 구조인자
- 네 방법의 technical pilot
- 총 OOF prediction 9,536개
- producer QA PASS, independent QA 36/36 PASS

이번 작업은 feature/method promotion이나 production model 결정이 아니다.

## 2. 가장 중요한 결과

pooled OOF에서는 다음 target이 상대적으로 높았다.

| Target | Best method | Pooled R² | Median within-block R² | 판단 |
|---|---:|---:|---:|---|
| Yield strength | Method-04 | 0.552 | 0.022 | 약한 block 내부 신호 + 큰 block 간 신호 |
| AS | Method-04 | 0.501 | 0.002 | 약한 block 내부 신호 + 큰 block 간 신호 |
| APS | Method-04 | 0.498 | 0.000 | 약한 block 내부 신호 + 큰 block 간 신호 |
| Max. Plateau stress | Method-04 | 0.498 | 0.000 | APS와 exact duplicate |
| Com. Strength | Method-04 | 0.373 | -0.023 | block 간 신호가 지배적 |
| SE | Method-04 | 0.244 | 0.029 | 약한 block 내부 신호 |
| EAE | Method-04 | 0.241 | 0.027 | 약한 block 내부 신호 |
| Modulus | Method-04 | 0.219 | 0.002 | 약한 block 내부 신호 + 큰 block 간 신호 |

따라서 `pooled R²=0.55`를 곧바로 “구조인자가 Yield strength를 잘 예측한다”고 표현하면 안 된다.

## 3. source-block 효과

대표 target 평균은 원본 summary 파일 범위에 따라 단조 증가한다.

| Target | AI001–050 | AI051–100 | AI101–150 |
|---|---:|---:|---:|
| Yield strength | 4.553 | 5.989 | 7.306 |
| Modulus | 96.422 | 118.413 | 145.140 |
| APS | 3.699 | 4.569 | 5.153 |
| AS | 3.581 | 4.422 | 4.986 |

모델의 OOF 예측도 이 세 군집을 주로 따라간다. 가능한 해석은 다음과 같다.

1. AI001–150이 실제로 성능이 개선되는 생성 세대/설계 순서다.
2. 세 summary 파일이 서로 다른 재료·제작·시험 batch를 포함한다.
3. 구조인자와 시험 batch가 동시에 변하여 confounding이 생겼다.
4. 위 요인이 함께 존재한다.

현재 파일만으로는 어느 해석인지 확정할 수 없다.

## 4. 반복적으로 선택된 구조인자

여러 target에서 세 outer fold 모두 선택된 주요 후보:

- `AIX004` — Actual VF
- `AIX019` — Global: l/d AVG
- `AIX020` — Global: l/d STDEV
- `AIX021` — Node: l/d AVG
- `AIX022` — Node: l/d STDEV
- `AIX034` — mean_radius_mm
- `AIX037` — surface_area_mm2
- `AIX038` — surface_to_solid_volume_1_per_mm

이 값들은 `primary feature`로 승격된 것이 아니다. 현재 target과 source-block을 함께 설명할 가능성이 있는 follow-up 후보다.

## 5. x-only 정리

상수라 제외:

- `AIX031` connected_components = 1
- `AIX035` std_radius_mm = 0
- `AIX040–042` bbox_x/y/z_mm = 30
- `AIX003` Target VF = 0.30은 계약에서 미리 제외

exact/proportional redundancy block:

- `AIX004 Actual VF` ↔ `AIX039 solid_volume_mm3_approx`
- `AIX007 Global strut count AVG` ↔ `AIX009 Node strut count AVG`
- `AIX008 Global strut count STDEV` ↔ `AIX010 Node strut count STDEV`
- `AIX034 mean_radius_mm` ↔ `AIX036 mean_diameter_mm`

중복 후보는 삭제하지 않고 non-selecting block으로 보존했으며, 각 fold에서 대표 하나만 선택했다.

## 6. y-y 정리

- `APS`와 `Max. Plateau stress`: 149/149 exact 동일
- `APS`와 `AS`: Pearson 0.9973
- `EAS`와 `Densifi. strain`: Pearson 0.9985
- `EAE`와 `SE`: Pearson 0.9988

따라서 16개 target은 독립적인 16개 정보원이 아니다. target 정의와 계산식을 확인한 뒤 대표 target과 파생 target을 분리해야 한다.

## 7. Method-01 runtime deviation

기존 대표 recipe의 `BayesianRidge`는 canonical KMK312에서
`scipy.linalg.svd → native Windows 0xC06D007F`로 종료됐다.

- NumPy `lstsq`: PASS
- scikit-learn `Ridge`: PASS
- 원본 KMK312 환경: 수정하지 않음
- Method-01 pilot: `Ridge(alpha=0.1)`과 `Ridge(alpha=10)`의 동일가중 surrogate

따라서 Method-01 결과는 교수님 원본 방법의 exact parity가 아니며 method promotion에 사용할 수 없다.

## 8. 현재 판단

- `confirmed`: AI Lattice 149개 intake와 exact x-y join
- `confirmed`: 네 방법 source-block OOF 기술 실행
- `confirmed`: QA 36/36과 metric 독립 재계산
- `confirmed`: target 및 feature 중복/상수 구조
- `likely`: 주요 pooled 신호에 source-block 효과가 크게 포함됨
- `unresolved`: 세 파일 범위가 생성 세대인지 시험 batch인지
- `unresolved`: target 단위·정확한 공학 정의·최적화 방향
- `unresolved`: AI 생성 lineage를 이용한 최종 leakage-safe grouping
- `rejected`: pooled R²만으로 예측 성공 또는 역설계 가능성을 주장

## 9. 다음 작업

1. 박사님 또는 source metadata로 1–50/51–100/101–150의 차이를 확인한다.
2. target 단위와 APS/AS/Max. Plateau stress의 계산 관계를 확인한다.
3. B/C/L 및 Voronoi 데이터가 입고되면 동일 intake/QA 공장을 실행한다.
4. 모든 group이 연결된 뒤 family/source-aware evaluation으로 다시 비교한다.
5. 그 전에는 Yield strength와 AS를 `follow-up target candidate`로만 유지한다.
