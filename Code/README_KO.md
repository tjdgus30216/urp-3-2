# Architected Material Descriptor Exhaustive Notebook v3 (+ v4 additions)

## v4에서 추가된 것 (요약)
기존 v3 파이프라인은 그대로 유지하면서, 다음 5개 descriptor family/기능을 새로 추가했습니다. 새 의존성은 없습니다 (`networkx`는 v3 requirements.txt에 이미 있었지만 실제로는 쓰이지 않고 있었고, Radon/FBP는 이미 의존성인 `scikit-image`에 포함되어 있습니다).

1. **`curvature_descriptors`** — mesh 기반 discrete mean curvature(H) / Gaussian curvature(K) / 주곡률 k1,k2 / shape index / curvedness. v3에는 곡률 자체가 없었고(surface_dihedral_angle만 존재) elliptic(dome/node) vs hyperbolic(saddle/TPMS-sheet) vs parabolic(cylindrical/strut) 표면적 비율은 strut-lattice와 TPMS-sheet 구조를 구분하는 핵심 신호입니다.
2. **`tortuosity_descriptors`** — solid/void 각 phase, z/y/x 각 축에 대한 geodesic/직선거리 tortuosity(τ). Permeability(void)와 전기/열전도 경로(solid)의 표준 지표이며 v3에는 없었습니다.
3. **`strut_graph_descriptors`** — skeleton voxel을 실제 node/strut 격자 그래프로 축약: junction coordination number Z(Maxwell isostaticity 기준 3D 중심력 골격은 Z=6), strut 길이/tortuosity/두께-균일도(CV) 분포. v3의 skeleton family는 voxel 단위 degree 통계만 있었습니다.
4. **Grayscale 기반 soft-TSPE** (`load_image_stack_grayscale`, `soft_triplet_descriptor_table`) — 사용자가 제안한 "grayscale 기반 3-layer 중첩" 개념을 실제로 구현합니다. v3의 `load_image_stack`은 로드 시점에 즉시 이진화(`im>threshold`)했기 때문에, grayscale 정보가 TSPE 계산에 도달하기 전에 이미 손실되고 있었습니다. Zadeh fuzzy-AND(`min`)로 A/B/C를 연속값으로 재정의하고, hard-threshold 대비 정보 손실량(`soft_A_hard_agreement_dice`, `soft_*_partial_volume_fraction`)도 함께 보고합니다.
5. **`xray_ct_projection_reconstruction`** — 실제 X-ray CT 알고리즘(Radon forward projection + filtered back-projection, ramp filter)을 axial slice마다 적용해 별도의 재구성 파이프라인을 만들고, 원본 slice-stack과의 Dice/IoU/relative-density 오차를 계산합니다. Poisson noise(저선량) 시뮬레이션과 sparse-view(투사 수 감소) 비교도 포함됩니다. Raw projection 데이터만 있는 경우 이 함수를 직접 호출해 slice-stack 단계를 건너뛸 수 있습니다.

노트북에는 Cell 19b~19g로 삽입되어 있으며 Cell 20(aggregate)이 `features/*.json`을 전부 자동으로 읽기 때문에 별도 연결 작업 없이 `descriptors_ALL.csv`에 합쳐집니다. `test_descriptor_library_v4.py`가 5개 family 각각의 정확성(구형 곡률 H,K 이론값 대비 오차, TPMS gyroid의 saddle-dominant 판별, 직선/지그재그 채널의 tortuosity, 격자의 coordination number, soft/hard TSPE 일치성, CT 재구성 Dice)을 합성 데이터로 검증합니다.

## v4.1에서 추가된 것: STL/STEP 슬라이싱 "튀는 현상" 근본 수정 + STEP import 지원

**증상**: STL 또는 STEP을 import해서 슬라이싱하면 일부 slice 이미지에 노이즈 같은 선/조각이 생기고, 그 위치가 slice마다 달라지며(마치 "튀는" 것처럼) 겹쳐 보였습니다.

**근본 원인**: STL 포맷은 삼각형마다 정점 좌표 3개를 독립적으로 저장합니다(공유 정점 인덱스가 없음). 그래서 기하학적으로 같은 정점이라도 CAD 툴이 내보낼 때 삼각형마다 서로 다른 사본으로 기록되고, 이 사본들 사이에는 보통 1e-6~1e-9 mm 수준의 부동소수점 오차가 남습니다. 기존 슬라이싱 코드(`vectorized_segments`)는 각 정점의 높이를 `z<=0` / `z>0`으로만 분류했는데, 절단면이 이런 "같은 정점의 서로 다른 사본" 높이 근처를 지나가면 두 사본이 절단면 기준 서로 반대편으로 분류될 수 있습니다. 이는 해당 scanline row의 교차점 개수 짝/홀 판정을 뒤집어버리고, 래스터라이저는 이 모순을 해결할 방법이 없어 마지막 교차점을 그냥 버립니다(`odd_rows` 문제) — 그 결과가 slice마다 위치가 달라지는 찢어진 픽셀, 즉 사용자가 관찰한 "노이즈처럼 튀는" 현상입니다. 합성 8-삼각형 bipyramid로 재현한 결과, 1e-9 mm 수준의 미세한 정점 오차만으로도 120 row 중 39 row에서 문제가 발생함을 확인했습니다(`test_mesh_slicing_fix.py`).

**적용한 수정 (2단계 방어)**:
1. **`repair_mesh_for_slicing()`** (1차 방어, 원인 제거) — 슬라이싱 전에 mesh를 정리합니다: 근접 정점 welding(`merge_vertices`), 중복/퇴화 face 제거, normal 방향 일관성 수정(`trimesh.repair.fix_normals`), 작은 구멍 메우기(`trimesh.repair.fill_holes`). Welding 전/후 watertight 여부를 진단으로 기록합니다.
2. **`vectorized_segments()`의 `vtol` dead-zone** (2차 방어, welding으로 못 잡는 경우 대비) — 절단면으로부터 `vtol` 이내 거리에 있는 정점 높이는 판정 전에 한쪽으로 스냅합니다. 실제 교차점 좌표 계산에는 원래 좌표를 그대로 쓰므로 기하학적 정확도는 그대로 유지됩니다. Voxel 크기에 비례해 자동 설정됩니다(`voxel_size * 5e-4`, 최소 1e-7mm).

격자형 architected material은 strut들을 boolean union 없이 그냥 겹쳐서 내보내는 경우가 흔한데, 이런 self-intersecting mesh는 welding만으로는 완전히 고쳐지지 않을 수 있습니다. 이를 위해 **`load_mesh_as_voxels(..., backend='auto')`** 는 기본적으로 trimesh의 flood-fill 기반 solid voxelization(`mesh.voxelized(pitch).fill()`)을 먼저 시도합니다 — 이 방식은 scanline parity에 전혀 의존하지 않으므로 self-intersecting mesh에도 강건합니다. Mesh의 analytic volume과 비교하는 sanity check를 통과하지 못하거나 예외가 발생하면, (이제 수정된) legacy scanline 방식으로 자동 fallback합니다. 어느 backend를 썼는지, scanline 방식을 썼다면 몇 개 slice에서 여전히 odd-parity row가 남았는지는 `meta['voxelization_backend']`, `meta['slicing_qa']`에 그대로 기록되어 사용자가 직접 확인할 수 있습니다.

**STEP(.stp/.step) import**: 기존 코드는 사실 STL만 지원했고 STEP은 `MESH_EXTS`에도 없어 애초에 정상 동작하지 않았습니다(STEP은 삼각형이 아니라 NURBS surface/B-rep이라 trimesh가 직접 읽을 수 없습니다). 이번에 optional 패키지 `cadquery`(OpenCASCADE 바인딩)를 통해 `load_step_as_mesh()`를 추가했고, `load_mesh_as_voxels()`가 확장자(`.stp`/`.step`)를 보고 자동으로 이 경로로 라우팅합니다. `cadquery`가 없으면 즉시 명확한 에러 메시지(CAD 툴에서 STEP → STL로 export해서 대신 사용하라는 안내 포함)를 띄웁니다.

새 CONFIG 키 (Cell 02): `MESH_REPAIR` (기본 True, repair 단계 on/off), `MESH_VOXELIZATION_BACKEND` (`auto`/`trimesh_fill`/`legacy_scanline`, 기본 `auto`). 신규 함수: `repair_mesh_for_slicing`, `load_step_as_mesh`, `_trimesh_fill_voxelize`. 새 회귀 테스트: `test_mesh_slicing_fix.py` (trimesh 없이도 실행 가능하며, 합성 unwelded/jittered mesh로 fix 자체를 검증).

## 별도 테스트 노트북: `Architected_Material_Descriptor_Test_v3.ipynb`

`Architected_Material_Descriptor_Exhaustive_v3.ipynb`(본 코드)와는 **완전히 별개의 `.ipynb` 파일**입니다. STL 폴더의 실제 파일들을 순서대로 처리하면서 Jupyter 안에서 바로:
- 실제 slice 이미지(잘린 단면)를 matplotlib으로 화면에 표시하고,
- hard-TSPE / soft-TSPE A/B/C 중첩 이미지를 화면에 표시하고,
- 전체 exhaustive 구조인자 결과(`descriptors_ALL.csv`)와 v4.1 슬라이싱 진단(mesh repair, voxelization backend, odd-scanline QA)을 표/그래프로 보여줍니다.

내부적으로는 `stl_pipeline_driver.py`를 통해 본 노트북(`Architected_Material_Descriptor_Exhaustive_v3.ipynb`)의 코드 셀을 그대로 재실행하므로, 여기서 나오는 구조인자 결과는 본 노트북을 직접 돌린 것과 항상 동일합니다 — 로직을 별도로 다시 구현하지 않았기 때문에 두 결과가 서로 어긋날 위험이 없습니다. 그래서 이 파일은 `descriptor_library.py`, `stl_pipeline_driver.py`, `Architected_Material_Descriptor_Exhaustive_v3.ipynb`와 **같은 폴더**에 있어야 정상 동작합니다.

CONFIG 셀에 이미 요청하신 `STL_INPUT_DIR`/`OUTPUT_BASE_DIR`(`Test_YYYYMMDD_HHMMSS` 폴더 자동 생성) 경로가 기본값으로 들어 있습니다. Jupyter에서 열어 셀을 위에서부터 순서대로 실행하시면 되고, `FILE_INDEX` 값을 바꾸면 다른 STL 파일의 결과를 다시 확인할 수 있습니다. matplotlib이 새 의존성으로 추가되었습니다(`requirements.txt` 참고).

## 목적
Architected material의 3D 구조를 STL/mesh 또는 2D slice stack으로 입력받아, feature selection 이전 단계에서 가능한 한 넓은 구조인자 후보군을 추출합니다. 서로 유사하거나 상관성이 높은 descriptor도 의도적으로 유지합니다.

## 핵심 파일
- `Architected_Material_Descriptor_Exhaustive_v3.ipynb`: **본 노트북**. 셀별 checkpoint 구조.
- `Architected_Material_Descriptor_Test_v3.ipynb`: **[v4.1]** 본 노트북과는 별도의 **테스트 전용 노트북**. 실제 STL 폴더로 슬라이싱/중첩 이미지/구조인자 결과를 Jupyter 화면에서 바로 확인합니다. 자세한 내용은 아래 "별도 테스트 노트북" 절 참고.
- `descriptor_library.py`: 노트북 Cell 01이 자동 생성하는 동일 helper library의 독립 사본.
- `requirements.txt`: 기본 의존성.
- `VALIDATION.md`: synthetic end-to-end 검증 결과.
- `test_descriptor_library_v4.py`: v4 descriptor family(곡률/tortuosity/strut graph/soft-TSPE/CT 재구성) 정확성 검증.
- `test_mesh_slicing_fix.py`: **[v4.1]** STL 슬라이싱 "튀는 현상" 수정 회귀 테스트 (trimesh 불필요).
- `stl_pipeline_driver.py`: **[v4.1]** 아래 두 실행 스크립트가 공유하는 배치 실행 엔진. 노트북의 코드 셀을 그대로 재실행하는 방식이라 descriptor 계산 로직이 중복 구현되지 않습니다 (결과가 노트북을 직접 실행한 것과 항상 동일).
- `run_stl_batch_descriptor_extraction.py`: **[v4.1]** 폴더 안의 STL/STEP/OBJ/PLY 파일 전체를 일괄로 처리해 `Result_<날짜_시간>/`에 저장하는 실행 스크립트. 자세한 사용법은 아래 "실제 STL 파일로 실행하기" 참고.
- `test_stl_pipeline_visual.py`: **[v4.1]** 위와 같은 파이프라인을 돌리되, 실제 slice 이미지·A/B/C 중첩 이미지·핵심 구조인자 요약까지 눈으로 확인할 수 있게 `Test_<날짜_시간>/`에 저장하는 시각 검증용 스크립트.

## 3-layer TSPE 정의
연속 slice N, N+1, N+2를 3-bit state로 encode합니다.
- 111 = A: 세 layer 모두 겹침
- 110 = B: N & N+1만 겹침
- 011 = C: N+1 & N+2만 겹침
- 101 = gap/re-entry
- 100,010,001 = single-layer states
- 000 = background

A/B/C 이미지를 별도로 저장할 수 있으며, 동시에 8-state grayscale image도 보존하여 정보 손실을 줄였습니다.

## Restart-safe 구조
각 단계는 이전 셀의 메모리 변수를 사용하지 않고 `WORKDIR/checkpoints` 또는 `WORKDIR/features`에서 결과를 다시 읽습니다. 각 셀 실행 후 결과를 즉시 `.npz`, `.csv`, `.json`으로 저장합니다.

예시 checkpoint:
- `01_volume_raw.npz`
- `02_volume_processed.npz`
- `03_slice_summary.json`
- `06_triplet_summary.json`
- `10_topology.json`
- `12_spatial_statistics.json`
- `descriptors_ALL.csv`

따라서 커널이 초기화되어도 완료된 checkpoint가 남아 있다면 해당 다음 단계부터 계속 실행할 수 있습니다.

## Descriptor families
1. 2D slice morphology and z-profile statistics
2. Orthogonal projection GLCM texture / Hu moments / entropy / gradients
3. Adjacent 2-layer overlap/change/boundary-distance descriptors
4. 3-layer A/B/C TSPE + complete 8-state statistics
5. k-layer persistence (k=2..K)
6. multi-lag Jaccard/Dice/symmetric difference/mutual information
7. 8x8 TSPE transition matrix and state dynamics
8. 3D density/volume/surface/sphericity/compactness/convex hull/moments
9. topology: components, spanning, Euler, Betti proxies, enclosed voids
10. Euler filtration under erosion/dilation
11. local solid thickness / void diameter / skeleton-sampled thickness
12. morphological granulometry
13. chord-length distributions
14. lineal-path survival
15. directional two-point correlations
16. selected three-point correlations
17. box-counting fractal dimension and lacunarity
18. 3D FFT spectrum, dominant wavelength, spectral entropy and anisotropy
19. directional occupancy / mean intercept length / phase transitions
20. 3D skeleton and graph descriptors, graph spectra when manageable
21. optional cubical persistent homology (`gudhi`)
22. **[v4]** discrete mean/Gaussian curvature, principal curvatures, shape index, curvedness, elliptic/hyperbolic/parabolic area fraction (`curvature_*`)
23. **[v4]** solid/void geodesic transport tortuosity per axis (`tortuosity_*`)
24. **[v4]** strut/node lattice graph: coordination number, strut length/tortuosity/thickness-uniformity (`strut_*`)
25. **[v4]** grayscale-preserving soft/fuzzy TSPE + partial-volume diagnostics (`soft_triplet_*`)
26. **[v4]** X-ray CT Radon/FBP projection-reconstruction fidelity vs. direct stack (`ct_recon_*`)

## 검증된 feature 규모
Synthetic 20x20x20 periodic architecture에서 기본 exhaustive 설정(일부 test radius 축소, Gudhi 미설치)으로 `descriptors_ALL.csv`가 sample ID 포함 5,883 columns, 즉 5,882 scalar descriptor candidates를 생성했습니다(v3 기준). v4 추가 이후, 28-slice synthetic 3-strut cubic lattice에 기본 설정(축소 없음)으로 전체 노트북을 end-to-end 실행한 결과 `descriptors_ALL.csv`는 8,034 columns(8,033 scalar descriptor)를 생성했으며, 이 중 신규 v4 columns는 curvature 132 + tortuosity 8 + strut 153 + soft_triplet 1,742 + ct_recon 74 = **2,109개**입니다. 실제 개수는 slice 수, lag/K 설정, optional dependency 등에 따라 달라질 수 있습니다.

## 사용 순서 (노트북을 직접, 파일 1개씩 실행하는 경우)
1. Cell 01 실행: helper library 저장.
2. Cell 02의 `INPUT_PATH`, voxel/slice resolution, `WORKDIR` 수정 후 실행.
3. Cell 03 이후 순서대로 실행.
4. 중간 중단 시 이미 완료된 checkpoint 다음 cell부터 재개.
5. 최종 `features/descriptors_ALL.csv`를 별도의 feature-selection 코드로 전달.

## 실제 STL 파일로 실행하기 (폴더 일괄 처리, v4.1)

STL 폴더 전체를 자동 처리하는 방법이 3가지 있습니다. 모두 `descriptor_library.py`, `stl_pipeline_driver.py`, `Architected_Material_Descriptor_Exhaustive_v3.ipynb`와 **같은 폴더**에 두고 실행해야 합니다(내부적으로 본 노트북의 코드 셀을 그대로 재실행해서 결과 일관성을 보장하는 방식이라, 이 세 파일이 한 세트로 필요합니다).

0. **`Architected_Material_Descriptor_Test_v3.ipynb`** (Jupyter 노트북, 시각 확인용 — 별도 파일로 요청하신 "테스트 코드"). Jupyter에서 열어 셀을 순서대로 실행하면, 실제 slice 이미지·A/B/C 중첩 이미지·구조인자 결과를 노트북 화면에 바로 표시해 눈으로 확인할 수 있습니다. `Test_YYYYMMDD_HHMMSS\` 폴더에 결과도 함께 저장됩니다. 자세한 내용은 아래 "별도 테스트 노트북" 절 참고.
1. **`run_stl_batch_descriptor_extraction.py`** — 본 작업용 스크립트(터미널에서 실행, 화면 표시 없이 파일로만 저장). 스크립트 상단 CONFIG의 `STL_INPUT_DIR`(STL 폴더), `OUTPUT_BASE_DIR`(결과 상위 폴더)를 확인한 뒤 `python run_stl_batch_descriptor_extraction.py` 실행. `STL_INPUT_DIR` 안의 모든 STL/STEP/OBJ/PLY 파일을 이름순으로 순차 처리하고, `OUTPUT_BASE_DIR\Result_YYYYMMDD_HHMMSS\` 아래에 파일별 결과 폴더(노트북과 동일한 checkpoints/features/images 구조) + 전체를 합친 `MASTER_descriptors_ALL.csv` + `batch_run_log.csv`(파일별 성공/실패/소요시간)를 저장합니다. 파일 하나가 실패해도 나머지는 계속 진행됩니다.
2. **`test_stl_pipeline_visual.py`** — 위 Test 노트북과 같은 목적이지만 터미널 스크립트 버전(화면 표시 없이 이미지를 파일로만 저장). 실제 slice 이미지(`images/raw_slices/`), hard-TSPE A/B/C 중첩 이미지(`images/triplets/`), grayscale soft-TSPE 중첩 이미지(`images/soft_triplets/`), 슬라이싱에서 역재구성한 STL(`reconstructed_from_slices.stl`), 핵심 구조인자 요약(`summary.txt`/`summary.json`)을 파일별로 저장합니다. `OUTPUT_BASE_DIR\Test_YYYYMMDD_HHMMSS\`에 저장됩니다.

모두 처음 실행할 때는 `MAX_FILES`를 1~2로 낮춰서 먼저 빠르게 확인해보는 것을 권장합니다(exhaustive 모드는 파일당 몇 분 걸릴 수 있습니다). `VOXEL_SIZE_MM`은 구조의 최소 특징 크기(strut 두께 등)보다 3~5배 작게 설정해야 형상을 제대로 포착합니다. STEP(.stp/.step) 파일을 쓰신다면 `cadquery`도 설치해야 합니다(`pip install cadquery`).

## 주의
- Feature pool을 의도적으로 크게 만들었으므로 NaN/constant/highly-correlated feature가 존재할 수 있습니다. `descriptor_QA.csv`에서 먼저 확인하세요.
- Surface/thickness/chord 등 길이 기반 descriptor는 voxel/slice spacing calibration에 직접 의존합니다.
- Persistent homology는 optional이며 `gudhi`가 없으면 자동으로 skip flag를 저장합니다.
- **[v4]** `trimesh`가 설치되지 않은 환경에서도 이제 전체 노트북이 끝까지 실행됩니다: mesh 기반 descriptor(`surface_*`, STL export)는 자동으로 skip flag를 남기고 건너뜁니다. 신규 curvature family는 trimesh 없이 `scikit-image`만으로 동작합니다.
- **[v4]** `curvature_*`의 elliptic/hyperbolic/parabolic 분류는 절대 threshold(`1e-6`, 코드 내 `k_eps`)를 사용합니다. voxel/spacing 단위가 mm 스케일에서 크게 벗어나면(예: 미터 단위의 sub-micron voxel) 이 값을 구조의 실제 곡률 스케일에 맞게 조정해야 합니다.
- **[v4]** `tortuosity_*`와 `strut_tortuosity`는 해당 phase가 해당 축을 따라 spanning/percolate하지 않으면(또는 skeleton이 없으면) NaN을 반환합니다 — 이는 버그가 아니라 "정의되지 않음"입니다.
- **[v4]** `ct_recon_*`는 이미 확보한 slice-stack을 가상으로 재-투사/재구성해 cross-validation하는 용도입니다. 실제 raw projection(sinogram)이 있다면 `xray_ct_projection_reconstruction`을 직접 그 데이터에 맞게 변형해 호출하십시오.
- **[v4.1]** STEP(.stp/.step) import에는 `trimesh` 외에 optional `cadquery`가 추가로 필요합니다. 설치가 어렵다면 CAD 툴에서 STL로 export해서 사용하세요.
- **[v4.1]** `backend='auto'`가 `trimesh_fill`을 쓰지 못하고 `legacy_scanline`으로 fallback한 경우, 또는 legacy_scanline을 직접 지정한 경우, `meta['slicing_qa']['n_odd_slices']`가 0보다 크면 해당 index의 slice는 여전히 완벽하지 않을 수 있습니다(대부분 mesh가 심하게 non-manifold인 경우). 이때는 `backend='trimesh_fill'`을 강제하거나 CAD 단계에서 strut들을 boolean union 해서 내보내는 것을 권장합니다.
