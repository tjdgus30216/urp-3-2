
from __future__ import annotations
from pathlib import Path
import numpy as np,pandas as pd,joblib,json,math
from scipy.optimize import differential_evolution
from scipy.stats import qmc
from gen2desc_model import predict_gen2desc
from compression_curve_model import predict_curve
from voxel_ml_common import atomic_csv,atomic_json

def _inv_cov(cov):
    cov=np.atleast_2d(np.asarray(cov,float));return np.linalg.pinv(cov+1e-6*np.eye(cov.shape[0]))
def mahal(z,mu,cov):
    z=np.asarray(z,float);d=z-np.asarray(mu,float);ic=_inv_cov(cov);return float(np.sqrt(max(d@ic@d,0)))

def _mahal_batch(Z,mu,cov):
    """Vectorized Mahalanobis distance for a batch of rows Z (S,d)."""
    Z=np.atleast_2d(np.asarray(Z,float));d=Z-np.asarray(mu,float)[None,:];ic=_inv_cov(cov)
    return np.sqrt(np.clip(np.einsum('ij,jk,ik->i',d,ic,d),0,None))

def performance_loss(pred_props,cols,target_spec,scales=None):
    p={c:float(v) for c,v in zip(cols,np.asarray(pred_props,float).reshape(-1))};loss=0.;parts={}
    for name,spec in target_spec.items():
        col=name if name.startswith('perf__') else 'perf__'+name
        if col not in p:continue
        v=p[col];w=float(spec.get('weight',1.0));mode=spec.get('mode','target');tar=spec.get('target',None);lo=spec.get('min',None);hi=spec.get('max',None);scale=float(spec.get('scale',scales.get(col,1.0) if scales else 1.0));scale=max(abs(scale),1e-9)
        e=0.
        if mode=='target' and tar is not None:e=((v-float(tar))/scale)**2
        elif mode=='maximize':e=-v/scale
        elif mode=='minimize':e=v/scale
        if lo is not None and v<float(lo):e+=((float(lo)-v)/scale)**2*4
        if hi is not None and v>float(hi):e+=((v-float(hi))/scale)**2*4
        parts[col]=e*w;loss+=e*w
    return float(loss),parts,p

# ---------------------------------------------------------------------------
# Differential evolution is run with SciPy's `vectorized=True` interface: every
# generation is scored in ONE batched call into the fitted RandomForest/ExtraTrees
# surrogates (which already parallelize their own tree predictions across every
# Threadripper core via n_jobs=-1) instead of one Python-level call per population
# member. This is deliberately NOT done with DE's own `workers=` multiprocessing
# option: that pickles the objective closure into separate worker *processes*,
# which is fragile from inside a Jupyter kernel on Windows (spawn start method)
# and would also double-parallelize on top of the surrogate models' own n_jobs=-1,
# oversubscribing the CPU. Batched/vectorized evaluation gets the same speedup
# safely and portably, and composes cleanly with a workstation shared with other
# jobs (no extra worker processes are ever spawned).
# ---------------------------------------------------------------------------

def optimize_descriptor_state(curve_bundle,target_spec,target_curve=None,curve_weight=0.0,uncertainty_weight=.15,ood_weight=.10,maxiter=180,popsize=18,seed=42):
    lo=np.asarray(curve_bundle['training_desc_latent_min'],float);hi=np.asarray(curve_bundle['training_desc_latent_max'],float);mu=curve_bundle['training_desc_latent_mean'];cov=curve_bundle['training_desc_latent_cov'];cols=curve_bundle['property_columns'];grid=curve_bundle['strain_grid']
    tc=np.asarray(target_curve,float) if target_curve is not None else None
    tc_pow=float(np.mean(tc**2)) if tc is not None else None
    ndim=len(lo)

    def batch_loss(Z):
        # Z: (S, ndim) -- one row per population member.
        pr=predict_curve(curve_bundle,Z)
        S=Z.shape[0]
        o=_mahal_batch(Z,mu,cov)/max(ndim**.5,1)
        loss=np.empty(S,float)
        for i in range(S):
            pl,_,_=performance_loss(pr['property_mean'][i],cols,target_spec)
            u=float(np.mean(pr['property_std'][i]))
            cl=0.
            if tc is not None and curve_weight>0:
                pc=pr['curve_mean'][i];cl=float(np.mean((pc-tc)**2))/max(tc_pow,1e-9)
            loss[i]=pl+uncertainty_weight*u+ood_weight*max(o[i]-2.5,0)**2+curve_weight*cl
        return loss

    def obj_vectorized(Zt):
        # SciPy's vectorized convention hands parameters as rows, population as columns.
        return batch_loss(np.asarray(Zt,float).T)

    res=differential_evolution(obj_vectorized,list(zip(lo,hi)),seed=seed,maxiter=maxiter,popsize=popsize,polish=True,updating='deferred',vectorized=True)
    z=res.x;pr=predict_curve(curve_bundle,z[None,:]);loss,parts,p=performance_loss(pr['property_mean'][0],cols,target_spec)
    return {'z':z,'objective':float(res.fun),'performance_loss':loss,'property_prediction':p,'property_std':{c:float(v) for c,v in zip(cols,pr['property_std'][0])},'curve':pr['curve_mean'][0],'curve_std':pr['curve_std'][0],'strain_grid':grid,'ood_mahalanobis':mahal(z,mu,cov),'success':bool(res.success),'message':str(res.message)}

def _decode_generator_vector(x,template,bounds,features):
    row=dict(template);i=0
    for c in features:
        b=bounds[c]
        if b['type']=='categorical':continue
        v=float(x[i]);i+=1
        if c in {'gen__num_fourier_terms','gen__fourier_k_max'}:v=int(round(v))
        row[c]=v
    return row

def _decode_generator_vectors_batch(X,template,bounds,features):
    """Decode a whole DE population (S, n_continuous) into one DataFrame in a single
    Python-level loop over rows (cheap dict-building only, no model calls) so the
    downstream surrogate predict() calls can run as one batched call."""
    return pd.DataFrame([_decode_generator_vector(x,template,bounds,features) for x in X])

def _to_model_row(row,features,fidelity='final'):
    out={}
    for c in features:
        if c=='meta__fidelity':out[c]=fidelity
        else:out[c]=row.get(c,np.nan)
    return pd.DataFrame([out])

def _to_model_rows_batch(df_rows,features,fidelity='final'):
    out=df_rows.reindex(columns=[c for c in features if c!='meta__fidelity'])
    if 'meta__fidelity' in features:out['meta__fidelity']=fidelity
    return out.reindex(columns=features)

def optimize_generator_for_descriptor(gen_bundle,curve_bundle,target_z,target_spec,generator_family,descriptor_weight=1.0,performance_weight=.7,uncertainty_weight=.12,ood_weight=.08,maxiter=150,popsize=15,seed=42,target_curve=None,curve_weight=0.0):
    features=gen_bundle['generator_features'];bounds=gen_bundle['feature_bounds'];continuous=[c for c in features if c in bounds and bounds[c]['type']=='continuous'];template={c:np.nan for c in features};template['gen__generator_type']='voxel';template['gen__voxel_mode']=generator_family;template['meta__fidelity']='final'
    bnds=[(bounds[c]['low'],bounds[c]['high']) for c in continuous]
    t=np.asarray(target_z,float);mu=gen_bundle['training_latent_mean'];cov=gen_bundle['training_latent_cov']
    denom=np.maximum(gen_bundle['training_latent_max']-gen_bundle['training_latent_min'],1e-9)
    tc=np.asarray(target_curve,float) if target_curve is not None else None
    tc_pow=float(np.mean(tc**2)) if tc is not None else None
    zdim=len(mu)

    def batch_obj(X):
        # X: (S, n_continuous)
        rows=_decode_generator_vectors_batch(X,template,bounds,continuous)
        df=_to_model_rows_batch(rows,features)
        g=predict_gen2desc(gen_bundle,df,False)
        Z=g['latent_mean']
        du=np.mean(g['latent_std'],axis=1)
        dl=np.mean(((Z-t)/denom)**2,axis=1)
        cp=predict_curve(curve_bundle,Z)
        o=_mahal_batch(Z,mu,cov)/max(zdim**.5,1)
        S=len(X);loss=np.empty(S,float)
        for i in range(S):
            pl,_,_=performance_loss(cp['property_mean'][i],curve_bundle['property_columns'],target_spec)
            cl=0.
            if tc is not None and curve_weight>0:
                pc=cp['curve_mean'][i];cl=float(np.mean((pc-tc)**2))/max(tc_pow,1e-9)
            u=du[i]+float(np.mean(cp['property_std'][i]))
            loss[i]=descriptor_weight*dl[i]+performance_weight*pl+curve_weight*cl+uncertainty_weight*u+ood_weight*max(o[i]-2.5,0)**2
        return loss

    def obj_vectorized(Xt):
        return batch_obj(np.asarray(Xt,float).T)

    res=differential_evolution(obj_vectorized,bnds,seed=seed,maxiter=maxiter,popsize=popsize,polish=True,updating='deferred',vectorized=True)
    row=_decode_generator_vector(res.x,template,bounds,continuous);df=_to_model_row(row,features);g=predict_gen2desc(gen_bundle,df,True);z=g['latent_mean'][0];cp=predict_curve(curve_bundle,z[None,:]);pl,parts,p=performance_loss(cp['property_mean'][0],curve_bundle['property_columns'],target_spec)
    return {'row':row,'descriptor_latent':z,'descriptor_std':g['latent_std'][0],'descriptor_raw':g['descriptor_raw_mean'].iloc[0].to_dict(),'property_prediction':p,'property_std':{c:float(v) for c,v in zip(curve_bundle['property_columns'],cp['property_std'][0])},'curve':cp['curve_mean'][0],'curve_std':cp['curve_std'][0],'objective':float(res.fun),'performance_loss':pl,'success':bool(res.success)}

def pareto_front_mask(objectives):
    """objectives: (n, k) array-like, lower-is-better on every column.
    Returns a boolean mask marking the non-dominated (Pareto-optimal) rows: a row is
    dominated when some other row is at least as good on every objective and strictly
    better on at least one. This is the "Pareto/diversity" alternative-candidate concept
    referenced by the v19-derived optimizer philosophy, made concrete instead of only
    ever collapsing every candidate to one weighted scalar objective."""
    obj=np.atleast_2d(np.asarray(objectives,float))
    n=len(obj);dominated=np.zeros(n,dtype=bool)
    for i in range(n):
        if dominated[i]:continue
        le=np.all(obj<=obj[i],axis=1);lt=np.any(obj<obj[i],axis=1)
        beats=le&lt
        beats[i]=False
        if beats.any():dominated[i]=True
    return ~dominated

def run_hierarchical_inverse(gen_bundle,curve_bundle,target_spec,out_dir,generator_families=('latent_periodic_isotropic','latent_periodic_orthotropic','latent_stochastic'),n_descriptor_targets=3,seed=42,target_curve=None,curve_weight=0.0,descriptor_maxiter=180,descriptor_popsize=18,generator_maxiter=150,generator_popsize=15):
    """Runs the two-stage inverse optimizer. `descriptor_*`/`generator_*` control the
    differential-evolution search effort for each stage; the batched/vectorized surrogate
    evaluation (see optimize_descriptor_state/optimize_generator_for_descriptor) makes both
    stages CPU-cheap enough that raising these from a notebook is now practical when a
    higher-fidelity search is wanted, not just left at the historical defaults."""
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    # Generate several descriptor optima by jittered seeds; preserve alternatives for Pareto/diversity.
    desc=[]
    for i in range(int(n_descriptor_targets)):
        d=optimize_descriptor_state(curve_bundle,target_spec,target_curve=target_curve,curve_weight=curve_weight,maxiter=descriptor_maxiter,popsize=descriptor_popsize,seed=seed+101*i);d['rank_seed']=i;desc.append(d)
    desc=sorted(desc,key=lambda x:x['objective']);
    drows=[]
    for i,d in enumerate(desc,1):
        rr={'descriptor_target_rank':i,'objective':d['objective'],'ood_mahalanobis':d['ood_mahalanobis'],**d['property_prediction']}
        for j,v in enumerate(d['z']):rr[f'desc_latent_{j+1:02d}']=v
        drows.append(rr)
    atomic_csv(pd.DataFrame(drows),out/'optimized_descriptor_states.csv')
    raw=gen_bundle['descriptor_encoder'].inverse_transform(np.vstack([d['z'] for d in desc]));raw.insert(0,'descriptor_target_rank',np.arange(1,len(raw)+1));atomic_csv(raw,out/'optimized_raw_structural_descriptors.csv')
    grows=[];curves=[]
    for di,d in enumerate(desc):
        for fi,fam in enumerate(generator_families):
            g=optimize_generator_for_descriptor(gen_bundle,curve_bundle,d['z'],target_spec,fam,maxiter=generator_maxiter,popsize=generator_popsize,seed=seed+1000*di+31*fi,target_curve=target_curve,curve_weight=curve_weight)
            r={'candidate_id':f'INV_D{di+1:02d}_{fam}_{fi+1:02d}','generator_type':'voxel','voxel_mode':fam,'generator_version':'v4_latent_controlled','sampling_method':'inverse_design','design_id':'','realization_id':'','seed':int(seed+1000*di+31*fi),'size_mm':30.0,'strict_global_symmetry':('periodic' in fam),'force_connected':True,'inverse_objective':g['objective'],'performance_loss':g['performance_loss']}
            # convert gen__ model names back to DatasetFactory import names
            for k,v in g['row'].items():
                if k.startswith('gen__'):r[k[5:]]=v
                elif k.startswith('latent__'):r[k]=v
            for k,v in g['property_prediction'].items():r['pred__'+k]=v
            for k,v in g['property_std'].items():r['unc__'+k]=v
            grows.append(r);curves.append(pd.DataFrame({'candidate_id':r['candidate_id'],'strain':curve_bundle['strain_grid'],'predicted_stress':g['curve'],'predicted_std':g['curve_std']}))
    gdf=pd.DataFrame(grows)
    # Two-objective Pareto front (performance fit vs. predicted uncertainty): surfaces the
    # genuinely non-dominated candidates -- e.g. a slightly worse fit that is much more
    # confidently predicted -- instead of collapsing every trade-off into one scalar rank.
    unc_cols=[c for c in gdf.columns if c.startswith('unc__')]
    mean_unc=gdf[unc_cols].mean(axis=1) if unc_cols else pd.Series(0.0,index=gdf.index)
    gdf['mean_predicted_uncertainty']=mean_unc.to_numpy(float)
    gdf['pareto_optimal']=pareto_front_mask(gdf[['performance_loss','mean_predicted_uncertainty']].to_numpy(float))
    gdf=gdf.sort_values(['pareto_optimal','performance_loss','inverse_objective'],ascending=[False,True,True]).reset_index(drop=True)
    atomic_csv(gdf,out/'optimized_generator_parameters.csv');
    if curves:atomic_csv(pd.concat(curves,ignore_index=True),out/'optimized_predicted_curves.csv')
    atomic_json(out/'inverse_manifest.json',{'target_spec':target_spec,'target_curve_weight':float(curve_weight),'generator_families':list(generator_families),'pareto_optimal_candidates':int(gdf['pareto_optimal'].sum()),'recommended_candidate_file':str(out/'optimized_generator_parameters.csv'),'note':'Set DatasetFactory CANDIDATE_SOURCE=inverse_design and INVERSE_DESIGN_CANDIDATE_FILE to this CSV. Rows are ranked Pareto-optimal first, then by performance_loss: prefer pareto_optimal=True candidates when picking a diverse manufacturing batch instead of only row 1.'})
    return gdf,pd.DataFrame(drows)
