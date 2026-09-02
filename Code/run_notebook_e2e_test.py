"""
Executes every code cell of Architected_Material_Descriptor_Exhaustive_v3.ipynb
in order, in a persistent namespace (a minimal from-scratch notebook runner,
since nbclient/jupyter are not installable in this offline test environment).
Generates a small synthetic grayscale slice stack as input so the full v3+v4
pipeline -- including the new grayscale/soft-TSPE, curvature, tortuosity,
strut-graph and CT-reconstruction cells -- runs end to end exactly the way a
real user's Jupyter session would execute it, cell by cell.
"""
import json, sys, traceback
from pathlib import Path
import numpy as np
from PIL import Image

RUN_DIR = Path('/tmp/work/build/e2e_run')
if RUN_DIR.exists():
    import shutil; shutil.rmtree(RUN_DIR)
RUN_DIR.mkdir(parents=True)

# ---- synthesize a small grayscale slice stack: a simple 3-strut cubic lattice ----
slice_dir = RUN_DIR / 'slices'
slice_dir.mkdir()
n = 28
zz, yy, xx = np.mgrid[0:n, 0:n, 0:n]
vol = np.zeros((n, n, n), bool)
grid_pts = list(range(0, n, 9))
for gy in grid_pts:
    for gz in grid_pts:
        vol |= (np.abs(yy - gy) <= 1.6) & (np.abs(zz - gz) <= 1.6)
for gx in grid_pts:
    for gz in grid_pts:
        vol |= (np.abs(xx - gx) <= 1.6) & (np.abs(zz - gz) <= 1.6)
for gx in grid_pts:
    for gy in grid_pts:
        vol |= (np.abs(xx - gx) <= 1.6) & (np.abs(yy - gy) <= 1.6)
print('synthetic lattice density:', vol.mean(), 'shape', vol.shape)

from scipy import ndimage as ndi
gray = ndi.gaussian_filter(vol.astype(np.float32), sigma=0.6)
gray = (gray - gray.min()) / (gray.max() - gray.min() + 1e-9)
for z in range(n):
    im = (np.clip(gray[z], 0, 1) * 255).astype(np.uint8)
    Image.fromarray(im).save(slice_dir / f'slice_{z:03d}.png')
print('wrote', n, 'slice PNGs to', slice_dir)

# ---- load notebook, execute every code cell sequentially ----
nb_path = Path('/tmp/work/build/pkg/Architected_Material_Descriptor_Exhaustive_v3.ipynb')
nb = json.load(open(nb_path, encoding='utf-8'))

work_dir = Path('/tmp/work/build/pkg')  # execute with CWD = package dir, like a real user would
import os
os.chdir(work_dir)

ns = {'display': lambda *a, **k: None}  # notebook uses display(); no-op outside IPython

fail = False
for i, c in enumerate(nb['cells']):
    if c['cell_type'] != 'code':
        continue
    src = ''.join(c['source'])
    if i == 4:  # Cell 02 config: point INPUT_PATH/WORKDIR at our synthetic data
        src = src.replace('"INPUT_PATH": r"CHANGE_ME/sample.stl"',
                           f'"INPUT_PATH": r"{slice_dir.as_posix()}"')
        src = src.replace('"WORKDIR": r"descriptor_run"',
                           f'"WORKDIR": r"{(RUN_DIR / "descriptor_run").as_posix()}"')
        # keep CT recon cheap for the smoke test
        src = src.replace('"CT_RECON_N_ANGLES_FULL": 180', '"CT_RECON_N_ANGLES_FULL": 60')
        src = src.replace('"CT_RECON_N_ANGLES_SPARSE": 60', '"CT_RECON_N_ANGLES_SPARSE": 15')
    try:
        exec(compile(src, f'cell_{i}', 'exec'), ns)
    except Exception:
        print(f'\n!!!!! FAILURE in cell index {i} !!!!!')
        print(src)
        traceback.print_exc()
        fail = True
        break

if not fail:
    print('\n=== ALL CELLS EXECUTED WITHOUT ERROR ===')
    import pandas as pd
    csv_path = RUN_DIR / 'descriptor_run' / 'features' / 'descriptors_ALL.csv'
    df = pd.read_csv(csv_path)
    print('descriptors_ALL.csv shape:', df.shape)
    prefixes = ['curvature_', 'tortuosity_', 'strut_', 'soft_triplet_', 'ct_recon_']
    for p in prefixes:
        cols = [c for c in df.columns if c.startswith(p)]
        print(f'  {p:15s} -> {len(cols)} columns; sample: {cols[:3]}')
        assert len(cols) > 0, f'no columns found for prefix {p}'
    print('\nv4 INTEGRATION CHECK: PASS')
else:
    print('\nv4 INTEGRATION CHECK: FAIL')
    sys.exit(1)
