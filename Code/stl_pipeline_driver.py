# -*- coding: utf-8 -*-
"""
Shared driver used by both `run_stl_batch_descriptor_extraction.py` (Result_* 배치 실행) and
`test_stl_pipeline_visual.py` (Test_* 시각 검증). It runs the FULL
Architected_Material_Descriptor_Exhaustive_v3 notebook pipeline against one input mesh
by directly re-executing the notebook's own code cells (the same approach used internally
by run_notebook_e2e_test.py) -- no descriptor logic is duplicated or re-implemented here,
so results are guaranteed identical to running the notebook interactively in Jupyter.

Keep this file, descriptor_library.py, and Architected_Material_Descriptor_Exhaustive_v3.ipynb
in the SAME folder. Both entry-point scripts add that folder to sys.path automatically.
"""
from __future__ import annotations
import json
import time
import traceback
from pathlib import Path

DEFAULT_CONFIG = {
    "INPUT_PATH": r"CHANGE_ME/sample.stl",
    "WORKDIR": r"descriptor_run",
    "INPUT_KIND": "mesh",
    "VOXEL_SIZE_MM": 0.20,
    "DX_MM": 0.20, "DY_MM": 0.20, "DZ_MM": 0.20,
    "THRESHOLD": 127, "INVERT": False,
    "Z_UPSAMPLE": 1,
    "MIN_COMPONENT_VOXELS": 1,
    "FILL_HOLES": False,
    "SAVE_TRIPLET_IMAGES": True,
    "TRIPLET_IMAGE_STRIDE": 1,
    "MAX_LAYER_LAG": 12,
    "MAX_PERSISTENCE_K": 7,
    "GRANULOMETRY_MAX_RADIUS": 8,
    "EULER_FILTRATION_MAX_RADIUS": 6,
    "SPECTRAL_MAX_DIM": 128,
    "OPTIONAL_PERSISTENT_HOMOLOGY": True,
    "PH_MAX_DIM_VOX": 64,
    "MODE": "exhaustive",
    # --- v4 ---
    "CURVATURE_SMOOTH_ITERATIONS": 12,
    "TORTUOSITY_MAX_SIDE": 48,
    "STRUT_GRAPH_MAX_SKELETON_VOXELS": 250000,
    "SOFT_TSPE_FALLBACK_BLUR_SIGMA": 0.8,
    "COMPUTE_CT_RECONSTRUCTION": True,
    "CT_RECON_N_ANGLES_FULL": 180,
    "CT_RECON_N_ANGLES_SPARSE": 60,
    "CT_RECON_ADD_POISSON_NOISE": False,
    # --- v4.1: mesh-slicing robustness ---
    "MESH_REPAIR": True,
    "MESH_VOXELIZATION_BACKEND": "auto",
}

# Notebook cells this driver replaces / handles itself, so they are skipped during
# per-file execution:
#   4  -- CONFIG cell (we build+write config.json ourselves, per input file)
#   58 -- cross-run MASTER_descriptors_ALL.csv aggregator (we aggregate across the whole
#         batch ourselves, in the calling script, instead of one run at a time)
# Cell 2 (writes descriptor_library.py from the embedded LIB_SOURCE) is intentionally NOT
# skipped -- it is cheap and idempotent, and re-running it every iteration guarantees the
# library on disk always matches this exact notebook, even if this driver is copied
# somewhere without descriptor_library.py alongside it.
SKIP_CELL_INDICES = {4, 58}

MESH_FILE_EXTS = ('.stl', '.step', '.stp', '.obj', '.ply')


def find_notebook_path(engine_dir: Path) -> Path:
    candidates = sorted(engine_dir.glob('Architected_Material_Descriptor_Exhaustive_v3*.ipynb'))
    if not candidates:
        raise FileNotFoundError(
            f"Notebook not found in {engine_dir}. Keep this script in the same folder as "
            f"Architected_Material_Descriptor_Exhaustive_v3.ipynb and descriptor_library.py."
        )
    return candidates[0]


def load_notebook_cells(nb_path: Path):
    nb = json.loads(nb_path.read_text(encoding='utf-8'))
    return nb['cells']


def discover_input_files(input_dir: Path):
    """Every STL/STEP/OBJ/PLY file directly inside input_dir (not recursive), case-insensitive
    extension match, de-duplicated, sorted by filename."""
    seen = set()
    out = []
    for p in sorted(input_dir.iterdir(), key=lambda x: x.name.lower()):
        if p.is_file() and p.suffix.lower() in MESH_FILE_EXTS:
            key = p.resolve()
            if key not in seen:
                seen.add(key)
                out.append(p)
    return out


def run_pipeline_for_one_input(cells, input_path: Path, workdir: Path, config_overrides: dict,
                                log_fn=print):
    """Executes the notebook's descriptor-extraction cells against ONE mesh file, writing all
    outputs under `workdir` (checkpoints/, features/, images/, logs/). Returns
    (ok: bool, elapsed_sec: float, error_str_or_None).

    A failure on one file (corrupt STL, unsupported geometry, etc.) is caught, logged to
    workdir/logs/error.txt, and reported back to the caller WITHOUT raising -- so a batch of
    many files keeps going instead of stopping at the first bad one.
    """
    t0 = time.time()
    for d in ('checkpoints', 'features', 'images', 'logs'):
        (workdir / d).mkdir(parents=True, exist_ok=True)

    cfg = dict(DEFAULT_CONFIG)
    cfg['INPUT_PATH'] = str(input_path)
    cfg['WORKDIR'] = str(workdir)
    cfg.update(config_overrides or {})
    (workdir / 'config.json').write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding='utf-8')
    # The notebook's cells locate the active run via this pointer file, resolved relative to CWD.
    Path('.architected_descriptor_active_workdir.txt').write_text(str(workdir), encoding='utf-8')

    namespace = {'display': lambda *a, **k: None}  # notebook cells call display(); no-op outside Jupyter
    for idx, cell in enumerate(cells):
        if idx in SKIP_CELL_INDICES or cell.get('cell_type') != 'code':
            continue
        src = ''.join(cell.get('source', []))
        try:
            exec(src, namespace)
        except Exception:
            err = f"cell {idx} failed:\n{traceback.format_exc()}"
            log_fn(f"  [ERROR] {err}")
            (workdir / 'logs' / 'error.txt').write_text(err, encoding='utf-8')
            return False, time.time() - t0, err
    return True, time.time() - t0, None


def save_raw_slice_images(workdir: Path, stride: int = 1, max_slices: int = 300):
    """Extra visual-QA output the notebook itself does not produce: dumps the actual
    post-processing binary slice volume as one PNG per slice, so 'did this STL actually
    slice into something sane' can be checked by eye without opening the .npz checkpoint in
    code. Returns the number of PNGs written (0 if no checkpoint was found, e.g. the run
    failed before Cell 04/Cell 07)."""
    import numpy as np
    from PIL import Image
    ckpt = workdir / 'checkpoints' / '02_volume_processed.npz'
    if not ckpt.exists():
        ckpt = workdir / 'checkpoints' / '01_volume_raw.npz'
    if not ckpt.exists():
        return 0
    z = np.load(ckpt, allow_pickle=False)
    vol = z['volume'].astype(bool)
    out_dir = workdir / 'images' / 'raw_slices'
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for i in range(0, vol.shape[0], max(1, stride)):
        if n >= max_slices:
            break
        Image.fromarray((vol[i] * 255).astype('uint8')).save(out_dir / f'slice_{i:04d}.png')
        n += 1
    return n


KEY_DESCRIPTORS_OF_INTEREST = [
    'relative_density',
    'surface_area_mm2', 'surface_to_volume_ratio_per_mm', 'surface_sphericity',
    'solid_local_thickness_mean_mm', 'solid_local_thickness_min_mm', 'solid_local_thickness_cv',
    'void_local_diameter_mean_mm',
    'curvature_area_weighted_mean_H_per_mm', 'curvature_area_weighted_mean_K_per_mm2',
    'curvature_area_fraction_elliptic', 'curvature_area_fraction_hyperbolic', 'curvature_area_fraction_parabolic',
    'tortuosity_solid_mean_xyz', 'tortuosity_void_mean_xyz',
    'strut_network_mean_coordination_number_Z', 'strut_count',
    'topology_components_count', 'topology_euler_characteristic',
    'mesh_repair', 'voxelization_backend',
]


def summarize_key_descriptors(workdir: Path):
    """Best-effort headline summary: reads features/descriptors_ALL.csv (produced by the
    notebook's own aggregation cell) plus checkpoints/01_input_meta.json (mesh-import
    diagnostics: repair report, voxelization backend, odd-scanline-row QA -- see the v4.1
    STL slicing fix), and returns a small flat dict for quick eyeballing. Missing keys are
    silently skipped rather than raising -- exact descriptor names can shift slightly with
    MODE/config, so this is a convenience view, not a schema contract; the full
    descriptors_ALL.csv is always the source of truth."""
    import pandas as pd
    out = {}
    csv_path = workdir / 'features' / 'descriptors_ALL.csv'
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if len(df):
            row = df.iloc[0].to_dict()
            for k in KEY_DESCRIPTORS_OF_INTEREST:
                if k in row:
                    out[k] = row[k]
            out['_descriptor_count'] = int(len(df.columns) - 1)
    meta_path = workdir / 'checkpoints' / '01_input_meta.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        out['_voxelization_backend'] = meta.get('voxelization_backend')
        out['_mesh_repair'] = meta.get('mesh_repair')
        qa = meta.get('slicing_qa', {})
        if qa:
            out['_slicing_qa_n_odd_slices'] = qa.get('n_odd_slices')
            out['_slicing_qa_n_slices'] = qa.get('n_slices')
    return out
