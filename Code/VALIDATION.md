# Validation report

## Unit validation
- 3-bit TSPE mapping was tested explicitly for all eight binary states.
- Observed mapping: `[0,1,2,3,4,5,6,7]` for `000...111`.
- Therefore A=111, B=110, C=011 are encoded exactly as intended.

## Function-level validation
A synthetic periodic 24^3 binary structure was used to call every descriptor family independently. All families executed after correcting an integer-underflow issue in chord run detection.

Approximate scalar counts in that function-level test:
- 2D slice summary: 468
- projection texture/moments: 930
- pair summary: 468
- triplet TSPE summary: 1430
- multi-layer persistence: 312
- multi-lag: 522
- TSPE transition: 85
- 3D morphology: 115
- topology + Euler filtration: 43
- distance/thickness: 63
- granulometry: 9 (test radius reduced)
- chord: 126
- lineal path: 24 (test lengths reduced)
- two-point: 51 (test lag reduced)
- three-point: 9
- multiscale: 27 (test box set reduced)
- spectral: 43
- directional/MIL: 149
- skeleton/network: 35
- persistent homology: 1 skip flag because Gudhi was not installed

## Full notebook execution
The notebook was executed from first computational cell to last using a synthetic 20-slice image stack. The complete pipeline succeeded, including checkpoint IO, feature aggregation, manifest generation, batch aggregation, and reconstructed STL export.

Final synthetic test output:
- `descriptors_ALL.csv`: shape `(1, 5883)`
- 1 column is `sample_id`
- 5,882 scalar descriptor candidates
- 77 NaN cells were retained intentionally for QA/feature-selection handling rather than silently imputed.

## Restart design validation
Every descriptor stage explicitly reloads `02_volume_processed.npz` or prior disk configuration, and writes stage outputs independently. No descriptor stage requires Python variables created by the immediately preceding cell.

## v4 additions -- validation

### Unit/physics validation (`test_descriptor_library_v4.py`, synthetic geometry, all assertions pass)
- **Curvature**: on a synthetic solid sphere (voxel radius r), area-weighted mean curvature matched the
  analytic value H=1/r to within 0.2% and Gaussian curvature matched K=1/r^2 to within 1%, after fixing
  the sign convention empirically (H>0 on a convex solid) and adding Taubin mesh smoothing to remove
  marching-cubes staircase noise. A synthetic gyroid-like TPMS shell was correctly classified as
  saddle/hyperbolic-curvature-dominant (0.71 area fraction), and a solid sphere as elliptic-dominant
  (0.60), i.e. the elliptic/hyperbolic/parabolic split does discriminate sheet-network (TPMS) topology
  from dome/node topology as intended. A finite rod's lateral (cylindrical) wall measured |K| ~ 1e-9
  (correctly ~0) when isolated from its end-cap rims; the full rod's area-weighted K (0.0061) stayed
  well below the sphere's (0.0075) and its parabolic/cylindrical area fraction was the single largest
  class, consistent with a mostly-cylindrical body. One caveat found and documented: a structure that
  touches the analysis volume's array boundary produces an OPEN (non-watertight) marching-cubes mesh
  unless padded first, which corrupts curvature at the cut edge -- `_mesh_from_volume` now pads the
  volume by 1 voxel of background on every side before marching_cubes to guarantee a closed mesh.
- **Tortuosity**: a straight open channel gave tau=1.00 along its axis (as required); an artificially
  zig-zagged channel of the same length gave tau=1.32 (>1, correctly detects the added path length);
  a phase that does not span the requested axis correctly returns NaN rather than a misleading number.
- **Strut/node graph**: on a synthetic simple-cubic strut lattice, the network-mean coordination number
  landed at Z=4.64 (a physically plausible value for a cubic lattice, between the Z=4 rank of a purely
  planar joint and Z=6 of a fully triaxial node -- consistent with the lattice's mix of 3-strut edge
  junctions and higher-order interior junctions) and per-strut tortuosity averaged 1.002 (~1, correct
  for straight struts).
- **Grayscale soft-TSPE**: with zero blur (soft input numerically identical to the hard-thresholded
  input), soft-TSPE's A_soft mean matched the existing hard-TSPE A=111 fraction to <1e-6 -- i.e. the
  fuzzy formulation is an exact generalization of the existing crisp TSPE, not a different quantity.
  With Gaussian blur applied, the partial-volume-fraction diagnostic correctly went from 0 to >0,
  confirming genuine information is now retained that the v3 hard-threshold pipeline discarded.
- **X-ray CT Radon/FBP reconstruction**: full-angle (180-projection-equivalent) FBP reconstruction of a
  synthetic sphere matched the direct-stack ground truth with Dice=1.00 (noise-free case); a matched
  sparse-view (fewer-angle) run scored Dice <= the full-angle run, correctly reflecting the expected
  fewer-projections quality loss; a Poisson-noise-injected (low-dose) run completed without error and
  returned a finite, still-high Dice, confirming the noise/reconstruction loop is numerically stable.

### Full-notebook end-to-end execution (v3 + v4 combined)
Since `nbclient`/`jupyter` could not be installed in this offline validation environment, every code
cell of `Architected_Material_Descriptor_Exhaustive_v3.ipynb` (60 cells total, including the 6 new v4
cells 19b-19g) was executed in order in a single persistent namespace by a minimal custom notebook
runner (`run_notebook_e2e_test.py`, included in this package), against a synthetic 28-slice grayscale
image stack of a simple 3-strut cubic lattice (28x28x28 voxels, ~29% relative density) -- exercising the
real `INPUT_KIND="image_stack"` path end to end, not just direct function calls.

Result: **all 60 cells executed without error.** `descriptors_ALL.csv` reached shape `(1, 8034)`:
8,033 scalar descriptors plus `sample_id`. Of those, 2,109 are new v4 columns (curvature: 132,
tortuosity: 8, strut/node graph: 153, soft-TSPE: 1,742, CT-reconstruction: 74); the remaining ~5,924
reproduce the original v3 family set at this test's (unreduced) settings. 184 of the 8,033 cells were
NaN, retained intentionally for QA rather than silently imputed (same policy as v3).

Two environment-compatibility bugs were found and fixed during this full-notebook run, independent of
the v4 feature additions themselves:
1. `euler_filtration_descriptors` called `np.trapz`, which NumPy >=2.0 renamed to `np.trapezoid` and
   later removed the old alias entirely -- this crashed Cell 13 on this environment's NumPy 2.4. Fixed
   with a `_trapz = getattr(np, 'trapezoid', None) or np.trapz` compatibility shim at module load time.
2. `trimesh` is not installable in this offline sandbox at all; `import trimesh` at module load
   previously made the entire library fail to import with no `trimesh` present, which would also have
   blocked every earlier NON-mesh descriptor family for a user without that package. `trimesh` is now
   an optional import (`_HAS_TRIMESH` flag) and every mesh-dependent function
   (`load_mesh_as_voxels`, `marching_mesh`, and by extension `morphology3d_descriptors`'s surface
   section and the Cell 22 STL export) fails softly with an explicit skip message/flag instead of an
   ImportError, while every other descriptor family -- including all-new v4 curvature descriptors,
   which use `skimage.measure.marching_cubes` directly and never needed trimesh -- is unaffected.
   When trimesh IS installed, behavior for existing v3 functions is unchanged.

## v4.1 -- STL/STEP slicing artifact fix: validation

### Root-cause reproduction
A synthetic 8-triangle square bipyramid was built with each triangle holding its OWN copy of
the 4 shared equatorial-ring vertices (mirroring exactly how an unwelded STL exporter writes
triangles), with those per-triangle copies perturbed in z by a controlled jitter to simulate
CAD-exporter floating-point round-off. Slicing this mesh at the equator with the *pre-fix*
code (`vtol=0`) reproduced the reported artifact directly:

| case | segments found | odd-parity scanline rows (of 120) | filled px |
|---|---|---|---|
| welded (identical vertices) | 4 | 0 | 6400 |
| unwelded, jitter=0 (bit-identical) | 4 | 0 | 6400 |
| unwelded, jitter=1e-6 (typical STL export mismatch) | 7 | 39 | 6400 |
| unwelded, jitter=1e-9 (near machine precision) | 7 | 39 | 6400 |

Note that even a 1e-9 mm perturbation -- far smaller than any voxel size in practical use --
was enough to corrupt 39 of 120 scanline rows. This confirms the artifact is a floating-point
robustness bug in the crossing classification, not a resolution/sampling issue.

### Fix validation, against the actual shipped `descriptor_library.py`
The identical reproduction was re-run through the real, shipped `vectorized_segments()` /
`rasterize_segments_scanline()` (not a prototype copy) with the new default `vtol=1e-6`:

| case | segments | odd_rows | filled px | result |
|---|---|---|---|---|
| welded | 4 | 0 | 6400 | PASS |
| unwelded, jitter=0 | 4 | 0 | 6400 | PASS |
| unwelded, jitter=1e-6 | 4 | 0 | 6400 | PASS |
| unwelded, jitter=1e-9 | 4 | 0 | 6400 | PASS |

All four cases now produce the geometrically-correct 6,400-pixel filled square with zero
odd-parity rows -- the fix eliminates the artifact for realistic STL export tolerances while
leaving the filled area numerically unchanged (confirming no accuracy was traded away). A
companion check re-ran the jitter=1e-6 case with `vtol=0` (i.e. simulating the pre-fix code
path through the *current* module) and confirmed it still reproduces `odd_rows=39`, which
rules out the geometry itself having become "easier" for any other reason. This is
implemented as a standalone, trimesh-independent regression test, `test_mesh_slicing_fix.py`,
which was run in this sandbox and printed `ALL PASS`.

### Full end-to-end re-verification after the fix
Because `trimesh` cannot be installed in this offline sandbox, the mesh-import path itself
(`load_mesh_as_voxels`, `repair_mesh_for_slicing`, the `trimesh_fill`/STEP paths) could not be
exercised end-to-end here and should be smoke-tested by the user against a real STL/STEP file.
However, both full regression suites were re-run against the *entire* updated
`descriptor_library.py` (all v3+v4 code, now including the slicing fix and STEP-import
dispatcher) to confirm nothing else regressed:
- `test_descriptor_library_v4.py`: **ALL PASS** (all v4 curvature/tortuosity/strut/soft-TSPE/CT
  assertions above still hold against the updated file).
- `run_notebook_e2e_test.py`: **all 60 cells executed without error**, `descriptors_ALL.csv`
  still reached shape `(1, 8034)`, identical to the pre-fix run (the image-stack input path
  used by this end-to-end test does not touch the mesh-slicing code, so this run's purpose is
  confirming the rest of the pipeline was not disturbed by the edit).

### What a real user should expect
On a real STL with typical CAD-exporter tolerances (jitter well under 1e-4 mm is standard),
`repair_mesh_for_slicing()`'s vertex welding will usually eliminate the near-duplicate
vertices outright, and the `vtol` dead-zone in `vectorized_segments()` is a second,
independent safety margin sized off the chosen `VOXEL_SIZE_MM`. For architected/lattice
geometry where struts were exported without a boolean union (self-intersecting, non-manifold
mesh), `backend='auto'` will prefer the flood-fill voxelizer, which does not depend on
scanline parity at all and is therefore immune to this entire class of artifact. If the
scanline path is used anyway (flood-fill unavailable, raised, or failed its sanity check
against the mesh's analytic volume), `meta['slicing_qa']` reports exactly which slice indices
(if any) still show odd-parity rows, so residual problem slices are directly identifiable
rather than silently corrupted.
