# Auto-generated durable runtime for AI-Voxel workflow v2.
# This file is deliberately importable from a fresh Jupyter kernel.
from __future__ import annotations
import os, sys, gc, json, math, time, traceback, warnings, shutil, hashlib, platform, tempfile
from pathlib import Path
from dataclasses import dataclass
from itertools import product, permutations
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.ndimage import gaussian_filter, binary_closing, binary_opening, binary_dilation, label, distance_transform_edt
from scipy.stats import qmc
from skimage import measure
import trimesh

try:
    from threadpoolctl import threadpool_limits
except Exception:
    class _NoLimit:
        def __enter__(self): return self
        def __exit__(self,*a): return False
    def threadpool_limits(*a, **k): return _NoLimit()

try:
    from IPython.display import display
except Exception:
    def display(x): print(x)

warnings.filterwarnings('ignore')

DEFAULT_BASE_DIR = Path(r"C:\Users\Administrator\Desktop\Minkyeom\AI-Voxel\Voxel generation")
ACTIVE_POINTER_FILENAME = '.ai_voxel_active_run.json'

def _pointer_path():
    env = os.environ.get('AI_VOXEL_ACTIVE_POINTER','').strip()
    if env:
        return Path(env)
    return DEFAULT_BASE_DIR / ACTIVE_POINTER_FILENAME

def _json_default(x):
    if isinstance(x, Path): return str(x)
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (np.floating,)): return float(x)
    if isinstance(x, np.ndarray): return x.tolist()
    return str(x)

def atomic_json(path, obj):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=_json_default), encoding='utf-8')
    os.replace(tmp, path)
    return path

def atomic_csv(df, path):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    df.to_csv(tmp, index=False, encoding='utf-8-sig')
    os.replace(tmp, path)
    return path

def atomic_pickle(df, path):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    df.to_pickle(tmp)
    os.replace(tmp, path)
    return path

def load_active_settings():
    ptr=_pointer_path()
    if not ptr.exists():
        raise FileNotFoundError(f'Active-run pointer not found: {ptr}. Run CELL 1 once.')
    meta=json.loads(ptr.read_text(encoding='utf-8'))
    run_dir=Path(meta['run_dir'])
    config_path=run_dir/'00_state'/'config.json'
    if not config_path.exists():
        raise FileNotFoundError(f'Run config not found: {config_path}. Run CELL 1 once.')
    s=json.loads(config_path.read_text(encoding='utf-8'))
    return s, run_dir, config_path

SETTINGS, RUN_DIR, CONFIG_PATH = load_active_settings()
_HASH_EXCLUDE={'FORCE_RERUN_STAGES','RESUME_SKIP_COMPLETED','SAVE_PICKLE_CHECKPOINTS','CREATE_NEW_TIMESTAMPED_RUN','START_NEW_RESULT_RUN'}
_hash_payload={k:v for k,v in SETTINGS.items() if k not in _HASH_EXCLUDE}
CONFIG_HASH=hashlib.sha256(json.dumps(_hash_payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()

_PATH_KEYS = {
    'BASE_DIR','RUN_DIR','STATE_DIR','STAGE_DIR','CHECKPOINT_DIR','RUNTIME_DIR','ENGINE_DIR',
    'POOL_ROOT','POOL_STL_DIR','POOL_DLP_RAW_DIR','POOL_DLP_DIR','POOL_DESCRIPTOR_DIR',
    'SELECTED_ROOT','SELECTED_STL_DIR','SELECTED_DLP_RAW_DIR','SELECTED_DLP_DIR','SELECTED_DESCRIPTOR_DIR',
    'TABLE_DIR','CANDIDATE_ROOT','SELECTION_ROOT','ML_ROOT','ML_PROJECT_ROOT','MODEL_ROOT','INVERSE_ROOT','ACTIVE_ROOT','VALIDATION_ROOT','DLP_TEMPLATE_SLICE_DIR','POOL_MASTER_XLSX','SELECTED_MASTER_XLSX','SELECTION_XLSX'
}
for _k,_v in SETTINGS.items():
    if _k in _PATH_KEYS:
        globals()[_k]=Path(_v)
    else:
        globals()[_k]=_v

STATE_DIR=Path(SETTINGS.get('STATE_DIR', RUN_DIR/'00_state'))
STAGE_DIR=Path(SETTINGS.get('STAGE_DIR', STATE_DIR/'stages'))
CHECKPOINT_DIR=Path(SETTINGS.get('CHECKPOINT_DIR', STATE_DIR/'checkpoints'))
RUNTIME_DIR=Path(SETTINGS.get('RUNTIME_DIR', RUN_DIR/'_runtime'))
ENGINE_DIR=Path(SETTINGS.get('ENGINE_DIR', RUN_DIR/'_descriptor_engine'))
for _p in (STATE_DIR,STAGE_DIR,CHECKPOINT_DIR,RUNTIME_DIR,ENGINE_DIR): _p.mkdir(parents=True, exist_ok=True)

@dataclass
class STLSliceConfig:
    canvas_w: int
    canvas_h: int
    target_length_mm: float
    pixel_size_mm: float
    part_px: int
    layer_height_mm: float
    fixed_layer_count: int
    six_region_crop_w: int=640
    six_region_crop_h: int=540
    additional_front_layers: int=5
    recursive_stl_search: bool=True
    recenter_xy: bool=True
    shift_z_min_to_zero: bool=True
    auto_scale_to_target: bool=False
    max_workers: int=1
    foreground: int=255
    background: int=0
    verbose: bool=False

CFG=STLSliceConfig(
    canvas_w=int(DLP_CANVAS_W), canvas_h=int(DLP_CANVAS_H),
    target_length_mm=float(BOUNDARY_SIZE_MM), pixel_size_mm=float(DLP_PIXEL_SIZE_MM),
    part_px=int(DLP_PART_PX), layer_height_mm=float(DLP_LAYER_HEIGHT_MM),
    fixed_layer_count=int(DLP_FIXED_LAYER_COUNT), max_workers=int(DLP_PARALLEL_WORKERS),
    verbose=bool(DLP_VERBOSE),
)
SIX_REGION_POSITIONS={1:(0,0),2:(CFG.six_region_crop_w,0),3:(2*CFG.six_region_crop_w,0),4:(0,CFG.six_region_crop_h),5:(CFG.six_region_crop_w,CFG.six_region_crop_h),6:(2*CFG.six_region_crop_w,CFG.six_region_crop_h)}

# DLP globals used by reference code
OUTPUT_ROOT=RUN_DIR
COM_INDIVIDUAL_CROP_PX=CFG.part_px
COM_INDIVIDUAL_MAP_TO_CANVAS=False
RAW_DATA_SAVE_AS_CENTER_CROP=False
RAW_DATA_CENTER_CROP_PX=COM_INDIVIDUAL_CROP_PX
RAW_BOUNDARY_MARGIN_PX=2
RAW_FORCE_ODD_IMAGE_SIZE=True
RAW_SAVE_BOUNDARY_INFO=True
MESH_PROCESS_VALIDATE=True
MESH_MERGE_VERTICES=True
MESH_FIX_NORMALS=True
SECTION_FILL_RULE='nested'
SECTION_REQUIRE_CLOSED_LOOPS=True
SECTION_CLOSE_TOLERANCE_MM=max(CFG.pixel_size_mm*1.5,1e-6)
SECTION_MIN_LOOP_AREA_MM2=max((CFG.pixel_size_mm**2)*0.20,1e-10)
STL_RASTER_MODE='scanline'
SCANLINE_SOLID_RULE='even_odd'
SCANLINE_INTERSECTION_TOL_MM=max(CFG.pixel_size_mm*1e-6,1e-9)
SCANLINE_VERTEX_JITTER_MM=max(CFG.pixel_size_mm*1e-4,1e-8)
SCANLINE_MAX_JITTER_RETRIES=4
SCANLINE_FAIL_ON_UNCLOSED_WINDING=False
SCANLINE_SUBPIXEL_STABILIZATION=True
SCANLINE_SUBPIXEL_OFFSET_FRACTION=0.20
SCANLINE_SUBPIXEL_MODE='majority_3'
SCANLINE_SINGLE_ROW_GUARD=True
SCANLINE_SINGLE_ROW_MIN_LENGTH_MM=0.75
SCANLINE_SINGLE_ROW_MIN_LENGTH_PX=max(3,int(np.ceil(SCANLINE_SINGLE_ROW_MIN_LENGTH_MM/CFG.pixel_size_mm)))
NODE_JUNCTION_REPAIR=False
NODE_JUNCTION_REPAIR_MODE='bounded_local_winding_components'
NODE_REPAIR_MIN_AREA_PX=3
NODE_REPAIR_MAX_SPAN_MM=1.60
NODE_REPAIR_MAX_AREA_MM2=1.20
NODE_REPAIR_MAX_ASPECT_RATIO=4.0
NODE_REPAIR_MIN_BASE_CONTACT_PX=1
NODE_REPAIR_CONNECTIVITY=8
NODE_REPAIR_MAX_SPAN_PX=max(3,int(np.ceil(NODE_REPAIR_MAX_SPAN_MM/CFG.pixel_size_mm)))
NODE_REPAIR_MAX_AREA_PX=max(8,int(np.ceil(NODE_REPAIR_MAX_AREA_MM2/(CFG.pixel_size_mm**2))))

# CUDA auto-selection: Windows Task Manager GPU numbering is intentionally ignored.
def detect_cuda_device(preferred_name='RTX 4070'):
    info={'cupy_available':False,'devices':[],'selected_cuda_device':None,'selected_name':None}
    try:
        import cupy as _cp
        info['cupy_available']=True
        n=int(_cp.cuda.runtime.getDeviceCount())
        preferred=str(preferred_name).lower()
        for i in range(n):
            prop=_cp.cuda.runtime.getDeviceProperties(i)
            name=prop.get('name',b'') if isinstance(prop,dict) else b''
            if isinstance(name,(bytes,bytearray)): name=name.decode(errors='replace')
            free,total=_cp.cuda.runtime.memGetInfo() if i==0 else (None,None)
            info['devices'].append({'cuda_id':i,'name':str(name)})
        selected=None
        for d in info['devices']:
            if preferred and preferred in d['name'].lower(): selected=d['cuda_id']; break
        if selected is None and info['devices']: selected=info['devices'][0]['cuda_id']
        if selected is not None:
            _cp.cuda.Device(selected).use()
            prop=_cp.cuda.runtime.getDeviceProperties(selected)
            name=prop.get('name',b'') if isinstance(prop,dict) else b''
            if isinstance(name,(bytes,bytearray)): name=name.decode(errors='replace')
            free,total=_cp.cuda.runtime.memGetInfo()
            info.update({'selected_cuda_device':int(selected),'selected_name':str(name),'free_vram_GB':free/1024**3,'total_vram_GB':total/1024**3})
    except Exception as e:
        info['error']=f'{type(e).__name__}: {e}'
    return info

CUDA_INFO=detect_cuda_device(SETTINGS.get('GPU_PREFERRED_NAME','RTX 4070')) if SETTINGS.get('ENABLE_NVIDIA_GPU',True) else {'selected_cuda_device':None}
CUDA_DEVICE_ID=CUDA_INFO.get('selected_cuda_device')
DESCRIPTOR_GPU_IDS=[int(CUDA_DEVICE_ID)] if CUDA_DEVICE_ID is not None else []

# Engine import
if str(ENGINE_DIR) not in sys.path: sys.path.insert(0,str(ENGINE_DIR))
try:
    import descriptor_library as dl
    import stl_pipeline_driver as drv
except Exception:
    dl=drv=None

def stage_manifest_path(stage): return STAGE_DIR/f'{stage}.json'
def save_stage_manifest(stage,status,outputs=None,metadata=None):
    obj={'stage':stage,'status':status,'updated_at':time.strftime('%Y-%m-%dT%H:%M:%S'),'config_sha256':CONFIG_HASH,'outputs':[str(x) for x in (outputs or [])],'metadata':metadata or {}}
    atomic_json(stage_manifest_path(stage),obj); return obj

def load_stage_manifest(stage):
    p=stage_manifest_path(stage)
    if not p.exists(): return None
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def stage_can_resume(stage, required_outputs=()):
    if stage in set(SETTINGS.get('FORCE_RERUN_STAGES',[])): return False
    if not bool(SETTINGS.get('RESUME_SKIP_COMPLETED',True)): return False
    m=load_stage_manifest(stage)
    if not m or m.get('status')!='completed' or m.get('config_sha256')!=CONFIG_HASH: return False
    return all(Path(p).exists() for p in required_outputs)

def save_df_checkpoint(df,name):
    csv=CHECKPOINT_DIR/f'{name}.csv'; pkl=CHECKPOINT_DIR/f'{name}.pkl'
    atomic_csv(df,csv)
    if bool(SETTINGS.get('SAVE_PICKLE_CHECKPOINTS',True)): atomic_pickle(df,pkl)
    return csv

def load_df_checkpoint(name, required=True):
    pkl=CHECKPOINT_DIR/f'{name}.pkl'; csv=CHECKPOINT_DIR/f'{name}.csv'
    if pkl.exists(): return pd.read_pickle(pkl)
    if csv.exists(): return pd.read_csv(csv)
    if required: raise FileNotFoundError(f'Checkpoint not found: {name} in {CHECKPOINT_DIR}')
    return pd.DataFrame()

def hardware_report():
    try:
        import psutil
        phys=psutil.cpu_count(logical=False); logical=psutil.cpu_count(logical=True); ram=psutil.virtual_memory().total/1024**3
    except Exception:
        phys=SETTINGS.get('CPU_PHYSICAL_CORES',12); logical=os.cpu_count(); ram=None
    return {
        'platform':platform.platform(),'python':sys.version,
        'cpu_physical_detected':phys,'cpu_logical_detected':logical,'ram_GB':ram,
        'cpu_physical_configured':SETTINGS.get('CPU_PHYSICAL_CORES',12),
        'cpu_workers_descriptor':SETTINGS.get('DESCRIPTOR_CPU_WORKERS',12),
        'dlp_parallel_workers':SETTINGS.get('DLP_PARALLEL_WORKERS',8),
        'cuda':CUDA_INFO,
        'note':'AMD Radeon integrated GPU is not selected. CUDA IDs enumerate NVIDIA CUDA devices only.'
    }


# ===== VOXEL CORE =====
# ============================================================
# CELL 3 — VOXEL GENERATION CORE (extracted/adapted from Model Generator)
# ============================================================

def json_dumps(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)

def estimate_mask_vf(mask):
    return float(np.mean(mask.astype(bool)))

def mesh_from_binary_mask(mask, size_mm=8.0):
    """Convert boolean voxel mask to closed triangular mesh using low/high quality marching cubes."""
    mask = np.asarray(mask, dtype=bool)
    if np.count_nonzero(mask) == 0:
        return np.empty((0, 3), dtype=np.float32), np.empty((0, 3), dtype=np.int32)

    # Padding closes boundary surfaces.
    padded = np.pad(mask.astype(np.float32), pad_width=1, mode="constant", constant_values=0)
    spacing = (size_mm / mask.shape[0], size_mm / mask.shape[1], size_mm / mask.shape[2])

    step_size = max(1, int(globals().get("MARCHING_CUBES_STEP_SIZE", 1)))
    verts, faces, normals, values = measure.marching_cubes(
        padded,
        level=0.5,
        spacing=spacing,
        step_size=step_size,
        allow_degenerate=False,
    )

    # Remove padding offset.
    verts -= np.array(spacing)
    verts = np.clip(verts, 0.0, size_mm)
    return verts.astype(np.float32), faces.astype(np.int32)

def keep_largest_component(mask):
    lab, n = label(mask)
    if n == 0:
        return mask
    counts = np.bincount(lab.ravel())
    counts[0] = 0
    return lab == int(np.argmax(counts))

def count_connected_components(mask):
    """Return the number of 6-neighbor connected solid components."""
    _, n = label(np.asarray(mask, dtype=bool))
    return int(n)

def _draw_voxel_bridge(mask, p0, p1, radius_vox=1):
    """Draw a 6-neighbor Manhattan voxel bridge between two coordinates.

    A straight rounded line can leave diagonally touching components disconnected
    under 6-neighbor labeling. This function moves one axis at a time, so the
    inserted bridge is guaranteed to be face-connected.
    """
    mask = np.asarray(mask, dtype=bool).copy()
    p0 = np.asarray(np.rint(p0), dtype=int)
    p1 = np.asarray(np.rint(p1), dtype=int)
    n = np.asarray(mask.shape, dtype=int)
    p0 = np.clip(p0, 0, n - 1)
    p1 = np.clip(p1, 0, n - 1)

    coords = []
    cur = p0.copy()
    coords.append(cur.copy())

    # Move along axes in descending gap order. This gives the shortest
    # Manhattan bridge while preserving 6-neighbor continuity.
    axis_order = list(np.argsort(-np.abs(p1 - p0)))
    for ax in axis_order:
        step = 1 if p1[ax] > cur[ax] else -1
        while cur[ax] != p1[ax]:
            cur = cur.copy()
            cur[ax] += step
            coords.append(cur.copy())

    coords = np.asarray(coords, dtype=int)
    coords = np.clip(coords, 0, n - 1)
    bridge = np.zeros_like(mask, dtype=bool)
    bridge[coords[:, 0], coords[:, 1], coords[:, 2]] = True

    r = max(0, int(radius_vox) - 1)
    if r > 0:
        bridge = binary_dilation(bridge, iterations=r)

    before = int(mask.sum())
    mask |= bridge
    added = int(mask.sum()) - before
    return mask, added

def repair_mask_connectivity(mask, mode="bridge", bridge_radius_vox=1, min_component_voxels=1, max_bridges=200):
    """Force a binary solid mask to become one connected component.

    mode="bridge" connects disconnected islands to the largest component using
    shortest voxel bridges. mode="largest" simply keeps the largest component.
    TPMS is not repaired unless this function is explicitly called.
    """
    mask = np.asarray(mask, dtype=bool).copy()
    info = {
        "component_count_before": count_connected_components(mask),
        "component_count_after": None,
        "connectivity_repaired": False,
        "connectivity_mode": str(mode),
        "bridges_added": 0,
        "voxels_added_by_bridges": 0,
        "small_components_removed": 0,
    }
    if info["component_count_before"] <= 1:
        info["component_count_after"] = info["component_count_before"]
        return mask, info

    lab, ncomp = label(mask)
    counts = np.bincount(lab.ravel())
    counts[0] = 0

    # Remove dust components if requested. Use 1 to keep and connect every island.
    min_size = max(1, int(min_component_voxels))
    if min_size > 1:
        remove_ids = [i for i in range(1, ncomp + 1) if counts[i] < min_size]
        if remove_ids:
            remove_mask = np.isin(lab, remove_ids)
            mask[remove_mask] = False
            info["small_components_removed"] = int(len(remove_ids))
            lab, ncomp = label(mask)
            counts = np.bincount(lab.ravel()) if ncomp > 0 else np.array([0])
            if len(counts) > 0:
                counts[0] = 0

    if ncomp <= 1:
        info["component_count_after"] = int(ncomp)
        info["connectivity_repaired"] = True
        return mask, info

    if str(mode).lower() == "largest":
        repaired = keep_largest_component(mask)
        info["component_count_after"] = count_connected_components(repaired)
        info["connectivity_repaired"] = True
        return repaired, info

    # Bridge mode: iteratively connect the nearest remaining component to the
    # current connected body. This preserves more geometry than keep-largest.
    largest_id = int(np.argmax(counts))
    connected = (lab == largest_id)
    remaining_ids = [i for i in range(1, ncomp + 1) if i != largest_id and counts[i] > 0]
    repaired = mask.copy()
    max_bridges = max(1, int(max_bridges))

    for _ in range(min(max_bridges, len(remaining_ids))):
        lab_cur, n_cur = label(repaired & (~connected))
        if n_cur == 0:
            break

        # Distance to current connected body; nearest indices give bridge endpoint.
        dist, inds = distance_transform_edt(~connected, return_indices=True)

        best = None
        for cid in range(1, n_cur + 1):
            coords = np.argwhere(lab_cur == cid)
            if coords.size == 0:
                continue
            dvals = dist[coords[:, 0], coords[:, 1], coords[:, 2]]
            k = int(np.argmin(dvals))
            p = coords[k]
            q = np.array([inds[0, p[0], p[1], p[2]], inds[1, p[0], p[1], p[2]], inds[2, p[0], p[1], p[2]]], dtype=int)
            d = float(dvals[k])
            if best is None or d < best[0]:
                best = (d, p, q)

        if best is None:
            break
        _, p, q = best
        repaired, added = _draw_voxel_bridge(repaired, p, q, radius_vox=bridge_radius_vox)
        info["bridges_added"] += 1
        info["voxels_added_by_bridges"] += int(added)
        connected = keep_largest_component(repaired)
        if count_connected_components(repaired) <= 1:
            break

    info["component_count_after"] = count_connected_components(repaired)
    info["connectivity_repaired"] = info["component_count_after"] <= 1
    return repaired, info

def repair_lattice_voxel_connectivity(mask, params, generator_type):
    """Apply connectivity repair only to Lattice and Voxel; TPMS is excluded."""
    if generator_type not in ["lattice", "voxel"]:
        return np.asarray(mask, dtype=bool), {
            "component_count_before": count_connected_components(mask),
            "component_count_after": count_connected_components(mask),
            "connectivity_repaired": None,
            "connectivity_mode": "not_applied_to_tpms",
            "bridges_added": 0,
            "voxels_added_by_bridges": 0,
            "small_components_removed": 0,
        }
    if not bool(params.get("force_connected", FORCE_CONNECTED_LATTICE_VOXEL)):
        return np.asarray(mask, dtype=bool), {
            "component_count_before": count_connected_components(mask),
            "component_count_after": count_connected_components(mask),
            "connectivity_repaired": False,
            "connectivity_mode": "disabled",
            "bridges_added": 0,
            "voxels_added_by_bridges": 0,
            "small_components_removed": 0,
        }
    return repair_mask_connectivity(
        mask,
        mode=params.get("connectivity_repair_mode", CONNECTIVITY_REPAIR_MODE),
        bridge_radius_vox=int(params.get("connectivity_bridge_radius_vox", CONNECTIVITY_BRIDGE_RADIUS_VOX)),
        min_component_voxels=int(params.get("connectivity_min_component_voxels", CONNECTIVITY_MIN_COMPONENT_VOXELS)),
        max_bridges=int(params.get("connectivity_max_bridges", CONNECTIVITY_MAX_BRIDGES)),
    )

def _canonical_face_layer(mask, face, d=0):
    """Return a boundary/contact layer in a common local 2D coordinate system.

    Local convention:
    - x0/x1 faces: (u, v) = (y, z)
    - y0/y1 faces: (u, v) = (x, z)
    - z0/z1 faces: (u, v) = (x, y)

    This avoids the previous bug where x/y/z faces were copied/compared without
    an explicit local-coordinate convention.
    """
    mask = np.asarray(mask, dtype=bool)
    d = int(d)
    if face == "x0":
        return mask[d, :, :].copy()
    if face == "x1":
        return mask[-1 - d, :, :].copy()
    if face == "y0":
        return mask[:, d, :].copy()
    if face == "y1":
        return mask[:, -1 - d, :].copy()
    if face == "z0":
        return mask[:, :, d].copy()
    if face == "z1":
        return mask[:, :, -1 - d].copy()
    raise ValueError(f"Unknown face name: {face}")

def _set_canonical_face_layer(mask, face, pattern, d=0):
    """Write a canonical 2D pattern to a selected boundary/contact layer."""
    pattern = np.asarray(pattern, dtype=bool)
    d = int(d)
    if face == "x0":
        mask[d, :, :] = pattern
    elif face == "x1":
        mask[-1 - d, :, :] = pattern
    elif face == "y0":
        mask[:, d, :] = pattern
    elif face == "y1":
        mask[:, -1 - d, :] = pattern
    elif face == "z0":
        mask[:, :, d] = pattern
    elif face == "z1":
        mask[:, :, -1 - d] = pattern
    else:
        raise ValueError(f"Unknown face name: {face}")
    return mask

def _stabilize_contact_pattern_edges(pattern):
    """Remove edge-line conflicts so face assignments stay deterministic.

    A cube edge belongs to two faces. If both faces write arbitrary edge pixels,
    the final edge can depend on assignment order. Clearing the 2D pattern edge
    lines makes the six/six or four/two face constraints exactly reproducible.
    """
    pattern = np.asarray(pattern, dtype=bool).copy()
    if pattern.shape[0] >= 2:
        pattern[0, :] = False
        pattern[-1, :] = False
    if pattern.shape[1] >= 2:
        pattern[:, 0] = False
        pattern[:, -1] = False
    return pattern

def _contact_depth(mask, depth_vox=1):
    n = int(np.asarray(mask).shape[0])
    return max(1, min(int(depth_vox), max(1, n // 8)))

def enforce_contact_face_symmetry(mask, mode, depth_vox=1):
    """Force only Lattice/Voxel contact layers to satisfy the required face rule.

    Rules implemented here:
    - periodic_isotropic: x0, x1, y0, y1, z0, z1 have the same canonical pattern.
    - periodic_orthotropic: x0, x1, y0, y1 share one side pattern; z0, z1 share
      another top/bottom pattern.

    TPMS is not passed through this function in the generation pipeline.
    """
    if not bool(globals().get("ENFORCE_CONTACT_FACE_SYMMETRY", True)):
        return mask

    mask = np.asarray(mask, dtype=bool).copy()
    mode = str(mode)
    depth = _contact_depth(mask, depth_vox)

    if mode == "periodic_isotropic":
        face_group = ["x0", "x1", "y0", "y1", "z0", "z1"]
        for d in range(depth):
            pattern = np.zeros_like(_canonical_face_layer(mask, "x0", d), dtype=bool)
            for face in face_group:
                pattern |= _canonical_face_layer(mask, face, d)
            pattern = _stabilize_contact_pattern_edges(pattern)
            for face in face_group:
                _set_canonical_face_layer(mask, face, pattern, d)

    elif mode == "periodic_orthotropic":
        side_faces = ["x0", "x1", "y0", "y1"]
        z_faces = ["z0", "z1"]
        for d in range(depth):
            side_pattern = np.zeros_like(_canonical_face_layer(mask, "x0", d), dtype=bool)
            for face in side_faces:
                side_pattern |= _canonical_face_layer(mask, face, d)
            side_pattern = _stabilize_contact_pattern_edges(side_pattern)

            z_pattern = np.zeros_like(_canonical_face_layer(mask, "z0", d), dtype=bool)
            for face in z_faces:
                z_pattern |= _canonical_face_layer(mask, face, d)
            z_pattern = _stabilize_contact_pattern_edges(z_pattern)

            for face in side_faces:
                _set_canonical_face_layer(mask, face, side_pattern, d)
            for face in z_faces:
                _set_canonical_face_layer(mask, face, z_pattern, d)

    return mask

def contact_face_symmetry_report(mask, mode, depth_vox=1):
    """Quantify face-rule mismatch over the enforced contact depth."""
    mask = np.asarray(mask, dtype=bool)
    mode = str(mode)
    depth = _contact_depth(mask, depth_vox)

    def mismatch(a, b):
        return int(np.count_nonzero(np.asarray(a, dtype=bool) ^ np.asarray(b, dtype=bool)))

    mismatches = {}
    if mode == "periodic_isotropic":
        for d in range(depth):
            ref = _canonical_face_layer(mask, "x0", d)
            for face in ["x1", "y0", "y1", "z0", "z1"]:
                mismatches[f"layer{d}_x0_vs_{face}"] = mismatch(ref, _canonical_face_layer(mask, face, d))
        ok = all(v == 0 for v in mismatches.values())

    elif mode == "periodic_orthotropic":
        for d in range(depth):
            side_ref = _canonical_face_layer(mask, "x0", d)
            for face in ["x1", "y0", "y1"]:
                mismatches[f"layer{d}_side_x0_vs_{face}"] = mismatch(side_ref, _canonical_face_layer(mask, face, d))
            z_ref = _canonical_face_layer(mask, "z0", d)
            mismatches[f"layer{d}_top_vs_bottom"] = mismatch(z_ref, _canonical_face_layer(mask, "z1", d))
        ok = all(v == 0 for v in mismatches.values())

    else:
        ok = None

    return ok, mismatches

def _axis_symmetry_views(arr, mode):
    """Return transformed views/copies representing the requested 3D symmetry group.

    periodic_isotropic:
        all axis permutations + axis flips are allowed. This makes x/y/z
        statistically/geometrically equivalent at the voxel-mask level.
    periodic_orthotropic:
        x and y directions are equivalent; z is independent but top/bottom are
        mirrored. This gives four equivalent side faces and one equivalent
        top-bottom pair.
    """
    arr = np.asarray(arr)
    mode = str(mode)
    outs = []

    if mode == "periodic_isotropic":
        from itertools import permutations, product
        for perm in permutations((0, 1, 2)):
            a = np.transpose(arr, perm)
            for flips in product([False, True], repeat=3):
                b = a
                for ax, do_flip in enumerate(flips):
                    if do_flip:
                        b = np.flip(b, axis=ax)
                outs.append(np.asarray(b))

    elif mode == "periodic_orthotropic":
        # D4-like xy symmetry + z mirror. z remains a distinct material axis.
        base_ops = [
            arr,
            np.swapaxes(arr, 0, 1),
            np.flip(arr, axis=0),
            np.flip(arr, axis=1),
            np.flip(np.swapaxes(arr, 0, 1), axis=0),
            np.flip(np.swapaxes(arr, 0, 1), axis=1),
            np.flip(np.flip(arr, axis=0), axis=1),
            np.flip(np.flip(np.swapaxes(arr, 0, 1), axis=0), axis=1),
        ]
        for a in base_ops:
            outs.append(np.asarray(a))
            outs.append(np.asarray(np.flip(a, axis=2)))
    else:
        outs = [arr]

    # Remove accidental duplicates to reduce compute while preserving symmetry.
    unique = []
    seen = set()
    for a in outs:
        key = (a.shape, a.strides, a.__array_interface__["data"][0] if np.shares_memory(a, arr) else hash(a.tobytes()[:64]))
        # Do not rely on the key for mathematical uniqueness; it is only a fast filter.
        unique.append(np.asarray(a))
    return unique

def symmetrize_scalar_field(field, mode):
    """Average a scalar field over the symmetry group before thresholding."""
    mode = str(mode)
    if mode not in ["periodic_isotropic", "periodic_orthotropic"]:
        return np.asarray(field)
    views = _axis_symmetry_views(np.asarray(field, dtype=np.float32), mode)
    acc = np.zeros_like(field, dtype=np.float32)
    for v in views:
        acc += np.asarray(v, dtype=np.float32)
    acc /= max(1, len(views))
    acc = (acc - np.mean(acc)) / (np.std(acc) + 1e-12)
    return acc.astype(np.float32)

def symmetrize_binary_mask(mask, mode, target_vf=None, method="score_threshold"):
    """Make a full 3D binary mask obey the requested global symmetry.

    method="or": keeps every voxel that appears in any symmetric copy. This is
    the strongest connectivity-preserving option but can increase VF.

    method="score_threshold": sums all symmetric copies and keeps score levels
    closest to the requested VF. Because the threshold is applied to the
    invariant score field, the result remains exactly symmetric.
    """
    mode = str(mode)
    if mode not in ["periodic_isotropic", "periodic_orthotropic"]:
        return np.asarray(mask, dtype=bool)

    mask = np.asarray(mask, dtype=bool)
    views = _axis_symmetry_views(mask.astype(np.uint8), mode)
    score = np.zeros(mask.shape, dtype=np.uint16)
    for v in views:
        score += np.asarray(v, dtype=np.uint16)

    method = str(method).lower()
    if method == "or" or target_vf is None:
        out = score > 0
    else:
        target = float(target_vf)
        unique_scores = np.unique(score)
        unique_scores = unique_scores[unique_scores > 0]
        if len(unique_scores) == 0:
            out = mask.copy()
        else:
            best_t, best_err = unique_scores[0], 1e9
            for t in unique_scores:
                vf = float(np.mean(score >= t))
                err = abs(vf - target)
                if err < best_err:
                    best_t, best_err = t, err
            out = score >= best_t

    return np.asarray(out, dtype=bool)

def strongest_connectivity_repair(mask, params, mode):
    """Guarantee one connected solid body while preserving symmetry.

    Components are bridged to the nearest center voxel, then the bridge itself is
    symmetrized. This avoids the common failure where a one-sided bridge fixes
    connectivity but breaks isotropic/orthotropic appearance.
    """
    mask = np.asarray(mask, dtype=bool).copy()
    bridge_radius = _safe_positive_int_scalar(params.get("connectivity_bridge_radius_vox", CONNECTIVITY_BRIDGE_RADIUS_VOX), CONNECTIVITY_BRIDGE_RADIUS_VOX)
    max_bridges = _safe_positive_int_scalar(params.get("connectivity_max_bridges", CONNECTIVITY_MAX_BRIDGES), CONNECTIVITY_MAX_BRIDGES)

    info = {"strong_bridges_added": 0, "strong_bridge_voxels_added": 0}
    for _ in range(8):
        lab, ncomp = label(mask)
        if ncomp <= 1:
            break
        center = (np.array(mask.shape) - 1) / 2.0
        center_idx = np.rint(center).astype(int)

        # Make sure the exact center region is solid. This creates a common hub
        # so all symmetrized bridges meet at one place.
        hub = np.zeros_like(mask, dtype=bool)
        hub[tuple(center_idx)] = True
        hub = binary_dilation(hub, iterations=max(1, bridge_radius))
        before = int(mask.sum())
        mask |= hub
        info["strong_bridge_voxels_added"] += int(mask.sum()) - before

        lab, ncomp = label(mask)
        if ncomp <= 1:
            break
        sizes = np.bincount(lab.ravel())
        sizes[0] = 0
        component_ids = [i for i in range(1, ncomp + 1) if sizes[i] > 0]
        component_ids = sorted(component_ids, key=lambda i: sizes[i], reverse=True)

        added_this_round = 0
        for cid in component_ids[:max_bridges]:
            coords = np.argwhere(lab == cid)
            if coords.size == 0:
                continue
            d2 = np.sum((coords.astype(float) - center) ** 2, axis=1)
            p = coords[int(np.argmin(d2))]
            mask, added = _draw_voxel_bridge(mask, p, center_idx, radius_vox=bridge_radius)
            info["strong_bridges_added"] += 1
            info["strong_bridge_voxels_added"] += int(added)
            added_this_round += int(added)
        # Duplicate the repair bridges according to the selected symmetry group.
        mask = symmetrize_binary_mask(mask, mode, target_vf=None, method="or")
        mask = binary_closing(mask, iterations=1)
        if added_this_round == 0 and count_connected_components(mask) > 1:
            # Last-resort: use a slightly thicker hub/bridge.
            bridge_radius += 1

    return mask, info

def _safe_positive_int_scalar(x, default=1):
    if isinstance(x, (list, tuple, np.ndarray)):
        if len(x) == 0:
            return int(default)
        x = x[0]
    try:
        if pd.isna(x):
            return int(default)
    except Exception:
        pass
    try:
        return max(1, int(round(float(x))))
    except Exception:
        return int(default)

def finalize_lattice_voxel_mask(mask, params, generator_type, mode_key, max_iter=6):
    """Finalize Lattice/Voxel masks with strict global symmetry + connectivity.

    Stronger than the previous boundary-only correction:
    1) symmetrize the full 3D mask for isotropic/orthotropic Lattice/Voxel modes,
    2) enforce exact contact-face equality over several voxel layers,
    3) repair disconnected components using center-directed symmetric bridges,
    4) re-apply symmetry and face rules, then validate both conditions.
    """
    generator_type = str(generator_type).lower()
    if generator_type not in ["lattice", "voxel"]:
        return np.asarray(mask, dtype=bool), {
            "finalizer_skipped": True,
            "reason": "TPMS_or_non_lattice_voxel_generator",
        }

    mode = str(params.get(mode_key, "stochastic"))
    depth = int(params.get("contact_surface_depth_vox", CONTACT_SURFACE_DEPTH_VOX))
    target_vf = float(params.get("target_vf", TARGET_VF))
    strict = bool(params.get("strict_global_symmetry", STRICT_GLOBAL_SYMMETRY))
    method = str(params.get("strict_symmetry_method", STRICT_SYMMETRY_METHOD))

    mask = np.asarray(mask, dtype=bool).copy()
    all_info = {
        "finalizer_skipped": False,
        "face_rule_mode": mode,
        "strict_global_symmetry": bool(strict and mode in ["periodic_isotropic", "periodic_orthotropic"]),
        "face_rule_depth_vox": int(_contact_depth(mask, depth)),
    }

    if strict and mode in ["periodic_isotropic", "periodic_orthotropic"]:
        # For the initial mask, use score-thresholding to avoid exploding VF.
        mask = symmetrize_binary_mask(mask, mode, target_vf=target_vf, method=method)

    for it in range(int(max_iter)):
        mask = enforce_contact_face_symmetry(mask, mode, depth_vox=depth)

        # Strong repair first; it makes a single hub-connected body and then
        # mirrors the repair, so symmetry is preserved rather than destroyed.
        if count_connected_components(mask) > 1:
            mask, strong_info = strongest_connectivity_repair(mask, params, mode)
            for k, v in strong_info.items():
                all_info[f"iter{it}_{k}"] = v

        mask, info = repair_lattice_voxel_connectivity(mask, params, generator_type=generator_type)
        for k, v in info.items():
            all_info[f"iter{it}_{k}"] = v

        if strict and mode in ["periodic_isotropic", "periodic_orthotropic"]:
            # After bridges are added, use OR-symmetry to preserve connectivity.
            mask = symmetrize_binary_mask(mask, mode, target_vf=None, method="or")
            mask = binary_closing(mask, iterations=1)

        mask = enforce_contact_face_symmetry(mask, mode, depth_vox=depth)

        ok, mismatches = contact_face_symmetry_report(mask, mode, depth_vox=depth)
        ncomp = count_connected_components(mask)
        all_info[f"iter{it}_post_face_symmetry_ok"] = None if ok is None else bool(ok)
        all_info[f"iter{it}_post_component_count"] = int(ncomp)
        all_info[f"iter{it}_vf"] = float(estimate_mask_vf(mask))
        if (ok is None or ok) and ncomp <= 1:
            break

    # Final hard pass.
    if strict and mode in ["periodic_isotropic", "periodic_orthotropic"]:
        mask = symmetrize_binary_mask(mask, mode, target_vf=None, method="or")
        mask = binary_closing(mask, iterations=1)
    mask = enforce_contact_face_symmetry(mask, mode, depth_vox=depth)
    if count_connected_components(mask) > 1:
        mask, strong_info = strongest_connectivity_repair(mask, params, mode)
        for k, v in strong_info.items():
            all_info[f"final_{k}"] = v
        if strict and mode in ["periodic_isotropic", "periodic_orthotropic"]:
            mask = symmetrize_binary_mask(mask, mode, target_vf=None, method="or")
            mask = binary_closing(mask, iterations=1)
        mask = enforce_contact_face_symmetry(mask, mode, depth_vox=depth)

    ok, mismatches = contact_face_symmetry_report(mask, mode, depth_vox=depth)
    ncomp = count_connected_components(mask)
    all_info["final_contact_face_symmetry_ok"] = None if ok is None else bool(ok)
    all_info["final_contact_face_mismatch_voxels"] = json_dumps(mismatches)
    all_info["final_component_count"] = int(ncomp)
    all_info["final_actual_vf_est"] = float(estimate_mask_vf(mask))
    return mask, all_info

def limit_max_thickness_approx(mask, max_thickness_vox):
    """Approximate maximum local thickness control by eroding extremely thick cores."""
    if max_thickness_vox is None or max_thickness_vox <= 0:
        return mask
    dist = distance_transform_edt(mask)
    too_thick = dist > float(max_thickness_vox)
    if np.any(too_thick):
        mask = mask.copy()
        # Remove only part of very thick core to avoid destroying connectivity.
        mask[too_thick] = False
        mask = binary_closing(mask, iterations=1)
    return mask

def enforce_voxel_min_hole_size(mask, min_hole_size_vox=1):
    min_hole_size_vox = int(min_hole_size_vox)
    if min_hole_size_vox <= 1:
        return mask
    pores = ~np.asarray(mask, dtype=bool)
    pores = binary_opening(pores, iterations=max(1, min_hole_size_vox - 1))
    return ~pores


# ---- globals expected by the extracted Model Generator helpers ----
import gc
import json
import math
import random
from itertools import product, permutations

import numpy as np
import pandas as pd
from scipy.ndimage import (
    gaussian_filter, binary_closing, binary_opening, binary_dilation,
    label, distance_transform_edt
)
from skimage import measure
import trimesh

SIZE_MM = float(BOUNDARY_SIZE_MM)
TARGET_VF = float(sum(GEN_PARAM_RANGES["target_vf"]) / 2.0)
VOXEL_GRID_N = int(round(BOUNDARY_SIZE_MM / (SCREENING_VOXEL_SIZE_MM if USE_SCREENING_RESOLUTION else VOXEL_SIZE_MM)))
MARCHING_CUBES_STEP_SIZE = int(MARCHING_CUBES_STEP_SCREENING)
CONTACT_SURFACE_DEPTH_VOX = max(1, int(round(GEN_PARAM_RANGES["contact_surface_depth_mm"][0] / max(VOXEL_SIZE_MM, 1e-9))))
CONNECTIVITY_BRIDGE_RADIUS_VOX = max(1, int(round(GEN_PARAM_RANGES["connectivity_bridge_radius_mm"][0] / max(VOXEL_SIZE_MM, 1e-9))))

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except Exception:
    cp = None
    CUPY_AVAILABLE = False

DEVICE = "cpu"
GPU_DEVICE_ID = 0
USE_GPU_FOR_GENERATION = False
_GPU_CONTEXT = {"device_id": 0}

def _get_generation_gpu_device():
    return int(_GPU_CONTEXT.get("device_id", GPU_DEVICE_ID))

def _xp_for_generation(n=None):
    """Use GPU only for grids that are small enough for the selected GPU memory budget."""
    global DEVICE, USE_GPU_FOR_GENERATION
    use_gpu = bool(CUPY_AVAILABLE and cp is not None and (n is None or int(n) <= int(GPU_MAX_GRID_N)))
    if use_gpu:
        try:
            cp.cuda.Device(_get_generation_gpu_device()).use()
            DEVICE = f"gpu:{_get_generation_gpu_device()}"
            USE_GPU_FOR_GENERATION = True
            return cp
        except Exception:
            pass
    DEVICE = "cpu"
    USE_GPU_FOR_GENERATION = False
    return np

def enforce_vf_by_rank(score, target_vf=0.30, available=None, prefer_high=True):
    """
    Original rank-selection intent with a memory-safe path for large 3D fields.
    Small/medium arrays use argpartition; very large arrays estimate the quantile
    from a deterministic uniform subsample and then threshold the full field.
    """
    score = np.asarray(score)
    target_vf = float(np.clip(target_vf, 1e-6, 1.0 - 1e-6))

    if available is not None:
        available = np.asarray(available, dtype=bool)
        valid_idx = np.flatnonzero(available.ravel())
        if len(valid_idx) == 0:
            return np.zeros(score.shape, dtype=bool)
        values = score.ravel()[valid_idx]
        k = max(1, min(int(round(target_vf * score.size)), len(valid_idx)))
        if len(values) <= 50_000_000:
            if prefer_high:
                chosen_local = np.argpartition(values, len(values) - k)[len(values) - k:]
            else:
                chosen_local = np.argpartition(values, k - 1)[:k]
            out = np.zeros(score.size, dtype=bool)
            out[valid_idx[chosen_local]] = True
            return out.reshape(score.shape)
        sample_n = min(2_000_000, len(values))
        sample_idx = np.linspace(0, len(values) - 1, sample_n, dtype=np.int64)
        q = 1.0 - target_vf if prefer_high else target_vf
        threshold = float(np.quantile(values[sample_idx], q))
        out = np.zeros(score.size, dtype=bool)
        flat = score.ravel()
        if prefer_high:
            out[valid_idx] = flat[valid_idx] >= threshold
        else:
            out[valid_idx] = flat[valid_idx] <= threshold
        return out.reshape(score.shape)

    flat = score.ravel()
    n_total = flat.size
    k = max(1, min(int(round(target_vf * n_total)), n_total))
    if n_total <= 50_000_000:
        if prefer_high:
            idx = np.argpartition(flat, n_total - k)[n_total - k:]
        else:
            idx = np.argpartition(flat, k - 1)[:k]
        out = np.zeros(n_total, dtype=bool)
        out[idx] = True
        return out.reshape(score.shape)

    sample_n = min(2_000_000, n_total)
    sample_idx = np.linspace(0, n_total - 1, sample_n, dtype=np.int64)
    q = 1.0 - target_vf if prefer_high else target_vf
    threshold = float(np.quantile(flat[sample_idx], q))
    return (score >= threshold) if prefer_high else (score <= threshold)

def periodic_fourier_field(
    n, num_terms=16, anisotropy=(1.0, 1.0, 1.0), seed=0,
    k_min=1, k_max=4
):
    """
    Model Generator의 periodic Fourier field를 유지하되,
    full X/Y/Z meshgrid 대신 broadcast 좌표를 사용하여 메모리를 줄였습니다.
    """
    rng = np.random.default_rng(int(seed))
    n = int(n)
    xp = _xp_for_generation(n)
    dtype = xp.float32
    x = xp.linspace(0.0, 2.0 * xp.pi, n, endpoint=False, dtype=dtype)
    X = x[:, None, None]
    Y = x[None, :, None]
    Z = x[None, None, :]
    F = xp.zeros((n, n, n), dtype=dtype)

    k_min = max(1, int(k_min))
    k_max = max(k_min, int(k_max))
    ax, ay, az = map(float, anisotropy)

    for _ in range(int(num_terms)):
        kx = int(rng.integers(k_min, k_max + 1))
        ky = int(rng.integers(k_min, k_max + 1))
        kz = int(rng.integers(k_min, k_max + 1))
        phase = float(rng.uniform(0, 2 * np.pi))
        amp = float(rng.normal(0, 1) / math.sqrt(max(1, int(num_terms))))
        term = (kx * ax) * X + (ky * ay) * Y + (kz * az) * Z + phase
        xp.sin(term, out=term)
        term *= amp
        F += term
        del term

    mean = xp.mean(F)
    std = xp.std(F)
    F = (F - mean) / (std + 1e-12)
    if CUPY_AVAILABLE and cp is not None and isinstance(F, cp.ndarray):
        F = cp.asnumpy(F)
    return np.asarray(F, dtype=np.float32)

def stochastic_gaussian_field(n, sigma=(3.0, 3.0, 3.0), seed=0):
    """Original Gaussian random field, changed to float32/in-place filtering for lower RAM."""
    n = int(n)
    rng = np.random.default_rng(int(seed))
    try:
        noise = rng.standard_normal(size=(n, n, n), dtype=np.float32)
    except TypeError:
        noise = rng.standard_normal(size=(n, n, n)).astype(np.float32)
    gaussian_filter(noise, sigma=tuple(float(v) for v in sigma), mode="reflect", output=noise)
    noise -= np.mean(noise, dtype=np.float64)
    noise /= (np.std(noise, dtype=np.float64) + 1e-12)
    return noise.astype(np.float32, copy=False)

def realize_voxel_params(row, voxel_size_mm, stage="screening"):
    """
    LHS에서 뽑은 물리 단위(mm) 생성인자를 현재 voxel resolution에 맞는
    voxel-count 인자로 변환합니다. 따라서 0.10 mm screening과 0.03 mm final 간에
    최소 두께/공극/bridge 의미가 유지됩니다.
    """
    r = row.to_dict() if hasattr(row, "to_dict") else dict(row)
    vs = float(voxel_size_mm)
    n = int(round(float(BOUNDARY_SIZE_MM) / vs))
    p = dict(r)
    p.update({
        "generator_type": "voxel",
        "size_mm": float(BOUNDARY_SIZE_MM),
        "grid_n": n,
        "voxel_size_mm": vs,
        "stage": str(stage),
        "target_vf": float(r["target_vf"]),
        "min_thickness_vox": max(1, int(round(float(r["min_thickness_mm"]) / vs))),
        "min_hole_size_vox": max(1, int(round(float(r["min_hole_size_mm"]) / vs))),
        "max_thickness_vox": max(1, int(round(float(r["max_thickness_mm"]) / vs))),
        "closing_iter": max(0, int(round(float(r["closing_radius_mm"]) / vs))),
        "opening_iter": max(0, int(round(float(r["opening_radius_mm"]) / vs))),
        "connectivity_bridge_radius_vox": max(1, int(round(float(r["connectivity_bridge_radius_mm"]) / vs))),
        "contact_surface_depth_vox": max(1, int(round(float(r["contact_surface_depth_mm"]) / vs))),
        "sigma": max(0.5, float(r["sigma_mm"]) / vs),
        "num_fourier_terms": int(r["num_fourier_terms"]),
        "fourier_k_min": 1,
        "fourier_k_max": int(r["fourier_k_max"]),
        "anisotropy_z": float(r["anisotropy_z"]),
        "force_connected": bool(FORCE_CONNECTED_LATTICE_VOXEL),
        "connectivity_repair_mode": str(CONNECTIVITY_REPAIR_MODE),
        "connectivity_min_component_voxels": int(CONNECTIVITY_MIN_COMPONENT_VOXELS),
        "connectivity_max_bridges": int(CONNECTIVITY_MAX_BRIDGES),
        "connectivity_retry_after_contact_symmetry": bool(CONNECTIVITY_RETRY_AFTER_CONTACT_SYMMETRY),
        "strict_global_symmetry": bool(STRICT_GLOBAL_SYMMETRY),
        "strict_symmetry_method": str(STRICT_SYMMETRY_METHOD),
    })
    return p

def generate_voxel_mask(params):
    seed = int(params["seed"])
    n = int(params.get("grid_n", VOXEL_GRID_N))
    mode = str(params["voxel_mode"])
    anisotropy_z = float(params.get("anisotropy_z", 1.0))
    target_vf = float(params.get("target_vf", TARGET_VF))

    if mode in ["periodic_isotropic", "periodic_orthotropic"]:
        anisotropy = (1.0, 1.0, anisotropy_z)
        F = periodic_fourier_field(
            n=n,
            num_terms=int(params.get("num_fourier_terms", 16)),
            anisotropy=anisotropy,
            seed=seed,
            k_min=int(params.get("fourier_k_min", 1)),
            k_max=int(params.get("fourier_k_max", 4)),
        )
    else:
        sigma_base = float(params.get("sigma", 4.0))
        sigma = (sigma_base, sigma_base, sigma_base * anisotropy_z)
        F = stochastic_gaussian_field(n=n, sigma=sigma, seed=seed)

    if (
        mode in ["periodic_isotropic", "periodic_orthotropic"]
        and bool(params.get("strict_global_symmetry", STRICT_GLOBAL_SYMMETRY))
    ):
        F = symmetrize_scalar_field(F, mode)

    mask = enforce_vf_by_rank(F, target_vf=target_vf, prefer_high=True)

    closing_iter = int(params.get("closing_iter", 0))
    opening_iter = int(params.get("opening_iter", 0))
    if closing_iter > 0:
        mask = binary_closing(mask, iterations=closing_iter)
    if opening_iter > 0:
        if not (
            mode in ["periodic_isotropic", "periodic_orthotropic"]
            and bool(params.get("strict_global_symmetry", STRICT_GLOBAL_SYMMETRY))
        ):
            mask = binary_opening(mask, iterations=opening_iter)

    min_thick = int(params.get("min_thickness_vox", 1))
    if min_thick > 1:
        mask = binary_closing(mask, iterations=max(1, min_thick - 1))
        if not (
            mode in ["periodic_isotropic", "periodic_orthotropic"]
            and bool(params.get("strict_global_symmetry", STRICT_GLOBAL_SYMMETRY))
        ):
            mask = binary_opening(mask, iterations=max(0, min_thick - 2))

    min_hole = int(params.get("min_hole_size_vox", 1))
    if min_hole > 1:
        mask = enforce_voxel_min_hole_size(mask, min_hole_size_vox=min_hole)

    mask, conn_info = finalize_lattice_voxel_mask(
        mask, params, generator_type="voxel", mode_key="voxel_mode", max_iter=6
    )

    strict_periodic = (
        mode in ["periodic_isotropic", "periodic_orthotropic"]
        and bool(params.get("strict_global_symmetry", STRICT_GLOBAL_SYMMETRY))
    )
    if strict_periodic:
        conn_info["max_thickness_trim_skipped_to_preserve_symmetry_connectivity"] = True
    elif ENABLE_MAX_THICKNESS_TRIM and n <= int(MAX_THICKNESS_TRIM_GRID_LIMIT):
        mask = limit_max_thickness_approx(mask, int(params.get("max_thickness_vox", 0)))
    else:
        conn_info["max_thickness_trim_skipped_for_memory"] = True

    mask, conn_info_2 = finalize_lattice_voxel_mask(
        mask, params, generator_type="voxel", mode_key="voxel_mode", max_iter=6
    )
    conn_info.update({f"after_thickness_{k}": v for k, v in conn_info_2.items()})

    # Original code's VF correction intention, but use the candidate-specific target_vf.
    if abs(estimate_mask_vf(mask) - target_vf) > float(VF_TOLERANCE):
        if strict_periodic:
            conn_info["vf_correction_skipped_to_preserve_symmetry_connectivity"] = True
            conn_info["vf_after_strict_symmetry"] = float(estimate_mask_vf(mask))
        else:
            mask = enforce_vf_by_rank(F, target_vf=target_vf, prefer_high=True)
            mask, conn_info_3 = finalize_lattice_voxel_mask(
                mask, params, generator_type="voxel", mode_key="voxel_mode", max_iter=6
            )
            conn_info.update({f"after_vf_{k}": v for k, v in conn_info_3.items()})

    params["_last_connectivity_info"] = conn_info
    del F
    gc.collect()
    return np.asarray(mask, dtype=bool)

def generate_voxel_candidate(params):
    mask = generate_voxel_mask(params)
    conn_info = params.get("_last_connectivity_info", {})
    verts, faces = mesh_from_binary_mask(mask, size_mm=params.get("size_mm", SIZE_MM))
    _, ncomp = label(mask)
    contact_ok, contact_mismatch = contact_face_symmetry_report(
        mask, params.get("voxel_mode", "stochastic"),
        depth_vox=int(params.get("contact_surface_depth_vox", CONTACT_SURFACE_DEPTH_VOX))
    )
    quick_desc = {
        "actual_vf_est": estimate_mask_vf(mask),
        "voxel_grid_n": int(mask.shape[0]),
        "voxel_size_mm": float(params.get("voxel_size_mm", np.nan)),
        "connected_components": int(ncomp),
        "slice_vf_mean_z": float(np.mean(mask.mean(axis=(0, 1)))),
        "slice_vf_std_z": float(np.std(mask.mean(axis=(0, 1)))),
        "min_thickness_vox": int(params.get("min_thickness_vox", 1)),
        "min_hole_size_vox": int(params.get("min_hole_size_vox", 1)),
        "contact_face_symmetry_ok": bool(contact_ok) if contact_ok is not None else None,
        "contact_face_mismatch_voxels": json_dumps(contact_mismatch),
        "component_count_before_repair": int(conn_info.get("component_count_before", int(ncomp))),
        "component_count_after_repair": int(ncomp),
        "is_single_connected_component": bool(int(ncomp) <= 1),
        "connectivity_repaired": bool(int(ncomp) <= 1),
        "connectivity_mode": str(conn_info.get("connectivity_mode", "bridge")),
    }
    del mask
    gc.collect()
    return verts, faces, quick_desc

def save_stl(verts, faces, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if len(verts) == 0 or len(faces) == 0:
        raise RuntimeError(f"Empty mesh cannot be exported: {output_path}")
    mesh = trimesh.Trimesh(vertices=np.asarray(verts), faces=np.asarray(faces), process=False)
    mesh.export(str(output_path))
    return output_path


# ===== CANDIDATE TABLE =====
# ============================================================
# CELL 4 — CANDIDATE PARAMETER TABLE
# Generator-parameter LHS + balanced mode allocation
# ============================================================
from scipy.stats import qmc

def _lhs_or_random(n, d, seed, use_lhs=True):
    if n <= 0:
        return np.empty((0, d), dtype=float)
    if use_lhs:
        sampler = qmc.LatinHypercube(d=d, seed=int(seed))
        return sampler.random(n=n)
    rng = np.random.default_rng(int(seed))
    return rng.random((n, d))

def _scale_unit(u, bounds, integer=False):
    lo, hi = bounds
    x = lo + np.asarray(u, float) * (hi - lo)
    if integer:
        x = np.rint(x).astype(int)
        x = np.clip(x, int(math.ceil(lo)), int(math.floor(hi)))
    return x

def _balanced_mode_counts(total, modes):
    total = int(total)
    q, r = divmod(total, len(modes))
    return {m: q + (1 if i < r else 0) for i, m in enumerate(modes)}

def build_voxel_candidate_table(
    n_total=N_RANDOM_STRUCTURES,
    seed=RANDOM_SEED,
    use_lhs=USE_GENERATOR_PARAMETER_LHS,
):
    rng = np.random.default_rng(int(seed))
    counts = _balanced_mode_counts(int(n_total), VOXEL_MODES)

    # 모든 mode에서 공통적으로 구조 다양성을 좌우하는 parameter.
    dims = [
        ("target_vf", False),
        ("min_thickness_mm", False),
        ("min_hole_size_mm", False),
        ("max_thickness_mm", False),
        ("closing_radius_mm", False),
        ("opening_radius_mm", False),
        ("connectivity_bridge_radius_mm", False),
        ("contact_surface_depth_mm", False),
        ("num_fourier_terms", True),
        ("fourier_k_max", True),
        ("anisotropy_z", False),
        ("sigma_mm", False),
    ]

    rows = []
    global_index = 0
    for mode_i, mode in enumerate(VOXEL_MODES):
        n_mode = counts[mode]
        U = _lhs_or_random(n_mode, len(dims), int(seed) + 1009 * (mode_i + 1), use_lhs)
        sampled = {}
        for j, (name, is_int) in enumerate(dims):
            sampled[name] = _scale_unit(U[:, j], GEN_PARAM_RANGES[name], integer=is_int)

        for i in range(n_mode):
            global_index += 1
            row = {
                "candidate_id": f"VOX_{mode}_{global_index:04d}",
                "generator_type": "voxel",
                "voxel_mode": mode,
                "seed": int(rng.integers(0, 2**31 - 1)),
                "size_mm": float(BOUNDARY_SIZE_MM),
                "target_vf": float(sampled["target_vf"][i]),
                "min_thickness_mm": float(sampled["min_thickness_mm"][i]),
                "min_hole_size_mm": float(sampled["min_hole_size_mm"][i]),
                "max_thickness_mm": float(sampled["max_thickness_mm"][i]),
                "closing_radius_mm": float(sampled["closing_radius_mm"][i]),
                "opening_radius_mm": float(sampled["opening_radius_mm"][i]),
                "connectivity_bridge_radius_mm": float(sampled["connectivity_bridge_radius_mm"][i]),
                "contact_surface_depth_mm": float(sampled["contact_surface_depth_mm"][i]),
                "num_fourier_terms": int(sampled["num_fourier_terms"][i]),
                "fourier_k_max": int(sampled["fourier_k_max"][i]),
                "anisotropy_z": float(sampled["anisotropy_z"][i]),
                "sigma_mm": float(sampled["sigma_mm"][i]),
                "strict_global_symmetry": bool(STRICT_GLOBAL_SYMMETRY if mode != "stochastic" else False),
                "force_connected": bool(FORCE_CONNECTED_LATTICE_VOXEL),
                "generator_param_sampling": "LHS" if use_lhs else "random_uniform",
                "screening_voxel_size_mm": float(SCREENING_VOXEL_SIZE_MM if USE_SCREENING_RESOLUTION else VOXEL_SIZE_MM),
                "final_voxel_size_mm": float(VOXEL_SIZE_MM),
            }

            # mode와 무관한 값을 NaN 처리하지 않고 그대로 보존:
            # LHS 공간은 동일하고, 실제 generator에서는 mode별 relevant parameter만 사용.
            rows.append(row)

    df = pd.DataFrame(rows)
    # mode 순서가 몰리지 않도록 reproducible shuffle
    order = np.random.default_rng(int(seed) + 777).permutation(len(df))
    df = df.iloc[order].reset_index(drop=True)

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLE_DIR / "Candidate_Generation_Parameters.csv", index=False, encoding="utf-8-sig")
    df.to_excel(TABLE_DIR / "Candidate_Generation_Parameters.xlsx", index=False)
    return df


# ===== GENERATION HELPERS =====
# ============================================================
# CELL 5 — GENERATE VOXEL -> STL
# ============================================================
import time
import traceback

def _memory_diagnostic(grid_n):
    n = int(grid_n)
    vox = n ** 3
    # rough lower-bound working set: float32 field + float32 temporary + bool mask + int32 labels
    est_gb = vox * (4 + 4 + 1 + 4) / (1024 ** 3)
    return {
        "grid_n": n,
        "voxel_count": vox,
        "rough_peak_working_set_GB_lower_bound": est_gb,
    }

def make_realized_parameter_row(row, voxel_size_mm, stage):
    p = realize_voxel_params(row, voxel_size_mm, stage)
    return {
        "candidate_id": p["candidate_id"],
        "stage": stage,
        "realized_voxel_size_mm": float(voxel_size_mm),
        "realized_grid_n": int(p["grid_n"]),
        "realized_min_thickness_vox": int(p["min_thickness_vox"]),
        "realized_min_hole_size_vox": int(p["min_hole_size_vox"]),
        "realized_max_thickness_vox": int(p["max_thickness_vox"]),
        "realized_closing_iter": int(p["closing_iter"]),
        "realized_opening_iter": int(p["opening_iter"]),
        "realized_connectivity_bridge_radius_vox": int(p["connectivity_bridge_radius_vox"]),
        "realized_contact_surface_depth_vox": int(p["contact_surface_depth_vox"]),
        "realized_sigma_vox": float(p["sigma"]),
    }

def run_voxel_generation(df, voxel_size_mm, stl_dir, stage, selected_ids=None):
    global MARCHING_CUBES_STEP_SIZE, VOXEL_GRID_N, CONTACT_SURFACE_DEPTH_VOX, CONNECTIVITY_BRIDGE_RADIUS_VOX

    stl_dir = Path(stl_dir)
    stl_dir.mkdir(parents=True, exist_ok=True)
    sub = df.copy()
    if selected_ids is not None:
        selected_ids = set(map(str, selected_ids))
        sub = sub[sub["candidate_id"].astype(str).isin(selected_ids)].copy()

    grid_n = int(round(BOUNDARY_SIZE_MM / float(voxel_size_mm)))
    diag = _memory_diagnostic(grid_n)
    print("Generation memory diagnostic:", diag)

    if grid_n >= 800 and not ALLOW_HIGH_MEMORY_FINAL_GRID:
        raise MemoryError(
            f"grid_n={grid_n} is high-memory. Set ALLOW_HIGH_MEMORY_FINAL_GRID=True "
            "or use a larger voxel size."
        )

    VOXEL_GRID_N = grid_n
    MARCHING_CUBES_STEP_SIZE = (
        int(MARCHING_CUBES_STEP_FINAL)
        if stage == "final"
        else int(MARCHING_CUBES_STEP_SCREENING)
    )
    rows = []
    total = len(sub)

    for j, (_, row) in enumerate(sub.iterrows(), 1):
        cid = str(row["candidate_id"])
        stl_path = stl_dir / f"{cid}.stl"
        param_json = stl_dir / f"{cid}_generation_parameters.json"
        t0 = time.time()

        try:
            p = realize_voxel_params(row, voxel_size_mm, stage)
            CONTACT_SURFACE_DEPTH_VOX = int(p["contact_surface_depth_vox"])
            CONNECTIVITY_BRIDGE_RADIUS_VOX = int(p["connectivity_bridge_radius_vox"])

            if stl_path.exists():
                status = "skipped_existing"
                quick = {}
            else:
                verts, faces, quick = generate_voxel_candidate(p)
                save_stl(verts, faces, stl_path)
                del verts, faces
                gc.collect()
                status = "OK"

            clean_param = {k: v for k, v in p.items() if not str(k).startswith("_")}
            param_json.write_text(
                json.dumps(clean_param, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8"
            )

            out = {
                "candidate_id": cid,
                "stage": stage,
                "status": status,
                "stl_path": str(stl_path),
                "elapsed_sec": round(time.time() - t0, 3),
                **make_realized_parameter_row(row, voxel_size_mm, stage),
                **{f"quick__{k}": v for k, v in quick.items()},
            }
        except Exception as exc:
            out = {
                "candidate_id": cid,
                "stage": stage,
                "status": "FAILED",
                "stl_path": str(stl_path),
                "elapsed_sec": round(time.time() - t0, 3),
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }

        rows.append(out)
        print(f"[{j:03d}/{total:03d}] {cid}: {out['status']} ({out['elapsed_sec']} s)")
        pd.DataFrame(rows).to_csv(
            TABLE_DIR / f"generation_log_{stage}.csv",
            index=False, encoding="utf-8-sig"
        )

    return pd.DataFrame(rows)


# ===== DLP CORE =====
# =============================================================================
# 2. Mesh slicing + .slice utilities
# =============================================================================
# Required packages:
#   pip install numpy pillow trimesh
#
# Mesh slicing (STL directly; STP/STEP through adapter):
#   STL -> horizontal cross-section loops -> raw binary part image sequence
#       -> saved first to `0. Raw data/*.slice`
#       -> then center-aligned layer extraction creates `1. Individual / Com/*.slice`
#          on a 1920×1080 black canvas
#
# Merge:
#   individual .slice folders are naturally sorted and grouped six at a time.
#   Each image is center-cropped to 640×540 and placed in a 3×2 layout.

import csv
import hashlib
import json
import math
import re
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw

try:
    from shapely.geometry import Polygon
except Exception:
    Polygon = None

try:
    import trimesh
except Exception as exc:
    raise ImportError(
        "trimesh가 필요합니다. 새 셀에서 `%pip install trimesh pillow numpy`를 실행한 뒤 kernel을 재시작하세요."
    ) from exc


# SIX_REGION_POSITIONS is configured in Cell 1.


def log(message: str, cfg: STLSliceConfig = CFG) -> None:
    if cfg.verbose:
        print(message)


def sec_name(layer_no: int) -> str:
    return f"SEC_{int(layer_no):04d}.png"


def safe_filename(value: object, max_length: int = 140) -> str:
    text = str(value).strip()
    text = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    if not text:
        text = "unnamed"
    if len(text) > max_length:
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
        text = text[: max_length - 11] + "_" + digest
    return text


def natural_sort_key(path_or_name: object):
    text = Path(path_or_name).name if not isinstance(path_or_name, str) else path_or_name
    return [int(token) if token.isdigit() else token.lower()
            for token in re.split(r"(\d+)", text)]


def list_sec_files(slice_folder: Path) -> Dict[int, Path]:
    result: Dict[int, Path] = {}
    for path in Path(slice_folder).glob("SEC_*.png"):
        match = re.fullmatch(r"SEC_(\d+)\.png", path.name, flags=re.IGNORECASE)
        if match:
            result[int(match.group(1))] = path
    return dict(sorted(result.items()))


def _stl_path_is_inside(path: Path, parent: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except (ValueError, OSError):
        return False


def discover_stl_files(
    import_dir: Path,
    recursive: bool = True,
    excluded_dirs: Optional[Sequence[Path]] = None,
) -> List[Path]:
    import_dir = Path(import_dir)
    if not import_dir.exists():
        raise FileNotFoundError(f"Import STL folder not found: {import_dir}")

    excluded = [Path(path) for path in (excluded_dirs or tuple())]
    pattern = "**/*.stl" if recursive else "*.stl"

    files: List[Path] = []
    for path in import_dir.glob(pattern):
        if not path.is_file():
            continue
        if any(_stl_path_is_inside(path, excluded_dir) for excluded_dir in excluded):
            continue
        files.append(path)

    files.sort(key=lambda p: natural_sort_key(str(p.relative_to(import_dir))))
    if not files:
        excluded_text = ""
        if excluded:
            excluded_text = "\nExcluded folders:\n" + "\n".join(
                f" - {path}" for path in excluded
            )
        raise RuntimeError(
            f"No STL files were found in: {import_dir}{excluded_text}"
        )
    return files


def make_unique_output_names(stl_files: Sequence[Path], import_root: Path) -> Dict[Path, str]:
    """Create collision-safe .slice folder stems while preserving natural order."""
    import_root = Path(import_root)
    counts: Dict[str, int] = {}
    result: Dict[Path, str] = {}

    for path in stl_files:
        base = safe_filename(path.stem)
        key = base.lower()
        counts[key] = counts.get(key, 0) + 1

    used: set[str] = set()
    for path in stl_files:
        base = safe_filename(path.stem)
        if counts[base.lower()] == 1:
            candidate = base
        else:
            rel_parent = path.parent.relative_to(import_root)
            prefix = safe_filename("__".join(rel_parent.parts)) if rel_parent.parts else "root"
            candidate = safe_filename(f"{prefix}__{base}")

        original_candidate = candidate
        suffix = 2
        while candidate.lower() in used:
            candidate = safe_filename(f"{original_candidate}_{suffix}")
            suffix += 1

        used.add(candidate.lower())
        result[path] = candidate

    return result


def load_stl_as_mesh(stl_path: Path):
    """Load STL and weld duplicated facet vertices before sectioning."""
    loaded = trimesh.load(
        str(stl_path),
        force=None,
        process=bool(MESH_PROCESS_VALIDATE),
    )

    if isinstance(loaded, trimesh.Scene):
        geometries = [
            geom.copy()
            for geom in loaded.geometry.values()
            if isinstance(geom, trimesh.Trimesh) and len(geom.faces) > 0
        ]
        if not geometries:
            raise RuntimeError(f"No mesh geometry in STL Scene: {stl_path}")
        mesh = trimesh.util.concatenate(geometries)
    elif isinstance(loaded, trimesh.Trimesh):
        mesh = loaded.copy()
    else:
        mesh = trimesh.load_mesh(
            str(stl_path),
            process=bool(MESH_PROCESS_VALIDATE),
        )

    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise RuntimeError(f"Invalid or empty STL mesh: {stl_path}")

    if MESH_PROCESS_VALIDATE:
        try:
            mesh.process(validate=True)
        except Exception:
            pass

    if MESH_MERGE_VERTICES:
        try:
            mesh.merge_vertices()
        except Exception:
            pass

    # Remove exact duplicate and degenerate triangles where supported.
    try:
        mesh.update_faces(mesh.unique_faces())
    except Exception:
        pass
    try:
        mesh.update_faces(mesh.nondegenerate_faces())
    except Exception:
        pass

    mesh.remove_unreferenced_vertices()

    if MESH_FIX_NORMALS:
        try:
            mesh.fix_normals(multibody=True)
        except Exception:
            pass

    return mesh


def prepare_mesh_for_slicing(mesh, cfg: STLSliceConfig = CFG):
    """
    Preserve the STL geometry by default.
    - optionally scale isotropically to target_length_mm
    - center X/Y at zero
    - move Z-min to zero
    """
    original_bounds = np.asarray(mesh.bounds, dtype=float)
    original_size = np.asarray(mesh.extents, dtype=float)

    if cfg.auto_scale_to_target:
        max_extent = float(np.max(original_size))
        if max_extent <= 0:
            raise RuntimeError("Mesh has zero size.")
        mesh.apply_scale(float(cfg.target_length_mm) / max_extent)

    bounds = np.asarray(mesh.bounds, dtype=float)
    translation = np.zeros(3, dtype=float)

    if cfg.recenter_xy:
        translation[0] = -0.5 * (bounds[0, 0] + bounds[1, 0])
        translation[1] = -0.5 * (bounds[0, 1] + bounds[1, 1])

    if cfg.shift_z_min_to_zero:
        translation[2] = -bounds[0, 2]

    mesh.apply_translation(translation)

    prepared_bounds = np.asarray(mesh.bounds, dtype=float)
    prepared_size = np.asarray(mesh.extents, dtype=float)

    try:
        _, edge_use_count = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
        boundary_edge_count = int(np.count_nonzero(edge_use_count == 1))
        nonmanifold_edge_count = int(np.count_nonzero(edge_use_count > 2))
    except Exception:
        boundary_edge_count = -1
        nonmanifold_edge_count = -1

    diagnostics = {
        "original_min_x_mm": float(original_bounds[0, 0]),
        "original_min_y_mm": float(original_bounds[0, 1]),
        "original_min_z_mm": float(original_bounds[0, 2]),
        "original_size_x_mm": float(original_size[0]),
        "original_size_y_mm": float(original_size[1]),
        "original_size_z_mm": float(original_size[2]),
        "prepared_min_x_mm": float(prepared_bounds[0, 0]),
        "prepared_min_y_mm": float(prepared_bounds[0, 1]),
        "prepared_min_z_mm": float(prepared_bounds[0, 2]),
        "prepared_size_x_mm": float(prepared_size[0]),
        "prepared_size_y_mm": float(prepared_size[1]),
        "prepared_size_z_mm": float(prepared_size[2]),
        "is_watertight": bool(mesh.is_watertight),
        "boundary_edge_count": boundary_edge_count,
        "nonmanifold_edge_count": nonmanifold_edge_count,
        "section_fill_rule": str(SECTION_FILL_RULE),
        "face_count": int(len(mesh.faces)),
        "vertex_count": int(len(mesh.vertices)),
    }
    return mesh, diagnostics


def _remove_consecutive_duplicate_points(xy: np.ndarray, tolerance: float = 1.0e-10) -> np.ndarray:
    if len(xy) <= 1:
        return xy
    delta = np.linalg.norm(np.diff(xy, axis=0), axis=1)
    keep = np.concatenate(([True], delta > float(tolerance)))
    return xy[keep]


def _signed_polygon_area(xy: np.ndarray) -> float:
    if len(xy) < 3:
        return 0.0
    x = xy[:, 0]
    y = xy[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - y * np.roll(x, -1)))


def section_polylines_xy(mesh, z_mm: float) -> List[np.ndarray]:
    """Return only valid closed X-Y contours at a horizontal slicing plane."""
    section = mesh.section(
        plane_origin=np.array([0.0, 0.0, float(z_mm)]),
        plane_normal=np.array([0.0, 0.0, 1.0]),
    )
    if section is None:
        return []

    try:
        discrete = section.discrete
    except Exception:
        return []

    loops: List[np.ndarray] = []
    for polyline in discrete:
        array = np.asarray(polyline, dtype=float)
        if array.ndim != 2 or array.shape[0] < 3 or array.shape[1] < 2:
            continue

        xy = array[:, :2]
        xy = xy[np.all(np.isfinite(xy), axis=1)]
        xy = _remove_consecutive_duplicate_points(xy)
        if len(xy) < 3:
            continue

        close_gap = float(np.linalg.norm(xy[0] - xy[-1]))
        if SECTION_REQUIRE_CLOSED_LOOPS and close_gap > float(SECTION_CLOSE_TOLERANCE_MM):
            # Never force a distant open path closed; that creates long triangles.
            continue

        if close_gap > 1.0e-12:
            xy = np.vstack([xy, xy[0]])

        area = abs(_signed_polygon_area(xy[:-1] if np.allclose(xy[0], xy[-1]) else xy))
        if area < float(SECTION_MIN_LOOP_AREA_MM2):
            continue

        loops.append(xy)

    return loops


def xy_to_part_pixels(xy: np.ndarray, cfg: STLSliceConfig = CFG) -> List[Tuple[int, int]]:
    center = 0.5 * (cfg.part_px - 1)
    px = center + xy[:, 0] / cfg.pixel_size_mm
    py = center - xy[:, 1] / cfg.pixel_size_mm
    return [(int(round(x)), int(round(y))) for x, y in zip(px, py)]



def _polygon_rings_from_loop(xy: np.ndarray) -> List[Tuple[np.ndarray, object]]:
    """Convert one closed contour to one or more valid Shapely polygon rings."""
    if Polygon is None:
        raise ImportError(
            "SECTION_FILL_RULE='nested' requires shapely. "
            "Run `%pip install shapely` and restart the kernel."
        )

    ring = np.asarray(xy, dtype=float)
    if ring.ndim != 2 or ring.shape[0] < 3:
        return []
    ring = ring[:, :2]
    if np.allclose(ring[0], ring[-1]):
        ring = ring[:-1]
    if len(ring) < 3:
        return []

    polygon = Polygon(ring)
    if not polygon.is_valid:
        # Repairs self-touching rings without force-closing distant open paths.
        polygon = polygon.buffer(0)
    if polygon.is_empty:
        return []

    polygons = [polygon] if polygon.geom_type == "Polygon" else [
        geom for geom in getattr(polygon, "geoms", [])
        if geom.geom_type == "Polygon" and not geom.is_empty
    ]

    records: List[Tuple[np.ndarray, object]] = []
    for poly in polygons:
        exterior = np.asarray(poly.exterior.coords, dtype=float)[:, :2]
        if len(exterior) >= 4:
            records.append((exterior, Polygon(exterior)))
        # Preserve any holes produced during geometry repair as independent rings;
        # the hierarchy step below will assign them to the correct parent shell.
        for interior in poly.interiors:
            hole = np.asarray(interior.coords, dtype=float)[:, :2]
            if len(hole) >= 4:
                records.append((hole, Polygon(hole)))
    return records


def _build_nested_contour_records(
    loops_xy: Sequence[np.ndarray],
) -> List[Dict[str, object]]:
    """
    Build a containment tree for section contours.

    Even depth = printable solid shell/island.
    Odd depth  = enclosed void/hole.

    This preserves true holes while still allowing separate or overlapping
    solid contours to be Boolean-unioned during rasterization.
    """
    records: List[Dict[str, object]] = []
    for xy in loops_xy:
        for ring_xy, polygon in _polygon_rings_from_loop(xy):
            area = float(polygon.area)
            if area < float(SECTION_MIN_LOOP_AREA_MM2):
                continue
            records.append({
                "xy": ring_xy,
                "polygon": polygon,
                "area": area,
                "parent": None,
                "depth": 0,
            })

    # Parent = smallest larger contour that contains the representative point.
    # Using continuous XY geometry prevents pixel-rounding from creating false
    # horizontal chords or accidentally filled cavities.
    for i, record in enumerate(records):
        point = record["polygon"].representative_point()
        candidates: List[int] = []
        for j, other in enumerate(records):
            if i == j or float(other["area"]) <= float(record["area"]):
                continue
            if other["polygon"].covers(point):
                candidates.append(j)
        if candidates:
            record["parent"] = min(
                candidates,
                key=lambda index: float(records[index]["area"]),
            )

    for i, record in enumerate(records):
        depth = 0
        parent = record["parent"]
        visited = set()
        while parent is not None:
            if parent in visited:
                # Defensive escape for duplicate/degenerate contour cycles.
                break
            visited.add(parent)
            depth += 1
            parent = records[parent]["parent"]
        record["depth"] = depth

    return records


def _rasterize_nested_contours(
    loops_xy: Sequence[np.ndarray],
    width_px: int,
    height_px: int,
    point_mapper,
) -> np.ndarray:
    """Rasterize shells with their direct child holes, then union all solids."""
    records = _build_nested_contour_records(loops_xy)
    result = np.zeros((int(height_px), int(width_px)), dtype=bool)

    for shell_index, shell in enumerate(records):
        shell_depth = int(shell["depth"])
        if shell_depth % 2 != 0:
            continue

        mask_img = Image.new("1", (int(width_px), int(height_px)), 0)
        drawer = ImageDraw.Draw(mask_img)
        shell_points = point_mapper(np.asarray(shell["xy"], dtype=float))
        if len(shell_points) < 3:
            continue
        drawer.polygon(shell_points, fill=1)

        # Only direct odd-depth children are holes of this shell. A depth-2
        # island is rasterized separately below, so nested solid islands survive.
        for hole in records:
            if (
                hole["parent"] == shell_index
                and int(hole["depth"]) == shell_depth + 1
            ):
                hole_points = point_mapper(np.asarray(hole["xy"], dtype=float))
                if len(hole_points) >= 3:
                    drawer.polygon(hole_points, fill=0)

        result |= np.asarray(mask_img, dtype=bool)

    return result


def rasterize_even_odd_contours(
    loops_xy: Sequence[np.ndarray],
    cfg: STLSliceConfig = CFG,
    fill_rule: str = SECTION_FILL_RULE,
) -> np.ndarray:
    """
    Rasterize section contours.

    nested:
        Recommended. Builds a contour-containment hierarchy, keeps enclosed
        cavities black, and unions independent/overlapping solid shells.
    even_odd:
        Legacy XOR behavior. Preserves nested holes but can erase overlaps.
    union:
        Legacy OR behavior. Useful only for open/intersecting shell sets with
        no true nested holes; otherwise enclosed voids are falsely filled.
    """
    fill_rule = str(fill_rule).strip().lower()
    if fill_rule not in {"nested", "union", "even_odd"}:
        raise ValueError(f"Unsupported SECTION_FILL_RULE: {fill_rule}")

    if fill_rule == "nested":
        return _rasterize_nested_contours(
            loops_xy,
            width_px=cfg.part_px,
            height_px=cfg.part_px,
            point_mapper=lambda xy: xy_to_part_pixels(xy, cfg),
        )

    result = np.zeros((cfg.part_px, cfg.part_px), dtype=bool)
    for xy in loops_xy:
        points = xy_to_part_pixels(xy, cfg)
        if len(points) < 3:
            continue

        mask_img = Image.new("1", (cfg.part_px, cfg.part_px), 0)
        drawer = ImageDraw.Draw(mask_img)
        drawer.polygon(points, fill=1)
        contour_mask = np.asarray(mask_img, dtype=bool)

        if fill_rule == "union":
            result |= contour_mask
        else:
            result ^= contour_mask

    return result


def place_part_on_canvas(part_binary: np.ndarray, cfg: STLSliceConfig = CFG) -> Image.Image:
    canvas = np.full(
        (cfg.canvas_h, cfg.canvas_w),
        int(cfg.background),
        dtype=np.uint8,
    )
    part = np.where(part_binary, cfg.foreground, cfg.background).astype(np.uint8)

    left = (cfg.canvas_w - cfg.part_px) // 2
    top = (cfg.canvas_h - cfg.part_px) // 2
    canvas[top:top + cfg.part_px, left:left + cfg.part_px] = part
    return Image.fromarray(canvas, mode="L")


def render_one_stl_to_raw_slice_folder(
    stl_path: Path,
    output_folder: Path,
    cfg: STLSliceConfig = CFG,
    overwrite: bool = True,
) -> Dict[str, object]:
    stl_path = Path(stl_path)
    output_folder = Path(output_folder)

    if output_folder.exists():
        if overwrite:
            shutil.rmtree(output_folder)
        else:
            existing = list_sec_files(output_folder)
            if len(existing) >= 1:
                return {
                    "source_stl": str(stl_path),
                    "slice_folder": str(output_folder),
                    "status": "skipped_existing",
                    "raw_layer_count": len(existing),
                }
            raise FileExistsError(f"Output folder already exists: {output_folder}")

    output_folder.mkdir(parents=True, exist_ok=True)
    mesh = load_stl_as_mesh(stl_path)
    mesh, diagnostics = prepare_mesh_for_slicing(mesh, cfg)

    # Boundary warnings: model is not rescaled unless auto_scale_to_target=True.
    half_target = 0.5 * cfg.target_length_mm
    bounds = np.asarray(mesh.bounds, dtype=float)
    warnings: List[str] = []
    if bounds[0, 0] < -half_target or bounds[1, 0] > half_target:
        warnings.append("X extent exceeds the 30 mm / 461 px part boundary and will be clipped.")
    if bounds[0, 1] < -half_target or bounds[1, 1] > half_target:
        warnings.append("Y extent exceeds the 30 mm / 461 px part boundary and will be clipped.")
    max_print_z = cfg.fixed_layer_count * cfg.layer_height_mm
    if bounds[1, 2] > max_print_z + 1e-9:
        warnings.append(
            f"Z extent exceeds the COM target thickness ({max_print_z:.3f} mm). "
            "Raw data will be saved fully, and COM Individual will be center-aligned by trimming/padding layers."
        )
    if not bool(mesh.is_watertight):
        warnings.append(
            "Mesh is not watertight. Open section contours may be missing or incompletely filled."
        )

    raw_layer_count = estimate_raw_layer_count(mesh, cfg)

    white_counts: Dict[int, int] = {}
    failed_layers: List[int] = []

    for layer_no in range(1, raw_layer_count + 1):
        # Slice through the center of each 0.1 mm layer.
        z_mm = (layer_no - 0.5) * cfg.layer_height_mm
        try:
            loops = section_polylines_xy(mesh, z_mm)
            binary = rasterize_even_odd_contours(loops, cfg)
        except Exception:
            binary = np.zeros((cfg.part_px, cfg.part_px), dtype=bool)
            failed_layers.append(layer_no)

        image = render_raw_slice_image(binary, cfg)
        image_path = output_folder / sec_name(layer_no)
        image.save(image_path)
        white_counts[layer_no] = int(np.count_nonzero(binary))

        if cfg.verbose and (
            layer_no == 1
            or layer_no % 50 == 0
            or layer_no == raw_layer_count
        ):
            print(
                f"  {output_folder.name}: layer "
                f"{layer_no}/{raw_layer_count}"
            )

    info = {
        "source_stl": str(stl_path),
        "slice_folder": str(output_folder),
        "status": "completed",
        "raw_layer_count": int(raw_layer_count),
        "target_com_layer_count": int(cfg.fixed_layer_count),
        "layer_height_mm": float(cfg.layer_height_mm),
        "canvas_w": int(cfg.canvas_w),
        "canvas_h": int(cfg.canvas_h),
        "part_px": int(cfg.part_px),
        "pixel_size_mm": float(cfg.pixel_size_mm),
        "failed_layer_count": int(len(failed_layers)),
        "failed_layers": failed_layers,
        "warning_count": int(len(warnings)),
        "warnings": warnings,
        **diagnostics,
    }

    (output_folder / "slice_info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return info


def run_all_raw_stl_slicing(
    import_dir: Path,
    raw_root: Path,
    cfg: STLSliceConfig = CFG,
    overwrite: bool = True,
    excluded_dirs: Optional[Sequence[Path]] = None,
) -> List[Dict[str, object]]:
    stl_files = discover_stl_files(
        import_dir,
        recursive=cfg.recursive_stl_search,
        excluded_dirs=excluded_dirs,
    )
    name_map = make_unique_output_names(stl_files, import_dir)
    raw_root = Path(raw_root)
    raw_root.mkdir(parents=True, exist_ok=True)

    log(f"Found STL files: {len(stl_files)}", cfg)
    results: List[Dict[str, object]] = []

    def task(path: Path):
        out_folder = raw_root / f"{name_map[path]}.slice"
        try:
            return render_one_stl_to_raw_slice_folder(
                path, out_folder, cfg=cfg, overwrite=overwrite
            )
        except Exception as exc:
            return {
                "source_stl": str(path),
                "slice_folder": str(out_folder),
                "status": "failed",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }

    if int(cfg.max_workers) <= 1:
        for index, path in enumerate(stl_files, start=1):
            log(f"\n[SLICE {index}/{len(stl_files)}] {path.name}", cfg)
            results.append(task(path))
    else:
        with ThreadPoolExecutor(max_workers=int(cfg.max_workers)) as executor:
            future_map = {executor.submit(task, path): path for path in stl_files}
            for index, future in enumerate(as_completed(future_map), start=1):
                path = future_map[future]
                result = future.result()
                log(
                    f"[SLICE DONE {index}/{len(stl_files)}] "
                    f"{path.name}: {result.get('status')}",
                    cfg,
                )
                results.append(result)

        # restore original natural order
        order = {str(path): i for i, path in enumerate(stl_files)}
        results.sort(key=lambda row: order.get(str(row.get("source_stl")), 10**9))

    manifest_path = Path(OUTPUT_ROOT) / "Raw_STL_Slicing_Manifest.csv"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Flatten list-like fields for CSV.
    csv_rows = []
    for row in results:
        flat = dict(row)
        for key in ("warnings", "failed_layers"):
            if isinstance(flat.get(key), list):
                flat[key] = " | ".join(map(str, flat[key]))
        flat.pop("traceback", None)
        csv_rows.append(flat)

    headers: List[str] = []
    for row in csv_rows:
        for key in row:
            if key not in headers:
                headers.append(key)

    with open(manifest_path, "w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)

    return results


def build_com_individual_from_raw_root(
    raw_root: Path,
    individual_root: Path,
    cfg: STLSliceConfig = CFG,
    overwrite: bool = True,
) -> List[Dict[str, object]]:
    raw_root = Path(raw_root)
    individual_root = Path(individual_root)

    if not raw_root.exists():
        raise FileNotFoundError(f"Raw root not found: {raw_root}")

    folders = sorted(
        [path for path in raw_root.glob("*.slice") if path.is_dir()],
        key=natural_sort_key,
    )
    if not folders:
        raise RuntimeError(f"No raw .slice folders found in: {raw_root}")

    individual_root.mkdir(parents=True, exist_ok=True)
    results: List[Dict[str, object]] = []
    for folder in folders:
        destination = individual_root / folder.name
        result = extract_center_aligned_com_layers(
            folder,
            destination,
            cfg=cfg,
            overwrite=overwrite,
        )
        results.append(result)

    write_manifest_rows(results, Path(OUTPUT_ROOT) / "Com_Individual_Extraction_Manifest.csv")
    return results




def render_raw_slice_image(
    part_binary: np.ndarray,
    cfg: STLSliceConfig = CFG,
    save_center_crop: bool = RAW_DATA_SAVE_AS_CENTER_CROP,
    crop_size_px: int = RAW_DATA_CENTER_CROP_PX,
) -> Image.Image:
    part = np.where(part_binary, cfg.foreground, cfg.background).astype(np.uint8)

    if save_center_crop:
        crop_size_px = int(crop_size_px)
        if part.shape != (crop_size_px, crop_size_px):
            raise ValueError(
                f"Expected raw slice image shape {(crop_size_px, crop_size_px)}, got {part.shape}"
            )
        return Image.fromarray(part, mode="L")

    return place_part_on_canvas(part_binary, cfg)


def ensure_image_centered_on_canvas(
    image: Image.Image,
    cfg: STLSliceConfig = CFG,
) -> Image.Image:
    gray = image.convert("L")
    if gray.size == (cfg.canvas_w, cfg.canvas_h):
        return gray

    canvas = Image.new("L", (cfg.canvas_w, cfg.canvas_h), int(cfg.background))
    left = (cfg.canvas_w - gray.size[0]) // 2
    top = (cfg.canvas_h - gray.size[1]) // 2
    canvas.paste(gray, (left, top))
    return canvas


def estimate_raw_layer_count(mesh, cfg: STLSliceConfig = CFG) -> int:
    bounds = np.asarray(mesh.bounds, dtype=float)
    z_max = float(bounds[1, 2])
    return max(1, int(np.ceil(max(0.0, z_max) / float(cfg.layer_height_mm))))


def build_center_aligned_layer_plan(
    source_count: int,
    target_count: int,
) -> Dict[str, int]:
    source_count = int(source_count)
    target_count = int(target_count)
    if source_count <= 0 or target_count <= 0:
        raise ValueError("source_count and target_count must be positive")

    if source_count >= target_count:
        front_trim = (source_count - target_count) // 2
        source_start = 1 + front_trim
        source_end = source_start + target_count - 1
        target_start = 1
        target_end = target_count
        mode = "trim"
    else:
        front_pad = (target_count - source_count) // 2
        source_start = 1
        source_end = source_count
        target_start = 1 + front_pad
        target_end = target_start + source_count - 1
        mode = "pad"

    return {
        "mode": mode,
        "source_start": int(source_start),
        "source_end": int(source_end),
        "target_start": int(target_start),
        "target_end": int(target_end),
        "source_count": int(source_count),
        "target_count": int(target_count),
    }


def extract_center_aligned_com_layers(
    raw_slice_folder: Path,
    output_folder: Path,
    cfg: STLSliceConfig = CFG,
    overwrite: bool = True,
) -> Dict[str, object]:
    raw_slice_folder = Path(raw_slice_folder)
    output_folder = Path(output_folder)

    raw_sec = list_sec_files(raw_slice_folder)
    if not raw_sec:
        raise RuntimeError(f"No SEC images found in raw slice folder: {raw_slice_folder}")

    if output_folder.exists():
        if overwrite:
            shutil.rmtree(output_folder)
        else:
            raise FileExistsError(f"Output folder already exists: {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)

    plan = build_center_aligned_layer_plan(len(raw_sec), int(cfg.fixed_layer_count))
    blank_canvas = Image.new("L", (cfg.canvas_w, cfg.canvas_h), int(cfg.background))

    for target_layer in range(1, int(cfg.fixed_layer_count) + 1):
        if plan["target_start"] <= target_layer <= plan["target_end"]:
            source_layer = plan["source_start"] + (target_layer - plan["target_start"])
            source_path = raw_sec.get(source_layer)
            if source_path is None:
                raise RuntimeError(
                    f"Missing raw source layer {sec_name(source_layer)} in {raw_slice_folder.name}"
                )
            with Image.open(source_path) as image:
                if COM_INDIVIDUAL_MAP_TO_CANVAS:
                    output_image = ensure_image_centered_on_canvas(image, cfg)
                else:
                    output_image = image.convert("L")
        else:
            output_image = blank_canvas.copy() if COM_INDIVIDUAL_MAP_TO_CANVAS else Image.new("L", (RAW_DATA_CENTER_CROP_PX, RAW_DATA_CENTER_CROP_PX), int(cfg.background))

        output_image.save(output_folder / sec_name(target_layer))

    info = {
        "raw_slice_folder": str(raw_slice_folder),
        "slice_folder": str(output_folder),
        "status": "completed",
        "raw_layer_count": int(len(raw_sec)),
        "target_layer_count": int(cfg.fixed_layer_count),
        "selection_mode": plan["mode"],
        "source_start_layer": int(plan["source_start"]),
        "source_end_layer": int(plan["source_end"]),
        "target_start_layer": int(plan["target_start"]),
        "target_end_layer": int(plan["target_end"]),
        "image_size": [int(cfg.canvas_w), int(cfg.canvas_h)] if COM_INDIVIDUAL_MAP_TO_CANVAS else [int(RAW_DATA_CENTER_CROP_PX), int(RAW_DATA_CENTER_CROP_PX)],
    }
    (output_folder / "com_extraction_info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return info
def ensure_image_centered_on_canvas(
    image: Image.Image,
    cfg: STLSliceConfig = CFG,
) -> Image.Image:
    gray = image.convert("L")
    if gray.size == (cfg.canvas_w, cfg.canvas_h):
        return gray

    canvas = Image.new("L", (cfg.canvas_w, cfg.canvas_h), int(cfg.background))
    left = (cfg.canvas_w - gray.size[0]) // 2
    top = (cfg.canvas_h - gray.size[1]) // 2
    canvas.paste(gray, (left, top))
    return canvas


def estimate_raw_layer_count(mesh, cfg: STLSliceConfig = CFG) -> int:
    bounds = np.asarray(mesh.bounds, dtype=float)
    z_max = float(bounds[1, 2])
    return max(1, int(np.ceil(max(0.0, z_max) / float(cfg.layer_height_mm))))


def build_center_aligned_layer_plan(
    source_count: int,
    target_count: int,
) -> Dict[str, int]:
    source_count = int(source_count)
    target_count = int(target_count)
    if source_count <= 0 or target_count <= 0:
        raise ValueError("source_count and target_count must be positive")

    if source_count >= target_count:
        front_trim = (source_count - target_count) // 2
        source_start = 1 + front_trim
        source_end = source_start + target_count - 1
        target_start = 1
        target_end = target_count
        mode = "trim"
    else:
        front_pad = (target_count - source_count) // 2
        source_start = 1
        source_end = source_count
        target_start = 1 + front_pad
        target_end = target_start + source_count - 1
        mode = "pad"

    return {
        "mode": mode,
        "source_start": int(source_start),
        "source_end": int(source_end),
        "target_start": int(target_start),
        "target_end": int(target_end),
        "source_count": int(source_count),
        "target_count": int(target_count),
    }


def extract_center_aligned_com_layers(
    raw_slice_folder: Path,
    output_folder: Path,
    cfg: STLSliceConfig = CFG,
    overwrite: bool = True,
) -> Dict[str, object]:
    raw_slice_folder = Path(raw_slice_folder)
    output_folder = Path(output_folder)

    raw_sec = list_sec_files(raw_slice_folder)
    if not raw_sec:
        raise RuntimeError(f"No SEC images found in raw slice folder: {raw_slice_folder}")

    if output_folder.exists():
        if overwrite:
            shutil.rmtree(output_folder)
        else:
            raise FileExistsError(f"Output folder already exists: {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)

    plan = build_center_aligned_layer_plan(len(raw_sec), int(cfg.fixed_layer_count))
    blank_canvas = Image.new("L", (cfg.canvas_w, cfg.canvas_h), int(cfg.background))

    for target_layer in range(1, int(cfg.fixed_layer_count) + 1):
        if plan["target_start"] <= target_layer <= plan["target_end"]:
            source_layer = plan["source_start"] + (target_layer - plan["target_start"])
            source_path = raw_sec.get(source_layer)
            if source_path is None:
                raise RuntimeError(
                    f"Missing raw source layer {sec_name(source_layer)} in {raw_slice_folder.name}"
                )
            with Image.open(source_path) as image:
                if COM_INDIVIDUAL_MAP_TO_CANVAS:
                    output_image = ensure_image_centered_on_canvas(image, cfg)
                else:
                    output_image = image.convert("L")
        else:
            output_image = blank_canvas.copy() if COM_INDIVIDUAL_MAP_TO_CANVAS else Image.new("L", (RAW_DATA_CENTER_CROP_PX, RAW_DATA_CENTER_CROP_PX), int(cfg.background))

        output_image.save(output_folder / sec_name(target_layer))

    info = {
        "raw_slice_folder": str(raw_slice_folder),
        "slice_folder": str(output_folder),
        "status": "completed",
        "raw_layer_count": int(len(raw_sec)),
        "target_layer_count": int(cfg.fixed_layer_count),
        "selection_mode": plan["mode"],
        "source_start_layer": int(plan["source_start"]),
        "source_end_layer": int(plan["source_end"]),
        "target_start_layer": int(plan["target_start"]),
        "target_end_layer": int(plan["target_end"]),
        "image_size": [int(cfg.canvas_w), int(cfg.canvas_h)] if COM_INDIVIDUAL_MAP_TO_CANVAS else [int(RAW_DATA_CENTER_CROP_PX), int(RAW_DATA_CENTER_CROP_PX)],
    }
    (output_folder / "com_extraction_info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return info


def center_crop_box(cfg: STLSliceConfig = CFG) -> Tuple[int, int, int, int]:
    left = (cfg.canvas_w - cfg.six_region_crop_w) // 2
    top = (cfg.canvas_h - cfg.six_region_crop_h) // 2
    return (
        left,
        top,
        left + cfg.six_region_crop_w,
        top + cfg.six_region_crop_h,
    )


def read_text_auto(path: Path) -> str:
    data = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp949", "utf-16", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def count_white_pixels(image_path: Path) -> int:
    with Image.open(image_path) as image:
        gray = np.asarray(image.convert("L"))
    return int(np.count_nonzero(gray > 0))


def rebuild_idx_text(
    template_text: str,
    total_layers: int,
    pixel_counts: Dict[int, int],
) -> str:
    """Update common layer-count and PixelData fields while preserving the template."""
    text = template_text
    total_white = int(sum(pixel_counts.values()))

    # Common total-layer keys used by DLP .idx files.
    patterns = [
        r"(?im)^(\s*TotalLayer\s*=\s*)\d+\s*$",
        r"(?im)^(\s*TotalLayers\s*=\s*)\d+\s*$",
        r"(?im)^(\s*LayerCount\s*=\s*)\d+\s*$",
        r"(?im)^(\s*TotalLayerCount\s*=\s*)\d+\s*$",
    ]
    replaced_layer_key = False
    for pattern in patterns:
        text, count = re.subn(
            pattern,
            rf"\g<1>{int(total_layers)}",
            text,
        )
        replaced_layer_key = replaced_layer_key or count > 0

    pixel_lines = [
        f"{sec_name(layer_no)} = {int(pixel_counts.get(layer_no, 0))}"
        for layer_no in range(1, total_layers + 1)
    ]
    pixel_block = "\n".join(pixel_lines)

    # Existing [PixelData] block
    text, pixel_block_count = re.subn(
        r"(\[PixelData\]\s*\r?\n)(.*?)(\r?\n\s*\[TotalPixelWhiteCount\])",
        lambda match: match.group(1) + pixel_block + match.group(3),
        text,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Existing TotalPixelWhiteCount value
    text, total_white_count = re.subn(
        r"(?im)^(\s*TotalPixelWhiteCount\s*=\s*)\d+\s*$",
        rf"\g<1>{total_white}",
        text,
        count=1,
    )

    # Conservative fallback when the template has no expected blocks.
    append_blocks: List[str] = []
    if not replaced_layer_key:
        append_blocks.append(f"TotalLayer = {int(total_layers)}")
    if pixel_block_count == 0:
        append_blocks.append("[PixelData]\n" + pixel_block)
    if total_white_count == 0:
        append_blocks.append(
            "[TotalPixelWhiteCount]\n"
            f"TotalPixelWhiteCount = {total_white}"
        )
    if append_blocks:
        text = text.rstrip() + "\n\n" + "\n\n".join(append_blocks) + "\n"

    return text


def copy_template_assets(
    template_slice_folder: Path,
    destination_slice_folder: Path,
) -> Optional[Path]:
    template_slice_folder = Path(template_slice_folder)
    destination_slice_folder = Path(destination_slice_folder)

    if not template_slice_folder.exists():
        raise FileNotFoundError(
            f"Template .slice folder not found: {template_slice_folder}"
        )

    destination_slice_folder.mkdir(parents=True, exist_ok=True)

    # copy common files
    for filename in ("default.gcode", "Preview_t.png"):
        source = template_slice_folder / filename
        if source.exists():
            shutil.copy2(source, destination_slice_folder / filename)

    idx_candidates = sorted(
        template_slice_folder.glob("*.idx"),
        key=natural_sort_key,
    )
    if not idx_candidates:
        return None

    idx_out = destination_slice_folder / f"{destination_slice_folder.stem}.idx"
    shutil.copy2(idx_candidates[0], idx_out)
    return idx_out


def update_idx_from_images(
    slice_folder: Path,
    idx_path: Path,
) -> None:
    sec_files = list_sec_files(slice_folder)
    if not sec_files:
        raise RuntimeError(f"No SEC images in: {slice_folder}")
    total_layers = max(sec_files)
    pixel_counts = {
        layer_no: count_white_pixels(sec_files[layer_no])
        for layer_no in range(1, total_layers + 1)
        if layer_no in sec_files
    }
    template_text = read_text_auto(idx_path)
    new_text = rebuild_idx_text(template_text, total_layers, pixel_counts)
    idx_path.write_text(new_text, encoding="utf-8")


def prepend_front_layers_in_place(
    slice_folder: Path,
    additional_layers: int,
    idx_path: Optional[Path] = None,
) -> None:
    slice_folder = Path(slice_folder)
    sec_files = list_sec_files(slice_folder)
    if not sec_files:
        raise RuntimeError(f"No SEC images in: {slice_folder}")
    if additional_layers <= 0:
        return

    original_layers = sorted(sec_files)
    first_image = sec_files[original_layers[0]]
    temporary = slice_folder / "__SEC_TEMP__"
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir()

    # Move original images out first to avoid filename collisions.
    for layer_no, path in sec_files.items():
        shutil.move(str(path), str(temporary / sec_name(layer_no)))

    # New front layers = copies of the original first layer.
    for layer_no in range(1, additional_layers + 1):
        shutil.copy2(first_image if first_image.exists() else temporary / sec_name(original_layers[0]),
                     slice_folder / sec_name(layer_no))

    # Shift original layers.
    for original_layer_no in original_layers:
        shutil.move(
            str(temporary / sec_name(original_layer_no)),
            str(slice_folder / sec_name(original_layer_no + additional_layers)),
        )

    shutil.rmtree(temporary)

    if idx_path is not None and Path(idx_path).exists():
        update_idx_from_images(slice_folder, Path(idx_path))


def make_merged_slice_name(batch: Sequence[Path]) -> str:
    if not batch:
        raise ValueError("Empty batch.")
    first = safe_filename(batch[0].stem)
    last = safe_filename(batch[-1].stem)
    return f"{first}-{last}.slice"


def merge_six_slice_folders(
    slice_folders: Sequence[Path],
    output_folder: Path,
    template_slice_folder: Optional[Path],
    cfg: STLSliceConfig = CFG,
    copy_template: bool = True,
    add_front_layers: bool = True,
    overwrite: bool = True,
) -> Dict[str, object]:
    if not 1 <= len(slice_folders) <= 6:
        raise ValueError("Each merge batch must contain 1 to 6 .slice folders.")

    slice_folders = [Path(path) for path in slice_folders]
    output_folder = Path(output_folder)

    if output_folder.exists():
        if overwrite:
            shutil.rmtree(output_folder)
        else:
            raise FileExistsError(f"Merged folder already exists: {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)

    sec_maps = [list_sec_files(folder) for folder in slice_folders]
    if any(not mapping for mapping in sec_maps):
        empty = [
            folder.name
            for folder, mapping in zip(slice_folders, sec_maps)
            if not mapping
        ]
        raise RuntimeError(f"Folders without SEC images: {empty}")

    total_layers = max(max(mapping) for mapping in sec_maps)
    crop_box = center_crop_box(cfg)

    for layer_no in range(1, total_layers + 1):
        canvas = Image.new(
            "L",
            (cfg.canvas_w, cfg.canvas_h),
            int(cfg.background),
        )

        for position, sec_map in enumerate(sec_maps, start=1):
            image_path = sec_map.get(layer_no)
            if image_path is None:
                continue
            with Image.open(image_path) as image:
                normalized_image = ensure_image_centered_on_canvas(image, cfg)
                patch = normalized_image.crop(crop_box)
            canvas.paste(patch, SIX_REGION_POSITIONS[position])

        canvas.save(output_folder / sec_name(layer_no))

        if cfg.verbose and (
            layer_no == 1
            or layer_no % 50 == 0
            or layer_no == total_layers
        ):
            print(
                f"  {output_folder.name}: merged layer "
                f"{layer_no}/{total_layers}"
            )

    idx_path: Optional[Path] = None
    if copy_template:
        if template_slice_folder is None:
            raise ValueError("template_slice_folder is required when copy_template=True.")
        idx_path = copy_template_assets(
            template_slice_folder,
            output_folder,
        )
        if idx_path is not None:
            update_idx_from_images(output_folder, idx_path)

    info_lines = [
        f"Merged folder: {output_folder.name}",
        f"Input folder count: {len(slice_folders)}",
        f"Original merged layers: {total_layers}",
        f"Additional front layers: {cfg.additional_front_layers if add_front_layers else 0}",
        "",
        "[3x2 position assignment]",
    ]
    for position in range(1, 7):
        if position <= len(slice_folders):
            info_lines.append(
                f"{position}: {slice_folders[position - 1].name}"
            )
        else:
            info_lines.append(f"{position}: (empty)")

    (output_folder / "combine_info.txt").write_text(
        "\n".join(info_lines),
        encoding="utf-8",
    )

    if add_front_layers:
        prepend_front_layers_in_place(
            output_folder,
            additional_layers=int(cfg.additional_front_layers),
            idx_path=idx_path,
        )

    final_sec = list_sec_files(output_folder)
    return {
        "merged_folder": str(output_folder),
        "input_count": len(slice_folders),
        "input_folders": " | ".join(folder.name for folder in slice_folders),
        "original_layer_count": int(total_layers),
        "additional_front_layers": int(
            cfg.additional_front_layers if add_front_layers else 0
        ),
        "final_layer_count": int(max(final_sec) if final_sec else 0),
        "template_copied": bool(copy_template),
        "idx_created": bool(idx_path is not None and idx_path.exists()),
    }


def merge_slice_root_in_batches_of_six(
    individual_root: Path,
    merged_root: Path,
    template_slice_folder: Optional[Path],
    cfg: STLSliceConfig = CFG,
    copy_template: bool = True,
    add_front_layers: bool = True,
    overwrite: bool = True,
    manifest_path: Optional[Path] = None,
) -> List[Dict[str, object]]:
    individual_root = Path(individual_root)
    merged_root = Path(merged_root)
    merged_root.mkdir(parents=True, exist_ok=True)

    folders = sorted(
        [
            path
            for path in individual_root.glob("*.slice")
            if path.is_dir()
        ],
        key=natural_sort_key,
    )
    if not folders:
        raise RuntimeError(f"No individual .slice folders in: {individual_root}")

    results: List[Dict[str, object]] = []
    for start in range(0, len(folders), 6):
        batch = folders[start:start + 6]
        merged_name = make_merged_slice_name(batch)
        log(
            "\n[MERGE] " + merged_name + "\n  "
            + "\n  ".join(folder.name for folder in batch),
            cfg,
        )
        result = merge_six_slice_folders(
            slice_folders=batch,
            output_folder=merged_root / merged_name,
            template_slice_folder=template_slice_folder,
            cfg=cfg,
            copy_template=copy_template,
            add_front_layers=add_front_layers,
            overwrite=overwrite,
        )
        results.append(result)

    if manifest_path is None:
        manifest_path = Path(OUTPUT_ROOT) / "Six_Model_Merge_Manifest.csv"
    write_manifest_rows(results, manifest_path)
    return results


def validate_slice_outputs(
    individual_root: Path,
    merged_root: Path,
    cfg: STLSliceConfig = CFG,
) -> Dict[str, object]:
    individual = sorted(
        [p for p in Path(individual_root).glob("*.slice") if p.is_dir()],
        key=natural_sort_key,
    )
    merged = sorted(
        [p for p in Path(merged_root).glob("*.slice") if p.is_dir()],
        key=natural_sort_key,
    )

    problems: List[str] = []
    for folder in individual:
        sec_files = list_sec_files(folder)
        if len(sec_files) != cfg.fixed_layer_count:
            problems.append(
                f"{folder.name}: individual layer count={len(sec_files)}"
            )
        if sec_files:
            with Image.open(next(iter(sec_files.values()))) as image:
                if image.size != (cfg.canvas_w, cfg.canvas_h):
                    problems.append(
                        f"{folder.name}: image size={image.size}"
                    )

    expected_merged_layers = (
        cfg.fixed_layer_count + cfg.additional_front_layers
    )
    for folder in merged:
        sec_files = list_sec_files(folder)
        if len(sec_files) != expected_merged_layers:
            problems.append(
                f"{folder.name}: merged layer count={len(sec_files)}"
            )
        if sec_files:
            with Image.open(next(iter(sec_files.values()))) as image:
                if image.size != (cfg.canvas_w, cfg.canvas_h):
                    problems.append(
                        f"{folder.name}: image size={image.size}"
                    )

    return {
        "individual_folder_count": len(individual),
        "merged_folder_count": len(merged),
        "expected_merged_folder_count": math.ceil(len(individual) / 6)
        if individual else 0,
        "problem_count": len(problems),
        "problems": problems,
    }


# =============================================================================
# Structured-output helpers
# =============================================================================
def write_manifest_rows(
    rows: Sequence[Dict[str, object]],
    manifest_path: Path,
) -> Path:
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    headers: List[str] = []
    normalized_rows: List[Dict[str, object]] = []
    for row in rows:
        normalized = dict(row)
        for key, value in list(normalized.items()):
            if isinstance(value, (list, tuple, set)):
                normalized[key] = " | ".join(map(str, value))
        normalized_rows.append(normalized)
        for key in normalized:
            if key not in headers:
                headers.append(key)

    with open(manifest_path, "w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(normalized_rows)

    return manifest_path


def copy_slice_folder_tree(
    source_folder: Path,
    destination_folder: Path,
    overwrite: bool = True,
) -> Path:
    source_folder = Path(source_folder)
    destination_folder = Path(destination_folder)

    if not source_folder.exists():
        raise FileNotFoundError(f"Source .slice folder not found: {source_folder}")

    if destination_folder.exists():
        if overwrite:
            shutil.rmtree(destination_folder)
        else:
            raise FileExistsError(f"Destination already exists: {destination_folder}")

    shutil.copytree(source_folder, destination_folder)
    return destination_folder


def duplicate_slice_root_with_front_layers(
    source_root: Path,
    output_root: Path,
    additional_layers: int,
    overwrite: bool = True,
    manifest_path: Optional[Path] = None,
) -> List[Dict[str, object]]:
    source_root = Path(source_root)
    output_root = Path(output_root)

    if not source_root.exists():
        raise FileNotFoundError(f"Source root not found: {source_root}")

    folders = sorted(
        [path for path in source_root.glob("*.slice") if path.is_dir()],
        key=natural_sort_key,
    )
    if not folders:
        raise RuntimeError(f"No .slice folders found in: {source_root}")

    output_root.mkdir(parents=True, exist_ok=True)
    results: List[Dict[str, object]] = []

    for folder in folders:
        destination = output_root / folder.name
        copy_slice_folder_tree(folder, destination, overwrite=overwrite)

        idx_candidates = sorted(destination.glob("*.idx"), key=natural_sort_key)
        idx_path = idx_candidates[0] if idx_candidates else None

        original_sec = list_sec_files(destination)
        original_layer_count = len(original_sec)

        prepend_front_layers_in_place(
            destination,
            additional_layers=int(additional_layers),
            idx_path=idx_path,
        )

        final_sec = list_sec_files(destination)
        results.append(
            {
                "source_folder": str(folder),
                "output_folder": str(destination),
                "original_layer_count": int(original_layer_count),
                "additional_front_layers": int(additional_layers),
                "final_layer_count": int(len(final_sec)),
                "idx_updated": bool(idx_path is not None and idx_path.exists()),
            }
        )

    if manifest_path is not None:
        write_manifest_rows(results, manifest_path)

    return results


def validate_slice_root(
    root: Path,
    expected_layers: int,
    cfg: STLSliceConfig = CFG,
    require_assets: bool = False,
    expected_image_size: Optional[Tuple[int, int]] = None,
) -> Dict[str, object]:
    root = Path(root)
    folders = sorted(
        [path for path in root.glob("*.slice") if path.is_dir()],
        key=natural_sort_key,
    ) if root.exists() else []

    problems: List[str] = []
    for folder in folders:
        sec_files = list_sec_files(folder)
        if int(expected_layers) > 0:
            if len(sec_files) != int(expected_layers):
                problems.append(
                    f"{folder.name}: SEC count={len(sec_files)}, expected={expected_layers}"
                )
            if sorted(sec_files) != list(range(1, int(expected_layers) + 1)):
                problems.append(
                    f"{folder.name}: SEC numbering is not 1~{expected_layers}"
                )
        else:
            if not sec_files:
                problems.append(f"{folder.name}: no SEC images found")
            elif sorted(sec_files) != list(range(1, len(sec_files) + 1)):
                problems.append(
                    f"{folder.name}: SEC numbering is not contiguous from 1"
                )
        if sec_files:
            first_path = sec_files[min(sec_files)]
            with Image.open(first_path) as image:
                expected_size = expected_image_size or (cfg.canvas_w, cfg.canvas_h)
                if image.size != expected_size:
                    problems.append(
                        f"{folder.name}: image size={image.size}, expected={expected_size}"
                    )
        if require_assets:
            expected_asset_paths = [
                folder / f"{folder.stem}.idx",
                folder / "default.gcode",
                folder / "Preview_t.png",
            ]
            for asset_path in expected_asset_paths:
                if not asset_path.exists():
                    problems.append(
                        f"{folder.name}: missing asset {asset_path.name}"
                    )

    return {
        "root": str(root),
        "folder_count": len(folders),
        "expected_layers": int(expected_layers),
        "problem_count": len(problems),
        "problems": problems,
    }


# =============================================================================
# TRUE MODEL-BOUNDARY RAW RASTERIZATION OVERRIDES
# =============================================================================
# The earlier fixed 461 x 461 raster functions remain above for compatibility,
# but the functions below override the actual Raw/COM workflow.

@dataclass(frozen=True)
class RawRasterSpec:
    width_px: int
    height_px: int
    pixel_size_mm: float
    center_x_mm: float
    center_y_mm: float
    x_left_center_mm: float
    y_top_center_mm: float
    mesh_min_x_mm: float
    mesh_max_x_mm: float
    mesh_min_y_mm: float
    mesh_max_y_mm: float
    margin_px: int


def _odd_pixel_count_for_span(
    span_mm: float,
    pixel_size_mm: float,
    margin_px: int,
    force_odd: bool,
) -> int:
    span_mm = max(0.0, float(span_mm))
    pixel_size_mm = float(pixel_size_mm)
    margin_px = max(0, int(margin_px))
    if pixel_size_mm <= 0:
        raise ValueError("pixel_size_mm must be positive")

    # +1 includes both boundary-end pixel centers.
    core_pixels = int(math.ceil(span_mm / pixel_size_mm)) + 1
    total_pixels = max(1, core_pixels + 2 * margin_px)
    if force_odd and total_pixels % 2 == 0:
        total_pixels += 1
    return total_pixels


def make_raw_raster_spec(
    mesh,
    cfg: STLSliceConfig = CFG,
    margin_px: int = RAW_BOUNDARY_MARGIN_PX,
    force_odd: bool = RAW_FORCE_ODD_IMAGE_SIZE,
) -> RawRasterSpec:
    bounds = np.asarray(mesh.bounds, dtype=float)
    min_x, min_y = float(bounds[0, 0]), float(bounds[0, 1])
    max_x, max_y = float(bounds[1, 0]), float(bounds[1, 1])

    center_x = 0.5 * (min_x + max_x)
    center_y = 0.5 * (min_y + max_y)
    span_x = max_x - min_x
    span_y = max_y - min_y

    width_px = _odd_pixel_count_for_span(
        span_x, cfg.pixel_size_mm, margin_px, force_odd
    )
    height_px = _odd_pixel_count_for_span(
        span_y, cfg.pixel_size_mm, margin_px, force_odd
    )

    half_width_mm = 0.5 * (width_px - 1) * cfg.pixel_size_mm
    half_height_mm = 0.5 * (height_px - 1) * cfg.pixel_size_mm

    return RawRasterSpec(
        width_px=int(width_px),
        height_px=int(height_px),
        pixel_size_mm=float(cfg.pixel_size_mm),
        center_x_mm=float(center_x),
        center_y_mm=float(center_y),
        x_left_center_mm=float(center_x - half_width_mm),
        y_top_center_mm=float(center_y + half_height_mm),
        mesh_min_x_mm=min_x,
        mesh_max_x_mm=max_x,
        mesh_min_y_mm=min_y,
        mesh_max_y_mm=max_y,
        margin_px=int(margin_px),
    )


def xy_to_raw_pixels(
    xy: np.ndarray,
    spec: RawRasterSpec,
) -> List[Tuple[int, int]]:
    xy = np.asarray(xy, dtype=float)
    px = (xy[:, 0] - spec.x_left_center_mm) / spec.pixel_size_mm
    py = (spec.y_top_center_mm - xy[:, 1]) / spec.pixel_size_mm
    return [(int(round(x)), int(round(y))) for x, y in zip(px, py)]


def rasterize_contours_to_raw(
    loops_xy: Sequence[np.ndarray],
    spec: RawRasterSpec,
    fill_rule: str = SECTION_FILL_RULE,
) -> np.ndarray:
    fill_rule = str(fill_rule).strip().lower()
    if fill_rule not in {"nested", "union", "even_odd"}:
        raise ValueError(f"Unsupported SECTION_FILL_RULE: {fill_rule}")

    if fill_rule == "nested":
        return _rasterize_nested_contours(
            loops_xy,
            width_px=spec.width_px,
            height_px=spec.height_px,
            point_mapper=lambda xy: xy_to_raw_pixels(xy, spec),
        )

    result = np.zeros((spec.height_px, spec.width_px), dtype=bool)
    for xy in loops_xy:
        points = xy_to_raw_pixels(xy, spec)
        if len(points) < 3:
            continue

        mask_img = Image.new("1", (spec.width_px, spec.height_px), 0)
        drawer = ImageDraw.Draw(mask_img)
        drawer.polygon(points, fill=1)
        contour_mask = np.asarray(mask_img, dtype=bool)

        if fill_rule == "union":
            result |= contour_mask
        else:
            result ^= contour_mask

    return result


def center_crop_or_pad_square(
    image: Image.Image,
    target_px: int,
    background: int = 0,
) -> Image.Image:
    target_px = int(target_px)
    if target_px <= 0:
        raise ValueError("target_px must be positive")

    gray = image.convert("L")
    width, height = gray.size

    crop_left = max(0, (width - target_px) // 2)
    crop_top = max(0, (height - target_px) // 2)
    crop_right = min(width, crop_left + target_px)
    crop_bottom = min(height, crop_top + target_px)
    cropped = gray.crop((crop_left, crop_top, crop_right, crop_bottom))

    if cropped.size == (target_px, target_px):
        return cropped

    result = Image.new("L", (target_px, target_px), int(background))
    paste_left = (target_px - cropped.size[0]) // 2
    paste_top = (target_px - cropped.size[1]) // 2
    result.paste(cropped, (paste_left, paste_top))
    return result


def render_one_stl_to_raw_slice_folder(
    stl_path: Path,
    output_folder: Path,
    cfg: STLSliceConfig = CFG,
    overwrite: bool = True,
) -> Dict[str, object]:
    stl_path = Path(stl_path)
    output_folder = Path(output_folder)

    if output_folder.exists():
        if overwrite:
            shutil.rmtree(output_folder)
        else:
            existing = list_sec_files(output_folder)
            if existing:
                return {
                    "source_stl": str(stl_path),
                    "slice_folder": str(output_folder),
                    "status": "skipped_existing",
                    "raw_layer_count": len(existing),
                }
            raise FileExistsError(f"Output folder already exists: {output_folder}")

    output_folder.mkdir(parents=True, exist_ok=True)
    mesh = load_stl_as_mesh(stl_path)
    mesh, diagnostics = prepare_mesh_for_slicing(mesh, cfg)
    raw_spec = make_raw_raster_spec(mesh, cfg)
    raw_layer_count = estimate_raw_layer_count(mesh, cfg)

    warnings: List[str] = []
    if not bool(mesh.is_watertight):
        warnings.append(
            f"Mesh is not watertight. Closed-loop filtering and {SECTION_FILL_RULE} fill are used for slicing."
        )

    white_counts: Dict[int, int] = {}
    failed_layers: List[int] = []

    for layer_no in range(1, raw_layer_count + 1):
        z_mm = (layer_no - 0.5) * cfg.layer_height_mm
        try:
            loops = section_polylines_xy(mesh, z_mm)
            binary = rasterize_contours_to_raw(loops, raw_spec, SECTION_FILL_RULE)
        except Exception:
            binary = np.zeros(
                (raw_spec.height_px, raw_spec.width_px), dtype=bool
            )
            failed_layers.append(layer_no)

        image = Image.fromarray(
            np.where(binary, cfg.foreground, cfg.background).astype(np.uint8),
            mode="L",
        )
        image.save(output_folder / sec_name(layer_no))
        white_counts[layer_no] = int(np.count_nonzero(binary))

        if cfg.verbose and (
            layer_no == 1
            or layer_no % 50 == 0
            or layer_no == raw_layer_count
        ):
            print(
                f"  {output_folder.name}: raw layer {layer_no}/{raw_layer_count} "
                f"size={raw_spec.width_px}x{raw_spec.height_px}"
            )

    boundary_info = {
        "pixel_size_mm": raw_spec.pixel_size_mm,
        "width_px": raw_spec.width_px,
        "height_px": raw_spec.height_px,
        "margin_px": raw_spec.margin_px,
        "mesh_min_x_mm": raw_spec.mesh_min_x_mm,
        "mesh_max_x_mm": raw_spec.mesh_max_x_mm,
        "mesh_min_y_mm": raw_spec.mesh_min_y_mm,
        "mesh_max_y_mm": raw_spec.mesh_max_y_mm,
        "mesh_center_x_mm": raw_spec.center_x_mm,
        "mesh_center_y_mm": raw_spec.center_y_mm,
        "raster_left_pixel_center_mm": raw_spec.x_left_center_mm,
        "raster_top_pixel_center_mm": raw_spec.y_top_center_mm,
    }
    if RAW_SAVE_BOUNDARY_INFO:
        (output_folder / "raw_boundary_info.json").write_text(
            json.dumps(boundary_info, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    info = {
        "source_stl": str(stl_path),
        "slice_folder": str(output_folder),
        "status": "completed",
        "raw_layer_count": int(raw_layer_count),
        "target_com_layer_count": int(cfg.fixed_layer_count),
        "raw_width_px": int(raw_spec.width_px),
        "raw_height_px": int(raw_spec.height_px),
        "pixel_size_mm": float(cfg.pixel_size_mm),
        "failed_layer_count": int(len(failed_layers)),
        "failed_layers": failed_layers,
        "warning_count": int(len(warnings)),
        "warnings": warnings,
        **boundary_info,
        **diagnostics,
    }
    (output_folder / "slice_info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return info


def extract_center_aligned_com_layers(
    raw_slice_folder: Path,
    output_folder: Path,
    cfg: STLSliceConfig = CFG,
    overwrite: bool = True,
) -> Dict[str, object]:
    raw_slice_folder = Path(raw_slice_folder)
    output_folder = Path(output_folder)
    raw_sec = list_sec_files(raw_slice_folder)
    if not raw_sec:
        raise RuntimeError(f"No SEC images found in raw slice folder: {raw_slice_folder}")

    if output_folder.exists():
        if overwrite:
            shutil.rmtree(output_folder)
        else:
            raise FileExistsError(f"Output folder already exists: {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)

    plan = build_center_aligned_layer_plan(
        len(raw_sec), int(cfg.fixed_layer_count)
    )
    target_px = int(COM_INDIVIDUAL_CROP_PX)
    blank_com = Image.new("L", (target_px, target_px), int(cfg.background))

    first_raw_size: Optional[Tuple[int, int]] = None
    for target_layer in range(1, int(cfg.fixed_layer_count) + 1):
        if plan["target_start"] <= target_layer <= plan["target_end"]:
            source_layer = plan["source_start"] + (
                target_layer - plan["target_start"]
            )
            source_path = raw_sec.get(source_layer)
            if source_path is None:
                raise RuntimeError(
                    f"Missing raw source layer {sec_name(source_layer)} "
                    f"in {raw_slice_folder.name}"
                )
            with Image.open(source_path) as image:
                if first_raw_size is None:
                    first_raw_size = image.size
                com_image = center_crop_or_pad_square(
                    image, target_px, cfg.background
                )
        else:
            com_image = blank_com.copy()

        if COM_INDIVIDUAL_MAP_TO_CANVAS:
            com_image = ensure_image_centered_on_canvas(com_image, cfg)
        com_image.save(output_folder / sec_name(target_layer))

    final_size = (
        (cfg.canvas_w, cfg.canvas_h)
        if COM_INDIVIDUAL_MAP_TO_CANVAS
        else (target_px, target_px)
    )
    info = {
        "raw_slice_folder": str(raw_slice_folder),
        "slice_folder": str(output_folder),
        "status": "completed",
        "raw_layer_count": int(len(raw_sec)),
        "target_layer_count": int(cfg.fixed_layer_count),
        "selection_mode": plan["mode"],
        "source_start_layer": int(plan["source_start"]),
        "source_end_layer": int(plan["source_end"]),
        "target_start_layer": int(plan["target_start"]),
        "target_end_layer": int(plan["target_end"]),
        "raw_image_size": list(first_raw_size) if first_raw_size else None,
        "com_crop_px": int(target_px),
        "image_size": list(final_size),
        "mapped_to_canvas": bool(COM_INDIVIDUAL_MAP_TO_CANVAS),
    }
    (output_folder / "com_extraction_info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return info


def validate_raw_boundary_root(
    root: Path,
    cfg: STLSliceConfig = CFG,
) -> Dict[str, object]:
    root = Path(root)
    folders = sorted(
        [path for path in root.glob("*.slice") if path.is_dir()],
        key=natural_sort_key,
    ) if root.exists() else []

    problems: List[str] = []
    sizes: Dict[str, Tuple[int, int]] = {}
    for folder in folders:
        sec_files = list_sec_files(folder)
        if not sec_files:
            problems.append(f"{folder.name}: no SEC images found")
            continue
        if sorted(sec_files) != list(range(1, len(sec_files) + 1)):
            problems.append(f"{folder.name}: SEC numbering is not contiguous")

        folder_sizes = set()
        for path in sec_files.values():
            with Image.open(path) as image:
                folder_sizes.add(image.size)
            if len(folder_sizes) > 1:
                break
        if len(folder_sizes) != 1:
            problems.append(f"{folder.name}: inconsistent Raw image sizes")
        else:
            sizes[folder.name] = next(iter(folder_sizes))

        boundary_path = folder / "raw_boundary_info.json"
        if RAW_SAVE_BOUNDARY_INFO and not boundary_path.exists():
            problems.append(f"{folder.name}: missing raw_boundary_info.json")

    return {
        "root": str(root),
        "folder_count": len(folders),
        "model_image_sizes": {k: list(v) for k, v in sizes.items()},
        "problem_count": len(problems),
        "problems": problems,
    }


# ===== ROBUST SCANLINE =====
# =============================================================================
# ROBUST MESH PIXEL-CENTER SCANLINE RASTERIZER — HYBRID NODE-UNION ENGINE
# =============================================================================
# Problem addressed
# -----------------
# Lattice STL files are often exported as overlapping strut/node triangle shells
# rather than one Boolean-unioned manifold. Global even-odd parity then behaves
# like XOR and creates black diamonds or cross-shaped voids at node overlaps.
#
# The default hybrid engine uses:
#   1) oriented non-zero winding for exact overlap union when the row closes;
#   2) bidirectional winding agreement when a non-manifold row does not close;
#   3) a small padded binary closing only on affected layers, sealing residual
#      node gaps without eroding the original white geometry.
#
# It continues to bypass contour joining and forced polygon closure, so the
# previously corrected artificial horizontal-line problem remains eliminated.


def _mesh_plane_oriented_segments_xy(mesh, z_mm: float) -> Tuple[np.ndarray, np.ndarray]:
    """Return consistently oriented XY section segments and source face IDs."""
    result = trimesh.intersections.mesh_plane(
        mesh=mesh,
        plane_normal=np.array([0.0, 0.0, 1.0], dtype=float),
        plane_origin=np.array([0.0, 0.0, float(z_mm)], dtype=float),
        return_faces=True,
    )
    if not isinstance(result, tuple) or len(result) != 2:
        raise RuntimeError(
            "mesh_plane(return_faces=True) must return (segments, face_index)."
        )

    segments_3d, face_index = result
    segments_3d = np.asarray(segments_3d, dtype=float)
    face_index = np.asarray(face_index, dtype=np.int64)

    if segments_3d.size == 0:
        return (
            np.empty((0, 2, 2), dtype=float),
            np.empty((0,), dtype=np.int64),
        )
    if segments_3d.ndim != 3 or segments_3d.shape[1:] != (2, 3):
        raise RuntimeError(
            f"Unexpected section segment shape at z={z_mm:.9f}: {segments_3d.shape}"
        )

    segments_xy = segments_3d[:, :, :2].copy()
    normals = np.asarray(mesh.face_normals[face_index], dtype=float)
    segment_vector = segments_xy[:, 1] - segments_xy[:, 0]

    # Viewed from +Z, +Z x outward normal gives consistent section orientation.
    desired_tangent = np.column_stack((-normals[:, 1], normals[:, 0]))
    valid = (
        np.all(np.isfinite(segments_xy), axis=(1, 2))
        & np.all(np.isfinite(normals), axis=1)
        & (np.linalg.norm(segment_vector, axis=1) > 1.0e-12)
        & (np.linalg.norm(desired_tangent, axis=1) > 1.0e-12)
    )
    segments_xy = segments_xy[valid]
    face_index = face_index[valid]
    desired_tangent = desired_tangent[valid]

    if len(segments_xy) == 0:
        return segments_xy.reshape(0, 2, 2), face_index

    actual_tangent = segments_xy[:, 1] - segments_xy[:, 0]
    flip = np.einsum("ij,ij->i", actual_tangent, desired_tangent) < 0.0
    segments_xy[flip] = segments_xy[flip][:, ::-1]
    return segments_xy, face_index


def _cluster_signed_scanline_events(
    x_intersections: np.ndarray,
    winding_delta: np.ndarray,
    tolerance_mm: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Cluster coincident crossings and sum their signed winding changes."""
    x = np.asarray(x_intersections, dtype=float)
    delta = np.asarray(winding_delta, dtype=np.int64)
    finite = np.isfinite(x)
    x = x[finite]
    delta = delta[finite]
    if x.size == 0:
        return x, delta

    order = np.argsort(x, kind="mergesort")
    x = x[order]
    delta = delta[order]
    tolerance_mm = max(float(tolerance_mm), 0.0)

    clustered_x: List[float] = []
    clustered_delta: List[int] = []
    start = 0
    for index in range(1, len(x) + 1):
        end_cluster = (
            index == len(x)
            or abs(float(x[index]) - float(x[index - 1])) > tolerance_mm
        )
        if not end_cluster:
            continue
        signed_sum = int(np.sum(delta[start:index]))
        if signed_sum != 0:
            clustered_x.append(float(np.mean(x[start:index])))
            clustered_delta.append(signed_sum)
        start = index

    return (
        np.asarray(clustered_x, dtype=float),
        np.asarray(clustered_delta, dtype=np.int64),
    )


def _row_signed_winding_events(
    oriented_segments_xy: np.ndarray,
    y_mm: float,
    tolerance_mm: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return ordered X crossings and signed winding deltas for one image row."""
    if len(oriented_segments_xy) == 0:
        return np.empty(0, dtype=float), np.empty(0, dtype=np.int64)

    y0 = oriented_segments_xy[:, 0, 1]
    y1 = oriented_segments_xy[:, 1, 1]

    # Half-open endpoint rule; horizontal segments are excluded automatically.
    crosses = ((y0 <= y_mm) & (y_mm < y1)) | ((y1 <= y_mm) & (y_mm < y0))
    active = oriented_segments_xy[crosses]
    if len(active) == 0:
        return np.empty(0, dtype=float), np.empty(0, dtype=np.int64)

    ax = active[:, 0, 0]
    ay = active[:, 0, 1]
    bx = active[:, 1, 0]
    by = active[:, 1, 1]
    denom = by - ay
    valid = np.abs(denom) > 1.0e-15
    if not np.any(valid):
        return np.empty(0, dtype=float), np.empty(0, dtype=np.int64)

    ax = ax[valid]
    ay = ay[valid]
    bx = bx[valid]
    by = by[valid]
    x = ax + (float(y_mm) - ay) * (bx - ax) / (by - ay)
    delta = np.where(by > ay, 1, -1).astype(np.int64)
    return _cluster_signed_scanline_events(x, delta, tolerance_mm)


def _row_even_odd_events(
    segments_xy: np.ndarray,
    y_mm: float,
    tolerance_mm: float,
) -> np.ndarray:
    """Legacy parity crossings for comparison/fallback only."""
    event_x, event_delta = _row_signed_winding_events(
        segments_xy, y_mm, tolerance_mm
    )
    # Expand signed multiplicity to parity: only odd absolute multiplicity stays.
    keep = (np.abs(event_delta) % 2) == 1
    return event_x[keep]


def _fill_pixel_center_interval(
    row_mask: np.ndarray,
    x_centers: np.ndarray,
    x_start: float,
    x_end: float,
) -> None:
    if x_end < x_start:
        x_start, x_end = x_end, x_start
    col_start = int(np.searchsorted(x_centers, x_start, side="left"))
    col_stop = int(np.searchsorted(x_centers, x_end, side="right"))
    col_start = max(0, min(len(x_centers), col_start))
    col_stop = max(0, min(len(x_centers), col_stop))
    if col_stop > col_start:
        row_mask[col_start:col_stop] = True



# -----------------------------------------------------------------------------
# Boundary-locked node-hole repair
# -----------------------------------------------------------------------------
# The old v7/v8 fallback used global binary closing. A long narrow black slot can
# be only a few pixels thick but tens of pixels long; closing therefore fills the
# entire slot and creates a solid connection that does not exist in the model.
#
# This implementation NEVER grows the exterior boundary. The v5 parity mask is
# the immutable base. Winding union may only fill a compact background component
# that is fully enclosed by that base boundary.

_SCIPY_NDIMAGE = None
_SCIPY_NDIMAGE_CHECKED = False


def _get_scipy_ndimage_optional():
    global _SCIPY_NDIMAGE, _SCIPY_NDIMAGE_CHECKED
    if _SCIPY_NDIMAGE_CHECKED:
        return _SCIPY_NDIMAGE
    _SCIPY_NDIMAGE_CHECKED = True
    try:
        from scipy import ndimage as ndi
        _SCIPY_NDIMAGE = ndi
    except Exception:
        _SCIPY_NDIMAGE = None
    return _SCIPY_NDIMAGE


def _label_binary_components(binary: np.ndarray, connectivity: int = 8):
    """Label True components and return (labels, records).

    Each record contains: label, slice, area, touches_border. SciPy is used when
    available; a dependency-free 8/4-connected fallback is provided.
    """
    binary = np.asarray(binary, dtype=bool)
    height, width = binary.shape
    connectivity = 8 if int(connectivity) == 8 else 4
    ndi = _get_scipy_ndimage_optional()

    if ndi is not None:
        structure = (
            np.ones((3, 3), dtype=np.uint8)
            if connectivity == 8
            else np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
        )
        labels, count = ndi.label(binary, structure=structure)
        records = []
        for label_id, component_slice in enumerate(ndi.find_objects(labels), start=1):
            if component_slice is None:
                continue
            ys, xs = component_slice
            local = labels[component_slice] == label_id
            area = int(np.count_nonzero(local))
            touches_border = bool(
                ys.start == 0 or xs.start == 0
                or ys.stop == height or xs.stop == width
            )
            records.append({
                "label": int(label_id),
                "slice": component_slice,
                "area": area,
                "touches_border": touches_border,
            })
        return labels.astype(np.int32, copy=False), records

    # Dependency-free fallback. This is slower than SciPy but deterministic.
    from collections import deque

    labels = np.zeros(binary.shape, dtype=np.int32)
    records = []
    if connectivity == 8:
        neighbors = (
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        )
    else:
        neighbors = ((-1, 0), (0, -1), (0, 1), (1, 0))

    next_label = 0
    for seed_y, seed_x in np.argwhere(binary):
        seed_y = int(seed_y)
        seed_x = int(seed_x)
        if labels[seed_y, seed_x] != 0:
            continue

        next_label += 1
        queue = deque([(seed_y, seed_x)])
        labels[seed_y, seed_x] = next_label
        area = 0
        min_y = max_y = seed_y
        min_x = max_x = seed_x
        touches_border = False

        while queue:
            y, x = queue.popleft()
            area += 1
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            if y == 0 or x == 0 or y == height - 1 or x == width - 1:
                touches_border = True

            for dy, dx in neighbors:
                ny = y + dy
                nx = x + dx
                if (
                    0 <= ny < height and 0 <= nx < width
                    and binary[ny, nx]
                    and labels[ny, nx] == 0
                ):
                    labels[ny, nx] = next_label
                    queue.append((ny, nx))

        records.append({
            "label": int(next_label),
            "slice": (slice(min_y, max_y + 1), slice(min_x, max_x + 1)),
            "area": int(area),
            "touches_border": bool(touches_border),
        })

    return labels, records


def _dilate_one_pixel(binary: np.ndarray, connectivity: int = 8) -> np.ndarray:
    """Dependency-free one-pixel binary dilation."""
    binary = np.asarray(binary, dtype=bool)
    height, width = binary.shape
    out = binary.copy()
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if int(connectivity) == 8:
        offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dy, dx in offsets:
        y_src_start = max(0, -dy)
        y_src_stop = min(height, height - dy)
        x_src_start = max(0, -dx)
        x_src_stop = min(width, width - dx)
        y_dst_start = y_src_start + dy
        y_dst_stop = y_src_stop + dy
        x_dst_start = x_src_start + dx
        x_dst_stop = x_src_stop + dx
        out[y_dst_start:y_dst_stop, x_dst_start:x_dst_stop] |= binary[
            y_src_start:y_src_stop, x_src_start:x_src_stop
        ]
    return out


def _add_boundary_locked_local_winding_components(
    parity_mask: np.ndarray,
    winding_proposal_mask: np.ndarray,
    min_area_px: int = NODE_REPAIR_MIN_AREA_PX,
    max_span_px: int = NODE_REPAIR_MAX_SPAN_PX,
    max_area_px: int = NODE_REPAIR_MAX_AREA_PX,
    max_aspect_ratio: float = NODE_REPAIR_MAX_ASPECT_RATIO,
    min_base_contact_px: int = NODE_REPAIR_MIN_BASE_CONTACT_PX,
    connectivity: int = NODE_REPAIR_CONNECTIVITY,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """Add only local compact components proposed by winding union.

    The base image is always the v5 parity mask. Candidate pixels are strictly
    `winding_proposal_mask & ~parity_mask`. Each connected candidate component is
    accepted only when it is small in area and span, not elongated, and touches
    the existing parity geometry. No morphology is used and rejected candidate
    pixels can never influence neighboring components.

    This fills local node-overlap cracks (including cracks connected to exterior
    background) while rejecting long horizontal slot filling and distant bridges.
    """
    parity_mask = np.asarray(parity_mask, dtype=bool)
    winding_proposal_mask = np.asarray(winding_proposal_mask, dtype=bool)
    if parity_mask.shape != winding_proposal_mask.shape:
        raise ValueError("parity_mask and winding_proposal_mask must have the same shape")

    candidate = winding_proposal_mask & ~parity_mask
    result = parity_mask.copy()
    labels, records = _label_binary_components(candidate, connectivity=connectivity)

    min_area_px = max(1, int(min_area_px))
    max_span_px = max(1, int(max_span_px))
    max_area_px = max(min_area_px, int(max_area_px))
    max_aspect_ratio = max(1.0, float(max_aspect_ratio))
    min_base_contact_px = max(0, int(min_base_contact_px))

    accepted_components = 0
    added_pixels = 0
    rejected_tiny = 0
    rejected_span_or_area = 0
    rejected_aspect = 0
    rejected_contact = 0
    largest_added_area = 0
    largest_added_span = 0

    for record in records:
        component_slice = record["slice"]
        ys, xs = component_slice
        height_px = int(ys.stop - ys.start)
        width_px = int(xs.stop - xs.start)
        area_px = int(record["area"])
        span_px = max(height_px, width_px)
        short_span_px = max(1, min(height_px, width_px))
        aspect_ratio = float(span_px) / float(short_span_px)

        if area_px < min_area_px:
            rejected_tiny += 1
            continue
        if (
            area_px > max_area_px
            or width_px > max_span_px
            or height_px > max_span_px
        ):
            rejected_span_or_area += 1
            continue
        if aspect_ratio > max_aspect_ratio:
            rejected_aspect += 1
            continue

        # Expand the local box by one pixel and verify that the proposed addition
        # actually touches existing parity solid. This rejects isolated winding
        # islands created by local orientation errors.
        y0 = max(0, ys.start - 1)
        y1 = min(parity_mask.shape[0], ys.stop + 1)
        x0 = max(0, xs.start - 1)
        x1 = min(parity_mask.shape[1], xs.stop + 1)
        expanded = (slice(y0, y1), slice(x0, x1))
        local_component = labels[expanded] == int(record["label"])
        contact_ring = _dilate_one_pixel(
            local_component, connectivity=connectivity
        ) & ~local_component
        base_contact_px = int(np.count_nonzero(
            contact_ring & parity_mask[expanded]
        ))
        if base_contact_px < min_base_contact_px:
            rejected_contact += 1
            continue

        local_result = result[component_slice]
        component = labels[component_slice] == int(record["label"])
        local_result[component] = True
        result[component_slice] = local_result
        accepted_components += 1
        added_pixels += area_px
        largest_added_area = max(largest_added_area, area_px)
        largest_added_span = max(largest_added_span, span_px)

    return result, {
        "junction_repair_applied": bool(accepted_components > 0),
        "junction_repair_added_pixels": int(added_pixels),
        "junction_repair_filled_holes": int(accepted_components),
        "junction_repair_candidate_components": int(len(records)),
        "junction_repair_rejected_tiny": int(rejected_tiny),
        "junction_repair_rejected_span_or_area": int(rejected_span_or_area),
        "junction_repair_rejected_aspect": int(rejected_aspect),
        "junction_repair_rejected_contact": int(rejected_contact),
        "junction_repair_largest_filled_area_px": int(largest_added_area),
        "junction_repair_largest_filled_span_px": int(largest_added_span),
    }



def _max_true_run_1d(values: np.ndarray) -> int:
    """Return the longest contiguous True run in a 1-D Boolean array."""
    values = np.asarray(values, dtype=bool)
    if values.size == 0 or not np.any(values):
        return 0
    padded = np.pad(values.astype(np.int8), (1, 1), constant_values=0)
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    stops = np.flatnonzero(changes == -1)
    return int(np.max(stops - starts)) if len(starts) else 0


def _rasterize_single_scanline_row(
    segments_xy: np.ndarray,
    y_mm: float,
    x_centers: np.ndarray,
    solid_rule: str,
    intersection_tolerance_mm: float,
    vertex_jitter_mm: float,
    max_jitter_retries: int,
    fail_on_unclosed_winding: bool,
    row_seed: int,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """Rasterize one horizontal pixel-center scanline.

    A separate helper is used so the same row can be evaluated at y-delta,
    y, and y+delta without copying the parity/winding logic.
    """
    row_mask = np.zeros(len(x_centers), dtype=bool)
    base_jitter = max(float(vertex_jitter_mm), 0.0)
    retries = max(0, int(max_jitter_retries))
    jittered = False

    if solid_rule == "even_odd":
        x_hits = _row_even_odd_events(
            segments_xy, float(y_mm), float(intersection_tolerance_mm)
        )
        if len(x_hits) % 2 == 1 and base_jitter > 0.0:
            for retry in range(1, retries + 1):
                magnitude = base_jitter * (10.0 ** (retry - 1))
                sign = 1.0 if (int(row_seed) + retry) % 2 == 0 else -1.0
                retry_hits = _row_even_odd_events(
                    segments_xy,
                    float(y_mm) + sign * magnitude,
                    float(intersection_tolerance_mm),
                )
                if len(retry_hits) % 2 == 0:
                    x_hits = retry_hits
                    jittered = True
                    break

        odd = (len(x_hits) % 2) == 1
        if odd:
            if fail_on_unclosed_winding:
                raise RuntimeError(
                    f"Odd parity count at row_seed={row_seed}, count={len(x_hits)}."
                )
            # Do not allow a lone unmatched crossing to fill toward the image
            # boundary. Drop only the final unmatched event as the legacy-safe
            # fallback; subpixel voting will normally replace this sample.
            x_hits = x_hits[:-1]

        for x_start, x_end in x_hits.reshape(-1, 2):
            _fill_pixel_center_interval(
                row_mask, x_centers, float(x_start), float(x_end)
            )
        return row_mask, {
            "odd": bool(odd),
            "unclosed": False,
            "jittered": bool(jittered),
            "max_abs_winding": 1 if len(x_hits) else 0,
        }

    event_x, event_delta = _row_signed_winding_events(
        segments_xy, float(y_mm), float(intersection_tolerance_mm)
    )
    final_winding = int(np.sum(event_delta)) if len(event_delta) else 0

    if final_winding != 0 and base_jitter > 0.0:
        for retry in range(1, retries + 1):
            magnitude = base_jitter * (10.0 ** (retry - 1))
            sign = 1.0 if (int(row_seed) + retry) % 2 == 0 else -1.0
            retry_x, retry_delta = _row_signed_winding_events(
                segments_xy,
                float(y_mm) + sign * magnitude,
                float(intersection_tolerance_mm),
            )
            if int(np.sum(retry_delta)) == 0:
                event_x = retry_x
                event_delta = retry_delta
                final_winding = 0
                jittered = True
                break

    unclosed = final_winding != 0
    if unclosed and fail_on_unclosed_winding:
        raise RuntimeError(
            f"Unclosed winding at row_seed={row_seed}, final={final_winding}."
        )

    left_winding = 0
    previous_x: Optional[float] = None
    max_abs_winding = 0
    for x_event, delta in zip(event_x, event_delta):
        if previous_x is not None:
            if solid_rule == "hybrid_winding_union" and final_winding != 0:
                right_winding = left_winding - final_winding
                inside = (left_winding != 0) and (right_winding != 0)
                max_abs_winding = max(
                    max_abs_winding,
                    abs(left_winding),
                    abs(right_winding),
                )
            else:
                inside = left_winding != 0
                max_abs_winding = max(max_abs_winding, abs(left_winding))
            if inside:
                _fill_pixel_center_interval(
                    row_mask, x_centers, float(previous_x), float(x_event)
                )
        left_winding += int(delta)
        previous_x = float(x_event)

    return row_mask, {
        "odd": False,
        "unclosed": bool(unclosed),
        "jittered": bool(jittered),
        "max_abs_winding": int(max_abs_winding),
    }


def _majority_three_rows(
    lower_row: np.ndarray,
    center_row: np.ndarray,
    upper_row: np.ndarray,
) -> np.ndarray:
    """Pixelwise 2-of-3 Boolean majority."""
    return (
        (lower_row & center_row)
        | (lower_row & upper_row)
        | (center_row & upper_row)
    )


def _rasterize_oriented_segments_by_rule(
    segments_xy: np.ndarray,
    spec: RawRasterSpec,
    solid_rule: str,
    intersection_tolerance_mm: float,
    vertex_jitter_mm: float,
    max_jitter_retries: int,
    fail_on_unclosed_winding: bool,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """Rasterize oriented section segments with subpixel-stable scanlines.

    When enabled, each output row is sampled at y-delta, y, and y+delta and
    combined by a 2-of-3 majority vote. A crossing configuration that exists
    only at the exact center (for example, a STEP tessellation vertex lying
    exactly on the scanline) is therefore rejected instead of pairing with a
    distant crossing and creating a one-pixel horizontal bridge.
    """
    solid_rule = str(solid_rule).strip().lower()
    if solid_rule not in {"hybrid_winding_union", "nonzero_winding", "even_odd"}:
        raise ValueError(f"Unsupported base scanline rule: {solid_rule!r}")

    mask = np.zeros((spec.height_px, spec.width_px), dtype=bool)
    if len(segments_xy) == 0:
        return mask, {
            "odd_row_count": 0,
            "odd_rows": [],
            "unclosed_row_count": 0,
            "unclosed_rows": [],
            "jittered_row_count": 0,
            "max_abs_winding": 0,
            "subpixel_stabilized_row_count": 0,
            "subpixel_changed_pixel_count": 0,
            "subpixel_max_center_only_run_px": 0,
        }

    pixel_size = float(spec.pixel_size_mm)
    x_centers = spec.x_left_center_mm + np.arange(spec.width_px) * pixel_size
    y_centers = spec.y_top_center_mm - np.arange(spec.height_px) * pixel_size

    use_subpixel = bool(SCANLINE_SUBPIXEL_STABILIZATION)
    subpixel_mode = str(SCANLINE_SUBPIXEL_MODE).strip().lower()
    if use_subpixel and subpixel_mode != "majority_3":
        raise ValueError(
            f"Unsupported SCANLINE_SUBPIXEL_MODE={SCANLINE_SUBPIXEL_MODE!r}; "
            "expected 'majority_3'."
        )
    offset_mm = (
        max(0.0, float(SCANLINE_SUBPIXEL_OFFSET_FRACTION)) * pixel_size
        if use_subpixel else 0.0
    )

    odd_rows: List[int] = []
    unclosed_rows: List[int] = []
    jittered_rows = 0
    max_abs_winding = 0
    stabilized_rows = 0
    changed_pixels = 0
    max_center_only_run = 0

    for row_index, y_center in enumerate(y_centers):
        center_row, center_diag = _rasterize_single_scanline_row(
            segments_xy=segments_xy,
            y_mm=float(y_center),
            x_centers=x_centers,
            solid_rule=solid_rule,
            intersection_tolerance_mm=float(intersection_tolerance_mm),
            vertex_jitter_mm=float(vertex_jitter_mm),
            max_jitter_retries=int(max_jitter_retries),
            fail_on_unclosed_winding=bool(fail_on_unclosed_winding),
            row_seed=int(row_index * 3 + 1),
        )

        if center_diag["odd"]:
            odd_rows.append(int(row_index))
        if center_diag["unclosed"]:
            unclosed_rows.append(int(row_index))
        jittered_rows += int(bool(center_diag["jittered"]))
        max_abs_winding = max(
            max_abs_winding, int(center_diag["max_abs_winding"])
        )

        if use_subpixel and offset_mm > 0.0:
            lower_row, lower_diag = _rasterize_single_scanline_row(
                segments_xy=segments_xy,
                y_mm=float(y_center) - offset_mm,
                x_centers=x_centers,
                solid_rule=solid_rule,
                intersection_tolerance_mm=float(intersection_tolerance_mm),
                vertex_jitter_mm=float(vertex_jitter_mm),
                max_jitter_retries=int(max_jitter_retries),
                fail_on_unclosed_winding=False,
                row_seed=int(row_index * 3),
            )
            upper_row, upper_diag = _rasterize_single_scanline_row(
                segments_xy=segments_xy,
                y_mm=float(y_center) + offset_mm,
                x_centers=x_centers,
                solid_rule=solid_rule,
                intersection_tolerance_mm=float(intersection_tolerance_mm),
                vertex_jitter_mm=float(vertex_jitter_mm),
                max_jitter_retries=int(max_jitter_retries),
                fail_on_unclosed_winding=False,
                row_seed=int(row_index * 3 + 2),
            )
            stable_row = _majority_three_rows(
                lower_row, center_row, upper_row
            )
            difference = stable_row ^ center_row
            if np.any(difference):
                stabilized_rows += 1
                changed_pixels += int(np.count_nonzero(difference))
                center_only = center_row & ~lower_row & ~upper_row
                max_center_only_run = max(
                    max_center_only_run,
                    _max_true_run_1d(center_only),
                )
            mask[row_index] = stable_row
            jittered_rows += int(bool(lower_diag["jittered"]))
            jittered_rows += int(bool(upper_diag["jittered"]))
            max_abs_winding = max(
                max_abs_winding,
                int(lower_diag["max_abs_winding"]),
                int(upper_diag["max_abs_winding"]),
            )
        else:
            mask[row_index] = center_row

    return mask, {
        "odd_row_count": int(len(odd_rows)),
        "odd_rows": odd_rows,
        "unclosed_row_count": int(len(unclosed_rows)),
        "unclosed_rows": unclosed_rows,
        "jittered_row_count": int(jittered_rows),
        "max_abs_winding": int(max_abs_winding),
        "subpixel_stabilized_row_count": int(stabilized_rows),
        "subpixel_changed_pixel_count": int(changed_pixels),
        "subpixel_max_center_only_run_px": int(max_center_only_run),
    }


def _remove_isolated_long_horizontal_runs(
    mask: np.ndarray,
    min_run_px: int = SCANLINE_SINGLE_ROW_MIN_LENGTH_PX,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """Remove only long one-row pixels unsupported vertically.

    For each row, candidate pixels are white in the current row but black in
    both immediately adjacent rows. Only contiguous candidate runs at least
    `min_run_px` long are removed. Existing nodes/struts supported on either
    neighboring row remain untouched. No background pixel is ever added.
    """
    mask = np.asarray(mask, dtype=bool)
    result = mask.copy()
    min_run_px = max(1, int(min_run_px))
    removed_runs = 0
    removed_pixels = 0
    affected_rows: List[int] = []
    max_removed_run_px = 0

    if mask.shape[0] < 3:
        return result, {
            "single_row_guard_applied": False,
            "single_row_removed_runs": 0,
            "single_row_removed_pixels": 0,
            "single_row_affected_rows": [],
            "single_row_max_removed_run_px": 0,
        }

    for y in range(1, mask.shape[0] - 1):
        unsupported = mask[y] & ~mask[y - 1] & ~mask[y + 1]
        if not np.any(unsupported):
            continue
        padded = np.pad(unsupported.astype(np.int8), (1, 1), constant_values=0)
        changes = np.diff(padded)
        starts = np.flatnonzero(changes == 1)
        stops = np.flatnonzero(changes == -1)
        row_changed = False
        for x0, x1 in zip(starts, stops):
            run_length = int(x1 - x0)
            if run_length < min_run_px:
                continue
            result[y, int(x0):int(x1)] = False
            removed_runs += 1
            removed_pixels += run_length
            max_removed_run_px = max(max_removed_run_px, run_length)
            row_changed = True
        if row_changed:
            affected_rows.append(int(y))

    return result, {
        "single_row_guard_applied": bool(removed_runs > 0),
        "single_row_removed_runs": int(removed_runs),
        "single_row_removed_pixels": int(removed_pixels),
        "single_row_affected_rows": affected_rows,
        "single_row_max_removed_run_px": int(max_removed_run_px),
    }


def rasterize_mesh_section_scanline(
    mesh,
    z_mm: float,
    spec: RawRasterSpec,
    solid_rule: str = SCANLINE_SOLID_RULE,
    intersection_tolerance_mm: float = SCANLINE_INTERSECTION_TOL_MM,
    vertex_jitter_mm: float = SCANLINE_VERTEX_JITTER_MM,
    max_jitter_retries: int = SCANLINE_MAX_JITTER_RETRIES,
    fail_on_unclosed_winding: bool = SCANLINE_FAIL_ON_UNCLOSED_WINDING,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """Rasterize one mesh section without contour assembly.

    boundary_locked_node_union (default)
        Uses v5 parity as the base and accepts only compact local components from
        the winding-union addition proposal.

    hybrid_winding_union / nonzero_winding / even_odd
        Diagnostic/legacy modes. They do not apply any morphology.
    """
    solid_rule = str(solid_rule).strip().lower()
    supported = {
        "boundary_locked_node_union",
        "hybrid_winding_union",
        "nonzero_winding",
        "even_odd",
    }
    if solid_rule not in supported:
        raise ValueError(
            f"Unsupported SCANLINE_SOLID_RULE={solid_rule!r}; "
            f"expected one of {sorted(supported)}."
        )

    segments_xy, _ = _mesh_plane_oriented_segments_xy(mesh, z_mm)
    empty = np.zeros((spec.height_px, spec.width_px), dtype=bool)
    if len(segments_xy) == 0:
        return empty, {
            "segment_count": 0,
            "odd_row_count": 0,
            "odd_rows": [],
            "unclosed_row_count": 0,
            "unclosed_rows": [],
            "jittered_row_count": 0,
            "max_abs_winding": 0,
            "subpixel_stabilized_row_count": 0,
            "subpixel_changed_pixel_count": 0,
            "subpixel_max_center_only_run_px": 0,
            "single_row_guard_applied": False,
            "single_row_removed_runs": 0,
            "single_row_removed_pixels": 0,
            "single_row_affected_rows": [],
            "single_row_max_removed_run_px": 0,
            "junction_repair_applied": False,
            "junction_repair_added_pixels": 0,
            "junction_repair_filled_holes": 0,
            "solid_rule": solid_rule,
        }

    common = dict(
        segments_xy=segments_xy,
        spec=spec,
        intersection_tolerance_mm=float(intersection_tolerance_mm),
        vertex_jitter_mm=float(vertex_jitter_mm),
        max_jitter_retries=int(max_jitter_retries),
        fail_on_unclosed_winding=bool(fail_on_unclosed_winding),
    )

    if solid_rule != "boundary_locked_node_union":
        mask, diag = _rasterize_oriented_segments_by_rule(
            solid_rule=solid_rule, **common
        )
        if bool(SCANLINE_SINGLE_ROW_GUARD):
            mask, single_row_diag = _remove_isolated_long_horizontal_runs(
                mask,
                min_run_px=int(SCANLINE_SINGLE_ROW_MIN_LENGTH_PX),
            )
        else:
            single_row_diag = {
                "single_row_guard_applied": False,
                "single_row_removed_runs": 0,
                "single_row_removed_pixels": 0,
                "single_row_affected_rows": [],
                "single_row_max_removed_run_px": 0,
            }
        diag.update({
            "segment_count": int(len(segments_xy)),
            "junction_repair_applied": False,
            "junction_repair_added_pixels": 0,
            "junction_repair_filled_holes": 0,
            "solid_rule": solid_rule,
            **single_row_diag,
        })
        return mask, diag

    # v5 result: trusted base geometry with no artificial long connections.
    parity_mask, parity_diag = _rasterize_oriented_segments_by_rule(
        solid_rule="even_odd", **common
    )

    # Winding result is a proposal only. Its added pixels are filtered component
    # by component before they are allowed into the output.
    winding_mask, winding_diag = _rasterize_oriented_segments_by_rule(
        solid_rule="hybrid_winding_union", **common
    )

    if bool(NODE_JUNCTION_REPAIR):
        mask, repair_diag = _add_boundary_locked_local_winding_components(
            parity_mask=parity_mask,
            winding_proposal_mask=winding_mask,
        )
    else:
        mask = parity_mask
        repair_diag = {
            "junction_repair_applied": False,
            "junction_repair_added_pixels": 0,
            "junction_repair_filled_holes": 0,
            "junction_repair_candidate_components": 0,
            "junction_repair_rejected_tiny": 0,
            "junction_repair_rejected_span_or_area": 0,
            "junction_repair_rejected_aspect": 0,
            "junction_repair_rejected_contact": 0,
            "junction_repair_largest_filled_area_px": 0,
            "junction_repair_largest_filled_span_px": 0,
        }

    if bool(SCANLINE_SINGLE_ROW_GUARD):
        mask, single_row_diag = _remove_isolated_long_horizontal_runs(
            mask,
            min_run_px=int(SCANLINE_SINGLE_ROW_MIN_LENGTH_PX),
        )
    else:
        single_row_diag = {
            "single_row_guard_applied": False,
            "single_row_removed_runs": 0,
            "single_row_removed_pixels": 0,
            "single_row_affected_rows": [],
            "single_row_max_removed_run_px": 0,
        }

    diagnostics = {
        "segment_count": int(len(segments_xy)),
        "odd_row_count": int(parity_diag.get("odd_row_count", 0)),
        "odd_rows": list(parity_diag.get("odd_rows", [])),
        "unclosed_row_count": int(winding_diag.get("unclosed_row_count", 0)),
        "unclosed_rows": list(winding_diag.get("unclosed_rows", [])),
        "jittered_row_count": int(
            parity_diag.get("jittered_row_count", 0)
            + winding_diag.get("jittered_row_count", 0)
        ),
        "parity_jittered_row_count": int(parity_diag.get("jittered_row_count", 0)),
        "winding_jittered_row_count": int(winding_diag.get("jittered_row_count", 0)),
        "max_abs_winding": int(winding_diag.get("max_abs_winding", 0)),
        "subpixel_stabilized_row_count": int(
            parity_diag.get("subpixel_stabilized_row_count", 0)
            + winding_diag.get("subpixel_stabilized_row_count", 0)
        ),
        "parity_subpixel_stabilized_row_count": int(
            parity_diag.get("subpixel_stabilized_row_count", 0)
        ),
        "winding_subpixel_stabilized_row_count": int(
            winding_diag.get("subpixel_stabilized_row_count", 0)
        ),
        "subpixel_changed_pixel_count": int(
            parity_diag.get("subpixel_changed_pixel_count", 0)
            + winding_diag.get("subpixel_changed_pixel_count", 0)
        ),
        "subpixel_max_center_only_run_px": int(max(
            parity_diag.get("subpixel_max_center_only_run_px", 0),
            winding_diag.get("subpixel_max_center_only_run_px", 0),
        )),
        "winding_proposal_added_pixels": int(np.count_nonzero(winding_mask & ~parity_mask)),
        "solid_rule": solid_rule,
        **repair_diag,
        **single_row_diag,
    }
    return mask, diagnostics

def render_one_stl_to_raw_slice_folder(
    stl_path: Path,
    output_folder: Path,
    cfg: STLSliceConfig = CFG,
    overwrite: bool = True,
) -> Dict[str, object]:
    """Raw STL slicer using the hybrid overlap-union scanline engine."""
    stl_path = Path(stl_path)
    output_folder = Path(output_folder)

    if output_folder.exists():
        if overwrite:
            shutil.rmtree(output_folder)
        else:
            existing = list_sec_files(output_folder)
            if existing:
                return {
                    "source_stl": str(stl_path),
                    "slice_folder": str(output_folder),
                    "status": "skipped_existing",
                    "raw_layer_count": len(existing),
                }
            raise FileExistsError(f"Output folder already exists: {output_folder}")

    output_folder.mkdir(parents=True, exist_ok=True)
    mesh = load_stl_as_mesh(stl_path)
    mesh, diagnostics = prepare_mesh_for_slicing(mesh, cfg)
    raw_spec = make_raw_raster_spec(mesh, cfg)
    raw_layer_count = estimate_raw_layer_count(mesh, cfg)

    if str(STL_RASTER_MODE).strip().lower() != "scanline":
        raise ValueError(
            f"This renderer requires STL_RASTER_MODE='scanline', got "
            f"{STL_RASTER_MODE!r}."
        )

    boundary_edge_count = int(diagnostics.get("boundary_edge_count", -1))
    nonmanifold_edge_count = int(diagnostics.get("nonmanifold_edge_count", -1))
    try:
        body_count = int(mesh.body_count)
    except Exception:
        body_count = -1

    warnings: List[str] = []
    if boundary_edge_count > 0:
        warnings.append(
            f"Open boundary edges detected: {boundary_edge_count}."
        )
    if nonmanifold_edge_count > 0:
        warnings.append(
            f"Non-manifold/overlapping edges detected: {nonmanifold_edge_count}. "
            "Boundary-locked local node repair is enabled; long/large winding additions are rejected."
        )
    if not bool(mesh.is_winding_consistent):
        warnings.append(
            "Face winding is inconsistent; MESH_FIX_NORMALS=True was applied."
        )

    white_counts: Dict[int, int] = {}
    failed_layers: List[int] = []
    failed_layer_errors: Dict[int, str] = {}
    layer_segment_counts: Dict[int, int] = {}
    layer_jittered_rows: Dict[int, int] = {}
    layer_unclosed_rows: Dict[int, int] = {}
    layer_max_winding: Dict[int, int] = {}
    layer_repair_pixels: Dict[int, int] = {}
    layer_repair_holes: Dict[int, int] = {}
    layer_rejected_large_holes: Dict[int, int] = {}
    layer_subpixel_rows: Dict[int, int] = {}
    layer_subpixel_changed_pixels: Dict[int, int] = {}
    layer_single_row_removed_runs: Dict[int, int] = {}
    layer_single_row_removed_pixels: Dict[int, int] = {}

    for layer_no in range(1, raw_layer_count + 1):
        z_mm = (layer_no - 0.5) * cfg.layer_height_mm
        try:
            binary, layer_diag = rasterize_mesh_section_scanline(
                mesh=mesh, z_mm=z_mm, spec=raw_spec
            )
            layer_segment_counts[layer_no] = int(layer_diag["segment_count"])
            layer_jittered_rows[layer_no] = int(layer_diag["jittered_row_count"])
            layer_unclosed_rows[layer_no] = int(layer_diag["unclosed_row_count"])
            layer_max_winding[layer_no] = int(layer_diag["max_abs_winding"])
            layer_repair_pixels[layer_no] = int(
                layer_diag.get("junction_repair_added_pixels", 0)
            )
            layer_repair_holes[layer_no] = int(
                layer_diag.get("junction_repair_filled_holes", 0)
            )
            layer_rejected_large_holes[layer_no] = int(
                layer_diag.get("junction_repair_rejected_span_or_area", 0)
            )
            layer_subpixel_rows[layer_no] = int(
                layer_diag.get("subpixel_stabilized_row_count", 0)
            )
            layer_subpixel_changed_pixels[layer_no] = int(
                layer_diag.get("subpixel_changed_pixel_count", 0)
            )
            layer_single_row_removed_runs[layer_no] = int(
                layer_diag.get("single_row_removed_runs", 0)
            )
            layer_single_row_removed_pixels[layer_no] = int(
                layer_diag.get("single_row_removed_pixels", 0)
            )
        except Exception as exc:
            binary = np.zeros(
                (raw_spec.height_px, raw_spec.width_px), dtype=bool
            )
            failed_layers.append(layer_no)
            failed_layer_errors[layer_no] = str(exc)

        Image.fromarray(
            np.where(binary, cfg.foreground, cfg.background).astype(np.uint8),
            mode="L",
        ).save(
            output_folder / sec_name(layer_no),
            optimize=False,
            compress_level=1,
        )
        white_counts[layer_no] = int(np.count_nonzero(binary))

        if cfg.verbose and (
            layer_no == 1
            or layer_no % 50 == 0
            or layer_no == raw_layer_count
        ):
            print(
                f"  {output_folder.name}: raw layer {layer_no}/{raw_layer_count} "
                f"size={raw_spec.width_px}x{raw_spec.height_px} "
                f"segments={layer_segment_counts.get(layer_no, 0)} "
                f"unclosed_rows={layer_unclosed_rows.get(layer_no, 0)} "
                f"subpixel_rows={layer_subpixel_rows.get(layer_no, 0)} "
                f"single_row_removed={layer_single_row_removed_pixels.get(layer_no, 0)} "
                f"repair_px={layer_repair_pixels.get(layer_no, 0)}"
            )

    boundary_info = {
        "pixel_size_mm": raw_spec.pixel_size_mm,
        "width_px": raw_spec.width_px,
        "height_px": raw_spec.height_px,
        "margin_px": raw_spec.margin_px,
        "mesh_min_x_mm": raw_spec.mesh_min_x_mm,
        "mesh_max_x_mm": raw_spec.mesh_max_x_mm,
        "mesh_min_y_mm": raw_spec.mesh_min_y_mm,
        "mesh_max_y_mm": raw_spec.mesh_max_y_mm,
        "mesh_center_x_mm": raw_spec.center_x_mm,
        "mesh_center_y_mm": raw_spec.center_y_mm,
        "raster_left_pixel_center_mm": raw_spec.x_left_center_mm,
        "raster_top_pixel_center_mm": raw_spec.y_top_center_mm,
    }
    if RAW_SAVE_BOUNDARY_INFO:
        (output_folder / "raw_boundary_info.json").write_text(
            json.dumps(boundary_info, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    info = {
        "source_stl": str(stl_path),
        "slice_folder": str(output_folder),
        "status": "completed" if not failed_layers else "completed_with_failures",
        "raster_mode": "scanline_boundary_locked_node_union",
        "scanline_solid_rule": str(SCANLINE_SOLID_RULE),
        "node_junction_repair": bool(NODE_JUNCTION_REPAIR),
        "node_junction_repair_mode": str(NODE_JUNCTION_REPAIR_MODE),
        "node_repair_min_area_px": int(NODE_REPAIR_MIN_AREA_PX),
        "node_repair_max_span_px": int(NODE_REPAIR_MAX_SPAN_PX),
        "node_repair_max_area_px": int(NODE_REPAIR_MAX_AREA_PX),
        "node_repair_max_aspect_ratio": float(NODE_REPAIR_MAX_ASPECT_RATIO),
        "node_repair_min_base_contact_px": int(NODE_REPAIR_MIN_BASE_CONTACT_PX),
        "scanline_subpixel_stabilization": bool(SCANLINE_SUBPIXEL_STABILIZATION),
        "scanline_subpixel_mode": str(SCANLINE_SUBPIXEL_MODE),
        "scanline_subpixel_offset_fraction": float(SCANLINE_SUBPIXEL_OFFSET_FRACTION),
        "scanline_single_row_guard": bool(SCANLINE_SINGLE_ROW_GUARD),
        "scanline_single_row_min_length_px": int(SCANLINE_SINGLE_ROW_MIN_LENGTH_PX),
        "scanline_single_row_min_length_mm": float(SCANLINE_SINGLE_ROW_MIN_LENGTH_MM),
        "raw_layer_count": int(raw_layer_count),
        "target_com_layer_count": int(cfg.fixed_layer_count),
        "raw_width_px": int(raw_spec.width_px),
        "raw_height_px": int(raw_spec.height_px),
        "pixel_size_mm": float(cfg.pixel_size_mm),
        "body_count": body_count,
        "failed_layer_count": int(len(failed_layers)),
        "failed_layers": failed_layers,
        "failed_layer_errors": failed_layer_errors,
        "total_jittered_rows": int(sum(layer_jittered_rows.values())),
        "total_unclosed_rows": int(sum(layer_unclosed_rows.values())),
        "total_junction_repair_added_pixels": int(sum(layer_repair_pixels.values())),
        "total_junction_repair_filled_holes": int(sum(layer_repair_holes.values())),
        "total_rejected_large_or_long_holes": int(sum(layer_rejected_large_holes.values())),
        "total_subpixel_stabilized_rows": int(sum(layer_subpixel_rows.values())),
        "total_subpixel_changed_pixels": int(sum(layer_subpixel_changed_pixels.values())),
        "total_single_row_removed_runs": int(sum(layer_single_row_removed_runs.values())),
        "total_single_row_removed_pixels": int(sum(layer_single_row_removed_pixels.values())),
        "global_max_abs_winding": int(max(layer_max_winding.values(), default=0)),
        "warning_count": int(len(warnings)),
        "warnings": warnings,
        **boundary_info,
        **diagnostics,
    }
    (output_folder / "slice_info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    pd.DataFrame({
        "Layer": np.arange(1, raw_layer_count + 1),
        "File": [sec_name(i) for i in range(1, raw_layer_count + 1)],
        "Z_mm_layer_center": [
            (i - 0.5) * cfg.layer_height_mm
            for i in range(1, raw_layer_count + 1)
        ],
        "WhitePixelCount": [white_counts.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "SectionSegmentCount": [layer_segment_counts.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "JitteredRowCount": [layer_jittered_rows.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "UnclosedWindingRowCount": [layer_unclosed_rows.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "MaxAbsWinding": [layer_max_winding.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "JunctionRepairAddedPixels": [layer_repair_pixels.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "JunctionRepairFilledHoles": [layer_repair_holes.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "RejectedLargeOrLongHoles": [layer_rejected_large_holes.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "SubpixelStabilizedRows": [layer_subpixel_rows.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "SubpixelChangedPixels": [layer_subpixel_changed_pixels.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "SingleRowRemovedRuns": [layer_single_row_removed_runs.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "SingleRowRemovedPixels": [layer_single_row_removed_pixels.get(i, 0) for i in range(1, raw_layer_count + 1)],
        "Failed": [i in failed_layers for i in range(1, raw_layer_count + 1)],
    }).to_csv(
        output_folder / "slice_pixel_counts.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return info



# ===== DLP RUNNER BASE =====
# ============================================================
# CELL 8 — DLP SLICING RUNNER
# STL -> raw SEC images -> center-aligned fixed-layer .slice folder
# ============================================================
def build_dlp_slice_from_stl(stl_path, raw_root, final_root):
    stl_path = Path(stl_path)
    raw_root = Path(raw_root)
    final_root = Path(final_root)
    raw_root.mkdir(parents=True, exist_ok=True)
    final_root.mkdir(parents=True, exist_ok=True)

    raw_folder = raw_root / f"{stl_path.stem}.slice"
    final_folder = final_root / f"{stl_path.stem}.slice"

    raw_info = render_one_stl_to_raw_slice_folder(
        stl_path=stl_path,
        output_folder=raw_folder,
        cfg=CFG,
        overwrite=DLP_OVERWRITE,
    )
    final_info = extract_center_aligned_com_layers(
        raw_slice_folder=raw_folder,
        output_folder=final_folder,
        cfg=CFG,
        overwrite=DLP_OVERWRITE,
    )

    idx_path = None
    printer_ready_assets = False
    if COPY_DLP_TEMPLATE_ASSETS_IF_AVAILABLE and DLP_TEMPLATE_SLICE_DIR.exists():
        idx_path = copy_template_assets(DLP_TEMPLATE_SLICE_DIR, final_folder)
        if idx_path is not None:
            update_idx_from_images(final_folder, idx_path)
        printer_ready_assets = True

    return {
        "candidate_id": stl_path.stem,
        "stl_path": str(stl_path),
        "raw_slice_folder": str(raw_folder),
        "dlp_slice_folder": str(final_folder),
        "raw_layer_count": raw_info.get("raw_layer_count"),
        "fixed_layer_count": final_info.get("target_layer_count"),
        "failed_layer_count": raw_info.get("failed_layer_count", 0),
        "template_assets_copied": printer_ready_assets,
        "idx_path": str(idx_path) if idx_path else "",
        "status": "OK" if int(raw_info.get("failed_layer_count", 0)) == 0 else "CHECK_FAILED_LAYERS",
    }

def run_dlp_batch(stl_dir, raw_root, final_root, enabled=True):
    if not enabled:
        print("DLP batch skipped by config.")
        return pd.DataFrame()
    stl_files = sorted(Path(stl_dir).glob("*.stl"))
    rows = []
    for i, stl_path in enumerate(stl_files, 1):
        try:
            row = build_dlp_slice_from_stl(stl_path, raw_root, final_root)
        except Exception as exc:
            row = {
                "candidate_id": stl_path.stem,
                "stl_path": str(stl_path),
                "status": "FAILED",
                "error": f"{type(exc).__name__}: {exc}",
            }
        rows.append(row)
        print(f"[DLP {i}/{len(stl_files)}] {stl_path.stem}: {row['status']}")
    out = pd.DataFrame(rows)
    if len(out):
        out.to_csv(TABLE_DIR / f"DLP_log_{Path(final_root).name}.csv", index=False, encoding="utf-8-sig")
    return out


# ===== DESCRIPTOR BASE =====
# ============================================================
# CELL 9 — STRUCTURAL DESCRIPTOR EXTRACTION
# Architected_Material_Descriptor_v6 pipeline
# ============================================================
def _descriptor_profile_overrides(profile):
    profile = str(profile).lower()
    if profile == "screening":
        return {
            "COMPUTE_CT_RECONSTRUCTION": False,
            "OPTIONAL_PERSISTENT_HOMOLOGY": False,
        }
    if profile == "full":
        return {
            "COMPUTE_CT_RECONSTRUCTION": True,
            "OPTIONAL_PERSISTENT_HOMOLOGY": True,
        }
    raise ValueError("profile must be 'screening' or 'full'")

def run_descriptor_batch(
    stl_dir,
    output_root,
    enabled=True,
    profile="full",
    save_raw_slice_files=True,
    save_debug_images=False,
):
    if not enabled:
        print("Descriptor batch skipped by config.")
        return pd.DataFrame()

    stl_files = sorted(Path(stl_dir).glob("*.stl"))
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    rows = []

    old_cwd = Path.cwd()
    try:
        # stl_pipeline_driver가 pointer file을 CWD에 기록하므로 engine 폴더에서 실행
        os.chdir(ENGINE_DIR)

        for i, stl_path in enumerate(stl_files, 1):
            workdir = output_root / stl_path.stem
            overrides = {
                "CROP_CUBE_SIZE_MM": float(DESCRIPTOR_CROP_CUBE_SIZE_MM),
                "VOXEL_SIZE_MM": float(DESCRIPTOR_REFERENCE_VOXEL_SIZE_MM),
                "IMAGE_PIXELS_PER_SIDE": int(DESCRIPTOR_IMAGE_PIXELS_PER_SIDE),
                "LAYER_SLICE_PERCENT": int(DESCRIPTOR_LAYER_SLICE_PERCENT),
                "SAVE_SLICE_IMAGES": bool(save_debug_images),
                "TRIPLET_IMAGE_STRIDE": 1,
                "RAW_SLICE_IMAGE_STRIDE": 1,
                "MAX_RAW_SLICE_IMAGES": None,
                "CPU_WORKERS": int(DESCRIPTOR_CPU_WORKERS),
                "ENABLE_PARALLEL_DESCRIPTOR_STAGES": bool(DESCRIPTOR_ENABLE_PARALLEL),
                "ENABLE_GPU_ACCELERATION": bool(DESCRIPTOR_ENABLE_GPU),
                "GPU_IDS": list(DESCRIPTOR_GPU_IDS),
                **_descriptor_profile_overrides(profile),
            }

            ok, elapsed, err = drv.run_pipeline_for_one_input(
                stl_path.resolve(),
                workdir.resolve(),
                config_overrides=overrides,
            )
            status = "OK" if ok else "FAILED"
            row = {
                "candidate_id": stl_path.stem,
                "file": stl_path.name,
                "status": status,
                "elapsed_sec": round(float(elapsed), 3),
                "error": (err or "").splitlines()[-1] if err else "",
                "workdir": str(workdir),
                "profile": profile,
                "save_raw_slice_files": bool(save_raw_slice_files),
                "save_debug_images": bool(save_debug_images),
            }
            if ok:
                # Descriptor 계산 자체는 debug PNG 저장과 독립적입니다.
                # 사용자가 요청한 "구조인자 추출용 슬라이스 파일"은 processed descriptor volume에서 별도 저장합니다.
                if save_raw_slice_files:
                    drv.save_raw_slice_images(workdir.resolve(), stride=1, max_slices=None)
                descriptor_csv = workdir / "features" / "descriptors_ALL.csv"
                raw_slice_dir = workdir / "images" / "raw_slices"
                row["descriptor_csv"] = str(descriptor_csv)
                row["descriptor_slice_dir"] = str(raw_slice_dir)
                row["raw_slice_image_count"] = len(list(raw_slice_dir.glob("*.png"))) if raw_slice_dir.exists() else 0
            rows.append(row)
            print(f"[DESC {i}/{len(stl_files)}] {stl_path.stem}: {status} ({elapsed:.1f}s)")

    finally:
        os.chdir(old_cwd)

    out = pd.DataFrame(rows)
    if len(out):
        out.to_csv(
            TABLE_DIR / f"descriptor_run_log_{Path(output_root).name}.csv",
            index=False, encoding="utf-8-sig"
        )
    return out


# ===== MERGE BASE =====
# ============================================================
# CELL 10 — MERGE DESCRIPTORS + APPEND GENERATION PARAMETERS
# Existing descriptor columns stay untouched and first.
# New generator parameters are appended only at the far-right columns.
# ============================================================
from openpyxl import load_workbook

def generation_parameter_append_table(candidate_table, voxel_size_mm, stage):
    rows = []
    for _, row in candidate_table.iterrows():
        p = realize_voxel_params(row, voxel_size_mm, stage)
        # 기존 descriptor 열과 절대 충돌하지 않도록 gen__ prefix 사용.
        # 물리단위 원본 + realized voxel-count를 모두 남김.
        out = {
            "sample_id": str(row["candidate_id"]),
            "gen__generator_type": str(row["generator_type"]),
            "gen__voxel_mode": str(row["voxel_mode"]),
            "gen__seed": int(row["seed"]),
            "gen__size_mm": float(row["size_mm"]),
            "gen__target_vf": float(row["target_vf"]),
            "gen__min_thickness_mm": float(row["min_thickness_mm"]),
            "gen__min_hole_size_mm": float(row["min_hole_size_mm"]),
            "gen__max_thickness_mm": float(row["max_thickness_mm"]),
            "gen__closing_radius_mm": float(row["closing_radius_mm"]),
            "gen__opening_radius_mm": float(row["opening_radius_mm"]),
            "gen__connectivity_bridge_radius_mm": float(row["connectivity_bridge_radius_mm"]),
            "gen__contact_surface_depth_mm": float(row["contact_surface_depth_mm"]),
            "gen__num_fourier_terms": int(row["num_fourier_terms"]),
            "gen__fourier_k_min": 1,
            "gen__fourier_k_max": int(row["fourier_k_max"]),
            "gen__anisotropy_z": float(row["anisotropy_z"]),
            "gen__sigma_mm": float(row["sigma_mm"]),
            "gen__strict_global_symmetry": bool(row["strict_global_symmetry"]),
            "gen__force_connected": bool(row["force_connected"]),
            "gen__generator_param_sampling": str(row["generator_param_sampling"]),
            "gen__stage": str(stage),
            "gen__realized_voxel_size_mm": float(voxel_size_mm),
            "gen__realized_grid_n": int(p["grid_n"]),
            "gen__realized_min_thickness_vox": int(p["min_thickness_vox"]),
            "gen__realized_min_hole_size_vox": int(p["min_hole_size_vox"]),
            "gen__realized_max_thickness_vox": int(p["max_thickness_vox"]),
            "gen__realized_closing_iter": int(p["closing_iter"]),
            "gen__realized_opening_iter": int(p["opening_iter"]),
            "gen__realized_connectivity_bridge_radius_vox": int(p["connectivity_bridge_radius_vox"]),
            "gen__realized_contact_surface_depth_vox": int(p["contact_surface_depth_vox"]),
            "gen__realized_sigma_vox": float(p["sigma"]),
        }
        rows.append(out)
    return pd.DataFrame(rows)

def _first_seen_union(columns_iterable):
    result = []
    seen = set()
    for cols in columns_iterable:
        for c in cols:
            if c not in seen:
                result.append(c)
                seen.add(c)
    return result

def _format_excel(path):
    wb = load_workbook(path)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        # 데이터 손실 없이 최소한의 가독성만 개선
        for col_cells in ws.iter_cols(min_row=1, max_row=min(ws.max_row, 50)):
            max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max(max_len + 2, 10), 40)
    wb.save(path)

def collect_descriptor_master(
    candidate_table,
    descriptor_root,
    out_xlsx,
    voxel_size_mm,
    stage,
    run_log=None,
):
    descriptor_root = Path(descriptor_root)
    frames = []
    catalogs = []

    for workdir in sorted([p for p in descriptor_root.iterdir() if p.is_dir()]) if descriptor_root.exists() else []:
        p = workdir / "features" / "descriptors_ALL.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p)
        frames.append(df)

        cp = workdir / "features" / "descriptor_catalog.csv"
        if cp.exists():
            catalogs.append(pd.read_csv(cp))

    if not frames:
        raise RuntimeError(f"No descriptors_ALL.csv found under {descriptor_root}")

    # descriptor engine이 실제로 만든 열을 first-seen 순서 그대로 유지.
    descriptor_cols = _first_seen_union([list(df.columns) for df in frames])
    descriptor_master = pd.concat(
        [df.reindex(columns=descriptor_cols) for df in frames],
        ignore_index=True,
        sort=False,
    )

    if "sample_id" not in descriptor_master.columns:
        raise RuntimeError("descriptor output does not contain sample_id")

    gen_append = generation_parameter_append_table(candidate_table, voxel_size_mm, stage)
    merged = descriptor_master.merge(gen_append, on="sample_id", how="left", sort=False)

    # merge 후 sample_id 위치는 그대로 첫 descriptor column에 유지하고,
    # gen__ columns는 descriptor columns 뒤에만 위치시킨다.
    final_cols = descriptor_cols + [c for c in gen_append.columns if c != "sample_id"]
    merged = merged.reindex(columns=final_cols)

    # Catalog: original descriptor catalog first; generator additions after.
    if catalogs:
        catalog = pd.concat(catalogs, ignore_index=True, sort=False)
        if "descriptor" in catalog.columns:
            catalog = catalog.drop_duplicates(subset=["descriptor"], keep="first")
    else:
        catalog = pd.DataFrame({"descriptor": [c for c in descriptor_cols if c != "sample_id"]})

    gen_catalog = pd.DataFrame({
        "descriptor": [c for c in gen_append.columns if c != "sample_id"],
        "family": "generator_parameter_appended",
    })
    catalog_out = pd.concat([catalog, gen_catalog], ignore_index=True, sort=False)

    out_xlsx = Path(out_xlsx)
    out_xlsx.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        merged.to_excel(writer, sheet_name="Descriptors", index=False)
        # 같은 열 순서의 빈 template sheet
        pd.DataFrame(columns=final_cols).to_excel(writer, sheet_name="Template", index=False)
        catalog_out.to_excel(writer, sheet_name="Descriptor_Catalog", index=False)
        if run_log is not None and len(run_log):
            run_log.to_excel(writer, sheet_name="Run_Log", index=False)

    _format_excel(out_xlsx)

    csv_path = out_xlsx.with_suffix(".csv")
    merged.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print("Saved:", out_xlsx)
    print("Descriptor columns:", len(descriptor_cols), "| appended generator columns:", len(final_cols) - len(descriptor_cols))
    return merged, descriptor_cols, catalog_out


# ===== SELECTION BASE =====
# ============================================================
# CELL 11 — DESCRIPTOR-SPACE LHS SAMPLE SELECTION
# ============================================================
_LAST_DESCRIPTOR_SELECTION_CACHE = {}

def _prepare_descriptor_matrix(df, descriptor_columns):
    """Prepare the descriptor-space matrix for LHS selection with 30k-pool memory safety.

    Key changes for large pools:
    - filters descriptor columns before allocating the matrix;
    - stores the working matrix as float32 rather than float64;
    - performs median/5–95% scaling column-by-column to avoid large temporary arrays;
    - uses randomized PCA when scikit-learn is available (much faster than full SVD for
      30,000 x thousands-of-descriptors matrices), with NumPy SVD as a fallback.
    """
    global _LAST_DESCRIPTOR_SELECTION_CACHE
    numeric_cols=[]
    for c in descriptor_columns:
        if c == 'sample_id' or c not in df.columns:
            continue
        s=pd.to_numeric(df[c],errors='coerce')
        missing=float(s.isna().mean())
        std=float(s.std(skipna=True)) if s.notna().sum()>1 else 0.0
        if missing <= float(DESCRIPTOR_MAX_MISSING_FRACTION) and np.isfinite(std) and std > float(DESCRIPTOR_MIN_STD):
            numeric_cols.append(c)
    if not numeric_cols:
        raise RuntimeError('No usable numeric descriptor columns for LHS selection.')

    nrow=len(df); ncol=len(numeric_cols)
    est_gb=nrow*ncol*4/(1024**3)
    print(f'[Descriptor-LHS] usable descriptors={ncol:,}, structures={nrow:,}, float32 matrix≈{est_gb:.2f} GB')
    X=np.empty((nrow,ncol),dtype=np.float32)
    med=np.empty(ncol,dtype=np.float32); lo=np.empty(ncol,dtype=np.float32); hi=np.empty(ncol,dtype=np.float32)
    for j,c in enumerate(numeric_cols):
        a=pd.to_numeric(df[c],errors='coerce').to_numpy(dtype=np.float32,copy=True)
        finite=np.isfinite(a)
        vals=a[finite]
        m=np.float32(np.median(vals)) if vals.size else np.float32(0.0)
        q05=np.float32(np.percentile(vals,5)) if vals.size else np.float32(0.0)
        q95=np.float32(np.percentile(vals,95)) if vals.size else np.float32(1.0)
        if not np.isfinite(q95-q05) or float(q95-q05)<=1e-12: q95=q05+np.float32(1.0)
        a[~finite]=m
        a=np.clip((a-q05)/(q95-q05),0.0,1.0).astype(np.float32,copy=False)
        X[:,j]=a; med[j]=m; lo[j]=q05; hi[j]=q95

    ncomp=max(1,min(int(DESCRIPTOR_LHS_PCA_COMPONENTS),nrow-1 if nrow>1 else 1,ncol))
    scaled_mean=X.mean(axis=0,dtype=np.float64).astype(np.float32)
    solver=str(SETTINGS.get('DESCRIPTOR_LHS_PCA_SOLVER','randomized')).lower()
    pca_basis=None
    try:
        if solver in {'randomized','auto'}:
            from sklearn.decomposition import PCA
            pca=PCA(n_components=ncomp,svd_solver='randomized',random_state=int(RANDOM_SEED)+811)
            scores=pca.fit_transform(X).astype(np.float32,copy=False)
            pca_basis=pca.components_.astype(np.float32,copy=False)
        else:
            raise RuntimeError('force numpy fallback')
    except Exception as exc:
        print(f'[Descriptor-LHS] randomized PCA unavailable -> NumPy SVD fallback: {type(exc).__name__}')
        Xc=X-scaled_mean[None,:]
        U,S,Vt=np.linalg.svd(Xc,full_matrices=False)
        pca_basis=Vt[:ncomp].astype(np.float32,copy=False)
        scores=(Xc@pca_basis.T).astype(np.float32,copy=False)
        del Xc,U,S,Vt

    smin=scores.min(axis=0); smax=scores.max(axis=0); sspan=np.where((smax-smin)>1e-12,smax-smin,1.0)
    scores01=((scores-smin)/sspan).astype(np.float32,copy=False)
    _LAST_DESCRIPTOR_SELECTION_CACHE={
        'n_rows':int(nrow),'used_cols':list(numeric_cols),'median':med,'p05':lo,'p95':hi,
        'robust_scaled_mean':scaled_mean,'pca_basis':pca_basis,'training_scores01':scores01,
    }
    del X,scores
    gc.collect()
    return scores01, numeric_cols, pca_basis, (lo,hi)

def _greedy_nearest_unique(points, targets):
    points = np.asarray(points, float)
    targets = np.asarray(targets, float)
    selected = []
    available = set(range(len(points)))

    # 가장 "corner-like" target부터 처리하면 duplicate nearest 충돌이 줄어듦
    center = np.full(points.shape[1], 0.5)
    target_order = np.argsort(-np.linalg.norm(targets - center, axis=1))

    for ti in target_order:
        if not available:
            break
        idxs = np.fromiter(sorted(available), dtype=int)
        d = np.linalg.norm(points[idxs] - targets[ti], axis=1)
        chosen = int(idxs[int(np.argmin(d))])
        selected.append(chosen)
        available.remove(chosen)

    return selected

def _maximin_select(points, n_select, seed=42):
    points = np.asarray(points, float)
    rng = np.random.default_rng(int(seed))
    if n_select >= len(points):
        return list(range(len(points)))
    first = int(rng.integers(0, len(points)))
    selected = [first]
    min_dist = np.linalg.norm(points - points[first], axis=1)
    for _ in range(1, int(n_select)):
        min_dist[selected] = -np.inf
        nxt = int(np.argmax(min_dist))
        selected.append(nxt)
        min_dist = np.minimum(min_dist, np.linalg.norm(points - points[nxt], axis=1))
    return selected

def select_samples_from_descriptor_space(master_df, descriptor_columns, n_select=N_FINAL_SAMPLES):
    n_select = min(int(n_select), len(master_df))
    scores01, used_cols, pca_basis, scaling = _prepare_descriptor_matrix(master_df, descriptor_columns)

    if USE_DESCRIPTOR_LHS_SELECTION:
        lhs = qmc.LatinHypercube(d=scores01.shape[1], seed=int(RANDOM_SEED) + 9001)
        targets = lhs.random(n_select)
        selected_idx = _greedy_nearest_unique(scores01, targets)
        method = "descriptor_LHS_nearest_unique"
    else:
        selected_idx = _maximin_select(scores01, n_select, seed=RANDOM_SEED)
        targets = None
        method = "descriptor_maximin"

    selected = master_df.iloc[selected_idx].copy()
    selected.insert(1, "selection_method", method)
    selected.insert(2, "selection_rank", np.arange(1, len(selected) + 1))
    selected["selection_PCA_dimensions"] = scores01.shape[1]
    selected["selection_numeric_descriptor_count"] = len(used_cols)

    meta = pd.DataFrame({
        "used_descriptor": used_cols,
    })

    with pd.ExcelWriter(SELECTION_XLSX, engine="openpyxl") as writer:
        selected.to_excel(writer, sheet_name="Selected_Samples", index=False)
        meta.to_excel(writer, sheet_name="Descriptors_Used_For_Selection", index=False)
        if targets is not None:
            pd.DataFrame(
                targets,
                columns=[f"LHS_target_PC{i+1}" for i in range(targets.shape[1])]
            ).to_excel(writer, sheet_name="LHS_Targets", index=False)
    _format_excel(SELECTION_XLSX)

    return selected, scores01, used_cols


# =====================================================================
# V2 OVERRIDES — RTX 4070 GPU, Ryzen 7900X CPU, durable item checkpoints
# =====================================================================
# Point the generation GPU context to the CUDA device selected by name.
if '_GPU_CONTEXT' in globals() and CUDA_DEVICE_ID is not None:
    _GPU_CONTEXT['device_id']=int(CUDA_DEVICE_ID)
    GPU_DEVICE_ID=int(CUDA_DEVICE_ID)

# GPU Gaussian random field for screening-size volumes; CPU fallback for larger grids.
def stochastic_gaussian_field(n, sigma=(3.0,3.0,3.0), seed=0):
    n=int(n)
    use_gpu=bool(SETTINGS.get('ENABLE_NVIDIA_GPU',True) and CUDA_DEVICE_ID is not None and n <= int(SETTINGS.get('GPU_MAX_GRID_N',520)))
    if use_gpu:
        try:
            import cupy as _cp
            import cupyx.scipy.ndimage as _cndi
            # Generate the random field with NumPy first so seed semantics stay stable
            # whether CUDA is available or not; GPU is used for the expensive Gaussian filter.
            _rng=np.random.default_rng(int(seed))
            try: _host=_rng.standard_normal(size=(n,n,n),dtype=np.float32)
            except TypeError: _host=_rng.standard_normal(size=(n,n,n)).astype(np.float32)
            with _cp.cuda.Device(int(CUDA_DEVICE_ID)):
                noise=_cp.asarray(_host); del _host
                _cndi.gaussian_filter(noise, sigma=tuple(float(v) for v in sigma), mode='reflect', output=noise)
                noise-= _cp.mean(noise)
                noise/= (_cp.std(noise)+1e-12)
                out=_cp.asnumpy(noise)
                del noise
                _cp.get_default_memory_pool().free_all_blocks()
            return out.astype(np.float32,copy=False)
        except Exception as e:
            print(f'[GPU fallback] stochastic field -> CPU: {type(e).__name__}: {e}')
    rng=np.random.default_rng(int(seed))
    try: noise=rng.standard_normal(size=(n,n,n),dtype=np.float32)
    except TypeError: noise=rng.standard_normal(size=(n,n,n)).astype(np.float32)
    gaussian_filter(noise,sigma=tuple(float(v) for v in sigma),mode='reflect',output=noise)
    noise-=np.mean(noise,dtype=np.float64); noise/=(np.std(noise,dtype=np.float64)+1e-12)
    return noise.astype(np.float32,copy=False)

# Save/restore quick generation metadata per structure. Existing validated STL is never regenerated unless force=True.
def run_voxel_generation(df, voxel_size_mm, stl_dir, stage, selected_ids=None, force=False):
    global MARCHING_CUBES_STEP_SIZE, VOXEL_GRID_N, CONTACT_SURFACE_DEPTH_VOX, CONNECTIVITY_BRIDGE_RADIUS_VOX
    stl_dir=Path(stl_dir); stl_dir.mkdir(parents=True,exist_ok=True)
    meta_dir=stl_dir.parent/'Generation_metadata'; meta_dir.mkdir(parents=True,exist_ok=True)
    sub=df.copy()
    if selected_ids is not None:
        ids=set(map(str,selected_ids)); sub=sub[sub['candidate_id'].astype(str).isin(ids)].copy()
    grid_n=int(round(float(BOUNDARY_SIZE_MM)/float(voxel_size_mm)))
    print('Generation memory diagnostic:',_memory_diagnostic(grid_n))
    if grid_n>=800 and not ALLOW_HIGH_MEMORY_FINAL_GRID: raise MemoryError(f'grid_n={grid_n} blocked by config')
    VOXEL_GRID_N=grid_n
    MARCHING_CUBES_STEP_SIZE=int(MARCHING_CUBES_STEP_FINAL if stage=='final' else MARCHING_CUBES_STEP_SCREENING)
    log_path=TABLE_DIR/f'generation_log_{stage}.csv'
    existing=pd.read_csv(log_path) if (log_path.exists() and not force) else pd.DataFrame()
    existing_map={str(r['candidate_id']):r.to_dict() for _,r in existing.iterrows()} if len(existing) else {}
    rows=[]; total=len(sub)
    for j,(_,row) in enumerate(sub.iterrows(),1):
        cid=str(row['candidate_id']); stl_path=stl_dir/f'{cid}.stl'; param_json=meta_dir/f'{cid}_generation_parameters.json'; quick_json=meta_dir/f'{cid}_quick_descriptors.json'
        prior=existing_map.get(cid)
        if not force and RESUME_SKIP_COMPLETED and stl_path.exists() and param_json.exists() and prior and str(prior.get('status','')).upper() in {'OK','SKIPPED_EXISTING','RESUMED_EXISTING'}:
            out=dict(prior); out['status']='RESUMED_EXISTING'; rows.append(out); print(f'[{j:03d}/{total:03d}] {cid}: RESUMED_EXISTING'); atomic_csv(pd.DataFrame(rows),log_path); continue
        t0=time.time()
        try:
            p=realize_voxel_params(row,voxel_size_mm,stage); CONTACT_SURFACE_DEPTH_VOX=int(p['contact_surface_depth_vox']); CONNECTIVITY_BRIDGE_RADIUS_VOX=int(p['connectivity_bridge_radius_vox'])
            verts,faces,quick=generate_voxel_candidate(p); save_stl(verts,faces,stl_path); del verts,faces; gc.collect()
            clean={k:v for k,v in p.items() if not str(k).startswith('_')}; atomic_json(param_json,clean); atomic_json(quick_json,quick)
            out={'candidate_id':cid,'stage':stage,'status':'OK','stl_path':str(stl_path),'elapsed_sec':round(time.time()-t0,3),**make_realized_parameter_row(row,voxel_size_mm,stage),**{f'quick__{k}':v for k,v in quick.items()}}
        except Exception as exc:
            out={'candidate_id':cid,'stage':stage,'status':'FAILED','stl_path':str(stl_path),'elapsed_sec':round(time.time()-t0,3),'error':f'{type(exc).__name__}: {exc}','traceback':traceback.format_exc()}
        rows.append(out); atomic_csv(pd.DataFrame(rows),log_path); print(f'[{j:03d}/{total:03d}] {cid}: {out["status"]} ({out["elapsed_sec"]} s)')
        try:
            if CUDA_DEVICE_ID is not None:
                import cupy as _cp; _cp.get_default_memory_pool().free_all_blocks()
        except Exception: pass
    out=pd.DataFrame(rows); save_df_checkpoint(out,f'generation_log_{stage}'); return out


def _dlp_existing_valid(stl_path, final_root):
    folder=Path(final_root)/f'{Path(stl_path).stem}.slice'; info=folder/'com_extraction_info.json'
    if not info.exists(): return False
    try:
        d=json.loads(info.read_text(encoding='utf-8'))
        sec=list(folder.glob('SEC_*.png'))
        return int(d.get('target_layer_count',-1))==int(DLP_FIXED_LAYER_COUNT) and len(sec)==int(DLP_FIXED_LAYER_COUNT)
    except Exception: return False

def _dlp_worker_tuple(args):
    stl_path,raw_root,final_root=args
    try: return build_dlp_slice_from_stl(Path(stl_path),Path(raw_root),Path(final_root))
    except Exception as exc: return {'candidate_id':Path(stl_path).stem,'stl_path':str(stl_path),'status':'FAILED','error':f'{type(exc).__name__}: {exc}','traceback':traceback.format_exc()}

def run_dlp_batch(stl_dir, raw_root, final_root, enabled=True, force=False, log_tag=None):
    if not enabled: print('DLP batch skipped by config.'); return pd.DataFrame()
    stl_files=sorted(Path(stl_dir).glob('*.stl')); final_root=Path(final_root); log_tag=str(log_tag or (final_root.parent.name+'_'+final_root.name)).replace(' ','_'); log_path=TABLE_DIR/f'DLP_log_{log_tag}.csv'
    pending=[]; rows=[]
    for p in stl_files:
        if not force and RESUME_SKIP_COMPLETED and _dlp_existing_valid(p,final_root):
            rows.append({'candidate_id':p.stem,'stl_path':str(p),'status':'RESUMED_EXISTING','dlp_slice_folder':str(final_root/f'{p.stem}.slice')})
        else: pending.append(p)
    workers=max(1,min(int(DLP_PARALLEL_WORKERS),int(CPU_PHYSICAL_CORES),len(pending) if pending else 1))
    backend=str(DLP_PARALLEL_BACKEND).lower()
    print(f'DLP: total={len(stl_files)}, resumed={len(rows)}, pending={len(pending)}, workers={workers}, backend={backend}')
    if pending and workers>1:
        try:
            if backend in {'loky','process','processes'}:
                from joblib import Parallel, delayed
                results=Parallel(n_jobs=workers,backend='loky',prefer='processes')(delayed(_dlp_worker_tuple)((str(p),str(raw_root),str(final_root))) for p in pending)
                for row in results:
                    rows.append(row); atomic_csv(pd.DataFrame(rows),log_path); print(f'[DLP] {row.get("candidate_id")}: {row.get("status")}')
            else:
                with ThreadPoolExecutor(max_workers=workers) as ex:
                    futs={ex.submit(_dlp_worker_tuple,(str(p),str(raw_root),str(final_root))):p for p in pending}
                    for fut in as_completed(futs):
                        row=fut.result(); rows.append(row); atomic_csv(pd.DataFrame(rows),log_path); print(f'[DLP] {row.get("candidate_id")}: {row.get("status")}')
        except Exception as e:
            print(f'[DLP parallel fallback -> sequential] {type(e).__name__}: {e}')
            for p in pending:
                row=_dlp_worker_tuple((str(p),str(raw_root),str(final_root))); rows.append(row); atomic_csv(pd.DataFrame(rows),log_path); print(f'[DLP] {row.get("candidate_id")}: {row.get("status")}')
    else:
        for p in pending:
            row=_dlp_worker_tuple((str(p),str(raw_root),str(final_root))); rows.append(row); atomic_csv(pd.DataFrame(rows),log_path); print(f'[DLP] {row.get("candidate_id")}: {row.get("status")}')
    out=pd.DataFrame(rows).sort_values('candidate_id').reset_index(drop=True) if rows else pd.DataFrame();
    if len(out): atomic_csv(out,log_path); save_df_checkpoint(out,f'DLP_log_{log_tag}')
    return out


def _descriptor_existing_valid(workdir):
    p=Path(workdir)/'features'/'descriptors_ALL.csv'; m=Path(workdir)/'manifest.json'
    return p.exists() and p.stat().st_size>50

def run_descriptor_batch(stl_dir, output_root, enabled=True, profile='full', save_raw_slice_files=True, save_debug_images=False, force=False, log_tag=None):
    if not enabled: print('Descriptor batch skipped by config.'); return pd.DataFrame()
    if drv is None or dl is None: raise ImportError('Descriptor engine not deployed. Run CELL 2 once.')
    stl_files=sorted(Path(stl_dir).glob('*.stl')); output_root=Path(output_root); output_root.mkdir(parents=True,exist_ok=True)
    log_tag=str(log_tag or (output_root.parent.name+'_'+output_root.name)).replace(' ','_'); log_path=TABLE_DIR/f'descriptor_run_log_{log_tag}.csv'; rows=[]
    old_cwd=Path.cwd()
    try:
        os.chdir(ENGINE_DIR)
        for i,stl_path in enumerate(stl_files,1):
            workdir=output_root/stl_path.stem
            if not force and RESUME_SKIP_COMPLETED and _descriptor_existing_valid(workdir):
                raw_slice_dir=workdir/'images'/'raw_slices'; row={'candidate_id':stl_path.stem,'file':stl_path.name,'status':'RESUMED_EXISTING','elapsed_sec':0.0,'error':'','workdir':str(workdir),'profile':profile,'descriptor_csv':str(workdir/'features'/'descriptors_ALL.csv'),'descriptor_slice_dir':str(raw_slice_dir),'raw_slice_image_count':len(list(raw_slice_dir.glob('*.png'))) if raw_slice_dir.exists() else 0}; rows.append(row); atomic_csv(pd.DataFrame(rows),log_path); print(f'[DESC {i}/{len(stl_files)}] {stl_path.stem}: RESUMED_EXISTING'); continue
            overrides={'CROP_CUBE_SIZE_MM':float(DESCRIPTOR_CROP_CUBE_SIZE_MM),'VOXEL_SIZE_MM':float(DESCRIPTOR_REFERENCE_VOXEL_SIZE_MM),'IMAGE_PIXELS_PER_SIDE':int(DESCRIPTOR_IMAGE_PIXELS_PER_SIDE),'LAYER_SLICE_PERCENT':int(DESCRIPTOR_LAYER_SLICE_PERCENT),'SAVE_SLICE_IMAGES':bool(save_debug_images),'TRIPLET_IMAGE_STRIDE':1,'RAW_SLICE_IMAGE_STRIDE':1,'MAX_RAW_SLICE_IMAGES':None,'CPU_WORKERS':int(DESCRIPTOR_CPU_WORKERS),'ENABLE_PARALLEL_DESCRIPTOR_STAGES':bool(DESCRIPTOR_ENABLE_PARALLEL),'ENABLE_GPU_ACCELERATION':bool(DESCRIPTOR_ENABLE_GPU and len(DESCRIPTOR_GPU_IDS)>0),'GPU_IDS':list(DESCRIPTOR_GPU_IDS),**_descriptor_profile_overrides(profile)}
            t0=time.time()
            # Descriptor engine already parallelizes descriptor families. Limit nested BLAS threads to avoid 6x12 oversubscription.
            with threadpool_limits(limits=int(DESCRIPTOR_INNER_BLAS_THREADS)):
                ok,elapsed,err=drv.run_pipeline_for_one_input(stl_path.resolve(),workdir.resolve(),config_overrides=overrides)
            row={'candidate_id':stl_path.stem,'file':stl_path.name,'status':'OK' if ok else 'FAILED','elapsed_sec':round(float(elapsed),3),'error':(err or '').splitlines()[-1] if err else '','workdir':str(workdir),'profile':profile,'cuda_device_ids':json.dumps(DESCRIPTOR_GPU_IDS),'cpu_workers':int(DESCRIPTOR_CPU_WORKERS)}
            if ok:
                if save_raw_slice_files: drv.save_raw_slice_images(workdir.resolve(),stride=1,max_slices=None)
                raw_slice_dir=workdir/'images'/'raw_slices'; row.update({'descriptor_csv':str(workdir/'features'/'descriptors_ALL.csv'),'descriptor_slice_dir':str(raw_slice_dir),'raw_slice_image_count':len(list(raw_slice_dir.glob('*.png'))) if raw_slice_dir.exists() else 0})
            rows.append(row); atomic_csv(pd.DataFrame(rows),log_path); print(f'[DESC {i}/{len(stl_files)}] {stl_path.stem}: {row["status"]} ({time.time()-t0:.1f}s)')
            try:
                if CUDA_DEVICE_ID is not None:
                    import cupy as _cp; _cp.get_default_memory_pool().free_all_blocks()
            except Exception: pass
    finally: os.chdir(old_cwd)
    out=pd.DataFrame(rows); save_df_checkpoint(out,f'descriptor_log_{log_tag}'); return out


def save_selection_model(master_df, descriptor_columns, selected_df):
    """Save descriptor-space selection transform without rebuilding the 30k x descriptor matrix."""
    global _LAST_DESCRIPTOR_SELECTION_CACHE
    cache=_LAST_DESCRIPTOR_SELECTION_CACHE
    valid=bool(cache and int(cache.get('n_rows',-1))==len(master_df))
    if not valid:
        scores01,used_cols,pca_basis,scaling=_prepare_descriptor_matrix(master_df,descriptor_columns)
        cache=_LAST_DESCRIPTOR_SELECTION_CACHE
    used_cols=list(cache['used_cols']); scores01=np.asarray(cache['training_scores01'],dtype=np.float32)
    selected_ids=selected_df['sample_id'].astype(str).tolist()
    model_path=CHECKPOINT_DIR/'descriptor_selection_model.npz'
    np.savez_compressed(
        model_path,
        used_cols=np.asarray(used_cols,dtype=object),
        median=np.asarray(cache['median'],dtype=np.float32),
        p05=np.asarray(cache['p05'],dtype=np.float32),
        p95=np.asarray(cache['p95'],dtype=np.float32),
        robust_scaled_mean=np.asarray(cache['robust_scaled_mean'],dtype=np.float32),
        pca_basis=np.asarray(cache['pca_basis'],dtype=np.float32),
        training_scores01=scores01,
        selected_ids=np.asarray(selected_ids,dtype=object),
    )
    state={'selected_ids':selected_ids,'model_path':str(model_path),'selection_xlsx':str(SELECTION_XLSX),'used_descriptor_count':len(used_cols),'pca_dimensions':int(scores01.shape[1])}
    atomic_json(CHECKPOINT_DIR/'selection_state.json',state)
    selected_df.to_csv(CHECKPOINT_DIR/'selected_samples.csv',index=False,encoding='utf-8-sig')
    return state


def run_final_qa():
    manifests={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in STAGE_DIR.glob('*.json')}
    report={'run_dir':str(RUN_DIR),'config_sha256':CONFIG_HASH,'hardware':hardware_report(),'stages':manifests}
    final_csv=Path(SELECTED_MASTER_XLSX).with_suffix('.csv')
    if final_csv.exists():
        df=pd.read_csv(final_csv); report['final_rows']=int(len(df)); report['final_columns']=int(df.shape[1]); report['generator_columns']=int(sum(str(c).startswith('gen__') for c in df.columns))
    atomic_json(STATE_DIR/'Final_QA.json',report)
    return report

# =====================================================================
# V3 OVERRIDES — Threadripper 3970X + dual RTX 3090 adaptive scheduler
# =====================================================================
# The workstation may be shared with other CUDA workloads.  GPU selection is
# therefore re-evaluated before every candidate / descriptor sample instead of
# being fixed once at kernel start.

def _v3_float(x, default=0.0):
    try: return float(x)
    except Exception: return float(default)

_GPU_STATUS_CACHE={'t':0.0,'rows':None}

def query_nvidia_gpu_status(force_refresh=False):
    """Return live NVIDIA GPU load/VRAM information.

    Primary source is nvidia-smi because it exposes utilization from other
    processes too.  CuPy is used as a fallback for device/free-memory discovery.
    CUDA-visible IDs are expected to match nvidia-smi indices on the standard
    dual-3090 workstation (no CUDA_VISIBLE_DEVICES remapping).

    A short-lived cache (GPU_STATUS_CACHE_SEC, default ~1s) avoids spawning a
    redundant `nvidia-smi` subprocess when several scheduling decisions happen
    back-to-back for the same candidate/descriptor file (choose_adaptive_gpu_ids
    followed by adaptive_gpu_snapshot, etc.) -- generation/descriptor work per
    structure takes seconds to minutes, so this changes nothing about how "live"
    the scheduling is, it just avoids calling nvidia-smi 2-3x for one decision.
    """
    import subprocess, csv, io
    ttl=float(SETTINGS.get('GPU_STATUS_CACHE_SEC',1.0))
    if not force_refresh and ttl>0:
        age=time.time()-_GPU_STATUS_CACHE['t']
        if _GPU_STATUS_CACHE['rows'] is not None and age<ttl:
            return _GPU_STATUS_CACHE['rows']
    rows=[]
    fields=[
        'index','name','memory.total','memory.used','memory.free',
        'utilization.gpu','utilization.memory','temperature.gpu','power.draw'
    ]
    try:
        cmd=['nvidia-smi','--query-gpu='+','.join(fields),'--format=csv,noheader,nounits']
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=5,check=True)
        for line in p.stdout.strip().splitlines():
            vals=[v.strip() for v in next(csv.reader([line]))]
            if len(vals)<len(fields): continue
            d=dict(zip(fields,vals))
            idx=int(d['index']); total=_v3_float(d['memory.total'])/1024.0; used=_v3_float(d['memory.used'])/1024.0; free=_v3_float(d['memory.free'])/1024.0
            rows.append({
                'cuda_id':idx,'name':d['name'],'total_vram_GB':total,'used_vram_GB':used,'free_vram_GB':free,
                'free_fraction':free/max(total,1e-9),'used_fraction':used/max(total,1e-9),
                'gpu_util_pct':_v3_float(d['utilization.gpu'],100.0),'memory_util_pct':_v3_float(d['utilization.memory'],100.0),
                'temperature_C':_v3_float(d['temperature.gpu'],0.0),'power_W':_v3_float(d['power.draw'],0.0),
                'source':'nvidia-smi'
            })
    except Exception as e:
        smi_error=f'{type(e).__name__}: {e}'
    else:
        smi_error=None
    if not rows:
        try:
            import cupy as _cp
            n=int(_cp.cuda.runtime.getDeviceCount())
            for i in range(n):
                with _cp.cuda.Device(i):
                    prop=_cp.cuda.runtime.getDeviceProperties(i); name=prop.get('name',b'') if isinstance(prop,dict) else b''
                    if isinstance(name,(bytes,bytearray)): name=name.decode(errors='replace')
                    free,total=_cp.cuda.runtime.memGetInfo(); free/=1024**3; total/=1024**3
                    rows.append({'cuda_id':i,'name':str(name),'total_vram_GB':total,'used_vram_GB':total-free,'free_vram_GB':free,
                                 'free_fraction':free/max(total,1e-9),'used_fraction':1-free/max(total,1e-9),
                                 'gpu_util_pct':0.0,'memory_util_pct':0.0,'temperature_C':None,'power_W':None,'source':'cupy_fallback'})
        except Exception as e:
            if smi_error is None: smi_error=f'{type(e).__name__}: {e}'
    allowed=set(int(x) for x in SETTINGS.get('GPU_CANDIDATE_IDS',[0,1]))
    name_filter=str(SETTINGS.get('GPU_REQUIRED_NAME_SUBSTRING','RTX 3090')).lower().strip()
    rows=[r for r in rows if r['cuda_id'] in allowed and (not name_filter or name_filter in str(r['name']).lower())]
    for r in rows:
        r['query_error']=smi_error
    _GPU_STATUS_CACHE['t']=time.time(); _GPU_STATUS_CACHE['rows']=rows
    return rows

def _gpu_score_v3(r):
    """Higher is better.  A small GPU0 penalty preserves GPU1 for this workflow when close."""
    free_w=float(SETTINGS.get('GPU_SCORE_FREE_WEIGHT',0.70)); util_w=float(SETTINGS.get('GPU_SCORE_UTIL_WEIGHT',0.30))
    score=free_w*float(r.get('free_fraction',0.0)) + util_w*(1.0-float(r.get('gpu_util_pct',100.0))/100.0)
    preferred=[int(x) for x in SETTINGS.get('GPU_PREFERRED_ORDER',[1,0])]
    if int(r['cuda_id']) in preferred:
        score += 0.02*(len(preferred)-preferred.index(int(r['cuda_id'])))
    if int(r['cuda_id'])==0:
        score -= float(SETTINGS.get('GPU0_SHARED_WORKLOAD_PENALTY',0.08))
    return float(score)

def choose_adaptive_gpu_ids(max_devices=2, purpose='descriptor'):
    """Choose currently useful GPUs, ordered best-first.

    - Both sufficiently idle -> returns both, usually [1, 0].
    - One busy -> returns only the freer GPU.
    - Both busy but one still has hard-min VRAM -> returns the least-busy GPU.
    - Both saturated -> [] (caller falls back to CPU instead of competing aggressively).
    """
    if not bool(SETTINGS.get('ENABLE_NVIDIA_GPU',True)): return []
    rows=query_nvidia_gpu_status()
    if not rows: return []
    min_free=float(SETTINGS.get('GPU_MIN_FREE_VRAM_GB',8.0))
    hard_min=float(SETTINGS.get('GPU_HARD_MIN_FREE_VRAM_GB',4.0))
    busy_util=float(SETTINGS.get('GPU_BUSY_UTILIZATION_PCT',72.0))
    busy_mem=float(SETTINGS.get('GPU_BUSY_MEMORY_USED_FRACTION',0.72))
    eligible=[r for r in rows if r['free_vram_GB']>=min_free and r['gpu_util_pct']<=busy_util and r['used_fraction']<=busy_mem]
    pool=eligible
    if not pool and bool(SETTINGS.get('GPU_ALLOW_LEAST_BUSY_FALLBACK',True)):
        pool=[r for r in rows if r['free_vram_GB']>=hard_min and r['gpu_util_pct']<98.0]
    pool=sorted(pool,key=lambda r:(_gpu_score_v3(r),r['free_vram_GB']),reverse=True)
    return [int(r['cuda_id']) for r in pool[:max(1,int(max_devices))]]

def adaptive_gpu_snapshot():
    rows=query_nvidia_gpu_status(); chosen=choose_adaptive_gpu_ids(max_devices=2,purpose='snapshot')
    return {'gpus':rows,'chosen_gpu_ids':chosen,'policy':{
        'preferred_order':SETTINGS.get('GPU_PREFERRED_ORDER',[1,0]),
        'min_free_vram_GB':SETTINGS.get('GPU_MIN_FREE_VRAM_GB',8.0),
        'hard_min_free_vram_GB':SETTINGS.get('GPU_HARD_MIN_FREE_VRAM_GB',4.0),
        'busy_utilization_pct':SETTINGS.get('GPU_BUSY_UTILIZATION_PCT',72.0),
        'busy_memory_used_fraction':SETTINGS.get('GPU_BUSY_MEMORY_USED_FRACTION',0.72),
        'gpu0_shared_penalty':SETTINGS.get('GPU0_SHARED_WORKLOAD_PENALTY',0.08),
    }}

def choose_adaptive_cpu_workers():
    """Leave some Threadripper capacity for other codes; scale down if CPU is already busy."""
    phys=int(SETTINGS.get('CPU_PHYSICAL_CORES',32)); maxw=int(SETTINGS.get('DESCRIPTOR_CPU_WORKERS_MAX',28)); minw=int(SETTINGS.get('DESCRIPTOR_CPU_WORKERS_MIN',16))
    if not bool(SETTINGS.get('ADAPTIVE_CPU_SCHEDULING',True)): return int(min(maxw,phys))
    try:
        import psutil
        util=float(psutil.cpu_percent(interval=float(SETTINGS.get('CPU_PROBE_INTERVAL_SEC',0.25))))
    except Exception:
        util=0.0
    if util < 30: target=maxw
    elif util < 55: target=max(minw, maxw-4)
    elif util < 75: target=max(minw, maxw-8)
    else: target=minw
    reserve=int(SETTINGS.get('CPU_RESERVE_PHYSICAL_CORES',4))
    return max(1,min(int(target),max(1,phys-reserve if util>=30 else phys)))

# Refresh compatibility globals at import, while every long-running stage re-queries live state.
_ADAPTIVE_GPU_IMPORT_SNAPSHOT=adaptive_gpu_snapshot()
DESCRIPTOR_GPU_IDS=list(_ADAPTIVE_GPU_IMPORT_SNAPSHOT.get('chosen_gpu_ids',[]))
CUDA_DEVICE_ID=DESCRIPTOR_GPU_IDS[0] if DESCRIPTOR_GPU_IDS else None
CUDA_INFO={'selected_cuda_device':CUDA_DEVICE_ID,'selected_name':None,'devices':_ADAPTIVE_GPU_IMPORT_SNAPSHOT.get('gpus',[]),'adaptive':True}
if CUDA_DEVICE_ID is not None:
    for _r in CUDA_INFO['devices']:
        if int(_r['cuda_id'])==int(CUDA_DEVICE_ID):
            CUDA_INFO.update({'selected_name':_r.get('name'),'free_vram_GB':_r.get('free_vram_GB'),'total_vram_GB':_r.get('total_vram_GB')}); break
if '_GPU_CONTEXT' in globals(): _GPU_CONTEXT['device_id']=CUDA_DEVICE_ID

# Override generation backend selection so an explicit per-worker GPU assignment is respected.
def _get_generation_gpu_device():
    d=_GPU_CONTEXT.get('device_id',None)
    return None if d is None else int(d)

def _xp_for_generation(n=None):
    global DEVICE, USE_GPU_FOR_GENERATION
    dev=_get_generation_gpu_device()
    use_gpu=bool(CUPY_AVAILABLE and cp is not None and dev is not None and (n is None or int(n)<=int(SETTINGS.get('GPU_MAX_GRID_N',720))))
    if use_gpu:
        try:
            cp.cuda.Device(int(dev)).use(); DEVICE=f'gpu:{dev}'; USE_GPU_FOR_GENERATION=True; return cp
        except Exception: pass
    DEVICE='cpu'; USE_GPU_FOR_GENERATION=False; return np

def stochastic_gaussian_field(n, sigma=(3.0,3.0,3.0), seed=0):
    n=int(n); dev=_get_generation_gpu_device()
    use_gpu=bool(SETTINGS.get('ENABLE_NVIDIA_GPU',True) and dev is not None and n<=int(SETTINGS.get('GPU_MAX_GRID_N',720)))
    if use_gpu:
        try:
            import cupy as _cp, cupyx.scipy.ndimage as _cndi
            _rng=np.random.default_rng(int(seed))
            try: _host=_rng.standard_normal(size=(n,n,n),dtype=np.float32)
            except TypeError: _host=_rng.standard_normal(size=(n,n,n)).astype(np.float32)
            with _cp.cuda.Device(int(dev)):
                noise=_cp.asarray(_host); del _host
                _cndi.gaussian_filter(noise,sigma=tuple(float(v) for v in sigma),mode='reflect',output=noise)
                noise-=_cp.mean(noise); noise/=(_cp.std(noise)+1e-12); out=_cp.asnumpy(noise); del noise
                _cp.get_default_memory_pool().free_all_blocks()
            return out.astype(np.float32,copy=False)
        except Exception as e:
            print(f'[GPU {dev} fallback] stochastic field -> CPU: {type(e).__name__}: {e}')
    rng=np.random.default_rng(int(seed))
    try: noise=rng.standard_normal(size=(n,n,n),dtype=np.float32)
    except TypeError: noise=rng.standard_normal(size=(n,n,n)).astype(np.float32)
    gaussian_filter(noise,sigma=tuple(float(v) for v in sigma),mode='reflect',output=noise)
    noise-=np.mean(noise,dtype=np.float64); noise/=(np.std(noise,dtype=np.float64)+1e-12)
    return noise.astype(np.float32,copy=False)

def _free_cupy_pool_v3(dev=None):
    try:
        import cupy as _cp
        if dev is not None:
            with _cp.cuda.Device(int(dev)): _cp.get_default_memory_pool().free_all_blocks(); _cp.get_default_pinned_memory_pool().free_all_blocks()
        else:
            _cp.get_default_memory_pool().free_all_blocks(); _cp.get_default_pinned_memory_pool().free_all_blocks()
    except Exception: pass

def _generation_worker_v3(row_dict, voxel_size_mm, stl_dir, stage, gpu_id):
    """One isolated candidate; safe for joblib/loky dual-GPU screening."""
    global MARCHING_CUBES_STEP_SIZE, VOXEL_GRID_N, CONTACT_SURFACE_DEPTH_VOX, CONNECTIVITY_BRIDGE_RADIUS_VOX
    cid=str(row_dict['candidate_id']); stl_dir=Path(stl_dir); meta_dir=stl_dir.parent/'Generation_metadata'; meta_dir.mkdir(parents=True,exist_ok=True)
    stl_path=stl_dir/f'{cid}.stl'; param_json=meta_dir/f'{cid}_generation_parameters.json'; quick_json=meta_dir/f'{cid}_quick_descriptors.json'
    grid_n=int(round(float(BOUNDARY_SIZE_MM)/float(voxel_size_mm))); VOXEL_GRID_N=grid_n
    MARCHING_CUBES_STEP_SIZE=int(MARCHING_CUBES_STEP_FINAL if stage=='final' else MARCHING_CUBES_STEP_SCREENING)
    _GPU_CONTEXT['device_id']=None if gpu_id is None else int(gpu_id)
    t0=time.time()
    try:
        row=pd.Series(row_dict); p=realize_voxel_params(row,voxel_size_mm,stage)
        CONTACT_SURFACE_DEPTH_VOX=int(p['contact_surface_depth_vox']); CONNECTIVITY_BRIDGE_RADIUS_VOX=int(p['connectivity_bridge_radius_vox'])
        verts,faces,quick=generate_voxel_candidate(p); save_stl(verts,faces,stl_path); del verts,faces; gc.collect()
        clean={k:v for k,v in p.items() if not str(k).startswith('_')}; atomic_json(param_json,clean); atomic_json(quick_json,quick)
        out={'candidate_id':cid,'stage':stage,'status':'OK','stl_path':str(stl_path),'elapsed_sec':round(time.time()-t0,3),'assigned_cuda_device':gpu_id,
             **make_realized_parameter_row(row,voxel_size_mm,stage),**{f'quick__{k}':v for k,v in quick.items()}}
    except Exception as exc:
        out={'candidate_id':cid,'stage':stage,'status':'FAILED','stl_path':str(stl_path),'elapsed_sec':round(time.time()-t0,3),'assigned_cuda_device':gpu_id,
             'error':f'{type(exc).__name__}: {exc}','traceback':traceback.format_exc()}
    _free_cupy_pool_v3(gpu_id); return out

def run_voxel_generation(df, voxel_size_mm, stl_dir, stage, selected_ids=None, force=False):
    """Durable generation with adaptive 1-or-2 GPU waves for screening; final 1000^3 remains serial.

    When both GPUs are busy/unavailable (e.g. GPU0 is saturated by another job and GPU1 is
    also over threshold), screening candidates no longer fall back to one-at-a-time CPU
    generation: several are generated concurrently across CPU worker processes instead, so a
    "no free GPU right now" moment still uses the Threadripper's many cores instead of idling
    them behind a serial loop.
    """
    stl_dir=Path(stl_dir); stl_dir.mkdir(parents=True,exist_ok=True); meta_dir=stl_dir.parent/'Generation_metadata'; meta_dir.mkdir(parents=True,exist_ok=True)
    sub=df.copy()
    if selected_ids is not None:
        ids=set(map(str,selected_ids)); sub=sub[sub['candidate_id'].astype(str).isin(ids)].copy()
    grid_n=int(round(float(BOUNDARY_SIZE_MM)/float(voxel_size_mm))); print('Generation memory diagnostic:',_memory_diagnostic(grid_n))
    if grid_n>=800 and not ALLOW_HIGH_MEMORY_FINAL_GRID: raise MemoryError(f'grid_n={grid_n} blocked by config')
    log_path=TABLE_DIR/f'generation_log_{stage}.csv'; existing=pd.read_csv(log_path) if (log_path.exists() and not force) else pd.DataFrame(); existing_map={str(r['candidate_id']):r.to_dict() for _,r in existing.iterrows()} if len(existing) else {}
    rows=[]; pending=[]
    for _,row in sub.iterrows():
        cid=str(row['candidate_id']); prior=existing_map.get(cid); stl_path=stl_dir/f'{cid}.stl'; param_json=meta_dir/f'{cid}_generation_parameters.json'
        if not force and RESUME_SKIP_COMPLETED and stl_path.exists() and param_json.exists():
            if prior:
                out=dict(prior)
            else:
                # A crash may happen after STL/metadata were safely written but before the batch CSV flush.
                # Reconstruct a minimal durable row from disk so the expensive candidate is never regenerated.
                try:
                    pp=json.loads(param_json.read_text(encoding='utf-8'))
                except Exception:
                    pp={}
                out={'candidate_id':cid,'stage':stage,'status':'RESUMED_EXISTING','stl_path':str(stl_path),'elapsed_sec':0.0,
                     'assigned_cuda_device':None,**{f'restored__{k}':v for k,v in pp.items() if isinstance(v,(str,int,float,bool))}}
            out['status']='RESUMED_EXISTING'; rows.append(out)
        else: pending.append(row.to_dict())
    atomic_csv(pd.DataFrame(rows),log_path) if rows else None
    is_screening=(stage!='final' and grid_n<=int(SETTINGS.get('GPU_MAX_GRID_N',720)))
    max_parallel=int(SETTINGS.get('GENERATION_PARALLEL_SCREENING_WORKERS',2) if is_screening else SETTINGS.get('GENERATION_PARALLEL_FINAL_WORKERS',1))
    # Each CPU-only worker generates one candidate on a moderate-size grid; several fit in
    # memory/CPU at once. Kept well below the full core count so descriptor extraction and
    # any other concurrently-running job still get a fair share of the Threadripper.
    cpu_fallback_workers=max(1,int(SETTINGS.get('GENERATION_CPU_FALLBACK_WORKERS',max(2,min(8,int(SETTINGS.get('CPU_PHYSICAL_CORES',32))//4)))))
    done=len(rows); total=len(sub)
    while pending:
        gpu_ids=choose_adaptive_gpu_ids(max_devices=min(2,max_parallel),purpose='generation') if is_screening else []
        if gpu_ids:
            wave_n=min(len(pending),len(gpu_ids),max_parallel); assignments=[(pending.pop(0),gpu_ids[i]) for i in range(wave_n)]
        elif is_screening:
            # Neither GPU is currently usable: batch several screening candidates onto CPU
            # worker processes instead of generating them one at a time.
            wave_n=min(len(pending),cpu_fallback_workers); assignments=[(pending.pop(0),None) for _ in range(wave_n)]
        else:
            assignments=[(pending.pop(0),None)]
        if len(assignments)>1:
            try:
                from joblib import Parallel, delayed
                outs=Parallel(n_jobs=len(assignments),backend='loky',prefer='processes')(
                    delayed(_generation_worker_v3)(r,float(voxel_size_mm),str(stl_dir),str(stage),g) for r,g in assignments)
            except Exception as e:
                print(f'[generation parallel fallback] {type(e).__name__}: {e}')
                outs=[_generation_worker_v3(r,float(voxel_size_mm),str(stl_dir),str(stage),g) for r,g in assignments]
        else:
            r,g=assignments[0]; outs=[_generation_worker_v3(r,float(voxel_size_mm),str(stl_dir),str(stage),g)]
        flush_every=max(1,int(SETTINGS.get('LARGE_POOL_LOG_FLUSH_EVERY_N',25)))
        for out in outs:
            rows.append(out); done+=1
            # STL + generation JSON are already item-level checkpoints. The aggregate table is flushed
            # periodically for 30k-scale speed; resume reconstructs rows from item checkpoints if needed.
            if done % flush_every == 0 or done == total:
                atomic_csv(pd.DataFrame(rows),log_path)
            print(f'[GEN {done:05d}/{total:05d}] {out.get("candidate_id")}: {out.get("status")} | GPU={out.get("assigned_cuda_device")} | {out.get("elapsed_sec")} s')
    out=pd.DataFrame(rows).sort_values('candidate_id').reset_index(drop=True) if rows else pd.DataFrame();
    if len(out): atomic_csv(out,log_path); save_df_checkpoint(out,f'generation_log_{stage}')
    return out

def run_descriptor_batch(stl_dir, output_root, enabled=True, profile='full', save_raw_slice_files=True, save_debug_images=False, force=False, log_tag=None):
    """Descriptor v6 with live per-sample dual-GPU selection and adaptive Threadripper workers."""
    if not enabled: print('Descriptor batch skipped by config.'); return pd.DataFrame()
    if drv is None or dl is None: raise ImportError('Descriptor engine not deployed. Run CELL 2 once.')
    stl_files=sorted(Path(stl_dir).glob('*.stl')); output_root=Path(output_root); output_root.mkdir(parents=True,exist_ok=True)
    log_tag=str(log_tag or (output_root.parent.name+'_'+output_root.name)).replace(' ','_'); log_path=TABLE_DIR/f'descriptor_run_log_{log_tag}.csv'; rows=[]; old_cwd=Path.cwd()
    try:
        os.chdir(ENGINE_DIR)
        for i,stl_path in enumerate(stl_files,1):
            workdir=output_root/stl_path.stem
            if not force and RESUME_SKIP_COMPLETED and _descriptor_existing_valid(workdir):
                raw_slice_dir=workdir/'images'/'raw_slices'; row={'candidate_id':stl_path.stem,'file':stl_path.name,'status':'RESUMED_EXISTING','elapsed_sec':0.0,'error':'','workdir':str(workdir),'profile':profile,'descriptor_csv':str(workdir/'features'/'descriptors_ALL.csv'),'descriptor_slice_dir':str(raw_slice_dir),'raw_slice_image_count':len(list(raw_slice_dir.glob('*.png'))) if raw_slice_dir.exists() else 0}; rows.append(row); atomic_csv(pd.DataFrame(rows),log_path); print(f'[DESC {i}/{len(stl_files)}] {stl_path.stem}: RESUMED_EXISTING'); continue
            gpu_ids=choose_adaptive_gpu_ids(max_devices=2,purpose='descriptor') if bool(DESCRIPTOR_ENABLE_GPU) else []
            cpu_workers=choose_adaptive_cpu_workers()
            snap=adaptive_gpu_snapshot()
            overrides={'CROP_CUBE_SIZE_MM':float(DESCRIPTOR_CROP_CUBE_SIZE_MM),'VOXEL_SIZE_MM':float(DESCRIPTOR_REFERENCE_VOXEL_SIZE_MM),'IMAGE_PIXELS_PER_SIDE':int(DESCRIPTOR_IMAGE_PIXELS_PER_SIDE),'LAYER_SLICE_PERCENT':int(DESCRIPTOR_LAYER_SLICE_PERCENT),'SAVE_SLICE_IMAGES':bool(save_debug_images),'TRIPLET_IMAGE_STRIDE':1,'RAW_SLICE_IMAGE_STRIDE':1,'MAX_RAW_SLICE_IMAGES':None,'CPU_WORKERS':int(cpu_workers),'ENABLE_PARALLEL_DESCRIPTOR_STAGES':bool(DESCRIPTOR_ENABLE_PARALLEL),'ENABLE_GPU_ACCELERATION':bool(gpu_ids),'GPU_IDS':list(gpu_ids),**_descriptor_profile_overrides(profile)}
            t0=time.time(); print(f'[DESC {i}/{len(stl_files)}] {stl_path.stem}: GPU_IDS={gpu_ids or "CPU fallback"}, CPU_WORKERS={cpu_workers}')
            with threadpool_limits(limits=int(DESCRIPTOR_INNER_BLAS_THREADS)):
                ok,elapsed,err=drv.run_pipeline_for_one_input(stl_path.resolve(),workdir.resolve(),config_overrides=overrides)
            row={'candidate_id':stl_path.stem,'file':stl_path.name,'status':'OK' if ok else 'FAILED','elapsed_sec':round(float(elapsed),3),'error':(err or '').splitlines()[-1] if err else '','workdir':str(workdir),'profile':profile,'cuda_device_ids':json.dumps(gpu_ids),'cpu_workers':int(cpu_workers),'gpu_snapshot_json':json.dumps(snap,ensure_ascii=False)}
            if ok:
                if save_raw_slice_files: drv.save_raw_slice_images(workdir.resolve(),stride=1,max_slices=None)
                raw_slice_dir=workdir/'images'/'raw_slices'; row.update({'descriptor_csv':str(workdir/'features'/'descriptors_ALL.csv'),'descriptor_slice_dir':str(raw_slice_dir),'raw_slice_image_count':len(list(raw_slice_dir.glob('*.png'))) if raw_slice_dir.exists() else 0})
            rows.append(row); atomic_csv(pd.DataFrame(rows),log_path); print(f'[DESC {i}/{len(stl_files)}] {stl_path.stem}: {row["status"]} ({time.time()-t0:.1f}s)')
            for g in gpu_ids: _free_cupy_pool_v3(g)
    finally: os.chdir(old_cwd)
    out=pd.DataFrame(rows); save_df_checkpoint(out,f'descriptor_log_{log_tag}'); return out

def hardware_report():
    try:
        import psutil
        phys=psutil.cpu_count(logical=False); logical=psutil.cpu_count(logical=True); ram=psutil.virtual_memory().total/1024**3; cpu_now=psutil.cpu_percent(interval=0.15)
    except Exception:
        phys=SETTINGS.get('CPU_PHYSICAL_CORES',32); logical=os.cpu_count(); ram=None; cpu_now=None
    snap=adaptive_gpu_snapshot()
    return {'platform':platform.platform(),'python':sys.version,'cpu_physical_detected':phys,'cpu_logical_detected':logical,'cpu_utilization_pct_probe':cpu_now,'ram_GB':ram,
            'cpu_physical_configured':SETTINGS.get('CPU_PHYSICAL_CORES',32),'descriptor_cpu_workers_now':choose_adaptive_cpu_workers(),'dlp_parallel_workers':SETTINGS.get('DLP_PARALLEL_WORKERS',24),
            'adaptive_gpu':snap,'note':'Both RTX 3090 are eligible. GPU1 receives a small tie-break preference because GPU0 is shared; live load/VRAM can override that preference.'}


# =====================================================================
# V4 ML / INVERSE-DESIGN READY OVERRIDES
# =====================================================================
# The v3 production/runtime behavior above is retained. The functions below add:
# - continuous latent-controlled generators (seed is provenance only, not an ML control)
# - persistent design/realization/geometry identifiers
# - import/inverse-design candidate sources
# - ML-ready data registry/schema exports while preserving descriptor columns

V4_RUNTIME_VERSION = 'v4-ml-inverse-ready-20260904'
LATENT_DIM = int(SETTINGS.get('LATENT_DIM', 16))
LATENT_COLUMNS = [f'latent__z{i:02d}' for i in range(1, LATENT_DIM+1)]
CANDIDATE_SOURCE = str(SETTINGS.get('CANDIDATE_SOURCE','generate')).lower()
GENERATOR_VERSION = str(SETTINGS.get('GENERATOR_VERSION','v4_latent_controlled'))
ML_ROOT = Path(SETTINGS.get('ML_ROOT', RUN_DIR/'04_ml_dataset'))
MODEL_ROOT = Path(SETTINGS.get('MODEL_ROOT', RUN_DIR/'05_models'))
INVERSE_ROOT = Path(SETTINGS.get('INVERSE_ROOT', RUN_DIR/'06_inverse_design'))
ACTIVE_ROOT = Path(SETTINGS.get('ACTIVE_ROOT', RUN_DIR/'07_active_learning'))
for _p in (ML_ROOT, MODEL_ROOT, INVERSE_ROOT, ACTIVE_ROOT): _p.mkdir(parents=True, exist_ok=True)

_V3_REALIZE = realize_voxel_params
_V3_GEN_MASK = generate_voxel_mask


def _norm_scalar(v):
    if isinstance(v,(np.integer,)): return int(v)
    if isinstance(v,(np.floating,)): return float(v)
    if isinstance(v,(bool,np.bool_)): return bool(v)
    if pd.isna(v) if not isinstance(v,(dict,list,tuple)) else False: return None
    return v


def _stable_hash_dict(d, n=12):
    payload=json.dumps({str(k):_norm_scalar(v) for k,v in sorted(d.items())},sort_keys=True,ensure_ascii=False,separators=(',',':'),default=_json_default)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:int(n)]


def _design_control_columns(df_or_row=None):
    base=[
        'voxel_mode','target_vf','min_thickness_mm','min_hole_size_mm','max_thickness_mm',
        'closing_radius_mm','opening_radius_mm','connectivity_bridge_radius_mm',
        'contact_surface_depth_mm','num_fourier_terms','fourier_k_max','anisotropy_z','sigma_mm'
    ]
    return base + LATENT_COLUMNS


def add_persistent_ids(df, run_id=None):
    out=df.copy()
    run_id=str(run_id or SETTINGS.get('RUN_NAME',RUN_DIR.name))
    if 'generator_version' not in out: out['generator_version']=GENERATOR_VERSION
    if 'sampling_method' not in out:
        out['sampling_method']=out.get('generator_param_sampling','unknown')
    design_ids=[]; realization_ids=[]
    for i,r in out.iterrows():
        d={c:r.get(c,None) for c in _design_control_columns() if c in out.columns}
        d['generator_version']=r.get('generator_version',GENERATOR_VERSION)
        did=str(r.get('design_id','')).strip()
        if not did or did.lower()=='nan': did='D_'+_stable_hash_dict(d,14)
        rid=str(r.get('realization_id','')).strip()
        if not rid or rid.lower()=='nan':
            seed=r.get('seed',i)
            rid=f'{did}_R{_stable_hash_dict({"seed":seed,"candidate_id":r.get("candidate_id",i)},8)}'
        design_ids.append(did); realization_ids.append(rid)
    out['design_id']=design_ids; out['realization_id']=realization_ids; out['run_id']=run_id
    return out


def _latent_vector(row):
    z=[]
    for c in LATENT_COLUMNS:
        try: z.append(float(row.get(c,0.0)))
        except Exception: z.append(0.0)
    return np.clip(np.asarray(z,float),-1.0,1.0)


def _basis_triplets(kmax, n_terms):
    vals=[]
    for kx in range(1,int(kmax)+1):
        for ky in range(1,int(kmax)+1):
            for kz in range(1,int(kmax)+1):
                vals.append((kx,ky,kz))
    vals.sort(key=lambda t:(t[0]**2+t[1]**2+t[2]**2,t[0]+t[1]+t[2],t))
    return vals[:max(1,int(n_terms))]


def latent_periodic_fourier_field(n, z, num_terms=16, anisotropy=(1,1,1), k_max=4):
    """Continuous deterministic Fourier generator. z changes field smoothly; no random seed in geometry map."""
    n=int(n); z=np.asarray(z,float).reshape(-1)
    if z.size==0: z=np.zeros(1,float)
    xp=_xp_for_generation(n); dtype=xp.float32
    x=xp.linspace(0.0,2.0*xp.pi,n,endpoint=False,dtype=dtype)
    X=x[:,None,None]; Y=x[None,:,None]; Z=x[None,None,:]
    F=xp.zeros((n,n,n),dtype=dtype); ax,ay,az=map(float,anisotropy)
    basis=_basis_triplets(int(k_max),int(num_terms))
    for j,(kx,ky,kz) in enumerate(basis):
        # Smooth bounded amplitude + phase maps from a compact latent vector.
        a=float(np.tanh(1.25*z[j%z.size]))/math.sqrt(len(basis))
        phase=float(np.pi*(z[(j*3+1)%z.size]+1.0))
        mod=1.0+0.25*float(z[(j*5+2)%z.size])
        term=(kx*ax)*X+(ky*ay)*Y+(kz*az)*Z+phase
        xp.sin(term,out=term); term*=a*mod; F+=term; del term
    F=(F-xp.mean(F))/(xp.std(F)+1e-12)
    if CUPY_AVAILABLE and cp is not None and isinstance(F,cp.ndarray): F=cp.asnumpy(F)
    return np.asarray(F,np.float32)


def latent_stochastic_spectral_field(n, z, sigma_vox=4.0, anisotropy_z=1.0, k_max=6):
    """Stochastic-looking but deterministic spectral random field controlled continuously by z."""
    n=int(n); z=np.asarray(z,float).reshape(-1)
    if z.size==0: z=np.zeros(1,float)
    n_terms=max(12,min(48,3*z.size)); basis=_basis_triplets(int(k_max),n_terms)
    xp=_xp_for_generation(n); dtype=xp.float32
    x=xp.linspace(0.0,2.0*xp.pi,n,endpoint=False,dtype=dtype)
    X=x[:,None,None]; Y=x[None,:,None]; Z=x[None,None,:]
    F=xp.zeros((n,n,n),dtype=dtype)
    sig=max(float(sigma_vox),0.5)/max(float(n),1.0)
    for j,(kx,ky,kz) in enumerate(basis):
        k2=kx*kx+ky*ky+(kz/max(float(anisotropy_z),1e-6))**2
        spectral=float(np.exp(-0.5*(2*np.pi*sig)**2*k2))
        a=float(np.tanh(1.4*z[j%z.size]))*spectral/math.sqrt(len(basis))
        phase=float(np.pi*(z[(j*7+3)%z.size]+1.0))
        term=kx*X+ky*Y+(kz*float(anisotropy_z))*Z+phase
        xp.cos(term,out=term); term*=a; F+=term; del term
    F=(F-xp.mean(F))/(xp.std(F)+1e-12)
    if CUPY_AVAILABLE and cp is not None and isinstance(F,cp.ndarray): F=cp.asnumpy(F)
    return np.asarray(F,np.float32)


def realize_voxel_params(row, voxel_size_mm, stage='screening'):
    p=_V3_REALIZE(row,voxel_size_mm,stage)
    r=row.to_dict() if hasattr(row,'to_dict') else dict(row)
    for c in LATENT_COLUMNS: p[c]=float(r.get(c,0.0))
    p['generator_version']=str(r.get('generator_version',GENERATOR_VERSION))
    p['design_id']=str(r.get('design_id',''))
    p['realization_id']=str(r.get('realization_id',''))
    return p


def _postprocess_latent_field(F, params, periodic=False):
    mode=str(params.get('voxel_mode','latent_stochastic')); target_vf=float(params.get('target_vf',0.3)); n=int(params['grid_n'])
    if periodic and bool(params.get('strict_global_symmetry',STRICT_GLOBAL_SYMMETRY)):
        # map latent periodic family to the closest validated symmetry implementation
        symmode='periodic_orthotropic' if 'orthotropic' in mode else 'periodic_isotropic'
        F=symmetrize_scalar_field(F,symmode)
    mask=enforce_vf_by_rank(F,target_vf=target_vf,prefer_high=True)
    ci=int(params.get('closing_iter',0)); oi=int(params.get('opening_iter',0))
    if ci>0: mask=binary_closing(mask,iterations=ci)
    if oi>0 and not periodic: mask=binary_opening(mask,iterations=oi)
    mt=int(params.get('min_thickness_vox',1))
    if mt>1:
        mask=binary_closing(mask,iterations=max(1,mt-1))
        if not periodic: mask=binary_opening(mask,iterations=max(0,mt-2))
    mh=int(params.get('min_hole_size_vox',1))
    if mh>1: mask=enforce_voxel_min_hole_size(mask,min_hole_size_vox=mh)
    # Existing validated connectivity/contact routines accept arbitrary mode; periodic symmetry is restored afterward.
    mask,conn_info=finalize_lattice_voxel_mask(mask,params,generator_type='voxel',mode_key='voxel_mode',max_iter=6)
    if (not periodic) and ENABLE_MAX_THICKNESS_TRIM and n<=int(MAX_THICKNESS_TRIM_GRID_LIMIT):
        mask=limit_max_thickness_approx(mask,int(params.get('max_thickness_vox',0)))
    mask,ci2=finalize_lattice_voxel_mask(mask,params,generator_type='voxel',mode_key='voxel_mode',max_iter=6)
    conn_info.update({f'after_thickness_{k}':v for k,v in ci2.items()})
    params['_last_connectivity_info']=conn_info
    return np.asarray(mask,bool)


def generate_voxel_mask(params):
    mode=str(params.get('voxel_mode',''))
    if mode not in {'latent_periodic_isotropic','latent_periodic_orthotropic','latent_stochastic'}:
        return _V3_GEN_MASK(params)
    z=np.asarray([float(params.get(c,0.0)) for c in LATENT_COLUMNS],float)
    n=int(params.get('grid_n',VOXEL_GRID_N)); az=float(params.get('anisotropy_z',1.0))
    if mode.startswith('latent_periodic'):
        F=latent_periodic_fourier_field(n,z,int(params.get('num_fourier_terms',16)),(1.0,1.0,az),int(params.get('fourier_k_max',4)))
        mask=_postprocess_latent_field(F,params,periodic=True)
    else:
        F=latent_stochastic_spectral_field(n,z,float(params.get('sigma',4.0)),az,int(params.get('fourier_k_max',6)))
        mask=_postprocess_latent_field(F,params,periodic=False)
    del F; gc.collect(); return mask


def _read_candidate_import(path):
    path=Path(path)
    if not path.exists(): raise FileNotFoundError(f'Candidate import file not found: {path}')
    if path.suffix.lower()=='.csv': return pd.read_csv(path)
    if path.suffix.lower() in {'.xlsx','.xls'}: return pd.read_excel(path)
    if path.suffix.lower() in {'.parquet','.pq'}: return pd.read_parquet(path)
    raise ValueError(f'Unsupported candidate file: {path}')


def _validate_candidate_columns(df):
    required=['voxel_mode','target_vf','min_thickness_mm','min_hole_size_mm','max_thickness_mm','closing_radius_mm','opening_radius_mm','connectivity_bridge_radius_mm','contact_surface_depth_mm','num_fourier_terms','fourier_k_max','anisotropy_z','sigma_mm']
    missing=[c for c in required if c not in df.columns]
    if missing: raise ValueError('Candidate table missing required columns: '+str(missing))
    out=df.copy()
    if 'candidate_id' not in out: out['candidate_id']=[f'IMP_{i+1:04d}' for i in range(len(out))]
    if 'generator_type' not in out: out['generator_type']='voxel'
    if 'seed' not in out: out['seed']=np.arange(len(out))+int(SETTINGS.get('RANDOM_SEED',42))*100000
    if 'size_mm' not in out: out['size_mm']=float(BOUNDARY_SIZE_MM)
    if 'strict_global_symmetry' not in out: out['strict_global_symmetry']=out['voxel_mode'].astype(str).str.contains('periodic')
    if 'force_connected' not in out: out['force_connected']=bool(FORCE_CONNECTED_LATTICE_VOXEL)
    if 'generator_param_sampling' not in out: out['generator_param_sampling']=CANDIDATE_SOURCE
    if 'sampling_method' not in out: out['sampling_method']=out['generator_param_sampling']
    if 'generator_version' not in out: out['generator_version']=GENERATOR_VERSION
    for c in LATENT_COLUMNS:
        if c not in out: out[c]=0.0
    return add_persistent_ids(out)


def build_voxel_candidate_table(n_total=N_RANDOM_STRUCTURES, seed=RANDOM_SEED, use_lhs=USE_GENERATOR_PARAMETER_LHS):
    source=str(SETTINGS.get('CANDIDATE_SOURCE','generate')).lower()
    if source in {'import','inverse_design','active_sampling'}:
        key={'import':'CANDIDATE_IMPORT_FILE','inverse_design':'INVERSE_DESIGN_CANDIDATE_FILE','active_sampling':'ACTIVE_SAMPLING_CANDIDATE_FILE'}[source]
        path=SETTINGS.get(key,'')
        if not path: raise ValueError(f'{key} must be set when CANDIDATE_SOURCE={source!r}')
        df=_validate_candidate_columns(_read_candidate_import(path))
    else:
        rng=np.random.default_rng(int(seed)); modes=list(SETTINGS.get('VOXEL_MODES',['latent_periodic_isotropic','latent_periodic_orthotropic','latent_stochastic']))
        counts=_balanced_mode_counts(int(n_total),modes)
        dims=[('target_vf',False),('min_thickness_mm',False),('min_hole_size_mm',False),('max_thickness_mm',False),('closing_radius_mm',False),('opening_radius_mm',False),('connectivity_bridge_radius_mm',False),('contact_surface_depth_mm',False),('num_fourier_terms',True),('fourier_k_max',True),('anisotropy_z',False),('sigma_mm',False)]
        rows=[]; gi=0
        for mi,mode in enumerate(modes):
            nm=counts[mode]; U=_lhs_or_random(nm,len(dims)+LATENT_DIM,int(seed)+1009*(mi+1),use_lhs)
            sm={name:_scale_unit(U[:,j],GEN_PARAM_RANGES[name],integer=is_int) for j,(name,is_int) in enumerate(dims)}
            zU=2.0*U[:,len(dims):]-1.0
            for i in range(nm):
                gi+=1
                row={'candidate_id':f'VOX_{mode}_{gi:05d}','generator_type':'voxel','voxel_mode':mode,'seed':int(rng.integers(0,2**31-1)),'size_mm':float(BOUNDARY_SIZE_MM),'generator_version':GENERATOR_VERSION,'sampling_method':'generator_LHS' if use_lhs else 'random_uniform','generator_param_sampling':'LHS' if use_lhs else 'random_uniform','strict_global_symmetry':bool(STRICT_GLOBAL_SYMMETRY if 'periodic' in mode else False),'force_connected':bool(FORCE_CONNECTED_LATTICE_VOXEL),'screening_voxel_size_mm':float(SCREENING_VOXEL_SIZE_MM if USE_SCREENING_RESOLUTION else VOXEL_SIZE_MM),'final_voxel_size_mm':float(VOXEL_SIZE_MM)}
                for name,_ in dims: row[name]=_norm_scalar(sm[name][i])
                for j,c in enumerate(LATENT_COLUMNS): row[c]=float(zU[i,j])
                rows.append(row)
        df=add_persistent_ids(pd.DataFrame(rows))
        order=np.random.default_rng(int(seed)+777).permutation(len(df)); df=df.iloc[order].reset_index(drop=True)
    CANDIDATE_ROOT.mkdir(parents=True,exist_ok=True)
    atomic_csv(df,CANDIDATE_ROOT/'Candidate_Generation_Parameters.csv')
    try: df.to_parquet(CANDIDATE_ROOT/'Candidate_Generation_Parameters.parquet',index=False)
    except Exception: pass
    # Writing 30k x many columns to XLSX is much slower than CSV/Parquet. Keep a quick Excel preview
    # by default; users can enable the full workbook explicitly when it is really needed.
    try:
        preview_n=max(1,int(SETTINGS.get('CANDIDATE_XLSX_PREVIEW_ROWS',5000)))
        df.head(preview_n).to_excel(CANDIDATE_ROOT/'Candidate_Generation_Parameters_preview.xlsx',index=False)
        if bool(SETTINGS.get('EXPORT_FULL_CANDIDATE_XLSX',False)):
            df.to_excel(CANDIDATE_ROOT/'Candidate_Generation_Parameters_FULL.xlsx',index=False)
    except Exception as exc:
        print(f'[Candidate export] Excel export skipped/failed: {type(exc).__name__}: {exc}')
    return df


def generation_parameter_append_table(candidate_table, voxel_size_mm, stage):
    rows=[]
    candidate_table=add_persistent_ids(candidate_table)
    for _,row in candidate_table.iterrows():
        p=realize_voxel_params(row,voxel_size_mm,stage)
        out={
            'sample_id':str(row['candidate_id']),
            'meta__design_id':str(row['design_id']),'meta__realization_id':str(row['realization_id']),
            'meta__run_id':str(row.get('run_id',RUN_DIR.name)),'meta__generator_version':str(row.get('generator_version',GENERATOR_VERSION)),
            'meta__sampling_method':str(row.get('sampling_method',row.get('generator_param_sampling','unknown'))),
            'meta__seed':int(row.get('seed',0)),'meta__fidelity':str(stage),
            'gen__generator_type':str(row.get('generator_type','voxel')),'gen__voxel_mode':str(row['voxel_mode']),
            'gen__size_mm':float(row.get('size_mm',BOUNDARY_SIZE_MM)),'gen__target_vf':float(row['target_vf']),
            'gen__min_thickness_mm':float(row['min_thickness_mm']),'gen__min_hole_size_mm':float(row['min_hole_size_mm']),
            'gen__max_thickness_mm':float(row['max_thickness_mm']),'gen__closing_radius_mm':float(row['closing_radius_mm']),
            'gen__opening_radius_mm':float(row['opening_radius_mm']),'gen__connectivity_bridge_radius_mm':float(row['connectivity_bridge_radius_mm']),
            'gen__contact_surface_depth_mm':float(row['contact_surface_depth_mm']),'gen__num_fourier_terms':int(row['num_fourier_terms']),
            'gen__fourier_k_min':1,'gen__fourier_k_max':int(row['fourier_k_max']),'gen__anisotropy_z':float(row['anisotropy_z']),
            'gen__sigma_mm':float(row['sigma_mm']),'gen__strict_global_symmetry':bool(row.get('strict_global_symmetry',False)),
            'gen__force_connected':bool(row.get('force_connected',True)),'gen__stage':str(stage),
            'gen__realized_voxel_size_mm':float(voxel_size_mm),'gen__realized_grid_n':int(p['grid_n']),
            'gen__realized_min_thickness_vox':int(p['min_thickness_vox']),'gen__realized_min_hole_size_vox':int(p['min_hole_size_vox']),
            'gen__realized_max_thickness_vox':int(p['max_thickness_vox']),'gen__realized_closing_iter':int(p['closing_iter']),
            'gen__realized_opening_iter':int(p['opening_iter']),'gen__realized_connectivity_bridge_radius_vox':int(p['connectivity_bridge_radius_vox']),
            'gen__realized_contact_surface_depth_vox':int(p['contact_surface_depth_vox']),'gen__realized_sigma_vox':float(p['sigma']),
        }
        for c in LATENT_COLUMNS: out[c]=float(row.get(c,0.0))
        rows.append(out)
    return pd.DataFrame(rows)


def _sha256_file(path, chunk=2**20):
    h=hashlib.sha256(); path=Path(path)
    with path.open('rb') as f:
        while True:
            b=f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()


def build_ml_dataset_contract(pool_master=None, final_master=None):
    """Build permanent ML datasets. Non-LHS pool rows are intentionally retained."""
    if pool_master is None:
        pool_master=load_df_checkpoint('pool_master',required=False)
    if final_master is None:
        final_master=load_df_checkpoint('selected_final_master',required=False)
    frames=[]
    for df,fidelity in [(pool_master,'screening'),(final_master,'final')]:
        if df is None or len(df)==0: continue
        x=df.copy(); x['meta__fidelity']=fidelity
        frames.append(x)
    if not frames: raise RuntimeError('No descriptor master table available for ML export.')
    all_df=pd.concat(frames,ignore_index=True,sort=False)
    # Fill geometric provenance and file paths.
    is_sel=set()
    sp=CHECKPOINT_DIR/'selected_samples.csv'
    if sp.exists():
        try:is_sel=set(pd.read_csv(sp)['sample_id'].astype(str))
        except Exception:pass
    all_df['meta__is_descriptor_selected']=all_df['sample_id'].astype(str).isin(is_sel)
    geom_hash=[]; stl_paths=[]; slice_dirs=[]; dlp_paths=[]
    for _,r in all_df.iterrows():
        sid=str(r['sample_id']); fid=str(r.get('meta__fidelity','screening'))
        stldir=SELECTED_STL_DIR if fid=='final' else POOL_STL_DIR
        descdir=SELECTED_DESCRIPTOR_DIR if fid=='final' else POOL_DESCRIPTOR_DIR
        dlpdir=SELECTED_DLP_DIR if fid=='final' else POOL_DLP_DIR
        stl=stldir/f'{sid}.stl'; stl_paths.append(str(stl) if stl.exists() else '')
        geom_hash.append(('G_'+_sha256_file(stl)[:16]) if stl.exists() else '')
        sd=descdir/sid/'images'/'raw_slices'; slice_dirs.append(str(sd) if sd.exists() else '')
        dp=next(iter(sorted(dlpdir.glob(f'{sid}*.slice'))),None) if dlpdir.exists() else None; dlp_paths.append(str(dp) if dp else '')
    all_df['meta__geometry_id']=geom_hash; all_df['meta__stl_path']=stl_paths; all_df['meta__descriptor_slice_dir']=slice_dirs; all_df['meta__dlp_slice_path']=dlp_paths
    # Stable ordering: metadata -> raw descriptors -> generator inputs/latent/realized params.
    meta_cols=[c for c in all_df.columns if c.startswith('meta__') or c=='sample_id']
    gen_cols=[c for c in all_df.columns if c.startswith('gen__') or c.startswith('latent__')]
    desc_cols=[c for c in all_df.columns if c not in set(meta_cols+gen_cols)]
    all_df=all_df.reindex(columns=meta_cols+desc_cols+gen_cols)
    atomic_csv(all_df,ML_ROOT/'all_structures.csv')
    try: all_df.to_parquet(ML_ROOT/'all_structures.parquet',index=False)
    except Exception: pass
    # Model-1 dataset is identical in rows, but schema explicitly marks input/output roles.
    atomic_csv(all_df,ML_ROOT/'generator_to_descriptor.csv')
    # Schemas
    generator_inputs=[]
    for c in gen_cols:
        role='generator_input'
        optimizable=(c.startswith('latent__') or c in {
            'gen__target_vf','gen__min_thickness_mm','gen__min_hole_size_mm','gen__max_thickness_mm','gen__closing_radius_mm','gen__opening_radius_mm','gen__connectivity_bridge_radius_mm','gen__contact_surface_depth_mm','gen__num_fourier_terms','gen__fourier_k_max','gen__anisotropy_z','gen__sigma_mm'})
        if c.startswith('gen__realized_') or c in {'gen__stage','gen__size_mm','gen__generator_type','gen__strict_global_symmetry','gen__force_connected','gen__fourier_k_min'}: optimizable=False
        generator_inputs.append({'name':c,'role':role,'optimizable':bool(optimizable),'dtype':str(all_df[c].dtype),'unit':'mm' if c.endswith('_mm') else '-'})
    desc_schema=[]
    for c in desc_cols:
        desc_schema.append({'name':c,'role':'structural_descriptor','dtype':str(all_df[c].dtype),'family':'pixel_slice_or_3d_descriptor'})
    performance=[
        {'name':'perf__modulus_MPa','source':'curve'}, {'name':'perf__yield_stress_MPa','source':'curve'},
        {'name':'perf__peak_stress_MPa','source':'curve'}, {'name':'perf__plateau_stress_MPa','source':'curve'},
        {'name':'perf__densification_strain','source':'curve'}, {'name':'perf__energy_density_MJ_m3','source':'curve'},
        {'name':'perf__absorbed_energy_to_densification_MJ_m3','source':'curve'}, {'name':'perf__cfe','source':'curve'}]
    atomic_json(ML_ROOT/'generator_schema.json',{'schema_version':'1.0','generator_version':GENERATOR_VERSION,'latent_dim':LATENT_DIM,'features':generator_inputs,'excluded_from_model':['meta__seed']})
    atomic_json(ML_ROOT/'descriptor_schema.json',{'schema_version':'1.0','features':desc_schema,'note':'Original descriptor names preserved; representation model is trained separately.'})
    atomic_json(ML_ROOT/'performance_schema.json',{'schema_version':'1.0','targets':performance})
    registry_cols=[c for c in ['sample_id','meta__design_id','meta__realization_id','meta__geometry_id','meta__run_id','meta__generator_version','meta__sampling_method','meta__fidelity','meta__is_descriptor_selected','meta__stl_path','meta__descriptor_slice_dir','meta__dlp_slice_path'] if c in all_df]
    registry=all_df[registry_cols].copy(); atomic_csv(registry,ML_ROOT/'data_registry.csv')
    # Recommended long-format compression template; the curve-training adapter also accepts the legacy v22 Excel layout.
    template=pd.DataFrame(columns=['specimen_id','design_id','geometry_id','replicate_id','strain','stress_MPa','test_fidelity','material_batch','print_batch','strain_rate_s-1','temperature_C'])
    atomic_csv(template,ML_ROOT/'compression_curve_long_template.csv')
    project_contract={
        'contract_version':'1.0','voxel_run_dir':str(RUN_DIR),'ml_root':str(ML_ROOT),'model_root':str(MODEL_ROOT),
        'inverse_root':str(INVERSE_ROOT),'active_root':str(ACTIVE_ROOT),'all_structures_csv':str(ML_ROOT/'all_structures.csv'),
        'generator_schema':str(ML_ROOT/'generator_schema.json'),'descriptor_schema':str(ML_ROOT/'descriptor_schema.json'),
        'performance_schema':str(ML_ROOT/'performance_schema.json'),'compression_template':str(ML_ROOT/'compression_curve_long_template.csv'),
        'runtime_version':V4_RUNTIME_VERSION,'updated_at':time.strftime('%Y-%m-%dT%H:%M:%S')}
    atomic_json(ML_ROOT/'project_contract.json',project_contract)
    # Project-level pointer independent of the current Python kernel.
    proj_ptr=Path(SETTINGS.get('ML_PROJECT_POINTER',BASE_DIR/'.ai_voxel_ml_project.json'))
    atomic_json(proj_ptr,project_contract)
    return project_contract, all_df, registry

# V4 contract augmentation: explicit manufacturing/testing manifest.
_V4_CONTRACT_BASE = build_ml_dataset_contract
def build_ml_dataset_contract(pool_master=None, final_master=None):
    contract, all_df, registry = _V4_CONTRACT_BASE(pool_master, final_master)
    final = all_df[all_df['meta__fidelity'].astype(str).eq('final')].copy() if 'meta__fidelity' in all_df else all_df.iloc[0:0].copy()
    cols=[c for c in ['sample_id','meta__design_id','meta__realization_id','meta__geometry_id','meta__stl_path','meta__dlp_slice_path','meta__descriptor_slice_dir','gen__voxel_mode','gen__target_vf'] if c in final.columns]
    manifest=final[cols].copy()
    if len(manifest):
        manifest.insert(0,'specimen_id',[f'SPEC_{i+1:03d}' for i in range(len(manifest))])
        manifest['compression_curve_expected_design_id']=manifest['meta__design_id'] if 'meta__design_id' in manifest else manifest['sample_id']
    atomic_csv(manifest,ML_ROOT/'experimental_specimen_manifest.csv')
    contract['experimental_specimen_manifest']=str(ML_ROOT/'experimental_specimen_manifest.csv')
    atomic_json(ML_ROOT/'project_contract.json',contract)
    atomic_json(Path(SETTINGS.get('ML_PROJECT_POINTER',BASE_DIR/'.ai_voxel_ml_project.json')),contract)
    return contract, all_df, registry

# V4 cumulative project contract: every DatasetFactory run contributes to one persistent ML project.
_V4_CONTRACT_RUN_BASE = build_ml_dataset_contract
def build_ml_dataset_contract(pool_master=None, final_master=None):
    run_contract, all_df, registry = _V4_CONTRACT_RUN_BASE(pool_master, final_master)
    project_root=Path(SETTINGS.get('ML_PROJECT_ROOT',RUN_DIR/'06_ML_Dataset'/'Project_State'))
    data_root=Path(SETTINGS.get('ML_DATA_ROOT',RUN_DIR/'06_ML_Dataset'))
    model_root=Path(SETTINGS.get('MODEL_ROOT',RUN_DIR/'07_Models'))
    inverse_root=Path(SETTINGS.get('INVERSE_ROOT',RUN_DIR/'08_Inverse_Optimization'))
    active_root=Path(SETTINGS.get('ACTIVE_ROOT',RUN_DIR/'09_Active_Sampling'))
    validation_root=Path(SETTINGS.get('VALIDATION_ROOT',RUN_DIR/'10_Validation'))
    for p in (project_root,data_root,model_root,inverse_root,active_root,validation_root):p.mkdir(parents=True,exist_ok=True)
    cumulative=data_root/'all_structures_cumulative.csv'
    if cumulative.exists():
        old=pd.read_csv(cumulative);combined=pd.concat([old,all_df],ignore_index=True,sort=False)
    else:combined=all_df.copy()
    # Preserve even geometrically duplicated designs: many-to-one generator mappings are useful Model-1 data.
    # Only remove exact re-exports of the same run/sample/fidelity row.
    fb=[c for c in ['meta__run_id','sample_id','meta__fidelity'] if c in combined]
    if fb: combined=combined.drop_duplicates(fb,keep='last')
    atomic_csv(combined,cumulative)
    try:combined.to_parquet(data_root/'all_structures_cumulative.parquet',index=False)
    except Exception:pass
    # copy schemas from this run, keeping the cumulative project self-contained
    for name in ['generator_schema.json','descriptor_schema.json','performance_schema.json']:
        src=ML_ROOT/name
        if src.exists() and src.resolve()!= (data_root/name).resolve(): shutil.copy2(src,data_root/name)
    # performance schema matching the actual curve-model output names
    perf={'schema_version':'1.1','targets':[
        {'name':'perf__modulus','unit':'MPa'},{'name':'perf__yield_stress','unit':'MPa'},{'name':'perf__peak_stress','unit':'MPa'},
        {'name':'perf__compressive_stress','unit':'MPa'},{'name':'perf__plateau_stress','unit':'MPa'},
        {'name':'perf__densification_strain','unit':'-'},{'name':'perf__energy_density','unit':'MJ/m3'},
        {'name':'perf__absorbed_energy_to_densification','unit':'MJ/m3'},{'name':'perf__cfe','unit':'-'}]}
    atomic_json(data_root/'performance_schema.json',perf);atomic_json(ML_ROOT/'performance_schema.json',perf)
    # append manufacturing manifest across cycles
    run_manifest=ML_ROOT/'experimental_specimen_manifest.csv';global_manifest=data_root/'experimental_specimen_manifest_cumulative.csv'
    if run_manifest.exists():
        rm=pd.read_csv(run_manifest);gm=pd.read_csv(global_manifest) if global_manifest.exists() else pd.DataFrame();gg=pd.concat([gm,rm],ignore_index=True,sort=False)
        keys=[c for c in ['meta__geometry_id','sample_id'] if c in gg]
        if keys:gg=gg.drop_duplicates(keys,keep='last')
        atomic_csv(gg,global_manifest)
    # central curve master is the canonical Model-2 interface
    curve_master=data_root/'compression_curves_master.csv'
    if not curve_master.exists():
        atomic_csv(pd.DataFrame(columns=['specimen_id','design_id','geometry_id','replicate_id','strain','stress_MPa','test_fidelity','material_batch','print_batch','strain_rate_s-1','temperature_C']),curve_master)
    contract={
        **run_contract,'contract_version':'1.1-cumulative','project_root':str(project_root),'data_root':str(data_root),
        'current_voxel_run_dir':str(RUN_DIR),'current_run_snapshot_csv':str(ML_ROOT/'all_structures.csv'),
        'all_structures_csv':str(cumulative),'all_structures_parquet':str(data_root/'all_structures_cumulative.parquet'),
        'generator_schema':str(data_root/'generator_schema.json'),'descriptor_schema':str(data_root/'descriptor_schema.json'),
        'performance_schema':str(data_root/'performance_schema.json'),'compression_curve_master':str(curve_master),
        'experimental_specimen_manifest':str(global_manifest),'model_root':str(model_root),'inverse_root':str(inverse_root),'active_root':str(active_root),'validation_root':str(validation_root),
        'runtime_version':V4_RUNTIME_VERSION,'updated_at':time.strftime('%Y-%m-%dT%H:%M:%S')}
    atomic_json(project_root/'project_contract.json',contract);atomic_json(Path(SETTINGS.get('ML_PROJECT_POINTER',BASE_DIR/'.ai_voxel_ml_project.json')),contract)
    return contract, combined, registry
