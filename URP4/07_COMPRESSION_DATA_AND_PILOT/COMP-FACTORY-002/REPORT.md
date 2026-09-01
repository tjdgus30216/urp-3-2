# COMP-FACTORY-002-AI-LATTICE-PILOT-20260731-144749

## Result

- Status: PASS
- Rows: 149
- Excluded missing-y model: AI092
- Evaluated targets: 16
- Eligible nonconstant x candidates: 37
- Outer policy: leave one source workbook block out (3 folds)
- Methods: 4
- OOF predictions: 9536
- Feature promotion: 0
- Production/inverse-design claim: 0
- Method-01 runtime deviation: fixed Ridge blend surrogate; exact BayesianRidge recipe not executed
- Figures: `figures/f1_yx.png`, `figures/f2_r2.png`, `figures/f3_block.png`

## Interpretation boundary

This is a source-block OOF technical pilot. The three summary workbooks are used as provisional groups,
but they are not proven generator-lineage groups. Target units and maximize/minimize directions remain unresolved.
All feature selection occurs inside each outer training fold. No feature or method is promoted.
Method-01 is a runtime-safe surrogate because canonical KMK312 crashed in SciPy SVD during BayesianRidge.
