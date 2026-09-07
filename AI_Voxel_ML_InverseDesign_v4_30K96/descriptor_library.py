from __future__ import annotations
import json, math, re, warnings, os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import ndimage as ndi
from scipy.stats import skew, kurtosis
from skimage import measure, morphology, feature
from skimage.measure import regionprops
from PIL import Image

# ----------------------------- optional GPU backend (CuPy) -----------------------------
try:
    import cupy as cp
    import cupyx.scipy.ndimage as cndi
    _HAS_CUPY = bool(cp.cuda.runtime.getDeviceCount() > 0)
except Exception:
    cp = None
    cndi = None
    _HAS_CUPY = False

def gpu_acceleration_status(gpu_ids=(0,1)):
    """Return a JSON-serializable CUDA/CuPy status report. No exception is raised when CUDA
    is unavailable; callers can use this for automatic CPU fallback diagnostics."""
    out={'cupy_imported': bool(cp is not None), 'gpu_acceleration_available': bool(_HAS_CUPY), 'requested_gpu_ids': list(gpu_ids or [])}
    if not _HAS_CUPY:
        out['detected_gpu_count']=0
        return out
    try:
        n=int(cp.cuda.runtime.getDeviceCount()); out['detected_gpu_count']=n; names=[]
        for i in range(n):
            prop=cp.cuda.runtime.getDeviceProperties(i)
            name=prop.get('name', b'') if isinstance(prop,dict) else b''
            if isinstance(name,(bytes,bytearray)): name=name.decode(errors='replace')
            names.append(str(name))
        out['detected_gpu_names']=names
        out['usable_gpu_ids']=[int(i) for i in (gpu_ids or []) if 0<=int(i)<n]
    except Exception as e:
        out['status_error']=str(e)
    return out

def _gpu_ok(use_gpu=False, gpu_id=0):
    if not use_gpu or not _HAS_CUPY:
        return False
    try:
        return 0 <= int(gpu_id) < int(cp.cuda.runtime.getDeviceCount())
    except Exception:
        return False

def _qstats_cupy(values, prefix):
    """qstats-equivalent scalar summary evaluated on a CuPy array. This keeps large EDT/TSPE
    arrays on the GPU and transfers only the final scalar statistics to host memory."""
    a=values.ravel().astype(cp.float64, copy=False)
    a=a[cp.isfinite(a)]
    base=['n','mean','std','min','q01','q05','q10','q25','median','q75','q90','q95','q99','max','iqr','range','cv','skew','kurtosis','rms','mad']
    n=int(a.size)
    if n==0:
        return {f'{prefix}_{k}':np.nan for k in base}
    q=cp.quantile(a,cp.asarray([.01,.05,.10,.25,.5,.75,.9,.95,.99]))
    mean=cp.mean(a); centered=a-mean; m2=cp.mean(centered**2); std=cp.sqrt(m2); med=q[4]; mad=cp.median(cp.abs(a-med))
    if n>2 and float(m2.get())>0:
        g1=cp.mean(centered**3)/(m2**1.5); skew_v=cp.sqrt(n*(n-1))/(n-2)*g1
    else: skew_v=cp.asarray(np.nan)
    if n>3 and float(m2.get())>0:
        g2=cp.mean(centered**4)/(m2*m2)-3.0
        kurt_v=((n-1)/((n-2)*(n-3)))*((n+1)*g2+6.0)
    else: kurt_v=cp.asarray(np.nan)
    vals={
      'n':n,'mean':mean,'std':std,'min':cp.min(a),'q01':q[0],'q05':q[1],'q10':q[2],'q25':q[3],
      'median':med,'q75':q[5],'q90':q[6],'q95':q[7],'q99':q[8],'max':cp.max(a),
      'iqr':q[5]-q[3],'range':cp.max(a)-cp.min(a),'cv':std/cp.maximum(cp.abs(mean),EPS),
      'skew':skew_v,'kurtosis':kurt_v,'rms':cp.sqrt(cp.mean(a*a)),'mad':mad}
    out={}
    for k,v in vals.items(): out[f'{prefix}_{k}']=int(v) if k=='n' else float(cp.asnumpy(v))
    return out

try:
    import trimesh
    _HAS_TRIMESH = True
except Exception:
    trimesh = None
    _HAS_TRIMESH = False

def _require_trimesh(feature_name):
    if not _HAS_TRIMESH:
        raise RuntimeError(f"'{feature_name}' requires the optional 'trimesh' package "
                            f"(pip install trimesh). It is not installed in this environment.")

try:
    import cadquery as _cq
    _HAS_CADQUERY = True
except Exception:
    _cq = None
    _HAS_CADQUERY = False

def _require_cadquery(feature_name):
    if not _HAS_CADQUERY:
        raise RuntimeError(f"'{feature_name}' requires the optional 'cadquery' package "
                            f"(pip install cadquery) to tessellate STEP/STP B-rep geometry into a "
                            f"triangle mesh -- STEP files store NURBS surfaces, not triangles, so "
                            f"trimesh cannot read them directly. It is not installed in this "
                            f"environment. Workaround: open the file in your CAD tool and use "
                            f"File > Export > STL, then point INPUT_PATH at that .stl instead.")

EPS=1e-12
IMAGE_EXTS={'.png','.tif','.tiff','.jpg','.jpeg','.bmp'}
MESH_EXTS={'.stl','.obj','.ply','.off','.3mf','.glb','.gltf'}
STEP_EXTS={'.stp','.step'}
# numpy>=2.0 renamed trapz->trapezoid and removed the old alias in later 2.x releases
# (this broke euler_filtration_descriptors on numpy>=2.4; harmless compatibility shim).
_trapz = getattr(np, 'trapezoid', None) or np.trapz
import scipy.sparse as _sp
from scipy.sparse.csgraph import dijkstra as _dijkstra
try:
    import networkx as nx
    _HAS_NETWORKX = True
except Exception:
    _HAS_NETWORKX = False

# ----------------------------- IO helpers -----------------------------
def save_json(obj, path):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,'w',encoding='utf-8') as f: json.dump(obj,f,indent=2,ensure_ascii=False,default=_json_default)

def load_json(path):
    with open(path,'r',encoding='utf-8') as f: return json.load(f)

def _json_default(x):
    if isinstance(x,(np.integer,)): return int(x)
    if isinstance(x,(np.floating,)): return float(x)
    if isinstance(x,np.ndarray): return x.tolist()
    return str(x)

def save_volume(path, volume, spacing, meta=None):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, volume=volume.astype(np.uint8), spacing=np.asarray(spacing,float), meta=json.dumps(meta or {}))

def load_volume(path):
    z=np.load(path,allow_pickle=False)
    vol=z['volume'].astype(bool); spacing=tuple(float(v) for v in z['spacing'])
    meta=json.loads(str(z['meta'])) if 'meta' in z else {}
    return vol, spacing, meta

def natural_key(path): return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)',Path(path).name)]

def load_image_stack(folder, threshold=127, invert=False, spacing=(1.,1.,1.)):
    folder=Path(folder); files=sorted([p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS],key=natural_key)
    if len(files)<3: raise ValueError('Need at least 3 slice images')
    arr=[]; shape=None
    for p in files:
        im=np.asarray(Image.open(p).convert('L'))
        if shape is None: shape=im.shape
        elif im.shape!=shape: raise ValueError(f'Shape mismatch: {p}')
        m=im>threshold
        if invert: m=~m
        arr.append(m)
    return np.stack(arr).astype(bool), tuple(spacing), {'source_type':'image_stack','source':str(folder),'slice_files':[p.name for p in files]}

def _scene_to_mesh(obj):
    _require_trimesh('_scene_to_mesh')
    if isinstance(obj,trimesh.Scene):
        meshes=[g for g in obj.geometry.values() if isinstance(g,trimesh.Trimesh)]
        if not meshes: raise ValueError('No mesh geometry')
        return trimesh.util.concatenate(meshes)
    if isinstance(obj,trimesh.Trimesh): return obj
    raise TypeError(type(obj))

def vectorized_segments(triangles,z,eps=1e-9,vtol=1e-6):
    """Intersect a triangle soup with the plane z=const, returning line segments.

    vtol: dead-zone half-width (same length units as the vertex coordinates) that snaps any
    vertex whose height lies within vtol of the cutting plane onto the '<=0' (non-crossing)
    side before the crossing test. This is the fix for the STL 'jumping / noisy slice'
    artifact: an STL stores 3 independent vertex coordinates per triangle (no shared vertex
    index), so a vertex that is geometrically shared by several triangles is written out
    multiple times, and CAD exporters routinely leave ~1e-6..1e-9 floating-point mismatches
    between those copies. Without vtol, a cutting plane that lands close to such a vertex can
    see nominally-identical vertices fall on OPPOSITE sides of the raw dz<=0/dz>0 sign test,
    which flips the parity of crossings on the affected scanline row and tears the rasterized
    slice at a location that effectively differs at random from one slice to the next. The
    snap only changes the *crossing classification*; the interpolated intersection point
    itself is still computed from the true (unsnapped) coordinates, so geometric accuracy is
    unaffected. See also repair_mesh_for_slicing(), which removes the near-duplicate vertices
    at the source and is the first line of defense; this dead-zone is the second, independent
    defense for cases welding cannot fully resolve (e.g. self-intersecting lattice unions).
    """
    if triangles.size==0: return np.zeros((0,4),float)
    p1=triangles[:,[0,1,2],:]; p2=triangles[:,[1,2,0],:]
    dz1=p1[:,:,2]-z; dz2=p2[:,:,2]-z
    if vtol>0:
        dz1=np.where(np.abs(dz1)<=vtol,-vtol,dz1)
        dz2=np.where(np.abs(dz2)<=vtol,-vtol,dz2)
    cross=((dz1<=0)&(dz2>0))|((dz2<=0)&(dz1>0)); valid=cross.sum(axis=1)==2
    if not valid.any(): return np.zeros((0,4),float)
    p1v,p2v,cv=p1[valid],p2[valid],cross[valid]
    den=p2v[:,:,2]-p1v[:,:,2]; frac=np.zeros_like(den,float)
    np.divide(z-p1v[:,:,2],den,out=frac,where=cv)
    xy=p1v[:,:,:2]+frac[:,:,None]*(p2v[:,:,:2]-p1v[:,:,:2])
    sel=xy[cv].reshape(-1,2,2); l2=((sel[:,0]-sel[:,1])**2).sum(1); sel=sel[l2>eps*eps]
    return sel.reshape(-1,4) if sel.size else np.zeros((0,4),float)

def rasterize_segments_scanline(segments,xmin,ymin,xmax,ymax,width,height,eps=1e-12):
    """Rasterize closed cross-section segments into a fixed XY field of view.

    IMPORTANT for centered-cube cropping: parity is resolved from *all* scanline intersections
    first, and only then are each inside interval clipped to [xmin, xmax].  The previous
    implementation discarded intersections outside the image boundary before pairing them; if
    the requested crop lay fully inside a larger solid, both true boundary crossings could be
    outside the crop and the interior was incorrectly rendered empty.
    """
    dx=(xmax-xmin)/width; dy=(ymax-ymin)/height; mask=np.zeros((height,width),bool)
    if not len(segments): return mask,{'odd_rows':0,'odd_row_frac':0.0}
    x1,y1,x2,y2=(segments[:,j] for j in range(4)); nh=np.abs(y2-y1)>eps; odd=0; n_active=0
    for r in range(height):
        y=ymax-(r+.5)*dy; a=nh&(((y1<=y)&(y<y2))|((y2<=y)&(y<y1)))
        if not a.any(): continue
        n_active+=1
        xi=x1[a]+(y-y1[a])*(x2[a]-x1[a])/(y2[a]-y1[a]); xi.sort()
        if len(xi)%2: odd+=1; xi=xi[:-1]
        for j in range(0,len(xi),2):
            # Pair in the full geometry first; only then clip the material interval to the ROI.
            l=max(float(xi[j]),xmin); rgt=min(float(xi[j+1]),xmax)
            if rgt<=l: continue
            c0=max(0,min(width-1,int(math.ceil((l-xmin)/dx-.5)))); c1=max(0,min(width-1,int(math.floor((rgt-xmin)/dx-.5))))
            if c1>=c0: mask[r,c0:c1+1]=True
    return mask,{'odd_rows':odd,'odd_row_frac':(odd/n_active if n_active else 0.0)}

def _merge_vertices_safe(mesh, weld_tol):
    """Best-effort vertex welding across trimesh API versions (digits-based rounding is the
    most stable calling convention across trimesh releases; distance-based kwargs vary)."""
    digits=int(max(0,min(12,round(-math.log10(max(weld_tol,1e-12))))))
    for kwargs in ({'digits':digits},{}):
        try:
            mesh.merge_vertices(**kwargs); return True
        except TypeError:
            continue
        except Exception:
            return False
    return False

def repair_mesh_for_slicing(mesh, voxel_size=0.2, verbose=False):
    """Defensive mesh cleanup applied before slicing/voxelization -- the primary fix for the
    'jumping / noisy slice' artifact (see vectorized_segments() docstring for the root-cause
    explanation). Welds near-duplicate vertex copies, drops duplicate/degenerate faces, fixes
    inconsistent face-normal winding, and attempts to close small holes so the mesh is
    watertight going into voxelization. Returns (repaired_mesh, report_dict)."""
    _require_trimesh('repair_mesh_for_slicing')
    report={'watertight_before':bool(mesh.is_watertight)}
    weld_tol=max(voxel_size*1e-3,1e-7)
    report['weld_tolerance_mm']=weld_tol
    report['vertex_weld_applied']=_merge_vertices_safe(mesh, weld_tol)
    for step in ('remove_duplicate_faces','remove_degenerate_faces','remove_unreferenced_vertices'):
        try: getattr(mesh,step)()
        except Exception: pass
    try: trimesh.repair.fix_normals(mesh)
    except Exception: pass
    try: trimesh.repair.fill_holes(mesh)
    except Exception: pass
    report['watertight_after']=bool(mesh.is_watertight)
    report['n_vertices']=int(mesh.vertices.shape[0]); report['n_faces']=int(mesh.faces.shape[0])
    if verbose:
        print(f"[repair_mesh_for_slicing] watertight {report['watertight_before']} -> {report['watertight_after']}, "
              f"V={report['n_vertices']} F={report['n_faces']}, weld_tol={weld_tol:.2e} mm")
    return mesh, report

def load_step_as_mesh(step_path, voxel_size=0.2, linear_deflection=None, angular_deflection=0.3):
    """Tessellate a STEP/STP B-rep CAD file (NURBS surfaces, not triangles) into a triangle
    mesh via OpenCASCADE, through the optional 'cadquery' package. STEP cannot be parsed by
    trimesh directly -- this must run before any slicing/voxelization code. linear_deflection
    controls tessellation fineness (mm); defaults to voxel_size/4 so the tessellation is finer
    than the voxel grid it will be sliced into."""
    _require_cadquery('load_step_as_mesh'); _require_trimesh('load_step_as_mesh')
    if linear_deflection is None: linear_deflection=max(voxel_size/4.0,1e-4)
    wp=_cq.importers.importStep(str(step_path))
    solids=wp.solids().vals()
    if not solids: solids=wp.vals()
    if not solids: raise ValueError(f'No solid geometry found in STEP file: {step_path}')
    parts=[]
    for solid in solids:
        verts,faces=solid.tessellate(linear_deflection,angular_deflection)
        v=np.array([[p.x,p.y,p.z] for p in verts],float); f=np.array(faces,int)
        parts.append(trimesh.Trimesh(vertices=v,faces=f,process=False))
    return trimesh.util.concatenate(parts) if len(parts)>1 else parts[0]

def _legacy_scanline_voxelize(mesh, voxel_size, vtol_frac=5e-4):
    """Plane-slicing voxelizer (the original method, now defended by the vtol dead-zone in
    vectorized_segments). Always available given trimesh alone. Returns
    (volume, spacing, bmin, bmax, qa_report) where qa_report lists any slices that still hit
    an odd-parity scanline row after the fix, so residual problem slices are directly
    identifiable."""
    tri=np.asarray(mesh.triangles,float)
    bmin=tri.reshape(-1,3).min(0); bmax=tri.reshape(-1,3).max(0); ext=np.maximum(bmax-bmin,voxel_size)
    nx,ny,nz=[max(1,int(math.ceil(v/voxel_size))) for v in ext]
    xmax,ymax,zmax=bmin+np.array([nx,ny,nz])*voxel_size
    zc=bmin[2]+(np.arange(nz)+.5)*voxel_size
    zmin_tri=tri[:,:,2].min(1); zmax_tri=tri[:,:,2].max(1)
    vtol=max(voxel_size*vtol_frac,1e-7)
    slices=[]; odd_total=0; odd_slices=[]
    for k,z in enumerate(zc):
        a=(zmin_tri<=z+1e-9)&(zmax_tri>z-1e-9)
        seg=vectorized_segments(tri[a],float(z),vtol=vtol)
        m,qa=rasterize_segments_scanline(seg,bmin[0],bmin[1],xmax,ymax,nx,ny)
        odd_total+=qa['odd_rows']
        if qa['odd_rows']>0: odd_slices.append({'slice_index':int(k),'z_mm':float(z),'odd_rows':int(qa['odd_rows'])})
        slices.append(m)
    vol=np.stack(slices).astype(bool)
    qa_report={'odd_scanline_rows_total':int(odd_total),'odd_scanline_slices':odd_slices[:50],
               'n_odd_slices':len(odd_slices),'n_slices':int(nz),'vtol_mm':vtol}
    return vol,(voxel_size,voxel_size,voxel_size),bmin,bmax,qa_report

def _trimesh_fill_voxelize(mesh, voxel_size):
    """Flood-fill solid voxelization (trimesh.voxelized(pitch).fill()). Does not rely on
    scanline parity at all, so it is robust to self-intersecting / non-boolean-unioned strut
    meshes -- a common source of noisy slices in architected-lattice CAD exports that vertex
    welding alone cannot fix. Preferred backend when available (backend='auto', the default).
    NOTE: trimesh.voxelized() only accepts a single isotropic pitch -- it cannot honor
    pixels_per_side/layer_slice_percent (independently-sized XY pixels vs. Z layers); see
    load_mesh_as_voxels()."""
    vg=mesh.voxelized(pitch=voxel_size).fill()
    vol=np.asarray(vg.matrix,bool)
    try: bmin=np.asarray(vg.bounds[0],float)
    except Exception: bmin=np.asarray(mesh.bounds[0],float)
    return vol,(voxel_size,voxel_size,voxel_size),bmin

def _anisotropic_grid_spec(bmin, bmax, pixels_per_side=None, layer_slice_percent=None,
                           fallback_voxel_size=0.2, crop_cube_size_mm=None):
    """Resolve the explicit mesh-slicing grid.

    Centered-cube workflow:
      1) detect the STL six-face bounding box and its center,
      2) define a fixed L x L x L field of view centered there,
      3) nx = ny = IMAGE_PIXELS_PER_SIDE,
      4) dx = dy = L / IMAGE_PIXELS_PER_SIDE,
      5) dz = L * (LAYER_SLICE_PERCENT / 100),
      6) sample 0%, P%, 2P%, ... 100% of the cube height, so
         nz = 100 / P + 1 (P must divide 100 exactly).

    Example: L=30 mm and P=5 gives dz=1.5 mm and nz=21.  The number of z planes therefore
    depends on the percentage, not on an absolute 0.05-mm pitch.
    """
    source_bmin=np.asarray(bmin,float); source_bmax=np.asarray(bmax,float)
    source_ext=source_bmax-source_bmin
    source_center=(source_bmin+source_bmax)/2.0

    if crop_cube_size_mm is not None:
        L=float(crop_cube_size_mm)
        if not np.isfinite(L) or L<=0:
            raise ValueError(f'crop_cube_size_mm must be > 0, got {crop_cube_size_mm!r}')
        grid_bmin=source_center-L/2.0
        grid_bmax=source_center+L/2.0
        ext=np.array([L,L,L],float)
    else:
        L=None
        grid_bmin=source_bmin.copy(); grid_bmax=source_bmax.copy(); ext=source_ext.copy()

    if pixels_per_side is not None and pixels_per_side > 0:
        nx=ny=int(pixels_per_side)
        vx=ext[0]/nx if ext[0]>0 else fallback_voxel_size
        vy=ext[1]/ny if ext[1]>0 else fallback_voxel_size
    else:
        nx=max(1,int(math.ceil(ext[0]/fallback_voxel_size)))
        ny=max(1,int(math.ceil(ext[1]/fallback_voxel_size)))
        vx=vy=fallback_voxel_size

    if layer_slice_percent is not None:
        pct=float(layer_slice_percent)
        if not np.isfinite(pct) or pct<=0 or pct>100:
            raise ValueError(f'LAYER_SLICE_PERCENT must satisfy 0 < percent <= 100, got {layer_slice_percent!r}')
        n_intervals_float=100.0/pct
        n_intervals=int(round(n_intervals_float))
        if not math.isclose(n_intervals_float,n_intervals,rel_tol=0.0,abs_tol=1e-10):
            raise ValueError(
                f'LAYER_SLICE_PERCENT={pct:g}% must divide 100% exactly so that both cube z faces '
                f'are included. 100/{pct:g}={n_intervals_float:.12g} is not an integer.'
            )
        reference_height=float(ext[2])
        vz=reference_height*pct/100.0
        nz=n_intervals+1
        z_mode='edge'
    else:
        vz=fallback_voxel_size
        nz=max(1,int(math.ceil(ext[2]/vz)))
        z_mode='center'
        pct=None

    return {
        'nx':nx,'ny':ny,'nz':nz,'vx':vx,'vy':vy,'vz':vz,'z_mode':z_mode,
        'layer_slice_percent':pct,
        'source_bmin':source_bmin,'source_bmax':source_bmax,'source_center':source_center,
        'bmin':grid_bmin,'bmax':grid_bmax,'crop_cube_size_mm':L,
        'extent_x_mm':float(grid_bmax[0]-grid_bmin[0]),
        'extent_y_mm':float(grid_bmax[1]-grid_bmin[1]),
        'extent_z_mm':float(grid_bmax[2]-grid_bmin[2]),
    }

def _legacy_scanline_voxelize_grid(mesh, grid, vtol_frac=5e-4):
    """Generalization of _legacy_scanline_voxelize() that accepts an explicit, possibly
    anisotropic grid spec (see _anisotropic_grid_spec) instead of a single voxel_size -- used
    when pixels_per_side / layer_slice_percent drive the resolution. The underlying
    slicing math (vectorized_segments/rasterize_segments_scanline) already supports
    independent X/Y pixel pitch, so this only generalizes the grid bookkeeping; the original
    isotropic _legacy_scanline_voxelize is left untouched to avoid disturbing its validated
    (v4.1) behavior."""
    tri=np.asarray(mesh.triangles,float)
    mesh_bmin=tri.reshape(-1,3).min(0); mesh_bmax=tri.reshape(-1,3).max(0)
    bmin=np.asarray(grid.get('bmin',mesh_bmin),float); bmax=np.asarray(grid.get('bmax',mesh_bmax),float)
    nx,ny,nz=grid['nx'],grid['ny'],grid['nz']; vx,vy,vz=grid['vx'],grid['vy'],grid['vz']
    xmax=bmin[0]+nx*vx; ymax=bmin[1]+ny*vy
    if grid.get('z_mode')=='edge':
        zc=bmin[2]+np.arange(nz)*vz
    else:
        zc=bmin[2]+(np.arange(nz)+.5)*vz
    zmin_tri=tri[:,:,2].min(1); zmax_tri=tri[:,:,2].max(1)
    vtol=max(min(vx,vy,vz)*vtol_frac,1e-7)
    slices=[]; odd_total=0; odd_slices=[]
    for k,z in enumerate(zc):
        a=(zmin_tri<=z+1e-9)&(zmax_tri>z-1e-9)
        seg=vectorized_segments(tri[a],float(z),vtol=vtol)
        m,qa=rasterize_segments_scanline(seg,bmin[0],bmin[1],xmax,ymax,nx,ny)
        odd_total+=qa['odd_rows']
        if qa['odd_rows']>0: odd_slices.append({'slice_index':int(k),'z_mm':float(z),'odd_rows':int(qa['odd_rows'])})
        slices.append(m)
    vol=np.stack(slices).astype(bool)
    qa_report={'odd_scanline_rows_total':int(odd_total),'odd_scanline_slices':odd_slices[:50],
               'n_odd_slices':len(odd_slices),'n_slices':int(nz),'vtol_mm':vtol,
               'pixel_pitch_x_mm':vx,'pixel_pitch_y_mm':vy,'layer_pitch_z_mm':vz,
               'pixels_per_side_x':nx,'pixels_per_side_y':ny,
               'grid_bounds_mm':[bmin.tolist(),bmax.tolist()],
               'grid_extent_xyz_mm':(bmax-bmin).tolist(),
               'z_mode':grid.get('z_mode','center'),'layer_slice_percent':grid.get('layer_slice_percent')}
    return vol,(vz,vy,vx),bmin,bmax,qa_report

def load_mesh_as_voxels(mesh_path, voxel_size=0.2, backend='auto', repair=True, verbose=False,
                         pixels_per_side=None, layer_slice_percent=None, crop_cube_size_mm=None):
    """Import a mesh -- or a STEP/STP CAD file, tessellated first via load_step_as_mesh -- and
    voxelize it for slicing-based descriptor extraction.

    backend: 'auto' (default) tries the robust flood-fill voxelizer first and sanity-checks it
        against the mesh's own analytic volume, falling back to the plane-slicing scanline
        method (now fixed, see vectorized_segments) if flood-fill is unavailable, raises, or
        fails the sanity check. 'trimesh_fill' or 'legacy_scanline' force one method.
    repair: run repair_mesh_for_slicing() (vertex welding + normal/hole repair) first. This is
        the primary fix for the 'jumping slice' artifact -- leave True unless the mesh is
        already known-clean.
    pixels_per_side: fixed X/Y pixel count. With crop_cube_size_mm=L, the physical pitch is
        dx=dy=L/pixels_per_side.
    layer_slice_percent: z slicing interval as a percentage of the crop height. With crop_cube_size_mm=L,
        dz=L*(percent/100) and nz=100/percent+1, with both cube z faces included.
    crop_cube_size_mm: centered physical field-of-view side length L. The original STL six-face
        bounding box is detected, its midpoint defines the crop center, and bounds are center±L/2.
        Geometry outside this cube is cropped; missing geometry inside a larger cube remains empty.
    Setting any explicit-grid argument switches to the scanline backend because trimesh's
    flood-fill voxelizer accepts only one isotropic pitch.
    Because trimesh's flood-fill voxelizer only accepts one isotropic pitch, this forces
    backend='legacy_scanline' (silently, under backend='auto'; passing backend='trimesh_fill'
    explicitly together with either argument raises ValueError instead of silently ignoring
    the request).
    """
    _require_trimesh('load_mesh_as_voxels')
    anisotropic_mode = pixels_per_side is not None or layer_slice_percent is not None or crop_cube_size_mm is not None
    if anisotropic_mode and backend=='trimesh_fill':
        raise ValueError(
            "backend='trimesh_fill' does not support the explicit fixed-grid crop (pixels_per_side/layer_slice_percent/crop_cube_size_mm) "
            "(trimesh.voxelized() only accepts a single isotropic pitch). Use backend='legacy_scanline' "
            "(or 'auto', which falls back automatically), or drop these two arguments and use voxel_size instead."
        )
    mesh_path=Path(mesh_path); suffix=mesh_path.suffix.lower()
    if suffix in STEP_EXTS:
        mesh=load_step_as_mesh(mesh_path, voxel_size=voxel_size)
    else:
        mesh=_scene_to_mesh(trimesh.load(mesh_path,force='mesh',process=True))
    mesh.remove_unreferenced_vertices()
    # Source six-face boundary and center are captured BEFORE any crop is defined.
    source_bmin=np.asarray(mesh.bounds[0],float); source_bmax=np.asarray(mesh.bounds[1],float)
    source_center=(source_bmin+source_bmax)/2.0

    repair_report={'repaired':False}
    if repair:
        mesh,repair_report=repair_mesh_for_slicing(mesh, voxel_size=voxel_size, verbose=verbose)
        repair_report['repaired']=True

    qa={}; vol=None; bmin=None; bmax=None; backend_used=None
    if anisotropic_mode:
        if verbose and backend=='auto':
            print("[load_mesh_as_voxels] explicit crop/pixel/layer grid requested -> "
                  "using backend='legacy_scanline' (trimesh_fill only supports isotropic pitch).")
        # Use the originally detected STL six-face boundary center.  Repair is allowed to clean
        # topology, but it does not redefine the user's requested crop center.
        grid=_anisotropic_grid_spec(source_bmin,source_bmax,pixels_per_side,layer_slice_percent,
                                    voxel_size,crop_cube_size_mm=crop_cube_size_mm)
        vol,spacing,bmin,bmax,scan_qa=_legacy_scanline_voxelize_grid(mesh,grid)
        backend_used='legacy_scanline'; qa.update(scan_qa)
        qa['grid_mode']='centered_cube/pixels_per_side/layer_slice_percent' if crop_cube_size_mm is not None else 'pixels_per_side/layer_slice_percent'
    else:
        if backend in ('auto','trimesh_fill'):
            try:
                vol,spacing,bmin=_trimesh_fill_voxelize(mesh, voxel_size)
                tri=np.asarray(mesh.triangles,float); bmax=tri.reshape(-1,3).max(0)
                expected_vox=(abs(float(mesh.volume))/(voxel_size**3)) if mesh.is_watertight else None
                actual_vox=int(vol.sum())
                sane=actual_vox>0 and (expected_vox is None or 0.2<=actual_vox/max(expected_vox,1e-9)<=5.0)
                if not sane:
                    raise RuntimeError(f'trimesh_fill sanity check failed: filled_voxels={actual_vox}, expected~{expected_vox}')
                backend_used='trimesh_fill'
                qa={'backend_sanity_check':'passed','expected_voxels_from_mesh_volume':expected_vox,'actual_filled_voxels':actual_vox}
            except Exception as ex:
                if backend=='trimesh_fill': raise
                qa={'trimesh_fill_fallback_reason':str(ex)}; vol=None
        if vol is None:
            vol,spacing,bmin,bmax,scan_qa=_legacy_scanline_voxelize(mesh, voxel_size)
            backend_used='legacy_scanline'; qa.update(scan_qa)
    if bmax is None:
        tri=np.asarray(mesh.triangles,float); bmax=tri.reshape(-1,3).max(0)

    meta={'source_type':'mesh','source':str(mesh_path),'source_format':suffix,
          'mesh_bounds_mm':[source_bmin.tolist(),source_bmax.tolist()],
          'mesh_center_mm':source_center.tolist(),
          'crop_cube_size_mm':crop_cube_size_mm,
          'crop_bounds_mm':[np.asarray(bmin).tolist(),np.asarray(bmax).tolist()],
          'grid_extent_xyz_mm':(np.asarray(bmax)-np.asarray(bmin)).tolist(),
          'grid_shape_zyx':[int(v) for v in vol.shape],
          'spacing_zyx_mm':[float(v) for v in spacing],
          'z_sampling_mode':qa.get('z_mode','center'),
          'voxelization_backend':backend_used,'mesh_repair':repair_report,'slicing_qa':qa,
          'odd_scanline_rows':qa.get('odd_scanline_rows_total',0),
          'pixels_per_side':pixels_per_side,'layer_slice_percent':layer_slice_percent}
    if verbose:
        print(f"[load_mesh_as_voxels] backend={backend_used} shape={vol.shape} density={vol.mean():.4f} spacing(z,y,x)={spacing}")
        if crop_cube_size_mm is not None:
            print(f"  source bounds={source_bmin.tolist()} .. {source_bmax.tolist()} center={source_center.tolist()}")
            print(f"  centered crop L={float(crop_cube_size_mm):g} mm bounds={np.asarray(bmin).tolist()} .. {np.asarray(bmax).tolist()}")
        if qa.get('n_odd_slices'):
            hint = "" if anisotropic_mode else " -- consider backend='trimesh_fill'"
            print(f"  odd-parity rows remain on {qa['n_odd_slices']}/{qa.get('n_slices','?')} slices after repair "
                  f"(see meta['slicing_qa']['odd_scanline_slices']){hint}")
    return vol,spacing,meta

def shape_based_z_interpolation(volume,spacing,factor=1):
    if factor<=1: return volume,spacing
    z,y,x=volume.shape; out=[]
    for i in range(z-1):
        a=volume[i]; b=volume[i+1]
        da=ndi.distance_transform_edt(a)-ndi.distance_transform_edt(~a)
        db=ndi.distance_transform_edt(b)-ndi.distance_transform_edt(~b)
        for j in range(factor):
            t=j/factor; out.append(((1-t)*da+t*db)>=0)
    out.append(volume[-1]); return np.stack(out), (spacing[0]/factor,spacing[1],spacing[2])

def preprocess_volume(volume,min_component_voxels=1,fill_holes=False):
    v=volume.astype(bool)
    if min_component_voxels>1:
        lab,n=ndi.label(v,structure=ndi.generate_binary_structure(3,1)); cnt=np.bincount(lab.ravel()); keep=np.where(cnt>=min_component_voxels)[0]; keep=keep[keep!=0]; v=np.isin(lab,keep)
    if fill_holes: v=ndi.binary_fill_holes(v)
    return v

# ----------------------------- statistics -----------------------------
def safe_div(a,b): return float(a/b) if abs(float(b))>EPS else np.nan

def qstats(values,prefix,extra=True):
    a=np.asarray(values,float); a=a[np.isfinite(a)]
    keys={}
    if a.size==0:
        base=['n','mean','std','min','q01','q05','q10','q25','median','q75','q90','q95','q99','max','iqr','range','cv','skew','kurtosis','rms','mad']
        return {f'{prefix}_{k}':np.nan for k in base}
    q=np.quantile(a,[.01,.05,.10,.25,.5,.75,.9,.95,.99])
    mean=float(a.mean()); std=float(a.std(ddof=0)); med=float(q[4]); mad=float(np.median(np.abs(a-med)))
    keys.update(n=int(a.size),mean=mean,std=std,min=float(a.min()),q01=float(q[0]),q05=float(q[1]),q10=float(q[2]),q25=float(q[3]),median=med,q75=float(q[5]),q90=float(q[6]),q95=float(q[7]),q99=float(q[8]),max=float(a.max()),iqr=float(q[5]-q[3]),range=float(a.max()-a.min()),cv=safe_div(std,abs(mean)),skew=float(skew(a,bias=False)) if a.size>2 else np.nan,kurtosis=float(kurtosis(a,bias=False)) if a.size>3 else np.nan,rms=float(np.sqrt(np.mean(a*a))),mad=mad)
    return {f'{prefix}_{k}':v for k,v in keys.items()}

def profile_stats(values,prefix):
    d=qstats(values,prefix); a=np.asarray(values,float); a=a[np.isfinite(a)]
    if len(a)>=2:
        x=np.arange(len(a)); p=np.polyfit(x,a,1); d[f'{prefix}_slope']=float(p[0]); d[f'{prefix}_lag1_corr']=float(np.corrcoef(a[:-1],a[1:])[0,1]) if np.std(a[:-1])>0 and np.std(a[1:])>0 else np.nan
        d[f'{prefix}_mean_abs_gradient']=float(np.mean(np.abs(np.diff(a)))); d[f'{prefix}_gradient_rms']=float(np.sqrt(np.mean(np.diff(a)**2)))
    if len(a)>=3: d[f'{prefix}_mean_abs_second_gradient']=float(np.mean(np.abs(np.diff(a,n=2))))
    return d

def normalized_entropy(counts):
    c=np.asarray(counts,float); c=c[c>0]
    if len(c)<=1: return 0.0
    p=c/c.sum(); return float(-(p*np.log(p)).sum()/np.log(len(c)))

# ----------------------------- slice descriptors -----------------------------
def _largest_region(mask):
    lab=measure.label(mask,connectivity=2); props=regionprops(lab)
    return max(props,key=lambda r:r.area) if props else None

def slice_descriptor_table(volume,spacing,z_origin_mm=0.0,z_mode='center'):
    dz,dy,dx=spacing; rows=[]
    for z,m in enumerate(volume):
        area=m.sum()*dx*dy; frac=m.mean(); per=measure.perimeter(m,neighborhood=8)*math.sqrt(dx*dy); lab=measure.label(m,connectivity=2); props=regionprops(lab)
        eul=measure.euler_number(m,connectivity=2); lr=max(props,key=lambda r:r.area) if props else None
        z_rel=(z*dz) if z_mode=='edge' else ((z+.5)*dz)
        row={'slice_index':z,'z_mm':z_rel,'z_absolute_mm':float(z_origin_mm)+z_rel,'area_fraction':frac,'area_mm2':area,'perimeter_mm':per,'specific_perimeter_per_mm':safe_div(per,area),'component_count':len(props),'euler_number':eul,'hole_count_proxy':len(props)-eul}
        if lr:
            cy,cx0=lr.centroid; row.update(largest_area_fraction=lr.area/m.size,largest_solidity=lr.solidity,largest_extent=lr.extent,largest_eccentricity=lr.eccentricity,largest_orientation_rad=lr.orientation,largest_equiv_diameter_mm=lr.equivalent_diameter_area*math.sqrt(dx*dy),largest_major_axis_mm=lr.axis_major_length*math.sqrt(dx*dy),largest_minor_axis_mm=lr.axis_minor_length*math.sqrt(dx*dy),centroid_x_norm=cx0/max(1,m.shape[1]-1),centroid_y_norm=cy/max(1,m.shape[0]-1),largest_circularity=safe_div(4*math.pi*lr.area,measure.perimeter(lr.image,neighborhood=8)**2))
        else:
            for k in ['largest_area_fraction','largest_solidity','largest_extent','largest_eccentricity','largest_orientation_rad','largest_equiv_diameter_mm','largest_major_axis_mm','largest_minor_axis_mm','centroid_x_norm','centroid_y_norm','largest_circularity']: row[k]=np.nan
        rows.append(row)
    df=pd.DataFrame(rows); out={}
    for c in df.columns:
        if c not in {'slice_index','z_mm','z_absolute_mm'}: out.update(profile_stats(df[c].values,f'slice_{c}'))
    return df,out

def projection_texture_descriptors(volume):
    out={}
    projections={'xy_occ':volume.mean(0),'xz_occ':volume.mean(1),'yz_occ':volume.mean(2),'xy_mip':volume.max(0).astype(float),'xz_mip':volume.max(1).astype(float),'yz_mip':volume.max(2).astype(float)}
    for name,imgf in projections.items():
        img=np.clip(np.round(imgf*255),0,255).astype(np.uint8)
        # quantize to 16 levels for stable GLCM
        q=(img//16).astype(np.uint8)
        gl=feature.graycomatrix(q,[1,2,4],[0,np.pi/4,np.pi/2,3*np.pi/4],levels=16,symmetric=True,normed=True)
        for prop in ['contrast','dissimilarity','homogeneity','ASM','energy','correlation']:
            vals=feature.graycoprops(gl,prop).ravel(); out.update(qstats(vals,f'proj_{name}_glcm_{prop}'))
        # image moments / Hu
        M=measure.moments(imgf); hu=measure.moments_hu(measure.moments_normalized(measure.moments_central(imgf)))
        for i,v in enumerate(hu): out[f'proj_{name}_hu{i+1}']=float(v)
        out[f'proj_{name}_entropy']=float(measure.shannon_entropy(img))
        gy,gx=np.gradient(imgf.astype(float)); gm=np.hypot(gx,gy); out.update(qstats(gm.ravel(),f'proj_{name}_gradient'))
    return out

# ----------------------------- pair / triplet -----------------------------
def pair_descriptor_table(volume,spacing):
    dz,dy,dx=spacing; rows=[]
    for i in range(len(volume)-1):
        a=volume[i]; b=volume[i+1]; inter=a&b; union=a|b; ao=a&~b; bo=b&~a
        ca=np.argwhere(a); cb=np.argwhere(b); shift=np.nan
        if len(ca) and len(cb): shift=float(np.linalg.norm((ca.mean(0)-cb.mean(0))*np.array([dy,dx])))
        # symmetric boundary distances
        ba=a^ndi.binary_erosion(a); bb=b^ndi.binary_erosion(b); d_ab=d_ba=np.nan
        if ba.any() and bb.any():
            db=ndi.distance_transform_edt(~bb,sampling=(dy,dx)); da=ndi.distance_transform_edt(~ba,sampling=(dy,dx)); d_ab=float(db[ba].mean()); d_ba=float(da[bb].mean())
        rows.append({'pair_index':i,'lower_fraction':a.mean(),'upper_fraction':b.mean(),'intersection_fraction':inter.mean(),'union_fraction':union.mean(),'red_lower_only_fraction':ao.mean(),'blue_upper_only_fraction':bo.mean(),'jaccard':safe_div(inter.sum(),union.sum()),'dice':safe_div(2*inter.sum(),a.sum()+b.sum()),'overlap_coefficient':safe_div(inter.sum(),min(a.sum(),b.sum())),'containment_lower_in_upper':safe_div(inter.sum(),a.sum()),'containment_upper_in_lower':safe_div(inter.sum(),b.sum()),'symmetric_difference_fraction':(a^b).mean(),'signed_area_change_fraction':b.mean()-a.mean(),'absolute_area_change_fraction':abs(b.mean()-a.mean()),'centroid_shift_mm':shift,'boundary_mean_distance_lower_to_upper_mm':d_ab,'boundary_mean_distance_upper_to_lower_mm':d_ba,'boundary_mean_distance_symmetric_mm':np.nanmean([d_ab,d_ba])})
    df=pd.DataFrame(rows); out={}
    for c in df.columns:
        if c!='pair_index': out.update(profile_stats(df[c].values,f'pair_{c}'))
    return df,out

def triplet_state(a,b,c): return (a.astype(np.uint8)<<2)|(b.astype(np.uint8)<<1)|c.astype(np.uint8)

def _interface_count(label_img,p,q):
    cnt=0
    for ax in (0,1):
        s1=[slice(None)]*2; s2=[slice(None)]*2; s1[ax]=slice(None,-1); s2[ax]=slice(1,None)
        x=label_img[tuple(s1)]; y=label_img[tuple(s2)]; cnt+=np.count_nonzero(((x==p)&(y==q))|((x==q)&(y==p)))
    return int(cnt)

def triplet_descriptor_table(volume,spacing,save_dir=None,image_stride=1):
    dz,dy,dx=spacing; rows=[]; save_dir=Path(save_dir) if save_dir else None
    if save_dir: save_dir.mkdir(parents=True,exist_ok=True)
    for i in range(len(volume)-2):
        s=triplet_state(volume[i],volume[i+1],volume[i+2]); cnt=np.bincount(s.ravel(),minlength=8); occ=cnt[1:].sum(); center=volume[i+1].sum(); abc=cnt[3]+cnt[6]+cnt[7]
        row={'triplet_index':i}
        for k in range(8): row[f'state_{k:03b}_count']=int(cnt[k]); row[f'state_{k:03b}_fraction_all']=cnt[k]/s.size
        for k in range(1,8): row[f'state_{k:03b}_fraction_occupied']=safe_div(cnt[k],occ)
        A,B,C=cnt[7],cnt[6],cnt[3]
        row.update(A_111_fraction_all=A/s.size,B_110_fraction_all=B/s.size,C_011_fraction_all=C/s.size,ABC_fraction_all=abc/s.size,A_fraction_center=safe_div(A,center),B_fraction_center=safe_div(B,center),C_fraction_center=safe_div(C,center),two_sided_persistence_center=safe_div(A,center),adjacent_persistence_center=safe_div(A+B+C,center),growth_decay_balance=safe_div(C-B,B+C),gap_reentry_fraction_all=cnt[5]/s.size,triplet_entropy_occupied=normalized_entropy(cnt[1:]),triplet_entropy_all=normalized_entropy(cnt))
        for state,name in [(7,'A111'),(6,'B110'),(3,'C011'),(5,'gap101')]:
            m=s==state; lab=measure.label(m,connectivity=2); props=regionprops(lab); row[f'{name}_component_count']=len(props); row[f'{name}_perimeter_px']=measure.perimeter(m,neighborhood=8)
            if props:
                areas=np.array([p.area for p in props]); row[f'{name}_largest_component_fraction']=areas.max()/max(1,m.sum()); row[f'{name}_component_area_cv']=safe_div(areas.std(),areas.mean())
            else: row[f'{name}_largest_component_fraction']=0.; row[f'{name}_component_area_cv']=np.nan
        row['interface_A_B_edges']=_interface_count(s,7,6); row['interface_A_C_edges']=_interface_count(s,7,3); row['interface_B_C_edges']=_interface_count(s,6,3)
        rows.append(row)
        if save_dir and i%image_stride==0:
            Image.fromarray(np.round(s/7*255).astype(np.uint8)).save(save_dir/f'triplet_{i:05d}_8state.png')
            abcimg=np.zeros_like(s,np.uint8); abcimg[s==7]=255; abcimg[s==6]=170; abcimg[s==3]=85; Image.fromarray(abcimg).save(save_dir/f'triplet_{i:05d}_ABC.png')
    df=pd.DataFrame(rows); out={}
    for c in df.columns:
        if c!='triplet_index': out.update(profile_stats(df[c].values,f'triplet_{c}'))
    return df,out

def multilevel_persistence_descriptors(volume,max_k=7):
    out={}; n=len(volume)
    for k in range(2,min(max_k,n)+1):
        vals_iou=[]; vals_min=[]; vals_center=[]
        for i in range(n-k+1):
            w=volume[i:i+k]; inter=np.logical_and.reduce(w); union=np.logical_or.reduce(w); occ=np.array([x.sum() for x in w]); vals_iou.append(safe_div(inter.sum(),union.sum())); vals_min.append(safe_div(inter.sum(),occ.min()))
            vals_center.append(safe_div(inter.sum(),w[k//2].sum()))
        out.update(profile_stats(vals_iou,f'persist_k{k}_intersection_over_union')); out.update(profile_stats(vals_min,f'persist_k{k}_intersection_over_min')); out.update(profile_stats(vals_center,f'persist_k{k}_intersection_over_center'))
    return out

def lag_overlap_descriptors(volume,max_lag=12):
    out={}; n=len(volume)
    for lag in range(1,min(max_lag,n-1)+1):
        jac=[]; dice=[]; sym=[]; mi=[]
        for i in range(n-lag):
            a=volume[i]; b=volume[i+lag]; inter=(a&b).sum(); union=(a|b).sum(); jac.append(safe_div(inter,union)); dice.append(safe_div(2*inter,a.sum()+b.sum())); sym.append((a^b).mean())
            # binary mutual information
            c00=np.count_nonzero(~a&~b); c01=np.count_nonzero(~a&b); c10=np.count_nonzero(a&~b); c11=np.count_nonzero(a&b); tab=np.array([[c00,c01],[c10,c11]],float); p=tab/tab.sum(); pa=p.sum(1); pb=p.sum(0); val=0
            for x in range(2):
                for y in range(2):
                    if p[x,y]>0: val+=p[x,y]*math.log(p[x,y]/(pa[x]*pb[y]+EPS)+EPS)
            mi.append(val)
        out.update(profile_stats(jac,f'lag{lag}_jaccard')); out.update(profile_stats(dice,f'lag{lag}_dice')); out.update(profile_stats(sym,f'lag{lag}_symdiff')); out.update(profile_stats(mi,f'lag{lag}_mutual_information'))
    # overlap-decay summaries
    means=np.array([out.get(f'lag{l}_jaccard_mean',np.nan) for l in range(1,min(max_lag,n-1)+1)])
    if np.isfinite(means).sum()>=2:
        out['lag_jaccard_decay_auc']=float(np.nansum(means)); out['lag_jaccard_decay_slope']=float(np.polyfit(np.arange(1,len(means)+1)[np.isfinite(means)],means[np.isfinite(means)],1)[0])
    return out

def triplet_transition_descriptors(volume):
    if len(volume)<4: return {}
    states=[triplet_state(volume[i],volume[i+1],volume[i+2]) for i in range(len(volume)-2)]; M=np.zeros((8,8),np.int64)
    for a,b in zip(states[:-1],states[1:]):
        idx=(a.ravel().astype(int)*8+b.ravel().astype(int)); M+=np.bincount(idx,minlength=64).reshape(8,8)
    out={}
    p=M/M.sum() if M.sum() else M.astype(float)
    for i in range(8):
        out[f'tspe_transition_from_{i:03b}_self_probability']=safe_div(M[i,i],M[i].sum())
        out[f'tspe_transition_from_{i:03b}_entropy']=normalized_entropy(M[i])
    out['tspe_transition_global_entropy']=normalized_entropy(M.ravel()); out['tspe_transition_diagonal_fraction']=safe_div(np.trace(M),M.sum()); out['tspe_transition_A111_persistence']=safe_div(M[7,7],M[7].sum()); out['tspe_transition_B110_to_A111']=safe_div(M[6,7],M[6].sum()); out['tspe_transition_A111_to_C011']=safe_div(M[7,3],M[7].sum())
    # full 64 transition probabilities for exhaustive feature pool
    for i in range(8):
        for j in range(8): out[f'tspe_T_{i:03b}_to_{j:03b}_fraction']=float(p[i,j]) if M.sum() else np.nan
    return out

# ----------------------------- 3D global morphology/topology -----------------------------
def marching_mesh(volume,spacing):
    if not volume.any() or volume.all(): return None
    _require_trimesh('marching_mesh')
    verts,faces,normals,vals=measure.marching_cubes(volume.astype(np.uint8),level=.5,spacing=spacing)
    # skimage coordinates are z,y,x; convert xyz
    verts_xyz=verts[:,[2,1,0]]; return trimesh.Trimesh(vertices=verts_xyz,faces=faces,process=False)

def morphology3d_descriptors(volume,spacing,grid_extent_xyz_mm=None,z_edge_inclusive=False):
    dz,dy,dx=spacing; vv=dz*dy*dx
    if grid_extent_xyz_mm is not None:
        gx,gy,gz=[float(v) for v in grid_extent_xyz_mm]; bbox=np.array([gz,gy,gx],float)
    else:
        bbox=np.array(volume.shape,dtype=float)*np.array(spacing,float)
        if z_edge_inclusive and volume.shape[0]>1:
            bbox[0]=(volume.shape[0]-1)*dz
    bboxV=float(np.prod(bbox))
    if z_edge_inclusive and volume.shape[0]>1:
        # The z array stores physical sampling planes including both cube faces.  Integrate
        # cross-sectional area with half-weighted endpoints instead of treating N planes as N
        # full dz-thick cells; a completely solid L-cube therefore has exactly L^3 volume.
        slice_area=volume.sum(axis=(1,2)).astype(float)*dx*dy
        V=float(np.trapezoid(slice_area,dx=dz)) if hasattr(np,'trapezoid') else float(np.trapz(slice_area,dx=dz))
        relative_density=safe_div(V,bboxV)
    else:
        V=float(volume.sum()*vv); relative_density=float(volume.mean())
    coords=np.argwhere(volume)
    out={'relative_density':relative_density,'solid_volume_mm3':V,'bbox_volume_mm3':bboxV,'bbox_fill_fraction':safe_div(V,bboxV),'void_fraction':1-relative_density,'bbox_x_mm':bbox[2],'bbox_y_mm':bbox[1],'bbox_z_mm':bbox[0]}
    if len(coords):
        # XY indices represent pixel cells, so use pixel centers.  In the centered-cube mesh
        # workflow Z is an edge-inclusive sampling-plane coordinate; otherwise use cell centers.
        x=(coords[:,2]+0.5)*dx; y=(coords[:,1]+0.5)*dy
        z=(coords[:,0]*dz) if z_edge_inclusive else ((coords[:,0]+0.5)*dz)
        xyz=np.column_stack([x,y,z]); cen=xyz.mean(0); C=np.cov(xyz,rowvar=False,bias=True); eig=np.sort(np.linalg.eigvalsh(C))[::-1]; out.update(centroid_x_mm=cen[0],centroid_y_mm=cen[1],centroid_z_mm=cen[2],radius_gyration_mm=float(np.sqrt(np.trace(C))),inertia_cov_eig1=float(eig[0]),inertia_cov_eig2=float(eig[1]),inertia_cov_eig3=float(eig[2]),inertia_anisotropy_13=safe_div(eig[0],eig[2]),inertia_planarity=safe_div(eig[1]-eig[2],eig[0]),inertia_linearity=safe_div(eig[0]-eig[1],eig[0]))
        # standardized coordinate moments
        for ax,name in enumerate('xyz'):
            vals=xyz[:,ax]; out.update(qstats(vals,f'coord_{name}'))
    try:
        mesh=marching_mesh(volume,spacing)
    except RuntimeError:
        mesh=None; out['surface_descriptors_skipped_no_trimesh']=1
    if mesh is not None:
        A=float(mesh.area); out.update(surface_area_mm2=A,specific_surface_area_per_mm=safe_div(A,V),surface_to_bbox_volume=safe_div(A,bboxV),sphericity=safe_div(math.pi**(1/3)*(6*V)**(2/3),A),compactness_36piV2_A3=safe_div(36*math.pi*V*V,A**3))
        try:
            hull=mesh.convex_hull; out['convex_hull_volume_mm3']=float(abs(hull.volume)); out['convex_hull_area_mm2']=float(hull.area); out['solidity_3d']=safe_div(V,abs(hull.volume)); out['convexity_area_ratio']=safe_div(hull.area,A)
        except Exception: pass
        # surface normal fabric and dihedral-angle statistics
        fn=np.asarray(mesh.face_normals); fa=np.asarray(mesh.area_faces); W=fa/fa.sum(); F=np.einsum('i,ij,ik->jk',W,fn,fn); ev=np.sort(np.linalg.eigvalsh(F))[::-1]
        for i,v in enumerate(ev,1): out[f'surface_fabric_eig{i}']=float(v)
        out['surface_fabric_fractional_anisotropy']=float(np.sqrt(1.5*np.sum((ev-ev.mean())**2)/(np.sum(ev**2)+EPS)))
        try:
            ang=np.asarray(mesh.face_adjacency_angles); out.update(qstats(ang,'surface_dihedral_angle_rad'))
        except Exception: pass
    return out

def topology_descriptors(volume):
    out={}
    for conn,name in [(1,'6'),(2,'18'),(3,'26')]:
        st=ndi.generate_binary_structure(3,conn); lab,n=ndi.label(volume,structure=st); out[f'solid_components_conn{name}']=int(n); vlab,vn=ndi.label(~volume,structure=st); out[f'void_components_conn{name}']=int(vn)
        spans={}
        for ax,axisname in enumerate('zyx'):
            a=np.unique(np.take(lab,0,axis=ax)); b=np.unique(np.take(lab,-1,axis=ax)); common=np.intersect1d(a[a>0],b[b>0]); spans[axisname]=len(common)
            out[f'solid_spanning_components_{axisname}_conn{name}']=int(len(common)); out[f'solid_percolates_{axisname}_conn{name}']=float(len(common)>0)
        # spanning material fraction
        if n:
            cnt=np.bincount(lab.ravel()); labels=np.arange(1,n+1); sp=set()
            for ax in range(3):
                a=np.unique(np.take(lab,0,axis=ax)); b=np.unique(np.take(lab,-1,axis=ax)); sp.update(np.intersect1d(a[a>0],b[b>0]).tolist())
            out[f'solid_spanning_voxel_fraction_conn{name}']=safe_div(sum(cnt[list(sp)]) if sp else 0,volume.sum())
    out['euler_number_conn6']=float(measure.euler_number(volume,connectivity=1)); out['euler_number_conn26']=float(measure.euler_number(volume,connectivity=3))
    # enclosed voids: remove void connected to boundary
    void=~volume; lab,n=ndi.label(void,structure=ndi.generate_binary_structure(3,1)); boundary=np.unique(np.concatenate([lab[0].ravel(),lab[-1].ravel(),lab[:,0].ravel(),lab[:,-1].ravel(),lab[:,:,0].ravel(),lab[:,:,-1].ravel()])); enclosed=[i for i in range(1,n+1) if i not in set(boundary.tolist())]; out['enclosed_void_count_conn6']=len(enclosed)
    if enclosed:
        cnt=np.bincount(lab.ravel()); out.update(qstats(cnt[enclosed],'enclosed_void_volume_vox'))
    # Betti proxy with cubical duality: beta0, beta2 and beta1 from Euler
    beta0=out['solid_components_conn6']; beta2=out['enclosed_void_count_conn6']; chi=out['euler_number_conn6']; out['betti0_proxy']=beta0; out['betti2_proxy']=beta2; out['betti1_proxy']=float(beta0+beta2-chi)
    return out

def euler_filtration_descriptors(volume,max_radius=6):
    out={}; vals=[]; radii=list(range(-max_radius,max_radius+1))
    for r in radii:
        if r<0: m=ndi.binary_erosion(volume,iterations=-r)
        elif r>0: m=ndi.binary_dilation(volume,iterations=r)
        else: m=volume
        e=float(measure.euler_number(m,connectivity=1)); vals.append(e); out[f'euler_filtration_r{r:+d}']=e
    a=np.asarray(vals); out['euler_filtration_auc']=float(_trapz(a,radii)); out['euler_filtration_range']=float(a.max()-a.min()); out['euler_filtration_zero_crossings']=int(np.count_nonzero(np.signbit(a[:-1])!=np.signbit(a[1:])))
    return out

# ----------------------------- size / thickness / granulometry -----------------------------
def distance_thickness_descriptors(volume,spacing,use_gpu=False,gpu_id=0):
    """Local solid/void distance descriptors. When CuPy/CUDA is available and use_gpu=True,
    the two exact Euclidean distance transforms run on the selected GPU; only scalar summaries
    (and skeleton-sampled values) are copied back to CPU."""
    if _gpu_ok(use_gpu,gpu_id):
        try:
            sk=morphology.skeletonize(volume)
            with cp.cuda.Device(int(gpu_id)):
                cv=cp.asarray(volume,dtype=cp.uint8)
                ds=cndi.distance_transform_edt(cv,sampling=spacing,float64_distances=False)
                out=_qstats_cupy(2.0*ds[cv.astype(bool)],'solid_local_thickness_proxy_mm')
                if sk.any():
                    csk=cp.asarray(sk)
                    out.update(_qstats_cupy(2.0*ds[csk],'skeleton_sampled_solid_thickness_mm'))
                    del csk
                del ds
                dv=cndi.distance_transform_edt(1-cv,sampling=spacing,float64_distances=False)
                out.update(_qstats_cupy(2.0*dv[(1-cv).astype(bool)],'void_local_diameter_proxy_mm'))
                del dv,cv
                cp.get_default_memory_pool().free_all_blocks()
            return out
        except Exception as e:
            warnings.warn(f'GPU distance transform failed on GPU {gpu_id}; CPU fallback: {e}')
    sampling=spacing; ds=ndi.distance_transform_edt(volume,sampling=sampling); dv=ndi.distance_transform_edt(~volume,sampling=sampling); out={}
    out.update(qstats(2*ds[volume],'solid_local_thickness_proxy_mm')); out.update(qstats(2*dv[~volume],'void_local_diameter_proxy_mm'))
    try:
        sk=morphology.skeletonize(volume); out.update(qstats(2*ds[sk],'skeleton_sampled_solid_thickness_mm'))
    except Exception: pass
    return out

def granulometry_descriptors(volume,max_radius=8,use_gpu=False,gpu_id=0):
    """Binary opening/closing granulometry. CUDA path uses cupyx.scipy.ndimage on one GPU."""
    if _gpu_ok(use_gpu,gpu_id):
        try:
            with cp.cuda.Device(int(gpu_id)):
                cv=cp.asarray(volume); base=max(1,int(cp.sum(cv).get())); cvoid=~cv; vbase=max(1,int(cp.sum(cvoid).get())); out={}
                for r in range(1,max_radius+1):
                    se=cp.asarray(morphology.ball(r))
                    op=cndi.binary_opening(cv,structure=se); cl=cndi.binary_closing(cv,structure=se)
                    out[f'granulo_solid_open_r{r}_retained_fraction']=float(cp.sum(op).get()/base)
                    out[f'granulo_solid_close_r{r}_volume_ratio']=float(cp.sum(cl).get()/base)
                    vop=cndi.binary_opening(cvoid,structure=se)
                    out[f'granulo_void_open_r{r}_retained_fraction']=float(cp.sum(vop).get()/vbase)
                    del se,op,cl,vop
                del cv,cvoid; cp.get_default_memory_pool().free_all_blocks()
            return out
        except Exception as e:
            warnings.warn(f'GPU granulometry failed on GPU {gpu_id}; CPU fallback: {e}')
    out={}; base=max(1,volume.sum()); vbase=max(1,(~volume).sum())
    for r in range(1,max_radius+1):
        se=morphology.ball(r); op=ndi.binary_opening(volume,structure=se); cl=ndi.binary_closing(volume,structure=se); out[f'granulo_solid_open_r{r}_retained_fraction']=op.sum()/base; out[f'granulo_solid_close_r{r}_volume_ratio']=cl.sum()/base
        vop=ndi.binary_opening(~volume,structure=se); out[f'granulo_void_open_r{r}_retained_fraction']=vop.sum()/vbase
    return out

# ----------------------------- chord / lineal / correlations -----------------------------
def _runs(line,phase=True):
    x=(line==phase).astype(np.int16); d=np.diff(np.r_[0,x,0]); starts=np.flatnonzero(d==1); ends=np.flatnonzero(d==-1); return ends-starts

def _runs_matrix(lines,phase=True):
    """Vectorized run-length extraction for a 2D [n_lines, line_length] boolean array.
    This replaces Python loops over up to one million XY lines in the 1000x1000 workflow."""
    x=(np.asarray(lines)==phase)
    if x.ndim!=2 or x.size==0: return np.array([],dtype=np.int32)
    padded=np.pad(x,((0,0),(1,1)),constant_values=False)
    d=np.diff(padded.astype(np.int8),axis=1)
    starts=np.argwhere(d==1); ends=np.argwhere(d==-1)
    if len(starts)!=len(ends):
        # Defensive fallback; should never happen because every row is False-padded at both ends.
        vals=[]
        for line in x: vals.extend(_runs(line,True).tolist())
        return np.asarray(vals,dtype=np.int32)
    return (ends[:,1]-starts[:,1]).astype(np.int32,copy=False)

def chord_descriptors(volume,spacing):
    out={}; names=['z','y','x']
    for ax,name in enumerate(names):
        pitch=spacing[ax]; arr=np.moveaxis(volume,ax,-1).reshape(-1,volume.shape[ax])
        for phase,pn in [(True,'solid'),(False,'void')]:
            vals=_runs_matrix(arr,phase).astype(float)*pitch
            out.update(qstats(vals,f'chord_{pn}_{name}_mm'))
    return out

def lineal_path_descriptors(volume,lengths=(1,2,4,8,16,32)):
    out={}
    for ax,name in enumerate('zyx'):
        for phase,pn in [(True,'solid'),(False,'void')]:
            m=volume if phase else ~volume
            for L in lengths:
                if L>m.shape[ax]: continue
                # probability every voxel in a segment of length L is phase
                c=np.ones_like(m,dtype=np.int16)
                # sliding convolution on axis
                sums=ndi.convolve1d(m.astype(np.int16),np.ones(L,np.int16),axis=ax,mode='constant',cval=0)
                # use centered implementation only as normalized surrogate
                out[f'lineal_{pn}_{name}_L{L}_survival']=float(np.mean(sums>=L))
    return out

def two_point_axis_descriptors(volume,max_lag=32):
    out={}; p=volume.mean()
    for ax,name in enumerate('zyx'):
        vals=[]
        for lag in range(1,min(max_lag,volume.shape[ax]-1)+1):
            s1=[slice(None)]*3; s2=[slice(None)]*3; s1[ax]=slice(None,-lag); s2[ax]=slice(lag,None); a=volume[tuple(s1)]; b=volume[tuple(s2)]; s2v=float(np.mean(a&b)); cov=s2v-p*p; norm=safe_div(cov,p*(1-p)); out[f'two_point_{name}_lag{lag}_S2']=s2v; out[f'two_point_{name}_lag{lag}_normalized_cov']=norm; vals.append(norm)
        ar=np.asarray(vals,float); valid=np.flatnonzero(np.isfinite(ar)&(ar<=math.exp(-1)))
        out[f'two_point_{name}_corr_length_e1_vox']=float(valid[0]+1) if len(valid) else np.nan
    return out

def three_point_descriptors(volume,lags=(1,2,4,8)):
    out={}; axes=[(0,1,'zy'),(0,2,'zx'),(1,2,'yx')]
    for a1,a2,name in axes:
        for r in lags:
            if r>=volume.shape[a1] or r>=volume.shape[a2]: continue
            sl0=[slice(None)]*3; sl1=[slice(None)]*3; sl2=[slice(None)]*3
            sl0[a1]=slice(None,-r); sl0[a2]=slice(None,-r)
            sl1[a1]=slice(r,None); sl1[a2]=slice(None,-r)
            sl2[a1]=slice(None,-r); sl2[a2]=slice(r,None)
            v=float(np.mean(volume[tuple(sl0)]&volume[tuple(sl1)]&volume[tuple(sl2)])); out[f'three_point_L_{name}_lag{r}']=v
    return out

# ----------------------------- multiscale / fractal / lacunarity -----------------------------
def boxcount(mask,k):
    shape=np.array(mask.shape); trim=(shape//k)*k
    if np.any(trim==0): return np.nan,np.nan
    m=mask[tuple(slice(0,int(t)) for t in trim)]; new=[]
    for n in trim: new.extend([int(n//k),k])
    axes=list(range(0,2*mask.ndim,2)); blocks=m.reshape(new); sums=blocks.sum(axis=tuple(a+1 for a in axes)); occupied=np.count_nonzero(sums); lac=float(np.var(sums)/(np.mean(sums)**2+EPS)+1)
    return occupied,lac

def multiscale_descriptors(volume,box_sizes=(2,3,4,6,8,12,16,24,32)):
    out={}; xs=[]; ys=[]; boundary=volume^ndi.binary_erosion(volume)
    for phase,name,m in [(1,'solid',volume),(0,'void',~volume),(2,'boundary',boundary)]:
        X=[];Y=[]
        for k in box_sizes:
            occ,lac=boxcount(m,k)
            if np.isfinite(occ): out[f'{name}_boxcount_k{k}']=occ; out[f'{name}_lacunarity_k{k}']=lac
            if np.isfinite(occ) and occ>0: X.append(math.log(1/k)); Y.append(math.log(occ))
        if len(X)>=2: out[f'{name}_boxcount_fractal_dimension']=float(np.polyfit(X,Y,1)[0])
    return out

# ----------------------------- spectral -----------------------------
def spectral_descriptors(volume,spacing,max_dim=128,use_gpu=False,gpu_id=1):
    v=volume.astype(float)-volume.mean(); step=max(1,int(math.ceil(max(volume.shape)/max_dim))); vd=v[::step,::step,::step]
    if _gpu_ok(use_gpu,gpu_id):
        try:
            with cp.cuda.Device(int(gpu_id)):
                cvd=cp.asarray(vd); cP=cp.abs(cp.fft.fftn(cvd))**2; cP.flat[0]=0; P=cp.asnumpy(cP); del cvd,cP; cp.get_default_memory_pool().free_all_blocks()
        except Exception as e:
            warnings.warn(f'GPU FFT failed on GPU {gpu_id}; CPU fallback: {e}'); F=np.fft.fftn(vd); P=np.abs(F)**2; P.flat[0]=0
    else:
        F=np.fft.fftn(vd); P=np.abs(F)**2; P.flat[0]=0
    total=P.sum(); out={'spectral_downsample_step':step}
    if total<=0: return out
    p=P.ravel()/total; p=p[p>0]; out['spectral_entropy']=float(-(p*np.log(p)).sum()/math.log(len(P.ravel())))
    kz=np.fft.fftfreq(vd.shape[0],d=spacing[0]*step); ky=np.fft.fftfreq(vd.shape[1],d=spacing[1]*step); kx=np.fft.fftfreq(vd.shape[2],d=spacing[2]*step); KZ,KY,KX=np.meshgrid(kz,ky,kx,indexing='ij'); km=np.sqrt(KX*KX+KY*KY+KZ*KZ)
    out['spectral_k_mean_per_mm']=float((P*km).sum()/total); out['spectral_k_rms_per_mm']=float(np.sqrt((P*km*km).sum()/total))
    idx=np.unravel_index(np.argmax(P),P.shape); kpeak=float(km[idx]); out['spectral_peak_k_per_mm']=kpeak; out['spectral_peak_wavelength_mm']=safe_div(1,kpeak)
    # power-weighted k covariance / anisotropy
    ks=np.stack([KX.ravel(),KY.ravel(),KZ.ravel()],1); w=P.ravel()/total; mu=(w[:,None]*ks).sum(0); C=((ks-mu)*w[:,None]).T@(ks-mu); ev=np.sort(np.linalg.eigvalsh(C))[::-1]
    for i,e in enumerate(ev,1): out[f'spectral_k_cov_eig{i}']=float(e)
    out['spectral_k_anisotropy_13']=safe_div(ev[0],ev[2]); out['spectral_fractional_anisotropy']=float(np.sqrt(1.5*np.sum((ev-ev.mean())**2)/(np.sum(ev**2)+EPS)))
    # radial bins
    kr=km.ravel(); pr=P.ravel(); edges=np.linspace(0,kr.max()+EPS,33); b=np.digitize(kr,edges)-1
    for i in range(32):
        mask=b==i; out[f'spectral_radial_bin{i:02d}_fraction']=float(pr[mask].sum()/total) if mask.any() else 0.
    return out

# ----------------------------- directional / MIL / profiles -----------------------------
def directional_descriptors(volume,spacing):
    out={}; dz,dy,dx=spacing
    # projection occupancy and gradient profile descriptors
    for ax,name in enumerate('zyx'):
        prof=volume.mean(axis=tuple(i for i in range(3) if i!=ax)); out.update(profile_stats(prof,f'directional_occupancy_{name}'))
    # mean intercept length via number of phase transitions along axis
    for ax,name,pitch in [(0,'z',dz),(1,'y',dy),(2,'x',dx)]:
        arr=np.moveaxis(volume,ax,-1).reshape(-1,volume.shape[ax])
        solid_lengths=_runs_matrix(arr,True).astype(float)*pitch
        void_lengths=_runs_matrix(arr,False).astype(float)*pitch
        transitions=np.count_nonzero(arr[:,1:]!=arr[:,:-1],axis=1) if arr.shape[1]>1 else np.zeros(arr.shape[0],dtype=int)
        out[f'MIL_solid_{name}_mm']=float(np.mean(solid_lengths)) if solid_lengths.size else np.nan; out[f'MIL_void_{name}_mm']=float(np.mean(void_lengths)) if void_lengths.size else np.nan; out.update(qstats(transitions,f'line_transition_count_{name}'))
    vals=np.array([out.get('MIL_solid_x_mm'),out.get('MIL_solid_y_mm'),out.get('MIL_solid_z_mm')],float); out['MIL_solid_max_min_ratio']=safe_div(np.nanmax(vals),np.nanmin(vals)); out['MIL_solid_cv_xyz']=safe_div(np.nanstd(vals),np.nanmean(vals))
    return out

# ----------------------------- skeleton / network -----------------------------
def skeleton_network_descriptors(volume,spacing,max_graph_nodes=5000):
    out={}; sk=morphology.skeletonize(volume); n=int(sk.sum()); out['skeleton_voxel_count']=n; out['skeleton_voxel_fraction']=safe_div(n,volume.sum()); out['skeleton_length_proxy_mm']=n*float(np.mean(spacing))
    if not n: return out
    kernel=np.ones((3,3,3),int); deg=ndi.convolve(sk.astype(int),kernel,mode='constant')-sk.astype(int); d=deg[sk]; out.update(qstats(d,'skeleton_voxel_degree26')); out['skeleton_endpoint_fraction']=float(np.mean(d==1)); out['skeleton_branchpoint_fraction']=float(np.mean(d>=3)); out['skeleton_isolated_fraction']=float(np.mean(d==0)); out['skeleton_degree_entropy']=normalized_entropy(np.bincount(np.clip(d,0,26),minlength=27))
    lab,c=ndi.label(sk,structure=ndi.generate_binary_structure(3,3)); out['skeleton_component_count']=int(c)
    # voxel-graph cycle-rank proxy from 26-neighbor adjacency
    E=int(d.sum()/2); V=n; out['skeleton_graph_edge_count_proxy']=E; out['skeleton_cycle_rank_proxy']=int(E-V+c); out['skeleton_mean_graph_degree']=safe_div(2*E,V)
    # graph spectral descriptors for manageable skeletons
    if n<=max_graph_nodes:
        try:
            import scipy.sparse as sp
            from scipy.sparse.csgraph import connected_components
            coords=np.argwhere(sk); mp={tuple(c):i for i,c in enumerate(coords)}; rr=[];cc=[]
            neigh=[(a,b,c) for a in (-1,0,1) for b in (-1,0,1) for c in (-1,0,1) if (a,b,c)!=(0,0,0)]
            for i,p in enumerate(coords):
                for dv in neigh:
                    q=tuple((p+dv).tolist()); j=mp.get(q)
                    if j is not None and j>i: rr.extend([i,j]); cc.extend([j,i])
            A=sp.csr_matrix((np.ones(len(rr)),(rr,cc)),shape=(n,n)); D=sp.diags(np.asarray(A.sum(1)).ravel()); L=D-A
            if n>2:
                from scipy.sparse.linalg import eigsh
                k=min(8,n-1); vals=np.sort(eigsh(L,k=k,which='SM',return_eigenvectors=False)); out['skeleton_laplacian_lambda2']=float(vals[1]) if len(vals)>1 else np.nan; out['skeleton_laplacian_small_eigs_sum']=float(vals.sum())
                valsA=eigsh(A,k=1,which='LA',return_eigenvectors=False); out['skeleton_adjacency_spectral_radius']=float(valsA[0])
        except Exception as e: out['skeleton_graph_spectral_skipped']=1
    else: out['skeleton_graph_spectral_skipped']=1
    return out

# ----------------------------- optional persistent homology -----------------------------
def persistent_homology_descriptors(volume,max_dim_vox=64):
    out={'persistent_homology_available':0}
    try:
        import gudhi as gd
    except Exception:
        return out
    step=max(1,int(math.ceil(max(volume.shape)/max_dim_vox))); v=volume[::step,::step,::step]; f=-ndi.distance_transform_edt(v)+ndi.distance_transform_edt(~v)
    cc=gd.CubicalComplex(top_dimensional_cells=f); pers=cc.persistence(); out['persistent_homology_available']=1; out['persistent_homology_downsample_step']=step
    for dim in [0,1,2]:
        life=[]
        for d,(b,e) in pers:
            if d==dim and np.isfinite(e): life.append(e-b)
        out.update(qstats(life,f'PH_dim{dim}_lifetime')); out[f'PH_dim{dim}_count']=len(life); out[f'PH_dim{dim}_total_persistence']=float(np.sum(life)) if life else 0.
    return out

# ----------------------------- QA/export -----------------------------
def flatten_stage_summaries(stage_files):
    row={}
    for p in stage_files:
        p=Path(p)
        if not p.exists(): continue
        if p.suffix.lower()=='.json':
            d=load_json(p); row.update({k:v for k,v in d.items() if np.isscalar(v) or v is None})
    return row

def descriptor_catalog_from_names(names):
    rules=[
      ('slice_','2D slice morphology','Per-slice morphology and z-profile statistics'),('proj_','2D projection texture','Orthogonal projection GLCM, Hu moments, entropy, gradients'),('pair_','2-layer transition','Adjacent-layer overlap/change/boundary displacement'),('triplet_','3-layer TSPE','3-layer A/B/C and 8-state statistics'),('persist_','multi-layer persistence','Intersection persistence across k consecutive layers'),('lag','multi-lag interlayer','Lagged overlap, mutual information and decay'),('tspe_','TSPE dynamics','8-state transition matrix and transition entropy'),('relative_density','3D morphology','Relative density'),('solid_volume','3D morphology','Volume'),('surface_','3D surface','Surface area/fabric/dihedral descriptors'),('specific_surface','3D surface','Specific surface area'),('sphericity','3D shape','Sphericity'),('compactness','3D shape','Compactness'),('convex_','3D shape','Convex-hull descriptors'),('inertia_','3D moments','Coordinate covariance/inertia anisotropy'),('coord_','3D moments','Coordinate distribution statistics'),('solid_components','3D topology','Connected solid components'),('void_components','3D topology','Connected void components'),('solid_spanning','3D connectivity','Spanning/percolation descriptors'),('euler_','3D topology','Euler characteristic and filtration'),('betti','3D topology','Betti-number proxies'),('enclosed_void','3D topology','Cavity statistics'),('solid_local_thickness','3D thickness','Distance-transform local thickness proxy'),('void_local_diameter','3D pore size','Distance-transform void diameter proxy'),('skeleton_sampled','3D thickness','Thickness sampled on skeleton'),('granulo_','multiscale size','Morphological granulometry'),('chord_','spatial statistics','Chord-length distributions'),('lineal_','spatial statistics','Lineal-path survival probabilities'),('two_point_','spatial statistics','Two-point correlation'),('three_point_','spatial statistics','Selected 3-point correlations'),('solid_boxcount','fractal/multiscale','Solid box-counting/lacunarity'),('void_boxcount','fractal/multiscale','Void box-counting/lacunarity'),('boundary_boxcount','fractal/multiscale','Boundary box-counting/lacunarity'),('solid_lacunarity','fractal/multiscale','Solid lacunarity'),('void_lacunarity','fractal/multiscale','Void lacunarity'),('spectral_','frequency-domain','3D FFT power spectrum, entropy, anisotropy'),('directional_','directionality','Directional occupancy profiles'),('MIL_','directionality','Mean intercept length'),('line_transition','directionality','Directional phase-transition counts'),('skeleton_','network','Skeleton morphology and graph descriptors'),('PH_','persistent homology','Cubical persistent-homology summaries'),
      ('curvature_','surface curvature','Discrete mean/Gaussian curvature, principal curvatures, shape index, curvedness (v4)'),
      ('tortuosity_','transport tortuosity','Geodesic/straight-line path tortuosity per phase and axis (v4)'),
      ('strut_','strut/node lattice graph','Junction coordination number, strut length/tortuosity/thickness distributions (v4)'),
      ('soft_triplet_','grayscale soft TSPE','Fuzzy-logic (grayscale-preserving) A/B/C overlap, partial-volume diagnostics (v4)'),
      ('ct_recon_','X-ray CT reconstruction','Radon-transform forward projection + filtered back-projection fidelity vs. direct stack (v4)')]
    rows=[]
    for n in names:
        fam='other'; desc='Generated geometric descriptor'
        for pre,f,d in rules:
            if n.startswith(pre): fam=f; desc=d; break
        rows.append({'descriptor':n,'family':fam,'description':desc})
    return pd.DataFrame(rows)


# =====================================================================
# v4 ADDITIONS -- see docstring below for the list of new descriptor families
# =====================================================================
"""
Descriptor Additions v4
========================
New descriptor families added on top of descriptor_library.py v3, per user request:

1. curvature_descriptors           - mesh-based discrete mean/Gaussian curvature (H, K),
                                      principal curvatures, shape index, curvedness.
                                      (was MISSING in v3: only dihedral-angle stats existed.)
2. tortuosity_descriptors          - geodesic/straight-line path tortuosity of solid and void
                                      phase along z/y/x (transport-relevant; was MISSING in v3).
3. strut_graph_descriptors         - true node/strut lattice graph: junction coordination
                                      number Z, strut length/tortuosity/thickness-uniformity
                                      distributions (v3 only had coarse per-voxel skeleton degree).
4. Grayscale-preserving soft TSPE  - load_image_stack_grayscale / soft_triplet_descriptor_table:
                                      implements the user's own "grayscale-based overlap" idea,
                                      which the v3 pipeline actually short-circuited by binarizing
                                      on load.
5. xray_ct_projection_reconstruction_descriptors
                                    - literal Radon-transform forward projection + filtered
                                      back-projection (FBP) reconstruction per axial slice,
                                      cross-validated against the direct slice-stack volume.
                                      Implements the "use real X-ray/CT reconstruction methods"
                                      request as an alternative/complementary extraction path.

Design constraints (kept consistent with descriptor_library.py):
- Pure numpy/scipy/scikit-image/networkx. No new hard dependency beyond what
  requirements.txt already lists (networkx was already required but unused by v3).
- Every function is self-contained, side-effect-free except for optional PNG/image export,
  and returns a flat dict of scalars so it drops into the existing restart-safe
  checkpoint -> features/*.json -> descriptors_ALL.csv pipeline unchanged.
- Mesh-based descriptors here use skimage.measure.marching_cubes directly (NOT trimesh),
  so they do not require trimesh to be installed.
"""
import scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra

# =====================================================================
# 1. CURVATURE  (mean H, Gaussian K, principal k1/k2, shape index, curvedness)
# =====================================================================
def _mesh_from_volume(volume, spacing):
    """
    Marching-cubes mesh built directly from skimage (no trimesh dependency).
    The volume is padded with one voxel of background on every side first: a
    structure that touches the array boundary (a strut or lattice unit cell
    cropped at the field of view, or a full-height rod as in the synthetic
    test) would otherwise produce an OPEN mesh with no end cap there. Discrete
    curvature (both the cotangent-Laplacian mean curvature and the
    angle-defect Gaussian curvature below) assumes a closed 1-ring of
    triangles around every vertex; at an open mesh boundary that assumption
    is violated and produces spuriously huge curvature at the cut edge. The
    1-voxel pad guarantees a watertight mesh so this artifact cannot occur.
    """
    if not volume.any() or volume.all():
        return None, None
    padded = np.pad(volume, 1, mode='constant', constant_values=False)
    verts, faces, normals, _ = measure.marching_cubes(padded.astype(np.uint8), level=.5, spacing=spacing)
    verts_xyz = verts[:, [2, 1, 0]]  # skimage returns (z,y,x) -> convert to (x,y,z)
    return verts_xyz.astype(np.float64), faces.astype(np.int64)


def _uniform_adjacency(n, faces):
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]], axis=0)
    rows = np.concatenate([edges[:, 0], edges[:, 1]])
    cols = np.concatenate([edges[:, 1], edges[:, 0]])
    data = np.ones(len(rows))
    A = sp.coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
    A.data[:] = 1.0  # binarize (dedupe duplicate entries from shared edges)
    deg = np.asarray(A.sum(axis=1)).ravel()
    return A, deg


def _taubin_smooth(verts, faces, iterations=12, lam=0.5, mu=-0.53):
    """
    Taubin (1995) lambda/mu mesh smoothing. Marching-cubes surfaces extracted
    directly from a voxel grid carry a strong staircase artifact (locally flat
    voxel-face terraces meeting at sharp voxel-edge ridges), which makes raw
    per-vertex discrete curvature estimates dominated by mesh-discretization
    noise rather than the underlying structure's shape. A few Taubin smoothing
    passes remove that staircase noise while -- unlike plain Laplacian
    smoothing -- not shrinking the surface, which is essential here since the
    absolute curvature magnitude (not just its sign/pattern) is reported.
    """
    n = len(verts)
    A, deg = _uniform_adjacency(n, faces)
    deg_safe = np.maximum(deg, 1.0)
    V = verts.copy()
    for _ in range(iterations):
        for factor in (lam, mu):
            avg = (A @ V) / deg_safe[:, None]
            V = V + factor * (avg - V)
    return V


def _corner_geometry(verts, faces):
    """For every (face, corner) pair, return cot(angle) at that corner and the angle itself."""
    tri = verts[faces]  # (F,3,3)
    corners = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
    cots = np.zeros((len(faces), 3))
    angles = np.zeros((len(faces), 3))
    for k, (a, b, c) in enumerate(corners):
        pa, pb, pc = tri[:, a], tri[:, b], tri[:, c]
        u = pb - pa
        v = pc - pa
        un = np.linalg.norm(u, axis=1)
        vn = np.linalg.norm(v, axis=1)
        cosang = np.einsum('ij,ij->i', u, v) / (un * vn + EPS)
        cosang = np.clip(cosang, -1.0, 1.0)
        crossn = np.linalg.norm(np.cross(u, v), axis=1)
        sinang = crossn / (un * vn + EPS)
        cots[:, k] = cosang / (sinang + EPS)
        angles[:, k] = np.arccos(cosang)
    return cots, angles, corners


def curvature_descriptors(volume, spacing, smooth_iterations=12):
    """
    Discrete differential-geometry curvature on the marching-cubes iso-surface
    (cotangent-Laplacian mean curvature + angle-defect Gaussian curvature,
    Meyer et al. 2003 "Discrete Differential-Geometry Operators for Triangulated
    2-Manifolds"). Produces per-vertex H, K, principal curvatures k1/k2,
    Koenderink shape index and curvedness, aggregated with qstats(), plus
    area-weighted elliptic/hyperbolic/parabolic surface-fraction descriptors
    that discriminate dome/node-like (K>0), saddle/sheet-like (K<0) and
    cylindrical strut-like (K~0) local topology -- directly relevant to telling
    strut-lattice vs. TPMS-sheet architected material apart.
    """
    out = {}
    verts, faces = _mesh_from_volume(volume, spacing)
    if verts is None or len(verts) < 4 or len(faces) < 4:
        out['curvature_mesh_available'] = 0
        return out
    out['curvature_mesh_available'] = 1
    n = len(verts)

    if smooth_iterations > 0:
        verts = _taubin_smooth(verts, faces, iterations=smooth_iterations)

    # face area (also needed for mixed vertex area, barycentric 1/3-split)
    tri = verts[faces]
    e0 = tri[:, 1] - tri[:, 0]
    e1 = tri[:, 2] - tri[:, 0]
    face_area = 0.5 * np.linalg.norm(np.cross(e0, e1), axis=1)
    area_per_vertex = np.zeros(n)
    np.add.at(area_per_vertex, faces[:, 0], face_area / 3.0)
    np.add.at(area_per_vertex, faces[:, 1], face_area / 3.0)
    np.add.at(area_per_vertex, faces[:, 2], face_area / 3.0)
    area_per_vertex = np.maximum(area_per_vertex, EPS)

    cots, angles, corners = _corner_geometry(verts, faces)

    # cotangent-weighted Laplacian: L(v_i) = sum_j w_ij (v_i - v_j)
    rows = []
    cols = []
    vals = []
    angle_sum = np.zeros(n)
    for k, (a, b, c) in enumerate(corners):
        ib = faces[:, b]
        ic = faces[:, c]
        w = 0.5 * cots[:, k]
        rows.append(ib); cols.append(ic); vals.append(w)
        rows.append(ic); cols.append(ib); vals.append(w)
        ia = faces[:, a]
        np.add.at(angle_sum, ia, angles[:, k])
    rows = np.concatenate(rows); cols = np.concatenate(cols); vals = np.concatenate(vals)
    W = sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
    deg = np.asarray(W.sum(axis=1)).ravel()
    Lx = deg * verts[:, 0] - W @ verts[:, 0]
    Ly = deg * verts[:, 1] - W @ verts[:, 1]
    Lz = deg * verts[:, 2] - W @ verts[:, 2]
    HN = np.stack([Lx, Ly, Lz], axis=1) / (2.0 * area_per_vertex[:, None])
    H_mag = np.linalg.norm(HN, axis=1)

    # vertex normals (area-weighted average of adjacent face normals) for sign convention
    fn = np.cross(e0, e1)
    fn_norm = np.linalg.norm(fn, axis=1, keepdims=True)
    fn = fn / np.maximum(fn_norm, EPS)
    vn = np.zeros((n, 3))
    for k in range(3):
        np.add.at(vn, faces[:, k], fn * face_area[:, None])
    vn_norm = np.linalg.norm(vn, axis=1, keepdims=True)
    vn = vn / np.maximum(vn_norm, EPS)

    sign = np.sign(np.einsum('ij,ij->i', HN, vn))
    sign[sign == 0] = 1.0
    # Sign convention fixed empirically against a synthetic solid sphere
    # (see test_additions_v4.py section 1): H = +sign(HN . n) * |HN| gives
    # POSITIVE mean curvature on a convex (ball) surface, matching the
    # standard convention where a convex solid has H > 0.
    H = sign * H_mag

    K = angle_sum_defect = (2 * math.pi - angle_sum) / area_per_vertex

    disc = np.maximum(H * H - K, 0.0)
    root = np.sqrt(disc)
    k1 = H + root
    k2 = H - root
    denom = (k1 - k2)
    shape_index = np.where(np.abs(denom) > 1e-9, (2.0 / math.pi) * np.arctan2(k1 + k2, denom), 0.0)
    curvedness = np.sqrt((k1 * k1 + k2 * k2) / 2.0)

    w = area_per_vertex  # area-weighting for physically meaningful surface averages
    out.update(qstats(H, 'curvature_mean_H_per_mm'))
    out.update(qstats(K, 'curvature_gaussian_K_per_mm2'))
    out.update(qstats(k1, 'curvature_k1_per_mm'))
    out.update(qstats(k2, 'curvature_k2_per_mm'))
    out.update(qstats(shape_index, 'curvature_shape_index'))
    out.update(qstats(curvedness, 'curvature_curvedness_per_mm'))
    out['curvature_area_weighted_mean_H_per_mm'] = float(np.sum(H * w) / w.sum())
    out['curvature_area_weighted_mean_K_per_mm2'] = float(np.sum(K * w) / w.sum())

    # Classification threshold: on a truly flat/cylindrical region K is theoretically
    # exactly 0, but floating-point round-off leaves it at ~1e-9..1e-12, so a threshold
    # relative to median(|K|) (which itself can be ~0 when most of the surface is flat)
    # mis-splits that noise ~50/50 into spurious "elliptic"/"hyperbolic" labels. A fixed
    # small absolute threshold in [1/spacing-unit]^2 comfortably separates float noise
    # (~1e-9) from any physically meaningful curvature at typical voxel/mm scales
    # (K >~ 1e-3 for sub-metre radii of curvature). If your spacing units are far from
    # ~1 (e.g. sub-micron voxels in metres), rescale CURVATURE_FLAT_EPS accordingly.
    k_eps = 1e-6
    ell = w[K > k_eps].sum(); hyp = w[K < -k_eps].sum(); par = w[np.abs(K) <= k_eps].sum()
    tot = w.sum()
    out['curvature_area_fraction_elliptic_dome_or_node'] = safe_div(ell, tot)
    out['curvature_area_fraction_hyperbolic_saddle_or_sheet'] = safe_div(hyp, tot)
    out['curvature_area_fraction_parabolic_cylindrical_or_strut'] = safe_div(par, tot)
    return out


# =====================================================================
# 2. TORTUOSITY  (geodesic / straight-line path length ratio, per phase & axis)
# =====================================================================
def _largest_component(mask, connectivity=1):
    st = ndi.generate_binary_structure(3, connectivity)
    lab, n = ndi.label(mask, structure=st)
    if n == 0:
        return None
    sizes = ndi.sum(mask, lab, index=np.arange(1, n + 1))
    biggest = 1 + int(np.argmax(sizes))
    return lab == biggest


def _build_voxel_graph(mask, spacing):
    """6-connected weighted sparse adjacency graph over voxels of `mask`."""
    Z, Y, X = mask.shape
    idx = -np.ones((Z, Y, X), dtype=np.int64)
    coords = np.argwhere(mask)
    idx[tuple(coords.T)] = np.arange(len(coords))
    rows, cols, data = [], [], []
    for (dz, dy, dx) in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        s1 = (slice(0, Z - dz or None), slice(0, Y - dy or None), slice(0, X - dx or None))
        s2 = (slice(dz, Z), slice(dy, Y), slice(dx, X))
        m = mask[s1] & mask[s2]
        i1 = idx[s1][m]
        i2 = idx[s2][m]
        w = math.sqrt((dz * spacing[0]) ** 2 + (dy * spacing[1]) ** 2 + (dx * spacing[2]) ** 2)
        rows.append(i1); cols.append(i2); data.append(np.full(i1.shape, w))
    if rows:
        rows = np.concatenate(rows); cols = np.concatenate(cols); data = np.concatenate(data)
    else:
        rows = np.array([], dtype=np.int64); cols = np.array([], dtype=np.int64); data = np.array([])
    n = len(coords)
    G = sp.coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
    G = G.maximum(G.T)
    return G, coords, idx


def _axis_tortuosity(mask, spacing, axis, max_side=48):
    factor = max(1, int(math.ceil(max(mask.shape) / max_side)))
    if factor > 1:
        mask = mask[::factor, ::factor, ::factor]
        spacing = tuple(s * factor for s in spacing)
    comp = _largest_component(mask)
    if comp is None or comp.sum() < 4:
        return np.nan
    lo = 0
    hi = comp.shape[axis] - 1
    sl_lo = [slice(None)] * 3; sl_lo[axis] = 0
    sl_hi = [slice(None)] * 3; sl_hi[axis] = hi
    src_mask = np.zeros_like(comp); src_mask[tuple(sl_lo)] = comp[tuple(sl_lo)]
    dst_mask = np.zeros_like(comp); dst_mask[tuple(sl_hi)] = comp[tuple(sl_hi)]
    if not src_mask.any() or not dst_mask.any():
        return np.nan  # phase does not span/percolate along this axis
    G, coords, idx = _build_voxel_graph(comp, spacing)
    src_idx = idx[src_mask]
    src_idx = src_idx[src_idx >= 0]
    dst_idx = idx[dst_mask]
    dst_idx = dst_idx[dst_idx >= 0]
    if len(src_idx) == 0 or len(dst_idx) == 0:
        return np.nan
    dist = dijkstra(G, directed=False, indices=src_idx, min_only=True)
    d_at_dst = dist[dst_idx]
    d_at_dst = d_at_dst[np.isfinite(d_at_dst)]
    if len(d_at_dst) == 0:
        return np.nan
    geodesic_mean = float(np.mean(d_at_dst))
    straight = hi * spacing[axis]
    return safe_div(geodesic_mean, straight)


def tortuosity_descriptors(volume, spacing, max_side=48):
    """
    Geodesic tortuosity tau = <L_geodesic> / L_straight of the LARGEST connected
    component of each phase, from the low-coordinate face to the high-coordinate
    face along each axis (multi-source Dijkstra on the 6-connected voxel graph,
    downsampled to <= max_side per dimension for tractability). NaN when the
    phase does not span/percolate that axis (mirrors the existing
    `solid_percolates_*` flags in topology_descriptors -- tortuosity is only
    defined for a spanning pathway). Void tortuosity is the standard transport
    descriptor for permeability/diffusivity (Kozeny-Carman-type estimates);
    solid tortuosity is the analogous descriptor for conduction path length
    (thermal/electrical) through the strut network.
    """
    out = {}
    for phase_mask, pname in [(volume, 'solid'), (~volume, 'void')]:
        for ax, axname in enumerate('zyx'):
            out[f'tortuosity_{pname}_{axname}'] = _axis_tortuosity(phase_mask, spacing, ax, max_side)
        vals = np.array([out[f'tortuosity_{pname}_{a}'] for a in 'zyx'], float)
        out[f'tortuosity_{pname}_mean_xyz'] = float(np.nanmean(vals)) if np.isfinite(vals).any() else np.nan
    return out


# =====================================================================
# 3. STRUT / NODE GRAPH DESCRIPTORS (true lattice topology)
# =====================================================================
def strut_graph_descriptors(volume, spacing, max_skeleton_voxels=250000):
    """
    Reduces the 26-connected skeleton voxel graph to the actual node/strut
    lattice graph used in architected-material literature: junction nodes
    (skeleton voxels of degree != 2) connected by struts (chains of degree-2
    voxels). Reports nodal coordination number Z (Maxwell isostaticity
    reference: Z=6 for a 3D central-force frame, Z=4 in 2D), strut
    geodesic/straight length, per-strut tortuosity, and per-strut thickness
    (sampled from the solid distance-transform along the strut path) including
    a thickness-uniformity CV -- descriptors the v3 skeleton family did not
    have (it only reported local, per-voxel degree statistics).
    """
    out = {}
    if not _HAS_NETWORKX:
        out['strut_graph_skipped_no_networkx'] = 1
        return out
    sk = morphology.skeletonize(volume)
    n_sk = int(sk.sum())
    if n_sk == 0:
        out['strut_graph_skipped_empty'] = 1
        return out
    if n_sk > max_skeleton_voxels:
        out['strut_graph_skipped_too_large'] = 1
        return out

    coords = np.argwhere(sk)
    coord_set = set(map(tuple, coords.tolist()))
    G = nx.Graph()
    neighbors26 = [(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1) if (a, b, c) != (0, 0, 0)]
    for p in coords:
        pt = tuple(int(v) for v in p)
        G.add_node(pt)
    for p in coords:
        pt = tuple(int(v) for v in p)
        for d in neighbors26:
            q = (pt[0] + d[0], pt[1] + d[1], pt[2] + d[2])
            if q in coord_set and q > pt:
                w = math.sqrt(sum((di * si) ** 2 for di, si in zip(d, spacing)))
                G.add_edge(pt, q, weight=w)

    deg = dict(G.degree())
    junction_nodes = [p for p, d in deg.items() if d != 2]

    def phys(p):
        return np.array([p[i] * spacing[i] for i in range(3)])

    visited_edges = set()
    struts = []
    for jn in junction_nodes:
        for nb in list(G.neighbors(jn)):
            e = frozenset((jn, nb))
            if e in visited_edges:
                continue
            visited_edges.add(e)
            path = [jn, nb]
            length = G[jn][nb]['weight']
            prev, cur = jn, nb
            steps = 0
            while deg.get(cur, 0) == 2 and steps < n_sk + 5:
                nxts = [x for x in G.neighbors(cur) if x != prev]
                if not nxts:
                    break
                nxt = nxts[0]
                e2 = frozenset((cur, nxt))
                if e2 in visited_edges:
                    break
                visited_edges.add(e2)
                length += G[cur][nxt]['weight']
                path.append(nxt)
                prev, cur = cur, nxt
                steps += 1
            end = cur
            straight = float(np.linalg.norm(phys(jn) - phys(end)))
            struts.append({
                'start': jn, 'end': end, 'geodesic_length': float(length),
                'straight_length': straight,
                'tortuosity': safe_div(length, straight) if straight > EPS else np.nan,
                'path': path,
            })

    dedup = {}
    for s in struts:
        key = (frozenset((s['start'], s['end'])), round(s['geodesic_length'], 6), len(s['path']))
        dedup[key] = s
    struts = list(dedup.values())

    node_degrees = np.array([deg[jn] for jn in junction_nodes], float)
    out['strut_node_count'] = int(len(junction_nodes))
    out['strut_endpoint_node_count'] = int(np.sum(node_degrees == 1))
    out['strut_junction_node_count'] = int(np.sum(node_degrees >= 3))
    junction_only = node_degrees[node_degrees >= 3]
    out.update(qstats(junction_only, 'strut_node_coordination_number_Z'))
    out['strut_count'] = int(len(struts))
    out['strut_network_mean_coordination_number_Z'] = safe_div(2 * len(struts), max(1, len(junction_nodes)))

    if struts:
        lengths = np.array([s['geodesic_length'] for s in struts])
        straight = np.array([s['straight_length'] for s in struts])
        tort = np.array([s['tortuosity'] for s in struts])
        out.update(qstats(lengths, 'strut_geodesic_length_mm'))
        out.update(qstats(straight, 'strut_straight_length_mm'))
        out.update(qstats(tort, 'strut_tortuosity'))

        ds = ndi.distance_transform_edt(volume, sampling=spacing)
        means, cvs, minmax = [], [], []
        for s in struts:
            pth = np.array(s['path'])
            vals = 2.0 * ds[tuple(pth.T)]
            if len(vals) == 0:
                continue
            m = float(vals.mean())
            means.append(m)
            cvs.append(safe_div(float(vals.std()), m))
            mx = float(vals.max())
            minmax.append(safe_div(float(vals.min()), mx) if mx > EPS else np.nan)
        out.update(qstats(means, 'strut_thickness_mean_mm'))
        out.update(qstats(cvs, 'strut_thickness_uniformity_cv'))
        out.update(qstats(minmax, 'strut_thickness_min_over_max'))
        out['strut_aspect_ratio_median'] = safe_div(float(np.median(lengths)), float(np.median(means))) if means else np.nan
    return out


# =====================================================================
# 4. GRAYSCALE-PRESERVING TSPE (soft/fuzzy A/B/C overlap)
# =====================================================================
def load_image_stack_grayscale(folder, spacing=(1., 1., 1.), invert=False):
    """
    Loads the same slice series as load_image_stack but WITHOUT binarizing:
    keeps normalized [0,1] grayscale intensity per voxel. This is what actually
    implements the user's stated concept ("grayscale 기반으로 겹치는 부분 결정")
    -- the v3 pipeline binarized on load (load_image_stack: `im>threshold`)
    before any A/B/C overlap logic ever saw the pixels, so the "grayscale" idea
    never reached the descriptor stage in the original code.
    """
    folder = Path(folder)
    files = sorted([p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS], key=natural_key)
    if len(files) < 3:
        raise ValueError('Need at least 3 slice images')
    arr = []
    shape = None
    for p in files:
        im = np.asarray(Image.open(p).convert('L')).astype(np.float32)
        if shape is None:
            shape = im.shape
        elif im.shape != shape:
            raise ValueError(f'Shape mismatch: {p}')
        if invert:
            im = 255.0 - im
        arr.append(im / 255.0)
    vol = np.stack(arr).astype(np.float32)
    return vol, tuple(spacing), {'source_type': 'image_stack_grayscale', 'source': str(folder),
                                  'slice_files': [p.name for p in files]}


def grayscale_stack_from_binary(volume, blur_sigma=0.0, use_gpu=False, gpu_id=1):
    """Create a soft [0,1] surrogate. Gaussian blur can run on a selected CUDA GPU."""
    v = volume.astype(np.float32)
    if blur_sigma > 0:
        if _gpu_ok(use_gpu,gpu_id):
            try:
                with cp.cuda.Device(int(gpu_id)):
                    cv=cp.asarray(v); cv=cndi.gaussian_filter(cv,sigma=blur_sigma); v=cp.asnumpy(cv)
                    del cv; cp.get_default_memory_pool().free_all_blocks()
            except Exception as e:
                warnings.warn(f'GPU Gaussian blur failed on GPU {gpu_id}; CPU fallback: {e}')
                v = ndi.gaussian_filter(v, sigma=blur_sigma)
        else:
            v = ndi.gaussian_filter(v, sigma=blur_sigma)
    return v

def save_grayscale_stack(path, gvol, spacing, meta=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, volume=gvol.astype(np.float32), spacing=np.asarray(spacing, float),
                         meta=json.dumps(meta or {}))


def load_grayscale_stack(path):
    z = np.load(path, allow_pickle=False)
    vol = z['volume'].astype(np.float32)
    spacing = tuple(float(v) for v in z['spacing'])
    meta = json.loads(str(z['meta'])) if 'meta' in z else {}
    return vol, spacing, meta


def _soft_triplet_descriptor_table_cpu(gvol, spacing, save_dir=None, image_stride=1, cut=0.5):
    """
    Continuous-valued counterpart of triplet_descriptor_table(): for
    consecutive grayscale slices I_N, I_{N+1}, I_{N+2} in [0,1], computes the
    fuzzy-logic (Zadeh min t-norm) equivalents of A/B/C:
        A_soft = min(I_N, I_{N+1}, I_{N+2})
        B_soft = min(I_N, I_{N+1}, 1 - I_{N+2})
        C_soft = min(I_{N+1}, I_{N+2}, 1 - I_N)
    min() is used (rather than the product t-norm) because it is the standard
    fuzzy-AND and keeps A_soft/B_soft/C_soft bounded by each slice's own
    intensity -- i.e. an overlap region can be no "stronger" than its weakest
    constituent slice, which is the same physical idea as partial-volume CT
    voxels: a voxel that is only 40% solid in one of the three layers cannot
    contribute more than 0.4 to a persistence measure spanning that layer.
    Also reports the information lost by hard-thresholding
    (soft_A_hard_agreement_dice) and the fraction of genuinely ambiguous
    partial-volume pixels (soft_A_partial_volume_fraction).
    """
    dz, dy, dx = spacing
    rows = []
    save_dir = Path(save_dir) if save_dir else None
    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
    for i in range(len(gvol) - 2):
        I0, I1, I2 = gvol[i], gvol[i + 1], gvol[i + 2]
        A_soft = np.minimum(np.minimum(I0, I1), I2)
        B_soft = np.minimum(np.minimum(I0, I1), 1 - I2)
        C_soft = np.minimum(np.minimum(I1, I2), 1 - I0)
        row = {'triplet_index': i}
        for name, img in [('A', A_soft), ('B', B_soft), ('C', C_soft)]:
            row.update(qstats(img.ravel(), f'soft_{name}'))
        hardA = (I0 > cut) & (I1 > cut) & (I2 > cut)
        pred_softA = A_soft > cut
        inter = np.count_nonzero(pred_softA & hardA)
        row['soft_A_hard_agreement_dice'] = safe_div(2 * inter, pred_softA.sum() + hardA.sum())
        row['soft_A_partial_volume_fraction'] = float(np.mean((A_soft > 0.02) & (A_soft < 0.98)))
        row['soft_B_partial_volume_fraction'] = float(np.mean((B_soft > 0.02) & (B_soft < 0.98)))
        row['soft_C_partial_volume_fraction'] = float(np.mean((C_soft > 0.02) & (C_soft < 0.98)))
        rows.append(row)
        if save_dir and i % image_stride == 0:
            comp = np.stack([np.clip(A_soft * 255, 0, 255), np.clip(B_soft * 255, 0, 255),
                              np.clip(C_soft * 255, 0, 255)], axis=-1).astype(np.uint8)
            Image.fromarray(comp).save(save_dir / f'soft_triplet_{i:05d}_ABC_rgb.png')
    df = pd.DataFrame(rows)
    out = {}
    for c in df.columns:
        if c != 'triplet_index':
            out.update(profile_stats(df[c].values, f'soft_triplet_{c}'))
    return df, out


def _soft_triplet_descriptor_table_gpu(gvol, spacing, save_dir=None, image_stride=1, cut=0.5, gpu_id=1):
    rows=[]; save_dir=Path(save_dir) if save_dir else None
    if save_dir: save_dir.mkdir(parents=True,exist_ok=True)
    with cp.cuda.Device(int(gpu_id)):
        cg=cp.asarray(gvol,dtype=cp.float32)
        for i in range(len(gvol)-2):
            I0,I1,I2=cg[i],cg[i+1],cg[i+2]
            A=cp.minimum(cp.minimum(I0,I1),I2); B=cp.minimum(cp.minimum(I0,I1),1-I2); C=cp.minimum(cp.minimum(I1,I2),1-I0)
            row={'triplet_index':i}
            for name,img in [('A',A),('B',B),('C',C)]: row.update(_qstats_cupy(img,f'soft_{name}'))
            hardA=(I0>cut)&(I1>cut)&(I2>cut); pred=A>cut; inter=cp.count_nonzero(pred&hardA)
            denom=cp.sum(pred)+cp.sum(hardA); row['soft_A_hard_agreement_dice']=float((2*inter/denom).get()) if int(denom.get()) else np.nan
            row['soft_A_partial_volume_fraction']=float(cp.mean((A>0.02)&(A<0.98)).get())
            row['soft_B_partial_volume_fraction']=float(cp.mean((B>0.02)&(B<0.98)).get())
            row['soft_C_partial_volume_fraction']=float(cp.mean((C>0.02)&(C<0.98)).get())
            rows.append(row)
            if save_dir and i%image_stride==0:
                comp=cp.stack([cp.clip(A*255,0,255),cp.clip(B*255,0,255),cp.clip(C*255,0,255)],axis=-1).astype(cp.uint8)
                Image.fromarray(cp.asnumpy(comp)).save(save_dir/f'soft_triplet_{i:05d}_ABC_rgb.png')
            del A,B,C
        del cg; cp.get_default_memory_pool().free_all_blocks()
    df=pd.DataFrame(rows); out={}
    for c in df.columns:
        if c!='triplet_index': out.update(profile_stats(df[c].values,f'soft_triplet_{c}'))
    return df,out

def soft_triplet_descriptor_table(gvol, spacing, save_dir=None, image_stride=1, cut=0.5, use_gpu=False, gpu_id=1):
    if _gpu_ok(use_gpu,gpu_id):
        try: return _soft_triplet_descriptor_table_gpu(gvol,spacing,save_dir,image_stride,cut,gpu_id)
        except Exception as e: warnings.warn(f'GPU soft-TSPE failed on GPU {gpu_id}; CPU fallback: {e}')
    return _soft_triplet_descriptor_table_cpu(gvol,spacing,save_dir,image_stride,cut)


# =====================================================================
# 5. X-RAY CT PROJECTION SIMULATION + FILTERED BACK-PROJECTION RECONSTRUCTION
# =====================================================================
def xray_ct_projection_reconstruction(volume, spacing, n_angles=180, sparse_n_angles=60,
                                       add_poisson_noise=False, photon_count=5000.0, mu=0.15,
                                       seed=0, cpu_workers=1):
    """
    Simulates an actual X-ray CT acquisition + reconstruction of this structure,
    independent of the direct slice-stack pipeline: for every axial (z) slice,
    forward-projects with the Radon transform (skimage.transform.radon,
    parallel-beam) at `n_angles` evenly spaced angles in [0,180), optionally
    injects Poisson photon-counting noise (Beer-Lambert attenuation model
    I = I0*exp(-mu*x)), then reconstructs with filtered back-projection
    (skimage.transform.iradon, ramp filter -- the same FBP algorithm described
    in the accompanying discussion). A second `sparse_n_angles` run demonstrates
    the effect of a lower-dose / fewer-projection acquisition.

    This is the concrete implementation of "use real X-ray/CT reconstruction
    techniques as an alternative 3D-structure extraction pathway": a user who
    only has raw radiographic projections (rather than already-registered
    slice images) can run their projections through the same
    `xray_ct_projection_reconstruction` call, feed the resulting reconstructed
    volume back into every descriptor function in this library, and skip the
    slice-stack step entirely.

    Returns (descriptors, recon_full_volume, recon_sparse_volume). Descriptors
    include reconstruction fidelity vs. the direct-stack ground truth (Dice,
    IoU, relative-density error) at both angle counts.
    """
    from skimage.transform import radon, iradon
    from concurrent.futures import ThreadPoolExecutor
    Z, Y, X = volume.shape
    theta_full = np.linspace(0., 180., n_angles, endpoint=False)
    theta_sparse = np.linspace(0., 180., sparse_n_angles, endpoint=False)
    recon_full = np.zeros_like(volume, dtype=bool)
    recon_sparse = np.zeros_like(volume, dtype=bool)

    def _project_and_reconstruct(sl, theta, local_seed):
        sino = radon(sl.astype(float), theta=theta, circle=False)
        if add_poisson_noise:
            atten = np.clip(sino, 0, None)
            transmitted = photon_count * np.exp(-atten * mu)
            noisy = np.random.default_rng(local_seed).poisson(np.clip(transmitted, 1, None)).astype(float)
            sino = -np.log(np.clip(noisy, 1, None) / photon_count) / mu
        rec = iradon(sino, theta=theta, filter_name='ramp', circle=False, output_size=sl.shape[0])
        thr = 0.5 * rec.max() if rec.max() > 0 else 0.5
        return rec > thr

    def _one_slice(z):
        sl=volume[z]
        if not sl.any(): return z,None,None
        return z,_project_and_reconstruct(sl,theta_full,seed+2*z),_project_and_reconstruct(sl,theta_sparse,seed+2*z+1)
    workers=max(1,min(int(cpu_workers or 1),Z))
    if workers==1:
        results=map(_one_slice,range(Z))
    else:
        pool=ThreadPoolExecutor(max_workers=workers); results=pool.map(_one_slice,range(Z))
    for z,rf,rs in results:
        if rf is not None: recon_full[z]=rf; recon_sparse[z]=rs
    if workers>1: pool.shutdown(wait=True)

    out = {'ct_recon_n_angles_full': n_angles, 'ct_recon_n_angles_sparse': sparse_n_angles,
           'ct_recon_poisson_noise_applied': int(add_poisson_noise)}
    for tag, rec in [('full_angle', recon_full), ('sparse_angle', recon_sparse)]:
        inter = int(np.count_nonzero(rec & volume))
        union = int(np.count_nonzero(rec | volume))
        out[f'ct_recon_{tag}_dice_vs_direct_stack'] = safe_div(2 * inter, int(rec.sum()) + int(volume.sum()))
        out[f'ct_recon_{tag}_iou_vs_direct_stack'] = safe_div(inter, union)
        out[f'ct_recon_{tag}_relative_density'] = float(rec.mean())
        out[f'ct_recon_{tag}_relative_density_error'] = float(rec.mean() - volume.mean())
    return out, recon_full, recon_sparse
