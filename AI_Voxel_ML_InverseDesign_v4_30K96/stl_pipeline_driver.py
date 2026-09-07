# -*- coding: utf-8 -*-
"""
Shared pipeline engine for Architected_Material_Descriptor_v6.ipynb.
The single notebook exposes one master SAVE_SLICE_IMAGES switch and max-performance CPU/GPU controls.

The actual descriptor-extraction pipeline (mesh/image-stack import through the full
exhaustive descriptor computation) is embedded directly in this file as _PIPELINE_CELLS,
generated once from the validated notebook pipeline -- so this module does NOT read either
notebook's .ipynb file at runtime. Both notebooks depend only on this file and
descriptor_library.py (plain .py files, same as any other requirement), so each notebook can
be opened and run completely on its own -- neither needs the other notebook to be present.

Keep this file and descriptor_library.py in the SAME folder as whichever notebook you run.
"""
from __future__ import annotations
import json
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    "SAVE_SLICE_IMAGES": True,
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
    # --- v5: centered fixed physical field-of-view around the STL six-face boundary center ---
    "CROP_CUBE_SIZE_MM": 30.0,       # L [mm]. Crop bounds = STL bbox center +/- L/2 on X/Y/Z.
    "IMAGE_PIXELS_PER_SIDE": 1000,   # nx=ny=1000; fixed XY pixel pitch = L / 1000 [mm/pixel].
    "LAYER_SLICE_PERCENT": 5,        # literal percent of crop height: dz=L*0.05; L=30 -> 1.5 mm.
                                      # z planes = 0%,5%,...,100% -> 21 planes.
    # --- image export (single notebook; controlled by SAVE_SLICE_IMAGES) ---
    "SAVE_RAW_SLICE_IMAGES": True,   # master SAVE_SLICE_IMAGES synchronizes this at run time.
    "RAW_SLICE_IMAGE_STRIDE": 1,
    "MAX_RAW_SLICE_IMAGES": None,    # None = no cap.
    # --- v6 performance defaults for Threadripper 3970X + 2 x RTX 3090 ---
    "ENABLE_PARALLEL_DESCRIPTOR_STAGES": True,
    "CPU_WORKERS": 32,
    "ENABLE_GPU_ACCELERATION": True,
    "GPU_IDS": [0, 1],
}

MESH_FILE_EXTS = ('.stl', '.step', '.stp', '.obj', '.ply')

# The full descriptor-extraction pipeline (env audit -> mesh/image import -> every descriptor
# family -> aggregation -> manifest), embedded verbatim from the validated reference pipeline.
# Excluded on purpose: the CONFIG cell (this driver builds+writes config.json itself, per
# input file) and the cross-run batch aggregator (the calling notebook aggregates across the
# whole batch itself, once, after the loop below finishes -- not once per file).
_PIPELINE_CELLS = [
'from pathlib import Path\nimport json, sys, importlib\nptr=Path(\'.architected_descriptor_active_workdir.txt\'); work=Path(ptr.read_text(encoding=\'utf-8\').strip()) if ptr.exists() else Path(\'descriptor_run\')\n# If WORKDIR was changed, discover it from the local config file path manually here once.\nconfig_path=work/"config.json"\nif not config_path.exists():\n    candidates=list(Path(\'.\').glob(\'*/config.json\'))\n    if len(candidates)==1: config_path=candidates[0]; work=config_path.parent\ncfg=json.loads(config_path.read_text(encoding=\'utf-8\'))\nmods=[\'numpy\',\'pandas\',\'scipy\',\'skimage\',\'trimesh\',\'networkx\',\'cv2\',\'sklearn\',\'gudhi\',\'cupy\']\nenv={\'python\':sys.version,\'mode\':cfg[\'MODE\']}\nfor m in mods:\n    try:\n        mod=importlib.import_module(m); env[m]=getattr(mod,\'__version__\',\'installed\')\n    except Exception as e: env[m]=f\'NOT_INSTALLED: {e}\'\ntry:\n    import descriptor_library as _dl\n    env[\'acceleration\']=_dl.gpu_acceleration_status(cfg.get(\'GPU_IDS\',[0,1]))\n    env[\'cpu_workers_requested\']=cfg.get(\'CPU_WORKERS\',32)\nexcept Exception as _e:\n    env[\'acceleration\']={\'status_error\':str(_e)}\n(work/\'checkpoints\').mkdir(parents=True,exist_ok=True)\n(work/\'checkpoints\'/\'00_environment.json\').write_text(json.dumps(env,indent=2),encoding=\'utf-8\')\nprint(json.dumps(env,indent=2))',
"from pathlib import Path\nimport json, sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); cfg=dl.load_json(work/'config.json'); inp=Path(cfg['INPUT_PATH'])\nkind=cfg['INPUT_KIND']\nif kind=='auto': kind='image_stack' if inp.is_dir() else 'mesh'\nif kind=='image_stack':\n    vol,spacing,meta=dl.load_image_stack(inp,cfg['THRESHOLD'],cfg['INVERT'],(cfg['DZ_MM'],cfg['DY_MM'],cfg['DX_MM']))\nelif kind=='mesh':\n    _pps=cfg.get('IMAGE_PIXELS_PER_SIDE')\n    _lsp=cfg.get('LAYER_SLICE_PERCENT')\n    # LAYER_SLICE_PERCENT is passed literally; with crop L, dz=L*(percent/100).\n    vol,spacing,meta=dl.load_mesh_as_voxels(inp,cfg['VOXEL_SIZE_MM'],\n                                              backend=cfg.get('MESH_VOXELIZATION_BACKEND','auto'),\n                                              repair=cfg.get('MESH_REPAIR',True),\n                                              verbose=True,\n                                              pixels_per_side=_pps,\n                                              layer_slice_percent=_lsp,\n                                              crop_cube_size_mm=cfg.get('CROP_CUBE_SIZE_MM'))\nelse: raise ValueError(kind)\ndl.save_volume(work/'checkpoints'/'01_volume_raw.npz',vol,spacing,meta)\ndl.save_json(meta,work/'checkpoints'/'01_input_meta.json')\nprint('raw volume:',vol.shape,'spacing z,y,x [mm]:',spacing,'density:',vol.mean())",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); cfg=dl.load_json(work/'config.json'); vol,spacing,meta=dl.load_volume(work/'checkpoints'/'01_volume_raw.npz')\nvol=dl.preprocess_volume(vol,cfg['MIN_COMPONENT_VOXELS'],cfg['FILL_HOLES'])\nvol,spacing=dl.shape_based_z_interpolation(vol,spacing,cfg['Z_UPSAMPLE'])\nmeta.update({'preprocessed':True,'z_upsample':cfg['Z_UPSAMPLE'],'processed_grid_shape_zyx':[int(v) for v in vol.shape],'processed_spacing_zyx_mm':[float(v) for v in spacing]})\ndl.save_volume(work/'checkpoints'/'02_volume_processed.npz',vol,spacing,meta)\nprint('processed:',vol.shape,'spacing:',spacing,'density:',vol.mean())",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,meta=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\n_crop=meta.get('crop_bounds_mm'); _z0=float(_crop[0][2]) if _crop else 0.0; _zmode=meta.get('z_sampling_mode','center')\ndf,s=dl.slice_descriptor_table(vol,spacing,z_origin_mm=_z0,z_mode=_zmode); df.to_csv(work/'features'/'03_slice_table.csv',index=False); dl.save_json(s,work/'features'/'03_slice_summary.json')\nprint('slice rows:',len(df),'summary descriptors:',len(s)); display(df.head())",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.projection_texture_descriptors(vol); dl.save_json(s,work/'features'/'04_projection_texture.json'); print('projection descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ndf,s=dl.pair_descriptor_table(vol,spacing); df.to_csv(work/'features'/'05_pair_table.csv',index=False); dl.save_json(s,work/'features'/'05_pair_summary.json')\nprint('pair rows:',len(df),'summary descriptors:',len(s)); display(df.head())",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); cfg=dl.load_json(work/'config.json'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\noutdir=work/'images'/'triplets' if cfg['SAVE_TRIPLET_IMAGES'] else None\ndf,s=dl.triplet_descriptor_table(vol,spacing,outdir,cfg['TRIPLET_IMAGE_STRIDE']); df.to_csv(work/'features'/'06_triplet_table.csv',index=False); dl.save_json(s,work/'features'/'06_triplet_summary.json')\nprint('triplet rows:',len(df),'summary descriptors:',len(s)); display(df.head())",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); cfg=dl.load_json(work/'config.json'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns={}; s.update(dl.multilevel_persistence_descriptors(vol,cfg['MAX_PERSISTENCE_K'])); s.update(dl.lag_overlap_descriptors(vol,cfg['MAX_LAYER_LAG']))\ndl.save_json(s,work/'features'/'07_multilayer_lag.json'); print('multi-layer/lag descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.triplet_transition_descriptors(vol); dl.save_json(s,work/'features'/'08_tspe_transition.json'); print('TSPE dynamic descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,meta=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.morphology3d_descriptors(vol,spacing,grid_extent_xyz_mm=meta.get('grid_extent_xyz_mm'),z_edge_inclusive=(meta.get('z_sampling_mode')=='edge')); dl.save_json(s,work/'features'/'09_morphology3d.json'); print('3D morphology descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); cfg=dl.load_json(work/'config.json'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.topology_descriptors(vol); s.update(dl.euler_filtration_descriptors(vol,cfg['EULER_FILTRATION_MAX_RADIUS'])); dl.save_json(s,work/'features'/'10_topology.json'); print('topology descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); cfg=dl.load_json(work/'config.json'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\n_g=bool(cfg.get('ENABLE_GPU_ACCELERATION',True)); _ids=cfg.get('GPU_IDS',[0,1]); _gid=int(_ids[0]) if _ids else 0; s=dl.distance_thickness_descriptors(vol,spacing,use_gpu=_g,gpu_id=_gid); s.update(dl.granulometry_descriptors(vol,cfg['GRANULOMETRY_MAX_RADIUS'],use_gpu=_g,gpu_id=_gid)); dl.save_json(s,work/'features'/'11_size_granulometry.json'); print('size/granulometry descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns={}; s.update(dl.chord_descriptors(vol,spacing)); s.update(dl.lineal_path_descriptors(vol)); s.update(dl.two_point_axis_descriptors(vol)); s.update(dl.three_point_descriptors(vol)); dl.save_json(s,work/'features'/'12_spatial_statistics.json'); print('spatial-stat descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.multiscale_descriptors(vol); dl.save_json(s,work/'features'/'13_multiscale_fractal.json'); print('multiscale/fractal descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); cfg=dl.load_json(work/'config.json'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\n_g=bool(cfg.get('ENABLE_GPU_ACCELERATION',True)); _ids=cfg.get('GPU_IDS',[0,1]); _gid=int(_ids[1] if len(_ids)>1 else (_ids[0] if _ids else 0)); s=dl.spectral_descriptors(vol,spacing,cfg['SPECTRAL_MAX_DIM'],use_gpu=_g,gpu_id=_gid); s.update(dl.directional_descriptors(vol,spacing)); dl.save_json(s,work/'features'/'14_spectral_directional.json'); print('spectral/directional descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.skeleton_network_descriptors(vol,spacing); dl.save_json(s,work/'features'/'15_skeleton_network.json'); print('skeleton/network descriptors:',len(s))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); cfg=dl.load_json(work/'config.json'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\nif cfg['OPTIONAL_PERSISTENT_HOMOLOGY']: s=dl.persistent_homology_descriptors(vol,cfg['PH_MAX_DIM_VOX'])\nelse: s={'persistent_homology_available':0,'persistent_homology_disabled_by_config':1}\ndl.save_json(s,work/'features'/'16_persistent_homology.json'); print(s)",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run')\ncfg=dl.load_json(work/'config.json')\ngpath=work/'checkpoints'/'01b_volume_grayscale.npz'\ninp=Path(cfg['INPUT_PATH']); kind=cfg['INPUT_KIND']\nif kind=='auto': kind='image_stack' if inp.is_dir() else 'mesh'\nif kind=='image_stack':\n    gvol,gspacing,gmeta=dl.load_image_stack_grayscale(inp,(cfg['DZ_MM'],cfg['DY_MM'],cfg['DX_MM']),cfg['INVERT'])\n    dl.save_grayscale_stack(gpath,gvol,gspacing,gmeta)\n    print('grayscale stack saved:',gvol.shape,'dtype',gvol.dtype,'range',(float(gvol.min()),float(gvol.max())))\nelse:\n    print('INPUT_KIND is mesh -> no native grayscale slices; Cell 19c will use a blurred-binary surrogate instead.')\n",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run')\ncfg=dl.load_json(work/'config.json')\ngpath=work/'checkpoints'/'01b_volume_grayscale.npz'\nif gpath.exists():\n    gvol,gspacing,_=dl.load_grayscale_stack(gpath)\nelse:\n    vol,gspacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\n    _g=bool(cfg.get('ENABLE_GPU_ACCELERATION',True)); _ids=cfg.get('GPU_IDS',[0,1]); _gid=int(_ids[1] if len(_ids)>1 else (_ids[0] if _ids else 0)); gvol=dl.grayscale_stack_from_binary(vol, blur_sigma=cfg.get('SOFT_TSPE_FALLBACK_BLUR_SIGMA',0.8),use_gpu=_g,gpu_id=_gid)\noutdir=work/'images'/'soft_triplets' if cfg['SAVE_TRIPLET_IMAGES'] else None\n_g=bool(cfg.get('ENABLE_GPU_ACCELERATION',True)); _ids=cfg.get('GPU_IDS',[0,1]); _gid=int(_ids[1] if len(_ids)>1 else (_ids[0] if _ids else 0)); df,s=dl.soft_triplet_descriptor_table(gvol,gspacing,outdir,cfg['TRIPLET_IMAGE_STRIDE'],use_gpu=_g,gpu_id=_gid)\ndf.to_csv(work/'features'/'v4_01_soft_triplet_table.csv',index=False)\ndl.save_json(s,work/'features'/'v4_01_soft_triplet_summary.json')\nprint('soft-triplet rows:',len(df),'summary descriptors:',len(s)); display(df.head())\n",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run')\ncfg=dl.load_json(work/'config.json')\nvol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.curvature_descriptors(vol,spacing,smooth_iterations=cfg.get('CURVATURE_SMOOTH_ITERATIONS',12))\ndl.save_json(s,work/'features'/'v4_02_curvature.json')\nprint('curvature descriptors:',len(s))\n",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run')\ncfg=dl.load_json(work/'config.json')\nvol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.tortuosity_descriptors(vol,spacing,max_side=cfg.get('TORTUOSITY_MAX_SIDE',48))\ndl.save_json(s,work/'features'/'v4_03_tortuosity.json')\nprint('tortuosity descriptors:',len(s)); print(s)\n",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run')\ncfg=dl.load_json(work/'config.json')\nvol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ns=dl.strut_graph_descriptors(vol,spacing,max_skeleton_voxels=cfg.get('STRUT_GRAPH_MAX_SKELETON_VOXELS',250000))\ndl.save_json(s,work/'features'/'v4_04_strut_graph.json')\nprint('strut/node graph descriptors:',len(s))\n",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run')\ncfg=dl.load_json(work/'config.json')\nvol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\nif cfg.get('COMPUTE_CT_RECONSTRUCTION', True):\n    s,rec_full,rec_sparse=dl.xray_ct_projection_reconstruction(\n        vol, spacing,\n        n_angles=cfg.get('CT_RECON_N_ANGLES_FULL',180),\n        sparse_n_angles=cfg.get('CT_RECON_N_ANGLES_SPARSE',60),\n        add_poisson_noise=cfg.get('CT_RECON_ADD_POISSON_NOISE',False),\n        cpu_workers=max(1,int(cfg.get('CPU_WORKERS',32))//2))\n    _g=bool(cfg.get('ENABLE_GPU_ACCELERATION',True)); _ids=cfg.get('GPU_IDS',[0,1]); _gid=int(_ids[0]) if _ids else 0\n    thick_ct=dl.distance_thickness_descriptors(rec_full,spacing,use_gpu=_g,gpu_id=_gid)\n    s.update({f'ct_recon_{k}':v for k,v in thick_ct.items()})\n    dl.save_volume(work/'checkpoints'/'v4_ct_recon_full_angle.npz', rec_full, spacing, {'source_type':'ct_recon_full_angle'})\n    dl.save_json(s,work/'features'/'v4_05_ct_recon_fidelity.json')\n    print('CT reconstruction descriptors:',len(s))\nelse:\n    print('CT reconstruction skipped by config (COMPUTE_CT_RECONSTRUCTION=False)')\n","from pathlib import Path\nimport json, sys, numpy as np, pandas as pd\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); feat=work/'features'; merged={}\nfor p in sorted(feat.glob('*.json')):\n    d=dl.load_json(p)\n    for k,v in d.items():\n        if isinstance(v,(int,float,bool)) or v is None: merged[k]=v\nmeta=dl.load_json(work/'checkpoints'/'01_input_meta.json')\nmerged={'sample_id':Path(meta.get('source','sample')).stem,**merged}\npd.DataFrame([merged]).to_csv(feat/'descriptors_ALL.csv',index=False)\ncatalog=dl.descriptor_catalog_from_names([k for k in merged if k!='sample_id']); catalog.to_csv(feat/'descriptor_catalog.csv',index=False)\nqa=[]\nfor k,v in merged.items():\n    if k=='sample_id': continue\n    try: x=float(v); state='finite' if np.isfinite(x) else ('nan' if np.isnan(x) else 'inf')\n    except Exception: state='non_numeric'\n    qa.append({'descriptor':k,'state':state,'value':v})\npd.DataFrame(qa).to_csv(feat/'descriptor_QA.csv',index=False)\nprint('TOTAL DESCRIPTORS:',len(merged)-1)\nprint(pd.Series([r['state'] for r in qa]).value_counts())\ndisplay(pd.DataFrame([merged]).iloc[:,:20])",
"from pathlib import Path\nimport json, pandas as pd\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); records=[]\nfor p in sorted((work/'features').glob('*')):\n    rec={'file':p.name,'bytes':p.stat().st_size}\n    if p.suffix=='.json':\n        try: rec['feature_count']=len(json.loads(p.read_text(encoding='utf-8')))\n        except: pass\n    elif p.suffix=='.csv':\n        try: rec['rows'],rec['columns']=pd.read_csv(p).shape\n        except: pass\n    records.append(rec)\npd.DataFrame(records).to_csv(work/'run_manifest.csv',index=False)\ndisplay(pd.DataFrame(records))",
"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path('.').resolve()))\nimport descriptor_library as dl\nptr=Path('.architected_descriptor_active_workdir.txt'); work=Path(ptr.read_text(encoding='utf-8').strip()) if ptr.exists() else Path('descriptor_run'); vol,spacing,_=dl.load_volume(work/'checkpoints'/'02_volume_processed.npz')\ntrimesh_missing=False\ntry:\n    mesh=dl.marching_mesh(vol,spacing)\nexcept RuntimeError as e:\n    mesh=None; trimesh_missing=True; print('STL export skipped:',e)\nif mesh is not None:\n    path=work/'reconstructed_from_slices.stl'; mesh.export(path); print('saved',path,'faces=',len(mesh.faces))\nelif not trimesh_missing:\n    print('Reconstruction skipped: empty/full volume')",
]


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


def run_pipeline_for_one_input(input_path: Path, workdir: Path, config_overrides: dict,
                                log_fn=print):
    """Executes the embedded descriptor-extraction pipeline against ONE mesh/image-stack input,
    writing all outputs under `workdir` (checkpoints/, features/, images/, logs/). When
    config['SAVE_SLICE_IMAGES'] is True and the run succeeds, also dumps the processed
    slice volume as one PNG per slice under workdir/images/raw_slices/ (see
    save_raw_slice_images()). Returns (ok: bool, elapsed_sec: float, error_str_or_None).

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
    _save_images=bool(cfg.get('SAVE_SLICE_IMAGES',True))
    cfg['SAVE_RAW_SLICE_IMAGES']=_save_images
    cfg['SAVE_TRIPLET_IMAGES']=_save_images
    (workdir / 'config.json').write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding='utf-8')
    # The pipeline cells locate the active run via this pointer file, resolved relative to CWD.
    Path('.architected_descriptor_active_workdir.txt').write_text(str(workdir), encoding='utf-8')

    engine_dir = str(Path(__file__).resolve().parent)
    if engine_dir not in sys.path:
        sys.path.insert(0, engine_dir)  # so "import descriptor_library as dl" resolves regardless of CWD

    def _exec_step(idx):
        ns={'display': lambda *a, **k: None}
        exec(_PIPELINE_CELLS[idx],ns)
        return idx

    # Sequential prerequisites: environment, import/voxelization, preprocessing, grayscale-source prep.
    for idx in (0,1,2,17):
        try:
            _exec_step(idx)
        except Exception:
            err=f"pipeline step {idx} failed:\n{traceback.format_exc()}"
            log_fn(f"  [ERROR] {err}"); (workdir/'logs'/'error.txt').write_text(err,encoding='utf-8')
            return False,time.time()-t0,err

    descriptor_steps=list(range(3,17))+list(range(18,23))
    try:
        if cfg.get('ENABLE_PARALLEL_DESCRIPTOR_STAGES',True):
            # 3970X default: 16 concurrent descriptor families. CT itself uses the other half
            # of CPU_WORKERS across z slices, giving near-full 32-core occupancy without launching
            # 32 memory-heavy descriptor families at once.
            stage_workers=max(1,min(len(descriptor_steps),max(1,int(cfg.get('CPU_WORKERS',32))//2)))
            log_fn(f"  parallel descriptor stages: {stage_workers} workers (CPU_WORKERS={cfg.get('CPU_WORKERS')})")
            with ThreadPoolExecutor(max_workers=stage_workers,thread_name_prefix='descriptor') as ex:
                futs={ex.submit(_exec_step,idx):idx for idx in descriptor_steps}
                for fut in as_completed(futs):
                    idx=futs[fut]; fut.result(); log_fn(f"  descriptor step {idx} done")
        else:
            for idx in descriptor_steps: _exec_step(idx)
    except Exception:
        idx=locals().get('idx','parallel')
        err=f"pipeline descriptor step {idx} failed:\n{traceback.format_exc()}"
        log_fn(f"  [ERROR] {err}"); (workdir/'logs'/'error.txt').write_text(err,encoding='utf-8')
        return False,time.time()-t0,err

    # Aggregation/manifest/reconstructed STL must wait for every descriptor file.
    for idx in (23,24,25):
        try: _exec_step(idx)
        except Exception:
            err=f"pipeline step {idx} failed:\n{traceback.format_exc()}"
            log_fn(f"  [ERROR] {err}"); (workdir/'logs'/'error.txt').write_text(err,encoding='utf-8')
            return False,time.time()-t0,err

    if cfg.get('SAVE_RAW_SLICE_IMAGES'):
        try:
            save_raw_slice_images(workdir, stride=cfg.get('RAW_SLICE_IMAGE_STRIDE', 1),
                                   max_slices=cfg.get('MAX_RAW_SLICE_IMAGES', None))
        except Exception:
            log_fn(f"  [WARN] raw slice image export failed:\n{traceback.format_exc()}")

    return True, time.time() - t0, None


def save_raw_slice_images(workdir: Path, stride: int = 1, max_slices: int | None = None):
    """Dumps the actual post-processing binary slice volume as one PNG per slice under
    workdir/images/raw_slices/, so 'did this STL actually slice into something sane' can be
    checked by eye without opening the .npz checkpoint in code. Returns the number of PNGs
    written (0 if no checkpoint was found, e.g. the run failed before the volume-import step).
    max_slices=None means no image-count cap. Called automatically by run_pipeline_for_one_input() when SAVE_SLICE_IMAGES=True; can
    also be called directly against any already-completed workdir."""
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
        if max_slices is not None and n >= int(max_slices):
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
    pipeline's own aggregation step) plus checkpoints/01_input_meta.json (mesh-import
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
