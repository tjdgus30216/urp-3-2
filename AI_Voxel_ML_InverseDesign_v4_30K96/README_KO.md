# AI-Voxel ML + Inverse Design v4 — 30,000 Candidate / 96 Descriptor-LHS Profile

## 이번 수정의 핵심

- Import/workspace: `C:\Users\Administrator\Desktop\Minkyeom\AI-Voxel\Voxel generation`
- 새 run을 시작하면 `Result_YYYYMMDD_HHMMSS`가 자동 생성됩니다.
- 전체 candidate Voxel: **30,000개**
- Descriptor-space LHS 최종 선정: **96개**
- 30,000개 pool은 기본적으로 0.10 mm screening grid(300³)로 생성하고, 선정 96개는 0.03 mm(1000³)로 재생성합니다.
- 30k 규모에 맞춰 generation aggregate log는 item-level STL/JSON checkpoint를 유지하면서 25개 단위로 flush합니다.
- Descriptor-LHS PCA는 float32 + randomized PCA를 기본 사용하여 full SVD보다 대규모 pool에 적합하게 수정했습니다.
- 30,000 candidate parameter의 source-of-truth는 `Candidate_Generation_Parameters.csv`(+가능하면 Parquet)이며, Excel은 기본 5,000행 preview입니다. `EXPORT_FULL_CANDIDATE_XLSX=True`로 전체 XLSX를 선택적으로 만들 수 있습니다.

## 요청한 sampling/geometry 변수의 정확한 의미

| 변수 | 의미 | 현재값 |
|---|---|---:|
| `RANDOM_SEED` | LHS/latent/candidate 생성의 재현성 seed. 동일 설정+seed면 같은 candidate parameter table을 재현하기 위한 값입니다. | 42 |
| `N_CANDIDATE_STRUCTURES` | **전체 후보 구조 수**. `USE_GENERATOR_PARAMETER_LHS=True`이면 random 수가 아니라 생성인자 LHS 후보 수입니다. | 30,000 |
| `N_RANDOM_STRUCTURES` | 기존 runtime 호환 alias. 실제 값은 `N_CANDIDATE_STRUCTURES`와 동일합니다. | 30,000 |
| `N_LHS_SELECTED_STRUCTURES` | 전체 descriptor pool에서 최종 정밀재생성/제작 대상으로 선정할 수입니다. | 96 |
| `N_FINAL_SAMPLES` | 기존 runtime 호환 alias. `N_LHS_SELECTED_STRUCTURES`와 동일합니다. | 96 |
| `USE_GENERATOR_PARAMETER_LHS` | 생성인자(VF, thickness, sigma, anisotropy, latent z 등) 공간을 LHS로 분산하여 후보를 만들지 여부입니다. | True |
| `USE_DESCRIPTOR_LHS_SELECTION` | 생성된 구조의 descriptor를 PCA 구조인자 공간으로 축약하고 그 공간에서 LHS로 최종 구조를 선택할지 여부입니다. | True |
| `DESCRIPTOR_LHS_PCA_COMPONENTS` | descriptor-LHS가 사용하는 PCA 구조공간 차원입니다. 수천 descriptor를 10개 주요 좌표로 축약합니다. | 10 |
| `DESCRIPTOR_MAX_MISSING_FRACTION` | NaN 비율이 이 값보다 큰 descriptor는 LHS selection에서 제외됩니다. 0.25 = 25% 초과 결측 시 제외. | 0.25 |
| `DESCRIPTOR_MIN_STD` | 구조 간 변화가 사실상 없는 descriptor 제거 기준입니다. std≤1e-12이면 selection feature에서 제외합니다. | 1e-12 |
| `BOUNDARY_SIZE_MM` | cubic Voxel 구조 한 변의 실제 길이입니다. | 30 mm |
| `VOXEL_SIZE_MM` | 최종 선정 구조의 voxel pitch입니다. 30/0.03=1000 → 1000³ grid. | 0.03 mm |
| `USE_SCREENING_RESOLUTION` | 전체 후보는 coarse resolution으로 처리하고 선정 구조만 final resolution으로 재생성할지 여부입니다. | True |
| `SCREENING_VOXEL_SIZE_MM` | 30k 후보 pool의 voxel pitch. 30/0.10=300 → 300³ grid. | 0.10 mm |
| `REGENERATE_SELECTED_AT_FINAL_RESOLUTION` | 선정 96개를 screening STL 복사가 아니라 동일 인자로 0.03 mm에서 새로 재생성합니다. | True |
| `MARCHING_CUBES_STEP_SCREENING` | screening voxel→STL 변환 시 marching-cubes sampling step. 2는 빠르지만 mesh가 다소 거칩니다. | 2 |
| `MARCHING_CUBES_STEP_FINAL` | final voxel→STL 변환 step. 1은 가장 정밀합니다. | 1 |
| `ALLOW_HIGH_MEMORY_FINAL_GRID` | 1000³처럼 grid_n≥800인 final grid 계산을 허용합니다. False면 메모리 보호를 위해 차단합니다. | True |
| `ENABLE_MAX_THICKNESS_TRIM` | max_thickness보다 지나치게 두꺼운 영역을 morphology 기반으로 제한하는 옵션입니다. | True |
| `MAX_THICKNESS_TRIM_GRID_LIMIT` | 위 trim을 적용할 최대 grid_n. 520이므로 300³ screening에는 가능하지만 1000³ final은 메모리 안전상 skip됩니다. | 520 |

## Result 폴더 구조

새 run 예:

```text
C:\Users\Administrator\Desktop\Minkyeom\AI-Voxel\Voxel generation\
└─ Result_20260904_042500\
   ├─ 00_state\
   ├─ 01_Candidate_Parameters\
   ├─ 02_Voxel_Pool\
   │  ├─ STL\
   │  ├─ Descriptor\
   │  ├─ DLP_raw\
   │  └─ DLP_slice\
   ├─ 03_Descriptor_LHS_Selection\
   ├─ 04_Selected_Final\
   │  ├─ STL\
   │  ├─ Descriptor\
   │  ├─ DLP_raw\
   │  └─ DLP_slice\
   ├─ 05_Tables\
   ├─ 06_ML_Dataset\
   ├─ 07_Models\
   ├─ 08_Inverse_Optimization\
   ├─ 09_Active_Sampling\
   └─ 10_Validation\
```

> `BASE_DIR/.ai_voxel_active_run.json`과 `.ai_voxel_ml_project.json`은 최신 Result 폴더를 찾기 위한 작은 pointer/control 파일입니다. 실제 데이터/모델/결과는 Result 폴더 안에 저장됩니다.

## 30,000개 운용 주의

30,000개 모두를 300³ Voxel + STL + exhaustive descriptor까지 처리하는 것은 매우 큰 계산입니다. 코드는 요청대로 수행하도록 설정되어 있으며, 각 STL/descriptor가 개별 checkpoint로 저장됩니다. 중단되면 완료된 item은 다시 계산하지 않습니다. 특히 `RUN_DESCRIPTOR_FOR_POOL=True`이면 30,000개 descriptor extraction이 전체 소요시간의 주 병목이 됩니다.

---

# AI-Voxel ML / Inverse Design Closed-Loop Workflow v4

## 1. 연구 목표

이 bundle은 다음의 계층형 학습 및 closed-loop inverse design을 수행합니다.

```text
[Algorithm]
Generator parameters + continuous latent variables
        ↓  Model 1
Pixel/slice/3D structural descriptor state
        ↓
[Experiment]
Descriptor-space selected Voxel → DLP printing → compression test
        ↓  Model 2
Compression curve + mechanical properties
        ↓
[Algorithm]
Desired curve/performance
        ↓
Descriptor inverse optimization
        ↓
Target structural descriptor state
        ↓
Generator inverse + cascaded Model1→Model2 refinement
        ↓
Optimal generator parameters
        ↓
[Experiment]
Voxel regeneration → DLP → compression validation
        ↓
[Algorithm]
If insufficient: active sampling → dataset update → retraining → repeat
```

핵심 설계 원칙은 **inverse network를 직접 학습하는 것이 아니라 두 개의 검증 가능한 forward surrogate를 학습한 후 optimizer가 역방향으로 탐색**하도록 하는 것입니다.

---

## 2. Notebook 실행 순서

### 00 — `00_AI_Voxel_DatasetFactory_v4.ipynb`

기존 Threadripper 3970X + Dual RTX 3090 adaptive v3를 기반으로 다음을 추가했습니다.

- disk-first / kernel-independent resume
- GPU 0/1 adaptive scheduling 유지
- `latent_periodic_isotropic`, `latent_periodic_orthotropic`, `latent_stochastic`
- `latent__z01 ... latent__z16` continuous morphology controls
- random `seed`는 provenance로만 저장하며 inverse-design input에서 제외
- `design_id`, `realization_id`, `geometry_id`, `run_id`
- non-LHS pool도 전부 cumulative dataset에 보존
- screening/final을 `meta__fidelity`로 구분
- `CANDIDATE_SOURCE = generate | import | inverse_design | active_sampling`
- final DLP specimen manifest 자동 생성

### 01 — `01_Gen2Desc_Training_v1.ipynb`

Model 1:

```text
Generator parameters + latent z + fidelity
    → descriptor representation
```

- 모든 구조를 descriptor representation 학습에 사용
- v4 latent-controlled 구조를 기본 forward Model 1 학습에 사용
- v3 seed-based legacy 구조는 representation에는 사용하지만 forward model에서는 기본 제외
- raw descriptors → robust scaling → correlation pruning → PCA structural state
- ExtraTrees / RandomForest group-safe CV 비교
- screening + final multi-fidelity context 동시 학습

### 02 — `02_Descriptor2CompressionCurve_Training_v1.ipynb`

Model 2:

```text
Descriptor latent state
    → full compression curve
    + direct mechanical properties
```

첨부 `Com_Training_Visualization_v22.ipynb`에서 다음 아이디어를 반영했습니다.

- multiple Excel / compression curve parsing concept
- common strain grid
- curve smoothing / valid-mask handling
- modulus, yield, peak/compressive stress, plateau stress
- event-aware densification strain
- absorbed energy to densification
- CFE
- design-group-safe CV
- curve latent surrogate + direct-property heads
- ensemble uncertainty + conformal-style residual radius
- OOF curve / property visualization

권장 시험 데이터 형식은 long format입니다.

```text
specimen_id, design_id, geometry_id, replicate_id,
strain, stress_MPa,
test_fidelity, material_batch, print_batch,
strain_rate_s-1, temperature_C
```

기존 v22의 5-column Excel block layout도 `CURVE_INPUT_MODE='legacy_v22_folder'`로 읽을 수 있습니다.

### 03 — `03_Hierarchical_Inverse_Optimization_v1.ipynb`

두 단계 inverse + final cascaded refinement를 수행합니다.

1. desired performance/curve → descriptor latent target
2. descriptor latent → raw structural descriptor target
3. structural descriptor target → generator parameters
4. generator → Model 1 → Model 2를 다시 통과시키며 최종 performance loss 최소화

지원 target 예:

- target plateau stress
- minimum/maximum peak stress
- maximize densification strain
- maximize absorbed energy
- optional whole compression-curve matching
- prediction uncertainty penalty
- descriptor manifold OOD penalty

첨부 `Com_Optimization_v19.ipynb`의 surrogate-assisted optimization, uncertainty-aware selection, target-driven search 개념을 Voxel continuous generator space에 적용했습니다.

산출물:

- `optimized_descriptor_states.csv`
- `optimized_raw_structural_descriptors.csv`
- `optimized_generator_parameters.csv`
- `optimized_predicted_curves.csv`

`optimized_generator_parameters.csv`는 DatasetFactory가 직접 읽습니다.

### 04 — `04_Experimental_Validation_Ingest_v1.ipynb`

Inverse-designed Voxel을 실제 제작/시험한 뒤:

- actual descriptor 등록
- actual compression curve 등록
- predicted vs measured curve RMSE / R²
- property prediction error
- validation plot
- cumulative dataset 승격
- central compression curve master append

을 수행합니다.

### 05 — `05_Active_Sampling_ClosedLoop_v1.ipynb`

최적화가 부족하거나 모델 불확실성이 큰 경우:

```text
Acquisition = performance proximity
            + surrogate uncertainty
            + descriptor novelty
```

를 이용해 Sobol virtual pool에서 diverse batch를 선택합니다.

산출물 `active_sampling_generator_parameters.csv`를 DatasetFactory의
`CANDIDATE_SOURCE='active_sampling'`으로 다시 입력합니다.

### 06 — `06_MEvoLattice_v22_Compatibility_Export.ipynb`

기존 `Com_Training_Visualization_v22.ipynb`를 계속 사용하고 싶을 때 cumulative Voxel descriptors를:

```text
Structural_Factors_All.xlsx
  └─ Summary
       모델명
       Type
       Source
       Target VF
       <Voxel descriptors...>
```

형태로 export합니다.

`Com_Optimization_v19.ipynb`의 line/strut geometry mutation은 Voxel generator와 geometry representation이 다르므로 직접 사용하지 않고, 최적화 아이디어를 Notebook 03에 별도로 구현했습니다.

### 07 — `07_Legacy_v3_Descriptor_Import_v1.ipynb`

기존 v2/v3에서 이미 계산한 non-LHS / descriptor 구조를 cumulative project에 추가합니다.

- legacy descriptor는 절대 버리지 않습니다.
- descriptor representation 및 Model 2에서 사용 가능합니다.
- seed-based generator는 inverse-continuous mapping이 아니므로 Model 1 forward fit에서는 기본 제외합니다.

---

## 3. Result 중심 Project 구조

이번 30K/96 profile에서는 데이터/모델/역설계 결과를 **현재 `Result_YYYYMMDD_HHMMSS` 안에 함께 저장**합니다.

- `06_ML_Dataset`: 현재 Result의 pool/final descriptor, cumulative table, schema, compression-curve master
- `07_Models`: Gen→Descriptor 및 Descriptor→Compression 모델
- `08_Inverse_Optimization`: target performance, optimized descriptors/generator parameters
- `09_Active_Sampling`: active-learning 후보
- `10_Validation`: 최적 구조의 실제 압축시험 검증

같은 연구 campaign에서 active-learning cycle을 반복할 때는 **같은 Result를 유지**하는 것을 권장합니다. Kernel restart 후에는 CELL 1을 다시 실행하지 않고 stage를 재개합니다. 설정을 바꿔 같은 Result를 계속 쓰려면 `START_NEW_RESULT_RUN=False`로 CELL 1을 실행해 active pointer의 Result를 다시 사용합니다. 완전히 독립적인 새 campaign만 `START_NEW_RESULT_RUN=True`로 새 Result를 생성하십시오.

---

## 4. 권장 실제 연구 순서

### Cycle 0 — 30,000 candidate design-space exploration

DatasetFactory 기본값:

```python
START_NEW_RESULT_RUN = True
CANDIDATE_SOURCE = 'generate'
N_CANDIDATE_STRUCTURES = 30_000
N_LHS_SELECTED_STRUCTURES = 96
USE_GENERATOR_PARAMETER_LHS = True
USE_DESCRIPTOR_LHS_SELECTION = True
```

30,000개 후보의 생성인자 공간을 LHS로 채우고, screening Voxel/STL/descriptor를 계산한 뒤 descriptor-PCA 공간에서 96개를 LHS로 선정합니다. LHS 비선정 구조도 Model 1 학습 데이터로 모두 유지됩니다.

### Cycle 1 — 제작/압축시험

`04_Selected_Final/DLP_slice`의 96개를 제작하고 compression curve를 `compression_curves_master.csv` 형식으로 등록합니다. 반복시험은 같은 `design_id` 아래 서로 다른 `specimen_id`, `replicate_id`로 기록합니다.

### Cycle 2 — Surrogate training

1. `01_Gen2Desc_Training_v1.ipynb`
2. `02_Descriptor2CompressionCurve_Training_v1.ipynb`

순서로 실행합니다.

### Cycle 3 — Inverse design

`03_Hierarchical_Inverse_Optimization_v1.ipynb`에서 목표 compression performance/curve를 설정합니다. 생성된 `optimized_generator_parameters.csv`를 DatasetFactory의 `CANDIDATE_SOURCE='inverse_design'` 입력으로 사용합니다.

### Cycle 4 — 최적 Voxel 제작/검증

DatasetFactory를 같은 Result에서 inverse-design candidate mode로 실행 → final Voxel/STL/DLP/descriptor 생성 → 실제 제작/압축시험 → `04_Experimental_Validation_Ingest_v1.ipynb` 실행.

### Cycle 5 — Active learning

목표 성능/모델 정확도가 충분하지 않으면 `05_Active_Sampling_ClosedLoop_v1.ipynb` → DatasetFactory `active_sampling` → 추가 제작/시험 → Notebook 01/02 재학습 → Notebook 03 재최적화를 반복합니다.

---

## 5. 중요한 연구 방법론

### Seed는 inverse variable이 아닙니다

random seed 숫자의 거리에는 morphology 의미가 없습니다. v4에서는 새 구조를 continuous latent z로 제어합니다.

### Structural descriptors는 중간 causal/mechanistic state로 사용합니다

단순 `generator → performance` black-box 하나보다:

```text
generator → structural state → mechanical response
```

를 유지하여 어떤 구조 상태가 성능을 지배하는지 분석할 수 있습니다.

### Raw descriptor 6000+개를 직접 inverse하지 않습니다

영구 descriptor encoder를 별도로 학습하여 low-dimensional structural-state manifold에서 optimization하고, 최종 target은 raw descriptor로 inverse transform해 해석합니다.

### Multi-fidelity

0.10 mm screening과 0.03 mm final은 같은 값으로 취급하지 않고 fidelity context를 저장합니다. 동일 design이 두 fidelity에 존재하면 Model 1이 resolution dependency까지 학습할 수 있습니다.

---

## 6. Hardware

DatasetFactory는 기존 v3의 Threadripper 3970X + Dual RTX3090 adaptive scheduler를 유지합니다.

- GPU 0/1 모두 사용 가능
- GPU 0에 다른 작업이 많으면 GPU 1 우선
- 매 candidate / descriptor run 직전 VRAM + utilization 재평가
- 둘 다 여유면 screening candidate 병렬 실행
- GPU busy 시 least-busy GPU 또는 CPU fallback
- CPU descriptor workers도 background load에 따라 조정

Model 1/2의 scikit-learn tree ensemble은 `n_jobs=-1` 또는 설정값으로 Threadripper CPU를 적극 사용합니다.

---

## 7. Reference code와의 관계

`Com_Training_Visualization_v22.ipynb`에서 특히 참고한 부분:

- robust stress-strain parser
- common strain grid
- event/regime-aware densification concept
- group-safe CV
- direct property heads + curve model
- uncertainty / validation
- persistent handoff 철학

`Com_Optimization_v19.ipynb`에서 특히 참고한 부분:

- surrogate-assisted inverse design
- target-weighted utility
- uncertainty-aware search
- diverse candidate selection
- baseline/target validation philosophy

그러나 v19의 line/strut graph mutation은 Voxel geometry에 직접 적용하지 않았습니다. Voxel에는 continuous latent generator + hierarchical surrogate optimizer가 더 자연스러운 inverse variable입니다.
