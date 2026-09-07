
from __future__ import annotations
import numpy as np, pandas as pd, joblib, json, math
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_squared_error
from voxel_ml_common import numeric_descriptor_columns,generator_feature_columns,design_groups,atomic_json,atomic_csv,get_feature_bounds

class DescriptorEncoder:
    def __init__(self,max_components=32,variance=0.985,corr_threshold=0.985):
        self.max_components=max_components;self.variance=variance;self.corr_threshold=corr_threshold
    def fit(self,df,cols):
        X=df[cols].apply(pd.to_numeric,errors='coerce')
        self.raw_columns=list(cols);self.medians=X.median().fillna(0.0)
        X=X.fillna(self.medians)
        # correlation prune, first-seen deterministic
        corr=X.corr().abs(); keep=[]
        for c in X.columns:
            if not keep or all((not np.isfinite(corr.loc[c,k])) or corr.loc[c,k]<self.corr_threshold for k in keep):keep.append(c)
        self.columns=keep; X=X[self.columns]
        self.scaler=RobustScaler(quantile_range=(5,95)).fit(X)
        Xs=self.scaler.transform(X)
        p0=PCA().fit(Xs); n=int(np.searchsorted(np.cumsum(p0.explained_variance_ratio_),self.variance)+1)
        n=max(1,min(n,self.max_components,Xs.shape[0]-1 if Xs.shape[0]>1 else 1,Xs.shape[1]))
        self.pca=PCA(n_components=n,random_state=42).fit(Xs);return self
    def transform(self,df):
        X=df.reindex(columns=self.columns).apply(pd.to_numeric,errors='coerce').fillna(self.medians.reindex(self.columns).fillna(0.0))
        return self.pca.transform(self.scaler.transform(X))
    def inverse_transform(self,Z):
        Xs=self.pca.inverse_transform(np.asarray(Z,float)); X=self.scaler.inverse_transform(Xs)
        return pd.DataFrame(X,columns=self.columns)
    @property
    def n_components_(self):return int(self.pca.n_components_)


def build_x_preprocessor(df,features):
    cats=[c for c in features if c in df and (df[c].dtype=='object' or c in {'gen__generator_type','gen__voxel_mode','meta__fidelity'})]
    nums=[c for c in features if c not in cats]
    pre=ColumnTransformer([
        ('num',Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums),
        ('cat',Pipeline([('imp',SimpleImputer(strategy='most_frequent')),('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cats),
    ],remainder='drop',verbose_feature_names_out=False)
    return pre,nums,cats


def _models(n_jobs=-1,seed=42,n_targets=5):
    return {
        'ExtraTrees':ExtraTreesRegressor(n_estimators=500,min_samples_leaf=2,max_features=0.8,n_jobs=n_jobs,random_state=seed),
        'RandomForest':RandomForestRegressor(n_estimators=450,min_samples_leaf=2,max_features=0.8,n_jobs=n_jobs,random_state=seed+1),
    }


def train_gen2desc(df,out_dir,max_components=32,variance=0.985,cv_splits=5,seed=42,n_jobs=-1,include_legacy_forward=False):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    dcols=numeric_descriptor_columns(df);gcols=generator_feature_columns(df)
    if len(dcols)<2:raise RuntimeError('Too few usable descriptors')
    # Representation learns from every available structure, including legacy/non-LHS data.
    enc=DescriptorEncoder(max_components,variance).fit(df,dcols)
    # Forward inverse-ready model excludes seed-only legacy generators by default because seed is non-continuous.
    if include_legacy_forward:
        fdf=df.copy()
    else:
        mode=df.get('gen__voxel_mode',pd.Series('',index=df.index)).astype(str)
        ver=df.get('meta__generator_version',pd.Series('',index=df.index)).astype(str)
        mask=mode.str.startswith('latent_') | ver.str.contains('v4_latent',case=False,na=False)
        fdf=df.loc[mask].copy()
        if len(fdf)<max(12,min(30,len(df)//3)):
            print('[WARN] Too few latent-controlled rows; falling back to all rows for Model 1 forward fit.')
            fdf=df.copy()
    Y=enc.transform(fdf)
    pre,nums,cats=build_x_preprocessor(fdf,gcols); groups=design_groups(fdf)
    ng=max(2,min(cv_splits,len(np.unique(groups))));gkf=GroupKFold(ng)
    rows=[]; oofs={}
    for name,est in _models(n_jobs,seed,Y.shape[1]).items():
        pred=np.full_like(Y,np.nan,float)
        for tr,te in gkf.split(fdf,Y,groups):
            pipe=Pipeline([('pre',build_x_preprocessor(fdf.iloc[tr],gcols)[0]),('model',est.__class__(**est.get_params()))])
            pipe.fit(fdf.iloc[tr][gcols],Y[tr]);pred[te]=pipe.predict(fdf.iloc[te][gcols])
        r2=float(r2_score(Y,pred,multioutput='variance_weighted'));rmse=float(np.sqrt(mean_squared_error(Y,pred)))
        rows.append({'model':name,'latent_r2':r2,'latent_rmse':rmse});oofs[name]=pred
    metrics=pd.DataFrame(rows).sort_values(['latent_r2','latent_rmse'],ascending=[False,True]);best=metrics.iloc[0]['model']
    # Inverse-CV-RMSE ensemble weights: the final prediction blends every fitted model
    # weighted by how well it actually generalized in group-safe CV, instead of a plain
    # unweighted average across models of very different quality.
    inv=metrics.set_index('model')['latent_rmse'].apply(lambda r: 1.0/max(float(r),1e-9))
    model_weights={k:float(v) for k,v in (inv/inv.sum()).items()}
    fitted={}
    for name,est in _models(n_jobs,seed,Y.shape[1]).items():
        pipe=Pipeline([('pre',build_x_preprocessor(fdf,gcols)[0]),('model',est)]);pipe.fit(fdf[gcols],Y);fitted[name]=pipe
    bundle={'version':'gen2desc-v1','generator_features':gcols,'numeric_features':nums,'categorical_features':cats,'descriptor_encoder':enc,'models':fitted,'model_weights':model_weights,'best_model':best,'cv_metrics':metrics,'feature_bounds':get_feature_bounds(fdf,gcols),'training_latent_min':Y.min(0),'training_latent_max':Y.max(0),'training_latent_mean':Y.mean(0),'training_latent_cov':np.cov(Y.T) if Y.shape[1]>1 else np.array([[np.var(Y[:,0])]]),'training_rows':len(fdf),'representation_rows':len(df),'forward_training_rows':len(fdf),'include_legacy_forward':bool(include_legacy_forward)}
    joblib.dump(bundle,out/'gen2desc_bundle.joblib',compress=3);atomic_csv(metrics,out/'cv_metrics.csv')
    # reconstruction audit in descriptor units from best OOF
    recon=enc.inverse_transform(oofs[best]);truth=fdf[enc.columns].apply(pd.to_numeric,errors='coerce').fillna(enc.medians.reindex(enc.columns))
    audit=[]
    for c in enc.columns:
        try:audit.append({'descriptor':c,'r2_from_oof_latent':float(r2_score(truth[c],recon[c]))})
        except Exception:audit.append({'descriptor':c,'r2_from_oof_latent':np.nan})
    atomic_csv(pd.DataFrame(audit),out/'descriptor_reconstruction_audit.csv')
    atomic_json(out/'model_manifest.json',{'version':bundle['version'],'best_model':best,'training_rows':len(fdf),'representation_rows':len(df),'generator_features':gcols,'descriptor_raw_count':len(enc.columns),'descriptor_latent_dim':enc.n_components_})
    return bundle,metrics


def predict_gen2desc(bundle,df,return_raw=True):
    names=list(bundle['models'].keys())
    preds=[np.asarray(bundle['models'][n].predict(df[bundle['generator_features']]),float) for n in names]
    A=np.stack(preds,axis=0)
    # Weighted-by-CV-accuracy ensemble mean (falls back to a plain average for bundles
    # trained before model_weights existed); std stays the raw member spread, used
    # elsewhere as an epistemic-uncertainty signal.
    w=bundle.get('model_weights')
    if w:
        wv=np.asarray([float(w.get(n,0.0)) for n in names],float); wv=wv/max(wv.sum(),1e-12)
    else:
        wv=np.full(len(names),1.0/len(names))
    mean=np.tensordot(wv,A,axes=(0,0));std=A.std(0)
    out={'latent_mean':mean,'latent_std':std}
    if return_raw:
        out['descriptor_raw_mean']=bundle['descriptor_encoder'].inverse_transform(mean)
    return out
