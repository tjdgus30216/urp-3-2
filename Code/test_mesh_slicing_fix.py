"""
Regression test for the STL/STEP 'jumping / noisy slice' fix.

Root cause (see descriptor_library.vectorized_segments docstring): an STL file stores 3
independent vertex coordinates per triangle -- there is no shared vertex index -- so a vertex
that is geometrically shared by several triangles is written out multiple times, and CAD
exporters routinely leave tiny (~1e-6..1e-9 mm) floating-point mismatches between those
copies. A cutting z-plane that lands close to such a vertex can then see nominally-identical
vertices fall on opposite sides of the crossing test, flipping the parity of intersections
counted on a scanline row and tearing the rasterized slice.

This test needs no CAD/mesh library (trimesh is NOT required) -- it feeds a small synthetic
"unwelded STL" triangle soup directly into vectorized_segments()/rasterize_segments_scanline(),
the two pure-numpy functions at the core of the bug, so it can run in any environment
(including this offline sandbox) and still exercise the exact code path used by
load_mesh_as_voxels() on a real STL import.
"""
import sys
import numpy as np
sys.path.insert(0, '.')
import descriptor_library as dl


def make_bipyramid(jitter=0.0, weld=True, seed=0):
    """An 8-triangle square bipyramid. When weld=False, each triangle gets its OWN copy of
    the 4 equatorial ring vertices (exactly how an unwelded STL exporter would write them),
    optionally perturbed in z by `jitter` to simulate float round-off between the copies."""
    apex_t = np.array([1, 1, 3.0]); apex_b = np.array([1, 1, -1.0])
    rng = np.random.default_rng(seed)

    def ring_copy():
        base = np.array([[0, 0, 1.0], [2, 0, 1.0], [2, 2, 1.0], [0, 2, 1.0]])
        if weld or jitter == 0.0:
            return base
        return base + rng.uniform(-jitter, jitter, size=base.shape) * np.array([0, 0, 1])

    tris = []
    for (i, j) in [(0, 1), (1, 2), (2, 3), (3, 0)]:
        r = ring_copy(); tris.append([apex_t, r[i], r[j]])
    for (i, j) in [(1, 0), (2, 1), (3, 2), (0, 3)]:
        r = ring_copy(); tris.append([apex_b, r[i], r[j]])
    return np.array(tris, dtype=float)


def slice_at_equator(tris, vtol):
    seg = dl.vectorized_segments(tris, 1.0, vtol=vtol)
    mask, qa = dl.rasterize_segments_scanline(seg, -0.5, -0.5, 2.5, 2.5, 120, 120)
    return seg, mask, qa


print("=== Mesh slicing fix: unwelded-vertex jitter, default vtol ===")
cases = [
    (True, 0.0, 'welded (identical vertices)'),
    (False, 0.0, 'unwelded, jitter=0 (still bit-identical)'),
    (False, 1e-6, 'unwelded, jitter=1e-6 (typical STL export mismatch)'),
    (False, 1e-9, 'unwelded, jitter=1e-9 (near machine precision)'),
]
all_ok = True
for weld, jitter, label in cases:
    tris = make_bipyramid(jitter=jitter, weld=weld)
    seg, mask, qa = slice_at_equator(tris, vtol=1e-6)  # library default
    ok = qa['odd_rows'] == 0 and mask.sum() == 6400
    all_ok &= ok
    print(f"{label:55s} segments={len(seg):3d}  odd_rows={qa['odd_rows']:3d}  "
          f"filled_px={mask.sum():5d}  {'PASS' if ok else 'FAIL'}")
assert all_ok, "default-vtol fix failed to clean up a realistic unwelded/jittered mesh"

print()
print("=== Sanity: with vtol=0 (pre-fix behavior), jitter DOES reproduce the artifact ===")
tris = make_bipyramid(jitter=1e-6, weld=False)
seg, mask, qa = slice_at_equator(tris, vtol=0.0)
print(f"vtol=0, jitter=1e-6   segments={len(seg)}  odd_rows={qa['odd_rows']}  filled_px={mask.sum()}")
assert qa['odd_rows'] > 0, "expected the pre-fix path (vtol=0) to still show odd-parity rows here"
print("PASS  confirms odd_rows==0 above comes from the vtol fix, not from this geometry being easy")

print()
print("=== Geometric accuracy: the weld/jitter/vtol fix must not change the filled area ===")
# every case above filled exactly 6400 px (a clean 2x2 mm square at 120x120 over a 3x3 mm frame
# -> (2/3*120)^2 = 6400); this is asserted inside the loop already.
print("PASS  filled_px constant at 6400 across all welded/unwelded/jitter combinations")

print()
print("ALL PASS")
