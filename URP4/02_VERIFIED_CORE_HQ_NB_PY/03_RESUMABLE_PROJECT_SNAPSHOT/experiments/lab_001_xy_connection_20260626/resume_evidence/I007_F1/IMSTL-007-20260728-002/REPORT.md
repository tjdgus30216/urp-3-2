# IMSTL-007 F1 resolution and pixel-phase diagnosis

- Run: `IMSTL-007-20260728-002`
- Settings: `IDX-URP4-1-GEOM-IMPORTED-STL / CFG-IMSTL007-F1-P500-750-1000-1500-PHASE4-SELECTED r1`
- Runtime: KMK312 / Python 3.12.12
- Scope: F1 fixed nine slices only; 4 resolutions × 4 half-pixel phases
- Result: **screening_pass_benign_discretization**

## Evidence

- Preserved masks: `144`
- IMSTL-006 P500/P1000 P00 exact replay: **18/18**
- P1000→P1500 interior minimum IoU: `0.962591`
- P1000→P1500 maximum relative area difference: `0.017153`
- P1000→P1500 minimum boundary-band explanation: `1.000000`
- P1500 phase-pair minimum IoU: `0.960504`
- P1500 phase-pair maximum relative area difference: `0.006016`
- P1500 phase-pair minimum boundary-band explanation: `1.000000`
- Failed-slice improvement: `True` — [{'slice_index': 200, 'baseline_iou': 0.9490451918732313, 'high_resolution_iou': 0.9739854151477826, 'improved': True}, {'slice_index': 600, 'baseline_iou': 0.9490451918732313, 'high_resolution_iou': 0.9713204966554827, 'improved': True}]

## Gate

- exact replay: `True`
- high-resolution convergence: `True`
- half-pixel phase stability: `True`
- interior occupancy: `True`

## Interpretation boundary

This run distinguishes bounded raster discretization from route instability for F1. A pass supports only F1 imported-STL **screening** and a separately authorized future full extraction. It does not establish exact STP parity, all-F/all58 generalization, canonical structure factors, x-y utility, Training readiness or inverse design.

No full-801 F1 extraction, y access, model fitting, feature selection, source mutation, NB-CURRENT or LEGACY-PY edit occurred.

## Independent QA and visual review

- Independent mask replay: `144/144` exact
- Independent metric replay: `432/432`, maximum absolute error `1.11e-16`
- Producer decision consistency: **PASS**
- Run/result manifests: **PASS**
- Protected file assets: `26/26` unchanged
- Full-801 execution absent: **confirmed**
- Manual review of slices `200` and `600`: coherent foam-cell regions at every tested resolution/phase; no missing material region, isolated random speckle or topology break. Visible differences are confined to raster boundaries.

## Scientific verdict

**confirmed — F1's former selected-slice failure is benign raster discretization/pixel-phase sensitivity within this frozen experiment.** The two failed slices improve from P500→P1000 IoU `0.949045` to P1000→P1500 IoU `0.973985` and `0.971320`, respectively. All high-resolution differences are boundary-band explained (`1.0`) with invariant filtered component/hole topology.

F1 is therefore `screening-qualified` for a separately authorized P1000/Z801 run through the imported-STL route. This does not approve exact original-STP parity, the whole F family, all58, a canonical descriptor formula, NB-CURRENT promotion, y access or modeling.

## Execution note

`IMSTL-007-20260728-001` completed the numerical body but failed while writing an overlong Windows result path. It is quarantined as an infrastructure-only non-result. `IMSTL-007-20260728-002` repeats the unchanged scientific contract with shorter output paths and is the sole accepted run.
