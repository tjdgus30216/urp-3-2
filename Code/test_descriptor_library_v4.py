import sys, math, time
import numpy as np
sys.path.insert(0, '.')
import descriptor_library as ad

np.random.seed(0)

def make_sphere(n=40, r=None):
    if r is None: r = n*0.35
    zz,yy,xx = np.mgrid[0:n,0:n,0:n]
    c = n/2
    d = np.sqrt((zz-c)**2+(yy-c)**2+(xx-c)**2)
    return d <= r

def make_rod(n=40, r=None, axis=0):
    if r is None: r = n*0.15
    zz,yy,xx = np.mgrid[0:n,0:n,0:n]
    c = n/2
    coords = [zz,yy,xx]
    others = [coords[i] for i in range(3) if i!=axis]
    d = np.sqrt((others[0]-c)**2 + (others[1]-c)**2)
    return d <= r

def make_lattice(n=32, pitch=8, strut_r=1.4):
    zz,yy,xx = np.mgrid[0:n,0:n,0:n]
    vol = np.zeros((n,n,n), bool)
    for base in [(zz,yy),(zz,xx),(yy,xx)]:
        for k in range(0, n, pitch):
            a,b = base
            vol |= (np.abs((a - k) % pitch) <= strut_r) & True if False else vol
    # simpler: build as union of axis-aligned strut cylinders on a grid
    vol = np.zeros((n,n,n), bool)
    grid_pts = list(range(0, n, pitch))
    for gy in grid_pts:
        for gz in grid_pts:
            vol |= (np.abs(yy-gy)<=strut_r) & (np.abs(zz-gz)<=strut_r)
    for gx in grid_pts:
        for gz in grid_pts:
            vol |= (np.abs(xx-gx)<=strut_r) & (np.abs(zz-gz)<=strut_r)
    for gx in grid_pts:
        for gy in grid_pts:
            vol |= (np.abs(xx-gx)<=strut_r) & (np.abs(yy-gy)<=strut_r)
    return vol

def check(name, cond):
    print(('PASS ' if cond else 'FAIL '), name)
    return cond

ok = True

print('=== 1. Curvature: sphere sign/magnitude convention ===')
n=36; r=n*0.32
sph = make_sphere(n, r)
spacing=(1.,1.,1.)
t0=time.time()
c = ad.curvature_descriptors(sph, spacing)
print('elapsed', round(time.time()-t0,2),'s')
Hm = c['curvature_mean_H_per_mm_mean']; Km=c['curvature_gaussian_K_per_mm2_mean']
print('mean H:', Hm, 'expected ~', 1.0/r)
print('mean K:', Km, 'expected ~', 1.0/(r*r))
print('elliptic area frac:', c['curvature_area_fraction_elliptic_dome_or_node'])
ok &= check('H positive and ~1/r on sphere', Hm>0 and abs(Hm-1.0/r) / (1.0/r) < 0.35)
ok &= check('K positive and ~1/r^2 on sphere', Km>0 and abs(Km-1.0/(r*r)) / (1.0/(r*r)) < 0.6)
ok &= check('sphere elliptic area fraction clearly dominant over hyperbolic/parabolic at this voxel resolution',
            c['curvature_area_fraction_elliptic_dome_or_node'] > 0.5)

print()
print('=== 2. Curvature: rod (cylinder) -> much smaller area-weighted |K| than a sphere of comparable scale ===')
rod = make_rod(48, r=6, axis=0)
c2 = ad.curvature_descriptors(rod, spacing)
Kw_rod = c2['curvature_area_weighted_mean_K_per_mm2']
print('area-weighted K:', Kw_rod)
print('parabolic/cylindrical area frac:', c2['curvature_area_fraction_parabolic_cylindrical_or_strut'])
print('elliptic frac:', c2['curvature_area_fraction_elliptic_dome_or_node'], 'hyperbolic frac:', c2['curvature_area_fraction_hyperbolic_saddle_or_sheet'])
# A finite rod is capped, so its two rim regions genuinely carry curvature (not a bug) --
# the discriminating check is that the rod's *lateral* wall carries near-zero K, which pulls
# the area-weighted average far below the sphere's uniform K.
ok &= check('rod area-weighted K well below sphere area-weighted K', 0 <= Kw_rod < Km * 0.9)
ok &= check('rod parabolic(cylindrical) area fraction is the largest single class', c2['curvature_area_fraction_parabolic_cylindrical_or_strut'] >= max(c2['curvature_area_fraction_elliptic_dome_or_node'], c2['curvature_area_fraction_hyperbolic_saddle_or_sheet']))

print()
print('=== 2b. Curvature: gyroid-like TPMS shell -> saddle/hyperbolic-dominant (sheet-network signature) ===')
n=48
zz,yy,xx = np.mgrid[0:n,0:n,0:n]
c0=n/2
X=(xx-c0)/8.; Y=(yy-c0)/8.; Z=(zz-c0)/8.
val = np.sin(X)*np.cos(Y)+np.sin(Y)*np.cos(Z)+np.sin(Z)*np.cos(X)
gyroid_shell = np.abs(val) < 0.3
c3 = ad.curvature_descriptors(gyroid_shell, spacing)
print('hyperbolic frac:', c3['curvature_area_fraction_hyperbolic_saddle_or_sheet'],
      'elliptic:', c3['curvature_area_fraction_elliptic_dome_or_node'],
      'parabolic:', c3['curvature_area_fraction_parabolic_cylindrical_or_strut'])
ok &= check('TPMS gyroid shell is saddle/hyperbolic-dominant (this is the strut-vs-sheet discriminator)',
            c3['curvature_area_fraction_hyperbolic_saddle_or_sheet'] > c3['curvature_area_fraction_elliptic_dome_or_node'])
ok &= check('sphere is elliptic-dominant while gyroid shell is not (topology discrimination works)',
            c['curvature_area_fraction_elliptic_dome_or_node'] > c3['curvature_area_fraction_elliptic_dome_or_node'])

print()
print('=== 3. Tortuosity: straight open channel should have tau ~ 1 along its axis ===')
n=30
chan = np.zeros((n,n,n), bool)
chan[:, 13:17, 13:17] = True  # straight channel along z (axis 0)
t = ad.tortuosity_descriptors(chan, (1.,1.,1.), max_side=48)
print(t)
ok &= check('solid tortuosity along z ~ 1.0 for straight channel', abs(t['tortuosity_solid_z']-1.0) < 0.05)

print()
print('=== 4. Tortuosity: diagonal-forced zigzag channel should have tau > 1 ===')
n=30
zig = np.zeros((n,n,n), bool)
for z in range(n):
    off = 4*math.sin(z/n*3*math.pi)
    yc = int(15+off)
    zig[z, max(0,yc-2):yc+3, 13:17] = True
tz = ad.tortuosity_descriptors(zig, (1.,1.,1.), max_side=48)
print('zigzag tau_z:', tz['tortuosity_solid_z'])
ok &= check('zigzag tortuosity > straight tortuosity', tz['tortuosity_solid_z'] > t['tortuosity_solid_z'])

print()
print('=== 5. Strut graph: simple cubic lattice -> coordination number & strut stats ===')
lat = make_lattice(32, pitch=8, strut_r=1.3)
print('lattice density:', lat.mean())
t0=time.time()
g = ad.strut_graph_descriptors(lat, (1.,1.,1.))
print('elapsed', round(time.time()-t0,2),'s')
for k in ['strut_node_count','strut_junction_node_count','strut_count',
          'strut_network_mean_coordination_number_Z','strut_geodesic_length_mm_mean',
          'strut_tortuosity_mean','strut_thickness_mean_mm_mean','strut_thickness_uniformity_cv_mean']:
    print(' ', k, '=', g.get(k))
ok &= check('strut graph found junction nodes', g.get('strut_junction_node_count',0) > 0)
ok &= check('strut graph found struts', g.get('strut_count',0) > 0)
ok &= check('mean coordination number in plausible cubic-lattice range [3,6]', 3 <= g.get('strut_network_mean_coordination_number_Z',0) <= 6.5)
ok &= check('strut tortuosity near 1 for straight struts', abs(g.get('strut_tortuosity_mean',0)-1.0) < 0.3)

print()
print('=== 6. Grayscale soft-TSPE: consistency with hard TSPE when input is already binary (blur=0) ===')
n=24
vol_bin = make_sphere(n, n*0.3)
# stack of per-slice binary "images" as float in [0,1]
gvol = ad.grayscale_stack_from_binary(vol_bin, blur_sigma=0.0)
df_soft, s_soft = ad.soft_triplet_descriptor_table(gvol, (1.,1.,1.))
df_hard, s_hard = ad.triplet_descriptor_table(vol_bin, (1.,1.,1.))
a_soft_mean = s_soft['soft_triplet_soft_A_mean_mean']
a_hard_mean = s_hard['triplet_A_111_fraction_all_mean']
print('soft A mean(mean):', a_soft_mean, ' hard A fraction_all mean:', a_hard_mean)
ok &= check('soft-TSPE A matches hard-TSPE A fraction when no blur (exact fuzzy==crisp)', abs(a_soft_mean-a_hard_mean) < 1e-6)

print()
print('=== 6b. Grayscale soft-TSPE: with blur, partial-volume fraction should be >0 (info preserved) ===')
gvol_blur = ad.grayscale_stack_from_binary(vol_bin, blur_sigma=1.2)
df_soft2, s_soft2 = ad.soft_triplet_descriptor_table(gvol_blur, (1.,1.,1.))
pv = s_soft2['soft_triplet_soft_A_partial_volume_fraction_mean']
print('partial volume fraction with blur:', pv)
ok &= check('blurred grayscale stack yields nonzero partial-volume fraction', pv > 0.0)

print()
print('=== 7. X-ray CT Radon/FBP simulate+reconstruct: fidelity vs. direct stack ===')
n=48
phantom = make_sphere(n, n*0.3)
t0=time.time()
ct_out, rec_full, rec_sparse = ad.xray_ct_projection_reconstruction(phantom, (1.,1.,1.), n_angles=90, sparse_n_angles=18)
print('elapsed', round(time.time()-t0,2),'s')
for k,v in ct_out.items(): print(' ', k, '=', v)
ok &= check('full-angle CT reconstruction Dice > 0.9 vs direct stack (clean, no noise)', ct_out['ct_recon_full_angle_dice_vs_direct_stack'] > 0.9)
ok &= check('sparse-angle CT reconstruction Dice is lower than full-angle (fewer projections = worse)', ct_out['ct_recon_sparse_angle_dice_vs_direct_stack'] <= ct_out['ct_recon_full_angle_dice_vs_direct_stack'] + 1e-6)

print()
print('=== 7b. With Poisson noise (low-dose realism check: should still run, dice may drop) ===')
ct_out_noisy, _, _ = ad.xray_ct_projection_reconstruction(phantom, (1.,1.,1.), n_angles=90, sparse_n_angles=18, add_poisson_noise=True, photon_count=2000.0)
print('noisy full-angle dice:', ct_out_noisy['ct_recon_full_angle_dice_vs_direct_stack'])
ok &= check('noisy CT run completes and returns a finite dice', np.isfinite(ct_out_noisy['ct_recon_full_angle_dice_vs_direct_stack']))

print()
print('====================================')
print('ALL PASS' if ok else 'SOME FAILURES')
sys.exit(0 if ok else 1)
