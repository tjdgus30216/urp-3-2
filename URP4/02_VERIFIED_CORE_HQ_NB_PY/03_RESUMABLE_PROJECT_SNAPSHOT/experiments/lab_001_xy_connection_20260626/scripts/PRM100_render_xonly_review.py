from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
LAB=ROOT/'experiments'/'lab_001_xy_connection_20260626'
TABLES=LAB/'reports'/'tables'

def main():
    routes=pd.read_csv(TABLES/'PRM100_full58_technical_route.csv')
    pairs=pd.read_csv(TABLES/'PRM100_difficult_pair_diagnostic.csv')
    cov=pd.read_csv(TABLES/'PRM100_full58_coverage_variation.csv')
    labels=[x.split('::',1)[1].replace('solid_void_chord_','').replace('_direction_mean_per_mm3','') for x in routes.candidate_id]
    fig,ax=plt.subplots(1,2,figsize=(14,6),constrained_layout=True)
    ax[0].barh(labels,routes.high_redundancy_vs_XREG,color=['#2563eb']*4+['#f59e0b','#059669'])
    ax[0].set_xlabel('full58 high-redundancy edges vs XREG-v0.2')
    ax[0].set_title('Only ECT absolute-AUC has full58 high-correlation warnings')
    for y,v in enumerate(routes.high_redundancy_vs_XREG):ax[0].text(v+.03,y,str(v),va='center')
    pivot=pairs.pivot(index='candidate_id',columns='pair_id',values='relative_delta').loc[routes.candidate_id]
    ax[1].barh(labels,pivot['T8_T9'],color='#7c3aed',label='T8–T9')
    ax[1].barh(labels,pivot['T5_T6'],left=pivot['T8_T9'],color='#94a3b8',label='T5–T6')
    ax[1].set_xscale('symlog',linthresh=1e-6)
    ax[1].set_xlabel('relative delta (symlog; diagnostic only)')
    ax[1].set_title('Difficult pairs remain nearly unresolved')
    ax[1].legend(frameon=False)
    fig.suptitle('PRM-100 full58 technical census — x-only, no feature selection',fontweight='bold',fontsize=14)
    out=LAB/'reports'/'figures'/'PRM100_full58_xonly_review.png';out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)
if __name__=='__main__':main()
