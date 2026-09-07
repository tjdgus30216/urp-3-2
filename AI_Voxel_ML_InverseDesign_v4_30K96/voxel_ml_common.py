
from __future__ import annotations
from pathlib import Path
import json, os, hashlib, time, warnings, math
import numpy as np
import pandas as pd
import joblib
from dataclasses import dataclass

warnings.filterwarnings('ignore')
DEFAULT_BASE_DIR=Path(r"C:\Users\Administrator\Desktop\Minkyeom\AI-Voxel\Voxel generation")
DEFAULT_PROJECT_POINTER=DEFAULT_BASE_DIR/'.ai_voxel_ml_project.json'

def atomic_json(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str),encoding='utf-8'); os.replace(tmp,path); return path

def atomic_csv(df,path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp')
    df.to_csv(tmp,index=False,encoding='utf-8-sig'); os.replace(tmp,path); return path

def load_contract(pointer=None):
    pointer=Path(pointer or os.environ.get('AI_VOXEL_ML_PROJECT_POINTER',DEFAULT_PROJECT_POINTER))
    if not pointer.exists(): raise FileNotFoundError(f'ML project pointer missing: {pointer}. Run Dataset Factory v4 ML-export cell first.')
    c=json.loads(pointer.read_text(encoding='utf-8'))
    c['_pointer']=str(pointer); return c

def load_all_structures(contract=None):
    c=contract or load_contract(); p=Path(c['all_structures_csv'])
    if not p.exists(): raise FileNotFoundError(p)
    return pd.read_csv(p)

def stage_dir(root,name):
    p=Path(root)/'_stages';p.mkdir(parents=True,exist_ok=True);return p/f'{name}.json'

def mark_stage(root,name,status,outputs=None,meta=None):
    obj={'stage':name,'status':status,'time':time.strftime('%Y-%m-%dT%H:%M:%S'),'outputs':[str(x) for x in (outputs or [])],'meta':meta or {}}
    atomic_json(stage_dir(root,name),obj);return obj

def stage_done(root,name,outputs=()):
    p=stage_dir(root,name)
    if not p.exists():return False
    try:m=json.loads(p.read_text(encoding='utf-8'))
    except Exception:return False
    return m.get('status')=='completed' and all(Path(x).exists() for x in outputs)

def numeric_descriptor_columns(df,max_missing=0.25,min_std=1e-12):
    excluded_prefix=('gen__','latent__','meta__')
    out=[]
    for c in df.columns:
        if c=='sample_id' or c.startswith(excluded_prefix):continue
        s=pd.to_numeric(df[c],errors='coerce')
        if s.isna().mean()<=max_missing and s.notna().sum()>2 and float(s.std(skipna=True))>min_std:out.append(c)
    return out

def generator_feature_columns(df):
    # Seed/provenance and realized voxel counts are not inverse-design controls.
    allowed=[]
    for c in df.columns:
        if c.startswith('latent__'): allowed.append(c);continue
        if not c.startswith('gen__'):continue
        if c in {'gen__generator_type','gen__voxel_mode','gen__target_vf','gen__min_thickness_mm','gen__min_hole_size_mm','gen__max_thickness_mm','gen__closing_radius_mm','gen__opening_radius_mm','gen__connectivity_bridge_radius_mm','gen__contact_surface_depth_mm','gen__num_fourier_terms','gen__fourier_k_max','gen__anisotropy_z','gen__sigma_mm'}:
            allowed.append(c)
    # Fidelity is a controlled context, not a structural generator variable, but lets one model use screening+final data.
    if 'meta__fidelity' in df.columns: allowed.append('meta__fidelity')
    return allowed

def design_groups(df):
    if 'meta__design_id' in df: return df['meta__design_id'].fillna(df['sample_id']).astype(str).to_numpy()
    return df['sample_id'].astype(str).to_numpy()

def get_feature_bounds(df,features,q=(0.0,1.0)):
    out={}
    for c in features:
        if c in {'gen__generator_type','gen__voxel_mode','meta__fidelity'}:
            out[c]={'type':'categorical','values':sorted(df[c].dropna().astype(str).unique().tolist())};continue
        s=pd.to_numeric(df[c],errors='coerce').dropna()
        if len(s):out[c]={'type':'continuous','low':float(s.quantile(q[0])),'high':float(s.quantile(q[1]))}
    return out
