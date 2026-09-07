# AI-Voxel ML + Inverse Design v4 — 30,000 Candidate / 96 Descriptor-LHS Profile

## 이번 수정의 핵심

- Import/workspace: `C:\Users\Administrator\Desktop\Minkyeom\AI-Voxel\Voxel generation`
- 새 run을 시작하면 `Result_YYYYMMDD_HHMMSS`가 자동 생성됩니다.
- 전체 candidate Voxel: **30,000개**
- Descriptor-space LHS 최종 선정: **96개**
- 30,000개 pool은 기본적으로 0.10 mm screening grid(300³)로 생성하고, 선정 96개는 0.03 mm(1000³)로 재생성합니다.
- 30k 규모에 맞춰 generation aggregate log는 item-level STL/JSON checkpoint를 유지하면서 25개 단위로 flush합니다.
- Descriptor-LHS PCA는 float32 + randomized PCA를 기본 사용하여 full SVD보다 대규모 pool에 적합하게 수정했습니다.

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

