# COMP-FACTORY-001 — compression intake factory

목적: 박사님에게 받은 압축 summary Excel과 `Structural_Factors_All.xlsx`를 원본 수정 없이 정규화하고, model ID 기준으로 결합한다.

## 현재 지원

- `ai_lattice`: ready
- `bcl`: intake + grouped technical pilot complete; warnings retained; no promotion
- `voronoi`: intake + grouped technical pilot complete; warnings retained; no promotion

AI Lattice 기준 run:

- `COMP-FACTORY-001-AI-LATTICE-20260731-142459`
- 149개 performance 행 + 150개 structural-factor 행
- exact eligible join 149개
- AI092는 `x_only_missing_target`으로 추적
- producer QA PASS, independent QA 22/22 PASS

AI Lattice modeling pilot:

- `COMP-FACTORY-002-AI-LATTICE-PILOT-20260731-144749`
- 16 targets × 4 methods × 3 source-block outer folds
- 9,536 OOF predictions
- independent QA 36/36 PASS
- pooled 성능과 source-block 내부 성능을 분리해서 기록
- source-block confounding 가능성 때문에 feature/method promotion은 0
- Method-01은 BayesianRidge native SVD 오류로 fixed Ridge-blend surrogate 사용

## 처리 흐름

```text
summary Excel / Raw data
  + Structural_Factors_All.xlsx / Summary
  -> source hash 검증
  -> model ID 추출
  -> y wide/long 정규화
  -> x 구조인자 추출
  -> model_id one-to-one join
  -> QA / manifest
```

`Summary` 시트의 무헤더 3×21 숫자 블록은 공식 입력에서 제외한다. 실제 압축 데이터는 `Raw data` 시트만 사용한다.

이 공장은 feature selection, model fitting, prediction, inverse design을 실행하지 않는다. 생성된 데이터는 기존 FS4 계약의 새 입력 후보일 뿐이며 별도 modeling authorization 전에는 학습하지 않는다.

## 실행

프로젝트 루트에서:

```text
experiments\lab_001_xy_connection_20260626\factories\COMP-FACTORY-001\RUN_AI_LATTICE_INTAKE.cmd
```

새 run ID를 사용하며 기존 결과를 덮어쓰지 않는다.

## 후속 데이터 입고

- B/C/L summary: `data/raw/doctor_compression_data_20260731/04_bcl_summaries_pending/`
- Voronoi summary: `data/raw/doctor_compression_data_20260731/05_voronoi_summaries_pending/`

입고 직후 원본 hash와 시트/ID 계약을 먼저 등록한다. AI Lattice에서 검증한 source audit → row registry → target/feature registry → exact join → producer/independent QA 흐름을 재사용한다. 그룹별 시트 구조와 ID 규칙이 다를 수 있으므로 파일을 단순 연결하거나 이름으로 추정하지 않는다.

## 2026-08-02 B/C/L + Voronoi intake

- Preserved originals: `data/raw/doctor_compression_data_20260802/`
- Intake: `COMP-FACTORY-003-BCL-VORONOI-20260802-001`
- B/C/L pilot: `COMP-FACTORY-004-BCL-FS4-20260802-001`
- Voronoi pilot: `COMP-FACTORY-004-VORONOI-FS4-20260802-001`

`New_VF30/45/60.xlsx`의 명시적 B1–T17 label과 cached formula outputs를 B/C/L 성능의 주 원천으로 사용했다. `Compression_Worked_VF30/45/60.xlsx` 뒤쪽 generic summary는 세 VF 파일에서 오래된 값이 반복되므로 current crosswalk 입력에서 제외하고 reference-only로 보존했다. Voronoi는 `Voronoi_Summary.xlsx / Raw data`의 명시적 30개 ID를 사용했다.

Exact x-y joins are `137 B/C/L + 30 Voronoi = 167`. B/C/L의 F/T 및 일부 L 61개 성능행은 구조인자가 없어 y-only로, SC2 3개 구조행은 성능이 없어 x-only로 남겼다. 두 pilot 모두 grouped OOF와 fold-local selection을 사용했으며 feature/method promotion은 하지 않았다.
