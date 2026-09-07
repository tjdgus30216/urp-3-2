
from __future__ import annotations
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import qmc
from gen2desc_model import predict_gen2desc
from compression_curve_model import predict_curve
from inverse_design_engine import performance_loss,mahal
from voxel_ml_common import atomic_csv,atomic_json

def _sample_space(gen_bundle,n,seed=42):
    f=gen_bundle['generator_features'];b=gen_bundle['feature_bounds'];cont=[c for c in f if c in b and b[c]['type']=='continuous'];cats=[c for c in f if c in b and b[c]['type']=='categorical'];U=qmc.Sobol(d=len(cont),scramble=True,seed=seed).random_base2(int(np.ceil(np.log2(max(n,2)))))[:n];rows=[]
    fams=b.get('gen__voxel_mode',{}).get('values',['latent_periodic_isotropic','latent_periodic_orthotropic','latent_stochastic']);fams=[x for x in fams if str(x).startswith('latent_')] or fams
    for i,u in enumerate(U):
        r={'gen__generator_type':'voxel','gen__voxel_mode':fams[i%len(fams)],'meta__fidelity':'final'}
        for j,c in enumerate(cont):r[c]=b[c]['low']+u[j]*(b[c]['high']-b[c]['low'])
        rows.append(r)
    return pd.DataFrame(rows),cont

def _maximin(points,scores,n):
    P=np.asarray(points,float);scores=np.asarray(scores,float);sel=[int(np.argmax(scores))];mind=np.linalg.norm(P-P[sel[0]],axis=1)
    for _ in range(1,min(n,len(P))):
        s=(scores-scores.min())/(np.ptp(scores)+1e-12);d=(mind-mind.min())/(np.ptp(mind)+1e-12);idx=int(np.argmax(.60*s+.40*d));sel.append(idx);mind=np.minimum(mind,np.linalg.norm(P-P[idx],axis=1));mind[sel]=-np.inf
    return sel

def propose_active_samples(gen_bundle,curve_bundle,target_spec,out_dir,n_virtual=4096,n_select=16,seed=42,weights=None):
    weights=weights or {'performance':.40,'uncertainty':.35,'novelty':.25};out=Path(out_dir);out.mkdir(parents=True,exist_ok=True);pool,cont=_sample_space(gen_bundle,n_virtual,seed);g=predict_gen2desc(gen_bundle,pool,False);Z=g['latent_mean'];du=np.mean(g['latent_std'],axis=1);cp=predict_curve(curve_bundle,Z);pu=np.mean(cp['property_std'],axis=1);perf=[]
    for p in cp['property_mean']:perf.append(-performance_loss(p,curve_bundle['property_columns'],target_spec)[0])
    perf=np.asarray(perf,float);mu=gen_bundle['training_latent_mean'];cov=gen_bundle['training_latent_cov'];nov=np.asarray([mahal(z,mu,cov) for z in Z]);
    def n01(x):x=np.asarray(x,float);return (x-np.nanmin(x))/(np.nanmax(x)-np.nanmin(x)+1e-12)
    acq=weights['performance']*n01(perf)+weights['uncertainty']*n01(du+pu)+weights['novelty']*n01(np.minimum(nov,4.0));sel=_maximin(Z,acq,n_select);q=pool.iloc[sel].copy();q['acquisition_score']=acq[sel];q['pred_uncertainty']=du[sel]+pu[sel];q['descriptor_novelty_mahal']=nov[sel]
    # DatasetFactory import names
    outrows=[]
    for rank,(_,r) in enumerate(q.sort_values('acquisition_score',ascending=False).iterrows(),1):
        o={'candidate_id':f'AL_{seed}_{rank:03d}','generator_type':'voxel','voxel_mode':r['gen__voxel_mode'],'generator_version':'v4_latent_controlled','sampling_method':'active_sampling','seed':int(seed+rank),'size_mm':30.0,'strict_global_symmetry':('periodic' in str(r['gen__voxel_mode'])),'force_connected':True,'acquisition_score':r['acquisition_score'],'pred_uncertainty':r['pred_uncertainty'],'descriptor_novelty_mahal':r['descriptor_novelty_mahal']}
        for c in cont:
            key=c[5:] if c.startswith('gen__') else c;v=r[c];v=int(round(v)) if key in {'num_fourier_terms','fourier_k_max'} else v;o[key]=v
        outrows.append(o)
    odf=pd.DataFrame(outrows);atomic_csv(odf,out/'active_sampling_generator_parameters.csv');atomic_json(out/'active_sampling_manifest.json',{'n_virtual':n_virtual,'n_select':n_select,'weights':weights,'candidate_file':str(out/'active_sampling_generator_parameters.csv'),'note':'Use DatasetFactory CANDIDATE_SOURCE=active_sampling.'});return odf
