
from __future__ import annotations
from pathlib import Path
from collections import Counter
import re, math, json
import numpy as np, pandas as pd, joblib
from scipy.signal import savgol_filter, find_peaks
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, GradientBoostingRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score,mean_squared_error
from voxel_ml_common import atomic_csv,atomic_json

# numpy>=2.0 renamed trapz->trapezoid and dropped the old alias entirely (mirrors the
# same compatibility shim in descriptor_library.py) -- np.trapz raises AttributeError
# on a fresh numpy 2.x install otherwise, breaking every compression-curve property.
_trapz=getattr(np,'trapezoid',None) or np.trapz

# Defaults intentionally follow the attached MEvoLattice v22 philosophy: event-aware curve processing.
ELASTIC_FIT_MAX_STRAIN=0.02; OFFSET_STRAIN=0.002; PLATEAU_RANGE=(0.20,0.40)
DENSIFICATION_SEARCH_MIN_STRAIN=0.20; DENSIFICATION_END_MARGIN=0.02


def _norm(s):return re.sub(r'[^A-Z0-9]+','',str(s).upper())
def _generic(s):return _norm(s) in {'','COMSTRAIN','STRAIN','STRESS','LCC','SE','ENGINEERINGSTRAIN','ENGINEERINGSTRESS'}

def load_canonical_long(path):
    p=Path(path)
    df=pd.read_csv(p) if p.suffix.lower()=='.csv' else pd.read_excel(p)
    req={'design_id','strain','stress_MPa'}
    if not req.issubset(df.columns):raise ValueError(f'Canonical compression file requires {req}')
    if 'specimen_id' not in df:df['specimen_id']=df['design_id'].astype(str)
    if 'replicate_id' not in df:df['replicate_id']=0
    curves=[]
    for (sid,did,rid),g in df.groupby(['specimen_id','design_id','replicate_id'],dropna=False):
        curves.append({'specimen_id':str(sid),'design_id':str(did),'replicate_id':str(rid),'strain':pd.to_numeric(g['strain'],errors='coerce').to_numpy(),'stress':pd.to_numeric(g['stress_MPa'],errors='coerce').to_numpy(),'source_file':p.name})
    return curves


def _numeric_pair_quality(raw,sc,tc,min_points=12):
    if sc>=raw.shape[1] or tc>=raw.shape[1]:return -1,None
    xs=pd.to_numeric(raw.iloc[:,sc],errors='coerce');ys=pd.to_numeric(raw.iloc[:,tc],errors='coerce');m=xs.notna()&ys.notna()
    if m.sum()<min_points:return -1,None
    x=xs[m].to_numpy(float);y=ys[m].to_numpy(float);span=float(np.nanmax(x)-np.nanmin(x));mono=float(np.mean(np.diff(x)>=-1e-10)) if len(x)>1 else 0
    q=(m.sum()/max(len(raw),1))*2 + (1 if span>0 else 0)+(1 if mono>.85 else 0)+(1 if np.nanmax(np.abs(y))>0 else 0)
    return q,{'x':x,'y':y}

def load_legacy_v22_excel_folder(folder,group_width=5,strain_offset=2,stress_offset=3,min_points=12):
    """Adapter for the attached v22 layout: scans every sheet and 5-column blocks; C-D/H-I/... preferred."""
    folder=Path(folder);files=sorted([p for p in folder.glob('*.xlsx') if not p.name.startswith('~$')]);curves=[];counter=Counter()
    for p in files:
        xls=pd.ExcelFile(p,engine='openpyxl')
        for so,sheet in enumerate(xls.sheet_names):
            raw=pd.read_excel(p,sheet_name=sheet,header=None,engine='openpyxl');max_col=raw.shape[1]
            for bo,start in enumerate(range(0,max_col,group_width)):
                cand=[(start+strain_offset,start+stress_offset)]+[(c,c+1) for c in range(start,min(start+group_width-1,max_col-1))]
                scored=[]
                for sc,tc in cand:
                    q,pi=_numeric_pair_quality(raw,sc,tc,min_points)
                    if pi is not None:
                        if (sc,tc)==(start+strain_offset,start+stress_offset):q+=1.5
                        scored.append((q,sc,tc,pi))
                if not scored:continue
                q,sc,tc,pi=max(scored,key=lambda z:z[0])
                if q<3:continue
                # name preference: first non-generic text in the local block, then sheet, then file stem.
                texts=[]
                for rr in range(min(8,raw.shape[0])):
                    for cc in range(start,min(start+group_width,raw.shape[1])):
                        v=raw.iat[rr,cc]
                        if isinstance(v,str) and not _generic(v):texts.append(v.strip())
                name=texts[0] if texts else (sheet if not _generic(sheet) else p.stem)
                rid=counter[name];counter[name]+=1
                x=np.asarray(pi['x'],float);y=np.asarray(pi['y'],float);m=np.isfinite(x)&np.isfinite(y)&(x>=0);x=x[m];y=y[m]
                if len(x)<min_points:continue
                if np.nanpercentile(x,95)>2 and np.nanpercentile(x,95)<=100:x=x*0.01
                curves.append({'specimen_id':f'{name}__r{rid+1}','design_id':str(name),'replicate_id':str(rid),'strain':x,'stress':y,'source_file':p.name,'source_sheet':sheet})
    return curves


def preprocess_curve(x,y,grid,smooth=True):
    d=pd.DataFrame({'x':x,'y':y}).replace([np.inf,-np.inf],np.nan).dropna();d=d[d.x>=0].groupby('x',as_index=False).y.mean().sort_values('x')
    x=d.x.to_numpy(float);y=np.maximum(d.y.to_numpy(float),0)
    if smooth and len(y)>=7:
        w=min(11,len(y) if len(y)%2 else len(y)-1)
        if w>=5:y=savgol_filter(y,w,min(3,w-2),mode='interp');y=np.maximum(y,0)
    mask=grid<=x.max()+1e-12;out=np.zeros_like(grid,float);out[mask]=np.interp(grid[mask],x,y)
    return out,mask.astype(float)

def densification_max_efficiency(x,y):
    x=np.asarray(x,float);y=np.maximum(np.asarray(y,float),0);W=np.zeros_like(y)
    if len(y)>1:W[1:]=np.cumsum(.5*(y[1:]+y[:-1])*np.diff(x))
    floor=max(.02*max(float(np.max(y)),1e-12),1e-12);eta=np.where(y>floor,W/y,np.nan)
    search=(x>=DENSIFICATION_SEARCH_MIN_STRAIN)&(x<=x[-1]-DENSIFICATION_END_MARGIN)&np.isfinite(eta)
    if not search.any():return float(x[-1])
    e=eta.copy(); fin=np.isfinite(e)
    if fin.sum()>=5:
        vv=np.interp(np.arange(len(e)),np.where(fin)[0],e[fin]);w=min(11,len(vv) if len(vv)%2 else len(vv)-1)
        if w>=5:vv=savgol_filter(vv,w,min(3,w-2),mode='interp')
        e[fin]=vv[fin]
    ids=np.where(search)[0];return float(x[ids[np.nanargmax(e[ids])]])

def densification_stiffness(x,y):
    x=np.asarray(x,float);y=np.maximum(np.asarray(y,float),0);ys=y.copy();w=min(11,len(y) if len(y)%2 else len(y)-1)
    if w>=5:ys=savgol_filter(ys,w,min(3,w-2),mode='interp');ys=np.maximum(ys,0)
    dy=np.gradient(ys,x);pm=(x>=PLATEAU_RANGE[0])&(x<=PLATEAU_RANGE[1]);p=float(np.nanmedian(ys[pm])) if pm.sum() else float(np.nanmedian(ys))
    ids=np.where((x>=DENSIFICATION_SEARCH_MIN_STRAIN)&(ys>=1.3*p)&(dy>np.nanpercentile(dy[x>=DENSIFICATION_SEARCH_MIN_STRAIN],60)))[0]
    return float(x[ids[0]]) if len(ids) else float(x[np.argmax(dy)])

def integrate_to(x,y,e):
    e=float(np.clip(e,x[0],x[-1]));ids=x<e;xx=x[ids];yy=y[ids];xx=np.r_[xx,e];yy=np.r_[yy,np.interp(e,x,y)]
    return float(_trapz(yy,xx)) if len(xx)>1 else 0.0

def extract_curve_properties(strain,stress,mask=None):
    x=np.asarray(strain,float);y=np.maximum(np.asarray(stress,float),0);valid=np.isfinite(x)&np.isfinite(y)
    if mask is not None:valid&=np.asarray(mask)>0.5
    x=x[valid];y=y[valid]
    if len(x)<6:return {}
    elastic=(x>=0)&(x<=min(ELASTIC_FIT_MAX_STRAIN,x.max()));E=max(float(stats.theilslopes(y[elastic],x[elastic])[0]),0) if elastic.sum()>=3 else max(float((y[1]-y[0])/max(x[1]-x[0],1e-12)),0)
    off=E*(x-OFFSET_STRAIN);diff=y-off;iy=None
    for i in np.where(x>=OFFSET_STRAIN)[0][:-1]:
        if diff[i]>=0 and diff[i+1]<0:iy=i;break
    if iy is None:iy=int(np.argmax(y))
    ey=float(x[iy]);sy=float(y[iy]);ed1=densification_max_efficiency(x,y);ed2=densification_stiffness(x,y);ed=float(np.median([ed1,ed2]));ed=float(x[np.argmin(abs(x-ed))])
    before=x<=ed;ip=int(np.where(before)[0][np.argmax(y[before])]) if before.any() else int(np.argmax(y));peak=float(y[ip])
    plo,phi=PLATEAU_RANGE;pm=(x>=plo)&(x<=min(phi,ed));
    if pm.sum()<3:pm=(x>=max(ey,.1))&(x<=max(ed,ey+.05))
    plat=float(np.mean(y[pm])) if pm.any() else np.nan;energy=integrate_to(x,y,ed);cfe=plat/max(peak,1e-12) if np.isfinite(plat) else np.nan
    return {'modulus':E,'yield_strain':ey,'yield_stress':sy,'peak_stress':peak,'compressive_stress':peak,'plateau_stress':plat,'densification_strain':ed,'absorbed_energy_to_densification':energy,'energy_density':energy,'cfe':cfe}

class CurveEncoder:
    def __init__(self,var=0.997,max_components=24):self.var=var;self.max_components=max_components
    def fit(self,Y):
        self.scaler=StandardScaler().fit(Y);Ys=self.scaler.transform(Y);p=PCA().fit(Ys);n=int(np.searchsorted(np.cumsum(p.explained_variance_ratio_),self.var)+1);n=max(1,min(n,self.max_components,Y.shape[0]-1,Y.shape[1]));self.pca=PCA(n_components=n,random_state=42).fit(Ys);return self
    def transform(self,Y):return self.pca.transform(self.scaler.transform(Y))
    def inverse_transform(self,Z):return np.maximum(self.scaler.inverse_transform(self.pca.inverse_transform(Z)),0)


def _curve_models(seed=42,n_jobs=-1):
    return {'ExtraTrees':ExtraTreesRegressor(n_estimators=600,min_samples_leaf=2,max_features=.85,n_jobs=n_jobs,random_state=seed),'RandomForest':RandomForestRegressor(n_estimators=500,min_samples_leaf=2,max_features=.85,n_jobs=n_jobs,random_state=seed+1)}

def _property_models(seed=42,n_jobs=-1):
    return {'ExtraTrees':ExtraTreesRegressor(n_estimators=500,min_samples_leaf=2,max_features=.85,n_jobs=n_jobs,random_state=seed+10),'RandomForest':RandomForestRegressor(n_estimators=450,min_samples_leaf=2,max_features=.85,n_jobs=n_jobs,random_state=seed+11)}

def build_curve_dataset(curves,all_structures,gen2desc_bundle,grid_points=301,grid_max=None,prefer_final=True):
    # Map experiment design_id -> highest fidelity available descriptor state.
    s=all_structures.copy();s['_fid_rank']=s.get('meta__fidelity','screening').astype(str).map({'final':2,'screening':1}).fillna(0)
    dmap={}
    for did,g in s.groupby(s.get('meta__design_id',s['sample_id']).astype(str)):
        r=g.sort_values('_fid_rank',ascending=False).iloc[0] if prefer_final else g.iloc[0];dmap[str(did)]=r
    # fall back sample_id mapping too
    for _,r in s.iterrows():dmap.setdefault(str(r['sample_id']),r)
    valid=[]
    for c in curves:
        if str(c['design_id']) in dmap:valid.append((c,dmap[str(c['design_id'])]))
    if not valid:raise RuntimeError('No compression curves matched ML registry design_id/sample_id.')
    mx=[np.nanmax(c['strain']) for c,_ in valid]
    gmax=float(grid_max) if grid_max is not None else float(np.nanpercentile(mx,90));grid=np.linspace(0,gmax,int(grid_points))
    rows=[];Y=[];M=[]
    enc=gen2desc_bundle['descriptor_encoder']
    for c,r in valid:
        yy,mm=preprocess_curve(c['strain'],c['stress'],grid);raw=pd.DataFrame([r]).reindex(columns=enc.columns);z=enc.transform(raw)[0]
        row={'specimen_id':c['specimen_id'],'design_id':str(c['design_id']),'replicate_id':str(c.get('replicate_id',0)),'sample_id':str(r['sample_id']),'fidelity':str(r.get('meta__fidelity','unknown'))}
        for j,v in enumerate(z):row[f'desc_latent_{j+1:02d}']=float(v)
        p=extract_curve_properties(grid,yy,mm)
        for k,v in p.items():row[f'perf__{k}']=v
        rows.append(row);Y.append(yy);M.append(mm)
    return pd.DataFrame(rows),np.asarray(Y,float),np.asarray(M,float),grid

def train_curve_model(table,Y,M,grid,out_dir,cv_splits=5,seed=42,n_jobs=-1):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True);feat=[c for c in table if c.startswith('desc_latent_')];X=table[feat].to_numpy(float);groups=table['design_id'].astype(str).to_numpy()
    enc=CurveEncoder().fit(Y);Z=enc.transform(Y);ng=max(2,min(cv_splits,len(np.unique(groups))));gkf=GroupKFold(ng)
    metrics=[];oof_by={}
    for name,base in _curve_models(seed,n_jobs).items():
        po=np.full_like(Z,np.nan)
        for tr,te in gkf.split(X,Z,groups):
            m=base.__class__(**base.get_params());m.fit(X[tr],Z[tr]);_pz=np.asarray(m.predict(X[te]),float);_pz=_pz[:,None] if _pz.ndim==1 else _pz;po[te]=_pz
        yc=enc.inverse_transform(po);r2=float(r2_score(Y,yc,multioutput='variance_weighted'));rmse=float(np.sqrt(mean_squared_error(Y,yc)));metrics.append({'model':name,'curve_r2':r2,'curve_rmse':rmse});oof_by[name]=yc
    mdf=pd.DataFrame(metrics).sort_values(['curve_r2','curve_rmse'],ascending=[False,True]);best=str(mdf.iloc[0].model)
    fitted={};
    for name,m in _curve_models(seed,n_jobs).items():m.fit(X,Z);fitted[name]=m
    pcols=[c for c in table if c.startswith('perf__') and c not in {'perf__yield_strain'}];P=table[pcols].apply(pd.to_numeric,errors='coerce').to_numpy(float)
    # Median-impute property targets for stable multioutput trees; mask statistics are retained.
    pmed=np.nanmedian(P,axis=0);P2=P.copy();bad=np.where(~np.isfinite(P2));P2[bad]=pmed[bad[1]]
    pfitted={};pmetrics=[];poof={}
    for name,m in _property_models(seed,n_jobs).items():
        pred=np.full_like(P2,np.nan)
        for tr,te in gkf.split(X,P2,groups):
            mm=m.__class__(**m.get_params());mm.fit(X[tr],P2[tr]);pred[te]=mm.predict(X[te])
        pmetrics.append({'model':name,'property_r2':float(r2_score(P2,pred,multioutput='variance_weighted')),'property_rmse':float(np.sqrt(mean_squared_error(P2,pred)))});poof[name]=pred;m.fit(X,P2);pfitted[name]=m
    pdf=pd.DataFrame(pmetrics).sort_values(['property_r2','property_rmse'],ascending=[False,True]);pbest=str(pdf.iloc[0].model)
    # conformal-ish uncertainty calibration from ensemble best OOF residuals
    curve_oof=oof_by[best];point_abs=np.abs(Y-curve_oof);point_radius=np.nanquantile(point_abs,.90,axis=0);sim_radius=float(np.nanquantile(np.nanmax(point_abs,axis=1),.90))
    # Inverse-CV-RMSE ensemble weights (mirrors gen2desc_model): predictions are blended by
    # how well each model actually generalized in group-safe CV rather than a plain average.
    cw=mdf.set_index('model')['curve_rmse'].apply(lambda r: 1.0/max(float(r),1e-9)); curve_model_weights={k:float(v) for k,v in (cw/cw.sum()).items()}
    pw=pdf.set_index('model')['property_rmse'].apply(lambda r: 1.0/max(float(r),1e-9)); property_model_weights={k:float(v) for k,v in (pw/pw.sum()).items()}
    bundle={'version':'desc2curve-v1','feature_columns':feat,'curve_encoder':enc,'curve_models':fitted,'curve_model_weights':curve_model_weights,'best_curve_model':best,'property_models':pfitted,'property_model_weights':property_model_weights,'best_property_model':pbest,'property_columns':pcols,'property_medians':pmed,'strain_grid':grid,'pointwise_conformal_radius':point_radius,'simultaneous_conformal_radius':sim_radius,'training_desc_latent_min':X.min(0),'training_desc_latent_max':X.max(0),'training_desc_latent_mean':X.mean(0),'training_desc_latent_cov':np.cov(X.T) if X.shape[1]>1 else np.array([[np.var(X[:,0])]]),'training_property_min':np.nanmin(P2,axis=0),'training_property_max':np.nanmax(P2,axis=0),'training_property_median':np.nanmedian(P2,axis=0),'training_rows':len(X)}
    joblib.dump(bundle,out/'desc2curve_bundle.joblib',compress=3);atomic_csv(mdf,out/'curve_cv_metrics.csv');atomic_csv(pdf,out/'property_cv_metrics.csv');atomic_csv(table,out/'compression_training_table.csv')
    pd.DataFrame(Y,columns=[f'{v:.6f}' for v in grid]).assign(specimen_id=table.specimen_id.values).to_csv(out/'processed_curves.csv',index=False,encoding='utf-8-sig')
    np.savez_compressed(out/'oof_curve_best.npz',Y_true=Y,Y_pred=curve_oof,grid=grid,specimen_id=table.specimen_id.astype(str).to_numpy())
    _pp=poof[pbest]; _prows=[]
    for i in range(len(table)):
        rr={'specimen_id':table.iloc[i]['specimen_id'],'design_id':table.iloc[i]['design_id']}
        for j,c in enumerate(pcols): rr[c+'__true']=P2[i,j]; rr[c+'__pred']=_pp[i,j]
        _prows.append(rr)
    atomic_csv(pd.DataFrame(_prows),out/'oof_property_best.csv')
    atomic_json(out/'model_manifest.json',{'version':bundle['version'],'training_rows':len(X),'best_curve_model':best,'best_property_model':pbest,'curve_pca_dim':int(enc.pca.n_components_),'property_columns':pcols})
    return bundle,mdf,pdf

def _weights_for(bundle,key,names):
    w=bundle.get(key)
    if w:
        wv=np.asarray([float(w.get(n,0.0)) for n in names],float)
        if wv.sum()>0: return wv/wv.sum()
    return np.full(len(names),1.0/len(names))

def predict_curve(bundle,Z):
    X=np.asarray(Z,float);cnames=list(bundle['curve_models'].keys());pnames=list(bundle['property_models'].keys());cp=[];pp=[]
    for n in cnames:
        m=bundle['curve_models'][n]
        _z=np.asarray(m.predict(X),float);_z=_z[:,None] if _z.ndim==1 else _z;cp.append(bundle['curve_encoder'].inverse_transform(_z))
    for n in pnames:pp.append(bundle['property_models'][n].predict(X))
    C=np.stack(cp);P=np.stack(pp)
    cw=_weights_for(bundle,'curve_model_weights',cnames);pw=_weights_for(bundle,'property_model_weights',pnames)
    curve_mean=np.tensordot(cw,C,axes=(0,0));property_mean=np.tensordot(pw,P,axes=(0,0))
    return {'curve_mean':curve_mean,'curve_std':C.std(0),'property_mean':property_mean,'property_std':P.std(0),'property_columns':bundle['property_columns'],'strain_grid':bundle['strain_grid']}
