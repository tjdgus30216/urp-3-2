import numpy as np
import pandas as pd
import open3d as o3d
import pyvista as pv
import os
from glob import glob

# =========================================
# 0) 유틸
# =========================================
def convert_o3d_to_pyvista(o3d_mesh, scalar_data, scalar_name):
    vertices = np.asarray(o3d_mesh.vertices)
    faces = np.asarray(o3d_mesh.triangles)
    faces_pv = np.hstack([[3, *f] for f in faces])
    mesh_pv = pv.PolyData(vertices, faces_pv)
    mesh_pv[scalar_name] = scalar_data
    return mesh_pv

def visualize_and_save(mesh_pv, scalar_name, clim_range, save_path):
    # 캔버스 크게 + 스칼라바를 오른쪽 끝으로 이동
    plotter = pv.Plotter(off_screen=True, window_size=(1600, 1200))
    # 먼저 메쉬만 추가 (스칼라바는 수동으로 추가)
    plotter.add_mesh(
        mesh_pv,
        scalars=scalar_name,
        cmap="coolwarm",
        clim=clim_range,
        show_edges=False,
        show_scalar_bar=False,  # 자동 스칼라바 비활성화
    )
    # 수동 스칼라바: 오른쪽에 충분히 붙이고 폭/폰트 조정
    plotter.add_scalar_bar(
        title=scalar_name,
        n_labels=5,
        vertical=True,
        position_x=0.92,    # 0~1, 오른쪽으로 이동
        position_y=0.10,    # 아래로 살짝 내림
        width=0.06,         # 더 슬림하게
        height=0.80,        # 충분히 길게
        label_font_size=12,
        title_font_size=14,
        italic=False,
        bold=False
    )
    plotter.show(screenshot=save_path)
    plotter.close()

def area_weighted_stats(x, w):
    w = np.asarray(w, dtype=float)
    w = w / (w.sum() + 1e-16)
    mu = (x * w).sum()
    var = ((x - mu) ** 2 * w).sum()
    return mu, np.sqrt(var)

def area_weighted_hist(values, areas, bins=100):
    hist, edges = np.histogram(values, bins=bins, weights=areas, density=False)
    prob = hist / np.sum(hist)
    centers = 0.5 * (edges[:-1] + edges[1:])
    return centers, prob, edges

# =========================================
# 1) 혼합 보로노이 면적 + DDG 곡률
# =========================================
def _face_areas_and_normals(V, F):
    v0 = V[F[:, 1]] - V[F[:, 0]]
    v1 = V[F[:, 2]] - V[F[:, 0]]
    n = np.cross(v0, v1)
    A = 0.5 * np.linalg.norm(n, axis=1)
    return A, n

def _angles_of_tri(v0, v1, v2):
    a = np.linalg.norm(v1 - v2)
    b = np.linalg.norm(v2 - v0)
    c = np.linalg.norm(v0 - v1)
    alpha = np.arccos(np.clip((b*b + c*c - a*a) / (2*b*c + 1e-16), -1.0, 1.0))
    beta  = np.arccos(np.clip((c*c + a*a - b*b) / (2*c*a + 1e-16), -1.0, 1.0))
    gamma = np.pi - alpha - beta
    return alpha, beta, gamma, a, b, c

def compute_mixed_voronoi_areas(mesh: o3d.geometry.TriangleMesh):
    V = np.asarray(mesh.vertices)
    F = np.asarray(mesh.triangles)
    A_f, _ = _face_areas_and_normals(V, F)
    nV = V.shape[0]
    A_v = np.zeros(nV)

    for f, (i0, i1, i2) in enumerate(F):
        v0, v1, v2 = V[i0], V[i1], V[i2]
        alpha, beta, gamma, a, b, c = _angles_of_tri(v0, v1, v2)
        obtuse = (alpha > np.pi/2) or (beta > np.pi/2) or (gamma > np.pi/2)
        if not obtuse:
            cot_alpha = 1/np.tan(alpha); cot_beta = 1/np.tan(beta); cot_gamma = 1/np.tan(gamma)
            A0 = (b*b * cot_gamma + c*c * cot_beta) / 8.0
            A1 = (c*c * cot_alpha + a*a * cot_gamma) / 8.0
            A2 = (a*a * cot_beta  + b*b * cot_alpha) / 8.0
        else:
            Af = A_f[f]
            if alpha > np.pi/2:
                A0, A1, A2 = Af/2.0, Af/4.0, Af/4.0
            elif beta > np.pi/2:
                A0, A1, A2 = Af/4.0, Af/2.0, Af/4.0
            else:
                A0, A1, A2 = Af/4.0, Af/4.0, Af/2.0
        A_v[i0] += A0; A_v[i1] += A1; A_v[i2] += A2

    A_v = np.maximum(A_v, 1e-16)
    return A_v

def _cot_angle(u, v):
    cross = np.linalg.norm(np.cross(u, v))
    if cross < 1e-16:
        return 0.0
    return np.dot(u, v) / cross

def _vertex_angles_sum(V, F):
    nV = V.shape[0]
    V_angles_sum = np.zeros(nV)
    for (i, j, k) in F:
        vi, vj, vk = V[i], V[j], V[k]
        def angle(a, b, c):
            u = a - b; v = c - b
            nu = np.linalg.norm(u) + 1e-16
            nv = np.linalg.norm(v) + 1e-16
            u = u / nu; v = v / nv
            return np.arccos(np.clip(np.dot(u, v), -1.0, 1.0))
        alpha = angle(vj, vi, vk)
        beta  = angle(vi, vj, vk)
        gamma = angle(vi, vk, vj)
        V_angles_sum[i] += alpha
        V_angles_sum[j] += beta
        V_angles_sum[k] += gamma
    return V_angles_sum

def _is_boundary_vertices(F, nV):
    from collections import defaultdict
    edge_count = defaultdict(int)
    for (i, j, k) in F:
        for a, b in [(i, j), (j, k), (k, i)]:
            if a > b: a, b = b, a
            edge_count[(a, b)] += 1
    boundary = np.zeros(nV, dtype=bool)
    for (a, b), c in edge_count.items():
        if c == 1:
            boundary[a] = True
            boundary[b] = True
    return boundary

def discrete_curvatures_ddg(mesh: o3d.geometry.TriangleMesh):
    V = np.asarray(mesh.vertices)
    F = np.asarray(mesh.triangles)
    nV = len(V)
    A_v = compute_mixed_voronoi_areas(mesh)

    # 평균곡률벡터
    Hn = np.zeros((nV, 3))
    for (i, j, k) in F:
        vi, vj, vk = V[i], V[j], V[k]
        cij = _cot_angle(vi - vk, vj - vk)
        cik = _cot_angle(vi - vj, vk - vj)
        cji = _cot_angle(vj - vk, vi - vk)
        cjk = _cot_angle(vj - vi, vk - vi)
        cki = _cot_angle(vk - vj, vi - vj)
        ckj = _cot_angle(vk - vi, vj - vi)
        Hn[i] += (cij + cik) * (vj - vi)
        Hn[j] += (cji + cjk) * (vk - vj)
        Hn[k] += (cki + ckj) * (vi - vk)
    Hn = 0.5 * (Hn / A_v[:, None])
    H_ddg = 0.5 * np.linalg.norm(Hn, axis=1)

    V_angles_sum = _vertex_angles_sum(V, F)
    boundary = _is_boundary_vertices(F, nV)
    full_angle = np.where(boundary, np.pi, 2.0 * np.pi)  # 경계 보정
    K_ddg = (full_angle - V_angles_sum) / A_v

    return H_ddg, K_ddg, A_v

# =========================================
# 2) 면적×거리 가중 2차 회귀 기반 주곡률(k1,k2)
# =========================================
def _build_adjacency(nV, F):
    adj = [[] for _ in range(nV)]
    for (i, j, k) in F:
        adj[i].extend([j, k])
        adj[j].extend([i, k])
        adj[k].extend([i, j])
    adj = [list(dict.fromkeys(l)) for l in adj]
    return adj

def estimate_principal_curvatures_area_weighted(mesh, A_v, geodesic_steps=2, sigma_scale=3.0):
    V = np.asarray(mesh.vertices)
    F = np.asarray(mesh.triangles)
    nV = len(V)
    adj = _build_adjacency(nV, F)

    # 지역 스케일(평균 에지길이) 추정
    edges = set()
    for (i, j, k) in F:
        edges.add(tuple(sorted((i, j))))
        edges.add(tuple(sorted((j, k))))
        edges.add(tuple(sorted((k, i))))
    edges = list(edges)
    elen = np.array([np.linalg.norm(V[a] - V[b]) for (a, b) in edges])
    mean_edge = np.mean(elen) if len(elen) > 0 else 1.0
    sigma = sigma_scale * mean_edge

    k1 = np.zeros(nV)
    k2 = np.zeros(nV)
    for i in range(nV):
        # 지오데식 BFS 링
        ring = {i}
        frontier = {i}
        for _ in range(geodesic_steps):
            nxt = set()
            for u in frontier:
                nxt.update(adj[u])
            ring.update(nxt)
            frontier = nxt
        ring = list(ring)

        P = V[ring]
        p0 = V[i]
        X = P - p0

        # PCA로 법선/접평면 추정
        C = np.cov(X.T) if X.shape[0] > 2 else np.eye(3)
        evals, evecs = np.linalg.eigh(C)
        n = evecs[:, 0]
        T = evecs[:, 1:]
        tcoord = X @ T
        z = (X @ n).reshape(-1, 1)

        # 면적×거리 가중
        r2 = np.sum(tcoord**2, axis=1)
        w = A_v[ring] * np.exp(-r2 / (2 * sigma * sigma))
        w = (w / (w.max() + 1e-16)).reshape(-1, 1)

        # 2차 + 1차 회귀
        A = np.column_stack([
            tcoord[:, 0]**2,
            tcoord[:, 1]**2,
            tcoord[:, 0]*tcoord[:, 1],
            tcoord[:, 0],
            tcoord[:, 1]
        ])
        Aw = A * w
        zw = z * w
        try:
            coef, *_ = np.linalg.lstsq(Aw, zw, rcond=None)
            a, b, c, d, e = coef.flatten()
            H2 = np.array([[2*a, c],
                           [c, 2*b]])
            ev = np.linalg.eigvalsh(H2)
            k1[i] = ev.max()
            k2[i] = ev.min()
        except Exception:
            k1[i] = 0.0
            k2[i] = 0.0

    return k1, k2

# =========================================
# 3) 기존 k-NN 회귀(비교용)
# =========================================
def estimate_principal_curvatures_knn(mesh, k=20):
    points = np.asarray(mesh.vertices)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    mesh_tree = o3d.geometry.KDTreeFlann(pcd)

    k1_list, k2_list = [], []
    for i in range(len(points)):
        _, idx, _ = mesh_tree.search_knn_vector_3d(points[i], k)
        neighbors = points[idx, :] - points[i]
        if neighbors.shape[0] < 6:
            k1_list.append(0.0); k2_list.append(0.0); continue
        cov = np.cov(neighbors.T)
        eigvals, eigvecs = np.linalg.eigh(cov)
        normal = eigvecs[:, 0]
        tangent_coords = neighbors @ eigvecs[:, 1:]

        Z = ((neighbors @ normal) / (np.linalg.norm(neighbors, axis=1).max() + 1e-12)).reshape(-1, 1)
        A = np.column_stack([
            tangent_coords[:, 0]**2,
            tangent_coords[:, 1]**2,
            tangent_coords[:, 0]*tangent_coords[:, 1]
        ])
        coef, _, _, _ = np.linalg.lstsq(A, Z, rcond=None)
        a, b, c = coef.flatten()
        H = np.array([[2 * a, c], [c, 2 * b]])
        evals = np.linalg.eigvalsh(H)
        k1_list.append(evals.max())
        k2_list.append(evals.min())

    return np.array(k1_list), np.array(k2_list)

# =========================================
# 4) 메인 파이프라인
# =========================================
import_root = r"C:\Users\Administrator\Desktop\SUB\Structure variable\Curvature\Ongoing2"
export_folder = os.path.join(import_root, "Result")
os.makedirs(export_folder, exist_ok=True)

resample = input("👉 Simplify mesh before curvature calculation? (Yes/No): ").strip().lower()
use_knn_baseline = True
geodesic_steps = 2
sigma_scale = 3.0
clim_range = [-3, 3]  # 시각화 범위 고정

stl_files = glob(os.path.join(import_root, "*.stl"))

for stl_path in stl_files:
    filename = os.path.splitext(os.path.basename(stl_path))[0]
    print(f"\n📂 Processing: {filename}")

    mesh = o3d.io.read_triangle_mesh(stl_path)
    if not mesh.has_triangle_normals():
        mesh.compute_triangle_normals()
    mesh.compute_vertex_normals()

    if resample == "yes":
        original_tri = len(mesh.triangles)
        mesh = mesh.simplify_quadric_decimation(target_triangle_count=min(100000, original_tri // 2))
        mesh.remove_unreferenced_vertices()
        mesh.remove_degenerate_triangles()
        mesh.remove_duplicated_vertices()
        mesh.remove_duplicated_triangles()
        mesh.compute_vertex_normals()
        print(f"🔧 Simplified from {original_tri} to {len(mesh.triangles)} triangles.")

    # --- DDG 기반 ---
    H_ddg, K_ddg, A_v = discrete_curvatures_ddg(mesh)

    # --- 면적×거리 가중 회귀 기반 주곡률 ---
    k1_w, k2_w = estimate_principal_curvatures_area_weighted(mesh, A_v,
                                                             geodesic_steps=geodesic_steps,
                                                             sigma_scale=sigma_scale)
    H_w = 0.5 * (k1_w + k2_w)
    K_w = k1_w * k2_w

    # --- kNN(비교용) ---
    if use_knn_baseline:
        k1_knn, k2_knn = estimate_principal_curvatures_knn(mesh, k=20)
        H_knn = 0.5 * (k1_knn + k2_knn)
        K_knn = k1_knn * k2_knn
    else:
        k1_knn = k2_knn = H_knn = K_knn = np.zeros_like(k1_w)

    # =========================================
    # 저장/요약: CSV + Excel(면적가중 통계 포함)
    # =========================================
    # CSV에는 Av 대신 확률(A_prob)로 저장 (Av/sum(Av))
    A_prob = A_v / (A_v.sum() + 1e-16)

    curvature_df = pd.DataFrame({
        'A_prob (area weight)': A_prob,       # ← Av 대신 확률로 저장
        'k1_w (weighted)': k1_w,
        'k2_w (weighted)': k2_w,
        'H_w (weighted mean)': H_w,
        'K_w (weighted gaussian)': K_w,
        'H_ddg': H_ddg,
        'K_ddg': K_ddg,
    })
    if use_knn_baseline:
        curvature_df['k1_knn'] = k1_knn
        curvature_df['k2_knn'] = k2_knn
        curvature_df['H_knn']  = H_knn
        curvature_df['K_knn']  = K_knn

    csv_path  = os.path.join(export_folder, f"{filename}_Curvature.csv")
    xlsx_path = os.path.join(export_folder, f"{filename}_Summary.xlsx")

    curvature_df.to_csv(csv_path, index=False)

    with pd.ExcelWriter(xlsx_path) as writer:
        curvature_df.describe().to_excel(writer, sheet_name='Summary Stats')

        # 면적가중 통계는 내부적으로 Av를 그대로 사용 (정확한 가중을 위해)
        stats = []
        for name in ['k1_w (weighted)', 'k2_w (weighted)', 'H_w (weighted mean)', 'K_w (weighted gaussian)', 'H_ddg', 'K_ddg']:
            mu, sd = area_weighted_stats(curvature_df[name].values, A_v)
            stats.append((name, mu, sd))
        if use_knn_baseline:
            for name in ['k1_knn', 'k2_knn', 'H_knn', 'K_knn']:
                mu, sd = area_weighted_stats(curvature_df[name].values, A_v)
                stats.append((name, mu, sd))
        df_wstats = pd.DataFrame(stats, columns=['metric', 'area_weighted_mean', 'area_weighted_std'])
        df_wstats.to_excel(writer, sheet_name='Area-Weighted Stats', index=False)

        # 면적가중 히스토그램 (left_edge, right_edge, bin_center, probability 구조)
        def hist_to_df(values, areas, bins=120, label='metric'):
            centers, prob, edges = area_weighted_hist(values, areas, bins=bins)
            return pd.DataFrame({
                'left_edge': edges[:-1],
                'right_edge': edges[1:],
                'bin_center': centers,
                'probability': prob,
                'metric': label
            })

        hist_frames = []
        hist_frames.append(hist_to_df(k1_w, A_v, label='k1_w'))
        hist_frames.append(hist_to_df(k2_w, A_v, label='k2_w'))
        hist_frames.append(hist_to_df(H_w,  A_v, label='H_w'))
        hist_frames.append(hist_to_df(K_w,  A_v, label='K_w'))
        hist_frames.append(hist_to_df(H_ddg, A_v, label='H_ddg'))
        hist_frames.append(hist_to_df(K_ddg, A_v, label='K_ddg'))
        if use_knn_baseline:
            hist_frames.append(hist_to_df(k1_knn, A_v, label='k1_knn'))
            hist_frames.append(hist_to_df(k2_knn, A_v, label='k2_knn'))
            hist_frames.append(hist_to_df(H_knn,  A_v, label='H_knn'))
            hist_frames.append(hist_to_df(K_knn,  A_v, label='K_knn'))

        df_hist = pd.concat(hist_frames, ignore_index=True)
        df_hist.to_excel(writer, sheet_name='Area-Weighted Hists', index=False)

         # 4) H, K 값을 20등분한 Probability 시트 추가
    def prob_bins(values, areas, bins=20, label='metric'):
        hist, edges = np.histogram(values, bins=bins, weights=areas, density=False)
        prob = hist / np.sum(hist)
        left_edges = edges[:-1]
        right_edges = edges[1:]
        centers = 0.5 * (left_edges + right_edges)
        return pd.DataFrame({
            'left_edge': left_edges,
            'right_edge': right_edges,
            'bin_center': centers,
            'probability': prob,
            'metric': label
        })

    prob_frames = []
    prob_frames.append(prob_bins(H_w, A_v, bins=20, label='H_w'))
    prob_frames.append(prob_bins(K_w, A_v, bins=20, label='K_w'))
    prob_frames.append(prob_bins(H_ddg, A_v, bins=20, label='H_ddg'))
    prob_frames.append(prob_bins(K_ddg, A_v, bins=20, label='K_ddg'))
    if use_knn_baseline:
        prob_frames.append(prob_bins(H_knn, A_v, bins=20, label='H_knn'))
        prob_frames.append(prob_bins(K_knn, A_v, bins=20, label='K_knn'))

    df_prob_bins = pd.concat(prob_frames, ignore_index=True)
    df_prob_bins.to_excel(writer, sheet_name='H_K_20bin_Probability', index=False)

    # =========================================
    # 시각화/PLY 저장
    # =========================================
    # DDG
    mesh_pv_K_ddg = convert_o3d_to_pyvista(mesh, np.clip(K_ddg, clim_range[0], clim_range[1]), "Gaussian Curvature (DDG)")
    visualize_and_save(mesh_pv_K_ddg, "Gaussian Curvature (DDG)", clim_range, os.path.join(export_folder, f"{filename}_Gaussian_DDG.png"))
    mesh_pv_K_ddg.save(os.path.join(export_folder, f"{filename}_Gaussian_DDG.ply"))

    mesh_pv_H_ddg = convert_o3d_to_pyvista(mesh, np.clip(H_ddg, clim_range[0], clim_range[1]), "Mean Curvature (DDG)")
    visualize_and_save(mesh_pv_H_ddg, "Mean Curvature (DDG)", clim_range, os.path.join(export_folder, f"{filename}_Mean_DDG.png"))
    mesh_pv_H_ddg.save(os.path.join(export_folder, f"{filename}_Mean_DDG.ply"))

    # WeightedFit
    mesh_pv_K_w = convert_o3d_to_pyvista(mesh, np.clip(K_w, clim_range[0], clim_range[1]), "Gaussian Curvature (WeightedFit)")
    visualize_and_save(mesh_pv_K_w, "Gaussian Curvature (WeightedFit)", clim_range, os.path.join(export_folder, f"{filename}_Gaussian_WeightedFit.png"))
    mesh_pv_K_w.save(os.path.join(export_folder, f"{filename}_Gaussian_WeightedFit.ply"))

    mesh_pv_H_w = convert_o3d_to_pyvista(mesh, np.clip(H_w, clim_range[0], clim_range[1]), "Mean Curvature (WeightedFit)")
    visualize_and_save(mesh_pv_H_w, "Mean Curvature (WeightedFit)", clim_range, os.path.join(export_folder, f"{filename}_Mean_WeightedFit.png"))
    mesh_pv_H_w.save(os.path.join(export_folder, f"{filename}_Mean_WeightedFit.ply"))

    # kNN
    if use_knn_baseline:
        mesh_pv_K_knn = convert_o3d_to_pyvista(mesh, np.clip(K_knn, clim_range[0], clim_range[1]), "Gaussian Curvature (kNN)")
        visualize_and_save(mesh_pv_K_knn, "Gaussian Curvature (kNN)", clim_range, os.path.join(export_folder, f"{filename}_Gaussian_kNN.png"))
        mesh_pv_K_knn.save(os.path.join(export_folder, f"{filename}_Gaussian_kNN.ply"))

        mesh_pv_H_knn = convert_o3d_to_pyvista(mesh, np.clip(H_knn, clim_range[0], clim_range[1]), "Mean Curvature (kNN)")
        visualize_and_save(mesh_pv_H_knn, "Mean Curvature (kNN)", clim_range, os.path.join(export_folder, f"{filename}_Mean_kNN.png"))
        mesh_pv_H_knn.save(os.path.join(export_folder, f"{filename}_Mean_kNN.ply"))

    print(f"✅ Saved CSV: {csv_path}")
    print(f"📊 Saved Summary: {xlsx_path}")
