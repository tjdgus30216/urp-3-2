from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-097"
CONTRACTS = FACTORY / "contracts"
REPORTS = FACTORY / "reports"
GROUPS = ["LIT-X006", "LIT-X008", "LIT-X019", "LIT-X024", "LIT-X028", "LIT-X031"]

INPUTS = {
    "PRM096_requirements": TABLES / "PRM096_third_wave_preregistration_requirements.csv",
    "PRM096_routing": TABLES / "PRM096_third_wave_candidate_routing.csv",
    "PRM096_bank": TABLES / "PRM096_enriched_xreg_v0_2_candidate_bank.csv",
    "PRM096_gates": TABLES / "PRM096_later_nested_gate_preservation.csv",
    "literature_candidates": TABLES / "PRM076_combined_literature_candidate_registry.csv",
    "literature_sources": TABLES / "PRM076_combined_literature_source_registry.csv",
    "uniform_gates": TABLES / "PRM076_uniform_qualification_gate.csv",
    "prior_fixtures": TABLES / "PRM076_synthetic_truth_fixture_spec.csv",
    "prior_resolution": TABLES / "PRM076_resolution_panel_spec.csv",
    "existing_roster": TABLES / "PRM081_full58_output_roster.csv",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def row(candidate_id: str, group: str, output: str, role: str, formula_id: str, unit: str,
        population: str, family: str, expected_range: str, lineage: str, direct: str,
        status: str, notes: str = "") -> dict:
    return {
        "candidate_id": candidate_id,
        "candidate_group_id": group,
        "output_name": output,
        "preregistered_role": role,
        "formula_id": formula_id,
        "unit": unit,
        "input_population": population,
        "applicable_family": family,
        "expected_range": expected_range,
        "source_lineage": lineage,
        "direct_or_derived": direct,
        "status_label": status,
        "execution_status": "not_executed_preregistration_only",
        "active_feature": False,
        "promoted": False,
        "y_evidence": False,
        "notes": notes,
    }


def build_output_roster() -> pd.DataFrame:
    rows: list[dict] = []
    x006 = [
        ("component_count", "count", "integer>=0", "X006-F03"),
        ("node_count", "count", "integer>=0", "X006-F03"),
        ("edge_count", "count", "integer>=0", "X006-F03"),
        ("endpoint_fraction", "dimensionless", "[0,1] or missing if V=0", "X006-F03"),
        ("branchpoint_fraction", "dimensionless", "[0,1] or missing if V=0", "X006-F03"),
        ("mean_node_degree", "dimensionless", ">=0 or missing", "X006-F03"),
        ("population_std_node_degree", "dimensionless", ">=0 or missing", "X006-F03"),
        ("cycle_rank", "count", "integer>=0", "X006-F03"),
        ("cycle_rank_density_per_mm3", "1/mm^3", ">=0", "X006-F03"),
        ("total_edge_length_mm", "mm", ">=0", "X006-F04"),
        ("edge_length_q50_mm", "mm", ">=0 or missing", "X006-F04"),
        ("edge_length_q90_mm", "mm", ">=0 or missing", "X006-F04"),
        ("z_alignment_abs_cos_mean", "dimensionless", "[0,1] or missing", "X006-F04"),
        ("dangling_edge_fraction", "dimensionless", "[0,1] or missing", "X006-F04"),
    ]
    for name, unit, rng, fid in x006:
        rows.append(row(f"LIT-X006::{name}", "LIT-X006", name, "BCL_specialist_candidate_FT_sensitivity", fid, unit,
                        "26-neighbour no-prune Lee skeleton collapsed to an undirected multigraph", "B|C|L primary; F|T sensitivity", rng,
                        "PRM097 frozen skeleton-graph lineage", "direct_from_fixed_mask", "likely",
                        "No periodic wrap; no canonical pruning. F/T cannot be mixed with B/C/L without a specialist policy."))

    x008 = [
        ("local_thickness_mean_mm", "technical_candidate", "X008-F02", "mm", ">0"),
        ("local_thickness_population_std_mm", "technical_candidate", "X008-F02", "mm", ">=0"),
        ("local_thickness_q10_mm", "technical_candidate", "X008-F02", "mm", ">0"),
        ("local_thickness_q50_mm", "technical_candidate", "X008-F02", "mm", ">0"),
        ("local_thickness_q90_mm", "technical_candidate", "X008-F02", "mm", ">0"),
        ("local_thickness_cv", "technical_candidate", "X008-F02", "dimensionless", ">=0"),
        ("bottleneck_q10_over_q50", "technical_candidate", "X008-F03", "dimensionless", "(0,1]"),
        ("constriction_index_one_minus_q10_q50", "diagnostic_affine_identity", "X008-F03", "dimensionless", "[0,1)"),
    ]
    for name, role, fid, unit, rng in x008:
        rows.append(row(f"LIT-X008::{name}", "LIT-X008", name, role, fid, unit,
                        "all solid voxel centers; maximal-inscribed digital sphere local thickness", "B|C|L|F|T", rng,
                        "Hildebrand-Ruegsegger local-thickness definition; PRM097 digital convention", "direct_from_fixed_mask", "likely",
                        "Outside-domain is explicit void padding; no half-voxel correction; PoreSpy is not required."))

    for axis in "xyz":
        for stat in ["mean", "q50"]:
            name = f"solid_void_chord_{axis}_{stat}_ratio"
            rows.append(row(f"LIT-X019::{name}", "LIT-X019", name, "derived_sensitivity_candidate", "X019-F01", "dimensionless",
                            f"matched LIT-X001 solid and LIT-X016 void {axis}-{stat} chord summaries", "B|C|L|F|T", ">=0 or missing",
                            f"LIT-X001::solid_chord_{axis}_{stat}_mm / LIT-X016::void_chord_{axis}_{stat}_mm parent lineage", "derived_from_X001_X016", "likely",
                            "A phase-scale ratio, not a classical beam slenderness or Euler-buckling parameter."))
    rows.append(row("LIT-X019::solid_void_chord_q50_geomean_ratio", "LIT-X019", "solid_void_chord_q50_geomean_ratio",
                    "derived_sensitivity_candidate", "X019-F02", "dimensionless", "three positive axiswise q50 ratios", "B|C|L|F|T", ">=0 or missing",
                    "geometric mean of the three X019 q50 ratios", "derived_from_X001_X016", "likely", "Requires all three axis ratios finite and positive."))

    x024 = [
        ("ECT_curve_26x129", "artifact_only_not_scalar_feature", "X024-F02", "1/mm^3", "integer Euler density curve"),
        ("ect_abs_auc_direction_mean_per_mm3", "technical_candidate", "X024-F03", "1/mm^3", ">=0"),
        ("ect_abs_auc_direction_std_per_mm3", "technical_candidate", "X024-F03", "1/mm^3", ">=0"),
        ("ect_total_variation_direction_mean_per_mm3", "technical_candidate", "X024-F03", "1/mm^3", ">=0"),
        ("ect_total_variation_direction_std_per_mm3", "technical_candidate", "X024-F03", "1/mm^3", ">=0"),
        ("ect_antipodal_l1_mean_per_mm3", "technical_candidate", "X024-F03", "1/mm^3", ">=0"),
        ("ect_final_chi_solid_density_trace_per_mm3", "diagnostic_identity_with_X004", "X024-F03", "1/mm^3", "finite"),
    ]
    for name, role, fid, unit, rng in x024:
        rows.append(row(f"LIT-X024::{name}", "LIT-X024", name, role, fid, unit,
                        "solid-26 cubical voxel sublevel sets over 26 fixed directions and 129 specimen-fixed heights", "B|C|L|F|T", rng,
                        "Euler characteristic transform; X004 solid-26 endpoint lineage", "direct_curve_or_fixed_summary", "likely",
                        "Full curve is an artifact; scalar summaries do not preserve ECT injectivity."))

    for axis in "xyz":
        for lag in ["2p5", "10"]:
            for metric, role, rng in [
                ("P11", "diagnostic_exact_identity_with_S2", "[0,1]"),
                ("contrast", "negative_control_metric", "[0,1]"),
                ("homogeneity", "diagnostic_affine_identity_with_contrast", "[0.5,1]"),
                ("asm", "negative_control_metric", "[0.25,1]"),
                ("entropy", "negative_control_metric", "[0,ln(4)]"),
            ]:
                name = f"binary_glcm_{axis}_{lag}mm_{metric}"
                fid = "X028-F01" if metric == "P11" else "X028-F02"
                rows.append(row(f"LIT-X028::{name}", "LIT-X028", name, role, fid, "dimensionless",
                                f"symmetrized 2x2 co-occurrence matrix for nonwrapped {axis} pairs at {lag.replace('p','.') } mm", "B|C|L|F|T", rng,
                                "Haralick co-occurrence family; exact pair population shared with LIT-X002 S2", "direct_from_fixed_mask", "likely",
                                "Negative control only. P11 must equal matched S2; homogeneity must equal 1-contrast/2."))

    for band in [2, 4, 6]:
        rows.append(row(f"LIT-X031::surface_normal_H{band}", "LIT-X031", f"surface_normal_H{band}",
                        "diagnostic_overlap_X005" if band == 2 else "technical_candidate", "X031-F02", "dimensionless",
                        "area-weighted antipodally symmetrized marching-cubes surface normals", "B|C|L|F|T", "[0,1] up to numerical tolerance",
                        "spherical-harmonic power of surface-normal ODF", "direct_from_fixed_mask_surface", "likely",
                        "H_l is rotation invariant; odd l are excluded by the unoriented-normal convention."))
        rows.append(row(f"LIT-X031::surface_normal_Q{band}_z", "LIT-X031", f"surface_normal_Q{band}_z",
                        "diagnostic_overlap_X005" if band == 2 else "technical_candidate", "X031-F03", "dimensionless",
                        "area-weighted antipodally symmetrized marching-cubes surface normals", "B|C|L|F|T", "[-1,1]",
                        "even Legendre moment relative to the PRM082 z axis", "direct_from_fixed_mask_surface", "likely",
                        "Q_l,z is load-axis sensitive; Q2,z is expected to overlap the second-rank fabric family."))
    return pd.DataFrame(rows)


def build_formula_registry() -> pd.DataFrame:
    formulas = [
        ("X006-F01", "LIT-X006", "Lee skeleton", "S=skeletonize(M, method='lee') on the Boolean solid mask; 26-neighbour adjacency; no wrap; no pruning.", "solid mask M; voxel pitch delta", "zero/void outside specimen; retain boundary skeleton voxels", "skimage.morphology.skeletonize", "independent explicit 26-neighbour degree census"),
        ("X006-F02", "LIT-X006", "skeleton-to-multigraph", "Cluster skeleton voxels with voxel-degree !=2 using 26-connectivity into graph nodes; connect nodes by maximal degree-2 chains. A pure closed chain receives one lexicographic anchor and one self-loop.", "S and 26 offsets", "undirected MultiGraph; boundary endpoints retained and flagged", "NumPy+NetworkX", "independent chain tracer with sorted voxel coordinates"),
        ("X006-F03", "LIT-X006", "graph topology summaries", "C=number of graph components; V=nodes; E=multiedges; cycle_rank=E-V+C; fractions divide by V or E only when denominator>0; population std uses ddof=0.", "collapsed graph", "missing rather than zero for undefined ratios", "NetworkX+NumPy", "direct graph arithmetic replay"),
        ("X006-F04", "LIT-X006", "graph geometry summaries", "Each skeleton step has length delta*sqrt(dx^2+dy^2+dz^2); edge length is step sum; z_alignment=sum(delta*abs(dz))/sum(step_length); dangling fraction counts edges incident to degree-1 nodes.", "ordered degree-2 chains", "no periodic edge; no canonical pruning", "NumPy", "independent step-list aggregation"),
        ("X008-F01", "LIT-X008", "digital local thickness field", "r(c)=EDT(c)*delta on one-voxel void-padded solid mask. LT(q)=max_{c: ||q-c||<=r(c)} 2*r(c), for every solid voxel center q.", "solid mask; isotropic pitch", "outside-domain void; center-distance digital convention; no half-voxel correction", "SciPy EDT + deterministic maximal-ball propagation", "independent descending-radius ball fill"),
        ("X008-F02", "LIT-X008", "local thickness summaries", "Equal-voxel population mean, ddof=0 std, q10/q50/q90; CV=std/mean only if mean>1e-12 mm.", "finite LT values on solid voxels", "empty solid -> explicit missing", "NumPy", "independent quantile/reduction replay"),
        ("X008-F03", "LIT-X008", "lower-tail bottleneck proxy", "B=q10(LT)/q50(LT) if q50>1e-12; constriction=1-B. This is a distributional proxy, not an axial minimum-cut.", "LT distribution", "undefined denominator -> missing", "NumPy", "analytic affine-identity check"),
        ("X019-F01", "LIT-X019", "axiswise matched phase-scale ratio", "R_{a,s}=solid_chord_{a,s}/void_chord_{a,s} for a in {x,y,z}, s in {mean,q50}; numerator and denominator must use the same V128 mask, axis and statistic.", "qualified X001/X016 parent values", "void value<=1e-12 or missing -> ratio missing; no estimator mixing", "CSV lineage join", "independent parent-ID join and division"),
        ("X019-F02", "LIT-X019", "pooled q50 phase-scale ratio", "R_geo=exp(mean(log(R_x,q50),log(R_y,q50),log(R_z,q50))) when all three are finite and >0.", "three axis q50 ratios", "any invalid axis -> missing; no arithmetic-mean substitution", "NumPy", "independent logarithmic replay"),
        ("X024-F01", "LIT-X024", "ECT direction-height grid", "Directions are all 26 normalized nonzero vectors in {-1,0,1}^3. Heights t_j=j/128, j=0..128, mapped to the fixed 40-mm specimen-cube projection interval for each direction.", "voxel-center coordinates in PRM082 axis semantics", "specimen-fixed, not shape-min/max; no wrap", "deterministic integer direction registry", "exact direction/antipode and height-grid audit"),
        ("X024-F02", "LIT-X024", "solid Euler curves", "chi_v(j)=euler_number(M AND <x,v><=h_v(t_j), connectivity=3); curve value is chi_v(j)/64000 mm^3.", "solid mask and X024-F01 grid", "solid-26 convention; empty sublevel chi=0", "skimage.measure.euler_number", "independent cubical-mask replay"),
        ("X024-F03", "LIT-X024", "ECT scalar summaries", "For each direction: A_v=trapezoid(|chi_v(t)|,t); TV_v=sum_j|Delta chi_v|. Report direction mean/ddof0 std; antipodal L1 is mean over 13 pairs and 129 heights of |chi_v-chi_-v|; final-chi is trace only.", "26x129 Euler-density curves", "no PCA/learned curve compression", "NumPy", "independent curve summary replay"),
        ("X028-F01", "LIT-X028", "binary co-occurrence population", "For each axis and physical lag, count valid nonwrapped ordered pairs into P_fwd(i,j), normalize by pair count, then P=(P_fwd+P_fwd^T)/2. P11 equals matched LIT-X002 S2 exactly.", "Boolean mask; lags 2.5 and 10 mm", "lag must be an integer voxel shift; otherwise stop rather than round", "NumPy slicing", "direct pair recount and P11=S2 identity"),
        ("X028-F02", "LIT-X028", "binary Haralick controls", "contrast=sum(i-j)^2Pij; homogeneity=sum Pij/(1+|i-j|); ASM=sum Pij^2; entropy=-sum_{Pij>0}Pij ln(Pij). For binary P, homogeneity=1-contrast/2.", "normalized symmetric 2x2 P", "natural log; 0log0=0", "NumPy", "analytic identities plus independent recount"),
        ("X031-F01", "LIT-X031", "unoriented surface-normal ODF", "Use the exact PRM082 marching-cubes surface. Each nonzero-area face contributes n and -n with weights A/(2*A_total); weights sum to one. Axes follow PRM082 array semantics.", "V64/V96/V128 mask-derived triangle normals/areas", "one-voxel void padding; no smoothing/remeshing; zero-area faces removed", "skimage marching_cubes + NumPy", "independent face-normal/area extraction"),
        ("X031-F02", "LIT-X031", "rotation-invariant harmonic power", "c_lm=sum_i w_i Y_lm(theta_i,phi_i); H_l=(4*pi/(2l+1))*sum_{m=-l..l}|c_lm|^2 for l=2,4,6. SciPy complex orthonormal sph_harm_y convention: theta=polar, phi=azimuth.", "antipodal ODF", "odd l excluded; no learned weighting", "scipy.special.sph_harm_y", "independent coefficient loop and rotation test"),
        ("X031-F03", "LIT-X031", "load-axis Legendre moments", "Q_l,z=sum_faces (A/A_total)*P_l(|n_z|), l=2,4,6, using even Legendre polynomials.", "unoriented face normals", "z axis exactly matches PRM082 v1_z_alignment semantics", "scipy.special.eval_legendre", "independent polynomial evaluation"),
    ]
    return pd.DataFrame(formulas, columns=["formula_id", "candidate_group_id", "formula_name", "exact_definition", "parameters", "boundary_or_missingness", "implementation_route", "independent_replay_route"])


def build_boundary_policy() -> pd.DataFrame:
    rows = [
        ("LIT-X006", "solid VoxelMask-V128", "26-neighbour skeleton and graph", "no wrap", "one-voxel outside void inherited from mask", "undefined ratios are missing", "B/C/L primary; F/T sensitivity", "canonical no-prune; 2delta and 4delta terminal pruning are sensitivity-only and not in the output roster"),
        ("LIT-X008", "solid VoxelMask", "Euclidean EDT/maximal digital balls", "no wrap", "one-voxel explicit void", "empty solid or invalid median -> missing", "all", "isotropic pitch required; no PoreSpy dependency"),
        ("LIT-X019", "X001 solid chord + X016 void chord", "same axis/statistic only", "inherits parents", "inherits parents", "invalid denominator or any pooled axis -> missing", "all", "not classical beam slenderness; inherits worst parent resolution status"),
        ("LIT-X024", "solid VoxelMask", "solid-26 Euler", "no wrap", "fixed 40-mm specimen projection", "empty sublevel chi=0", "all", "26 directions and 129 heights fixed before calculation"),
        ("LIT-X028", "solid VoxelMask", "valid ordered voxel pairs", "no wrap", "pairs outside array excluded", "noninteger physical lag/pitch -> stop", "all", "same pair population as X002 required"),
        ("LIT-X031", "PRM082 mask-derived surface triangles", "area-weighted antipodal normals", "not applicable", "one-voxel outside void before marching cubes", "no area -> missing", "all surface; skeleton version excluded", "no smoothing/remeshing and no skeleton orientation mixing"),
    ]
    return pd.DataFrame(rows, columns=["candidate_group_id", "source_population", "connectivity_or_sampling", "periodic_policy", "boundary_policy", "missingness_policy", "applicable_family", "separation_rule"])


def build_fixtures() -> pd.DataFrame:
    rows = [
        ("SYN-GRAPH-LINE", "LIT-X006", "one-voxel-thick 26-connected straight chain", "V=2,E=1,C=1,cycle_rank=0,endpoint_fraction=1", "integer exact", "topology baseline"),
        ("SYN-GRAPH-Y", "LIT-X006", "three equal arms meeting at one junction", "one degree-3 branch cluster, three endpoints, cycle_rank=0", "integer exact after fixed digital mask", "branch truth"),
        ("SYN-GRAPH-RING", "LIT-X006", "single closed digital loop away from boundary", "C=1,cycle_rank=1,no endpoints; lexicographic anchor/self-loop path", "integer exact", "pure-loop special case"),
        ("SYN-LT-SPHERE", "LIT-X008", "digital sphere of declared EDT radius R away from boundary", "central/maximal thickness approximately 2R and all outputs positive", "max error <=2 voxel pitches; ordering exact", "local-thickness truth"),
        ("SYN-LT-CYLINDER", "LIT-X008", "long digital cylinder diameter D away from boundary", "interior local-thickness q50 approximately D", "relative error <=5% at V128", "member thickness truth"),
        ("SYN-LT-STEP", "LIT-X008", "wide cylinder joined to narrower cylinder", "q10<q50<q90 and bottleneck ratio<1", "ordering exact", "bottleneck ordering"),
        ("SYN-GAP", "LIT-X019", "two solid plates with a known void gap", "matched solid/void chord ratios equal parent quotient", "<=1e-12 from parent replay", "parent lineage"),
        ("SYN-PHASE-STRIPES", "LIT-X019", "alternating solid and void slabs with declared widths", "axiswise mean and q50 ratio equals digital solid-run/void-run length ratio", "integer-run exact", "phase-scale ratio truth"),
        ("SYN-EMPTY", "LIT-X024", "all-void cube", "all 26x129 Euler-density curves and summaries are zero", "exact", "ECT zero case"),
        ("SYN-FULL", "LIT-X024", "all-solid cube", "final chi density is 1/64000 for every direction", "exact", "ECT endpoint identity"),
        ("SYN-2BODY", "LIT-X024", "two disjoint solid cubes", "final chi=2 for every direction", "exact", "component truth"),
        ("SYN-TORUS", "LIT-X024", "single digital torus away from boundary", "final chi=0 at resolutions passing the topology fixture", "exact integer after topology qualification", "loop truth"),
        ("SYN-CAVITY", "LIT-X024", "solid body with one enclosed cavity", "final chi=2 at resolutions passing the topology fixture", "exact integer after topology qualification", "cavity truth"),
        ("SYN-ECT-SHIFT", "LIT-X024", "same solid translated inside the fixed specimen cube", "final chi unchanged but direction-height curve location changes", "endpoint exact and curve nonidentity required", "translation sensitivity"),
        ("SYN-GLCM-ZERO", "LIT-X028", "all-void cube", "P00=1; P11=contrast=entropy=0; homogeneity=ASM=1", "<=1e-12", "co-occurrence edge case"),
        ("SYN-GLCM-ONE", "LIT-X028", "all-solid cube", "P11=1; contrast=entropy=0; homogeneity=ASM=1", "<=1e-12", "P11/S2 identity"),
        ("SYN-GLCM-CHECKER", "LIT-X028", "alternating binary checkerboard at one-voxel lag", "P01=P10=0.5; contrast=1; homogeneity=0.5; ASM=0.5; entropy=ln2", "<=1e-12", "analytic feature truth"),
        ("SYN-GLCM-STRIPES", "LIT-X028", "axis-aligned binary stripes", "axis permutation permutes directional outputs", "<=1e-12 after axis relabel", "direction truth"),
        ("SYN-ODF-AXIS-Z", "LIT-X031", "equal unoriented normals at plus/minus z", "H2=H4=H6=1 and Q2z=Q4z=Q6z=1", "<=1e-10", "harmonic normalization"),
        ("SYN-ODF-CUBIC", "LIT-X031", "equal area normals at plus/minus x/y/z", "H2=0 and Q2z=0; higher bands retained", "<=1e-10 for degree 2", "cubic symmetry"),
        ("SYN-ODF-ISOTROPIC", "LIT-X031", "deterministic antipodal Fibonacci-sphere normals", "H2/H4/H6 and Q2/Q4/Q6 converge toward zero", "all abs <=0.02 at registered sample size", "isotropic limit"),
        ("SYN-ODF-ROTATE", "LIT-X031", "fixed anisotropic normal set and deterministic rigid rotation", "H2/H4/H6 invariant; Q_l,z may change; sign inversion invariant", "H abs delta<=1e-10", "rotation/sign policy"),
    ]
    df = pd.DataFrame(rows, columns=["fixture_id", "candidate_group_id", "geometry_definition", "expected_truth", "tolerance_policy", "purpose"])
    df["execution_status"] = "not_executed_preregistered"
    return df


def build_source_crosswalk() -> pd.DataFrame:
    rows = [
        ("LIT-X006", "SRC-LIT-019", "Network models for characterization of trabecular bone", "https://arxiv.org/abs/1811.00092", "primary/preprint", "interpretable skeleton graph degree, link and orientation rationale"),
        ("LIT-X006", "SRC-LIT-030", "Graph-theoretical description and continuity problems for stress propagation through complex strut lattices", "https://doi.org/10.1038/s44431-025-00004-7", "peer-reviewed primary", "graph mechanics and B/C/L specialist rationale"),
        ("LIT-X008", "SRC-PRM097-001", "A new method for the model-independent assessment of thickness in three-dimensional images", "https://doi.org/10.1046/j.1365-2818.1997.1340694.x", "peer-reviewed primary", "maximal-sphere local-thickness definition"),
        ("LIT-X008", "SRC-LIT-032", "Microstructure characterization and stochastic modeling of open-cell foam based on micro-CT image analysis", "https://doi.org/10.1002/gamm.202200018", "peer-reviewed primary", "distance-transform scale distributions in foam"),
        ("LIT-X019", "SRC-LIT-015", "Density and architecture have greater effects on the toughness of trabecular bone than damage", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2746406/", "peer-reviewed primary", "thickness, spacing and slenderness in compression mechanics"),
        ("LIT-X019", "SRC-LIT-020", "Scaling laws for compressive properties of modified BCC lattices", "https://doi.org/10.1002/eng2.12566", "peer-reviewed primary", "strut scale/aspect-ratio compression rationale"),
        ("LIT-X024", "SRC-PRM097-002", "Persistent Homology and Euler Integral Transforms", "https://arxiv.org/abs/1804.04740", "primary/preprint", "direction-indexed Euler transform definition and injectivity context"),
        ("LIT-X024", "SRC-PRM097-003", "How Many Directions Determine a Shape and Other Sufficiency Results for Two Topological Transforms", "https://arxiv.org/abs/1805.09782", "primary/preprint", "finite-direction sufficiency context; not proof for this 26-direction discretization"),
        ("LIT-X028", "SRC-PRM097-004", "Textural Features for Image Classification", "https://doi.org/10.1109/TSMC.1973.4309314", "peer-reviewed primary", "co-occurrence probability and texture feature lineage"),
        ("LIT-X028", "SRC-LIT-029", "Material microstructures analyzed by using gray level co-occurrence matrices", "https://doi.org/10.1088/1674-1056/26/9/098104", "peer-reviewed primary", "materials-microstructure transfer context"),
        ("LIT-X031", "SRC-PRM097-005", "Expressing Crystallographic Textures through the Orientation Distribution Function", "https://doi.org/10.1007/s11661-009-9936-8", "peer-reviewed primary", "orientation-distribution harmonic expansion"),
        ("LIT-X031", "SRC-PRM097-006", "Rotation Invariant Spherical Harmonic Representation of 3D Shape Descriptors", "https://www.cs.jhu.edu/~misha/MyPapers/TOG03.pdf", "peer-reviewed primary", "degree-wise harmonic power as rotation-invariant descriptor"),
    ]
    df = pd.DataFrame(rows, columns=["candidate_group_id", "source_id", "title", "url", "source_type", "use_in_PRM097"])
    df["claim_boundary"] = "supports formula/rationale only; does not establish predictive utility for URP4-1"
    return df


def main() -> None:
    for p in [TABLES, CONTRACTS, REPORTS]:
        p.mkdir(parents=True, exist_ok=True)
    requirements = pd.read_csv(INPUTS["PRM096_requirements"])
    if set(requirements.candidate_group_id) != set(GROUPS):
        raise SystemExit("PRM096 six-group handoff mismatch")

    roster = build_output_roster()
    formulas = build_formula_registry()
    boundary = build_boundary_policy()
    fixtures = build_fixtures()
    sources = build_source_crosswalk()
    roster.to_csv(TABLES / "PRM097_candidate_output_schema.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    formulas.to_csv(TABLES / "PRM097_formula_contract_registry.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    boundary.to_csv(TABLES / "PRM097_population_boundary_missingness_policy.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    fixtures.to_csv(TABLES / "PRM097_synthetic_truth_fixture_registry.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    sources.to_csv(TABLES / "PRM097_primary_source_crosswalk.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    # Fixed representative panel; no cell is authorized here.
    panel_models = [("B3", "B", "simple lattice"), ("C1", "C", "combined cubic lattice"), ("L1", "L", "truss lattice"), ("F1", "F", "foam coverage canary"), ("T8", "T", "TPMS Diamond A"), ("T9", "T", "TPMS Diamond B difficult pair")]
    panel_rows = []
    for group in GROUPS:
        for model, family, reason in panel_models:
            role = "primary_panel" if not (group == "LIT-X006" and family in {"F", "T"}) else "family_sensitivity_only"
            panel_rows.append({"candidate_group_id": group, "model_id": model, "model_family": family, "panel_role": role, "reason": reason, "resolution_order": "V64 cost canary -> V96 -> V128 only after gates", "execution_authorized": False})
    panel = pd.DataFrame(panel_rows)
    panel.to_csv(TABLES / "PRM097_representative_panel_scope.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    # Resolution and parameter policies.
    resolution_rows = []
    for group in GROUPS:
        for rid, n, pitch, role in [("V064", 64, 0.625, "coarse cost/sensitivity"), ("V096", 96, 40/96, "mid diagnostic"), ("V128", 128, 0.3125, "reference candidate after prior gates"), ("V192", 192, 40/192, "fine confirmation cost-gated")]:
            resolution_rows.append({
                "candidate_group_id": group, "resolution_id": rid, "voxels_per_axis": n, "pitch_mm": pitch, "role": role,
                "group_specific_parameters": (
                    "prune=none canonical; terminal prune 2delta/4delta sensitivity" if group == "LIT-X006" else
                    "digital maximal-ball; no half-voxel correction" if group == "LIT-X008" else
                    "reuse matched X001/X016 at identical resolution" if group == "LIT-X019" else
                    "26 directions; 129 fixed heights" if group == "LIT-X024" else
                    "lags 2.5/10mm must divide pitch exactly" if group == "LIT-X028" else
                    "l=2,4,6; same marching-cubes convention as X005"
                ),
                "qualification_rule": "EQG-11 unchanged: median SRD<=5%, q90<=10%, >=6/8 strict, Spearman>=0.90, top2 overlap>=0.80; failure routes to hold, never threshold tuning",
                "execution_authorized": False,
            })
    resolution = pd.DataFrame(resolution_rows)
    resolution.to_csv(TABLES / "PRM097_resolution_parameter_panel.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    resource_limits = {
        "LIT-X006": (120, 4, "stop if graph extraction is nondeterministic or pure-loop fixture fails"),
        "LIT-X008": (300, 8, "stop if maximal-ball propagation exceeds limit; do not substitute 2*EDT silently"),
        "LIT-X019": (30, 2, "stop on parent-ID/resolution mismatch or any silent zero denominator"),
        "LIT-X024": (600, 8, "stop before panel if 26x129 V64 canary exceeds limit or topology fixtures fail"),
        "LIT-X028": (60, 2, "stop if physical lag is not an integer shift or P11/S2 identity fails"),
        "LIT-X031": (180, 4, "stop if harmonic rotation/sign fixtures or surface lineage fail"),
    }
    resources = pd.DataFrame([{"candidate_group_id": g, "max_seconds_per_cell": v[0], "max_rss_gib": v[1], "hard_stop": v[2], "parallel_workers": 1, "automatic_retry": 0, "execution_authorized": False} for g, v in resource_limits.items()])
    resources.to_csv(TABLES / "PRM097_resource_stop_policy.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    modules = ["numpy", "scipy", "skimage", "networkx", "porespy", "trimesh", "gudhi"]
    dep_rows = []
    for module in modules:
        spec = importlib.util.find_spec(module)
        version = ""
        if spec is not None:
            imported = __import__(module)
            version = getattr(imported, "__version__", "unknown")
        required = module in {"numpy", "scipy", "skimage", "networkx"}
        dep_rows.append({"module": module, "installed": spec is not None, "version": version, "required_for_PRM098": required, "policy": "required_present" if required else "optional_not_used_in_canonical_contract"})
    deps = pd.DataFrame(dep_rows)
    deps.to_csv(TABLES / "PRM097_KMK312_dependency_audit.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    gate_rows = [
        ("P097-G01", "input identity", "all PRM096/literature/gate inputs hash-match", "passed_preregistration"),
        ("P097-G02", "candidate identity", "six groups and unique output IDs; all mandatory lineage fields populated", "passed_preregistration"),
        ("P097-G03", "formula freeze", "every output references a frozen formula ID", "passed_preregistration"),
        ("P097-G04", "population separation", "voxel/graph/chord/ECT/co-occurrence/surface populations never silently mix", "passed_preregistration"),
        ("P097-G05", "synthetic truth", "all registered fixtures pass before representative models", "pending_PRM098_execution"),
        ("P097-G06", "independent replay", "separate implementation reproduces every synthetic and panel output", "pending_PRM098_execution"),
        ("P097-G07", "cost canary", "V64 single-cell resource stop passes before panel expansion", "pending_PRM098_execution"),
        ("P097-G08", "resolution", "unchanged EQG-11 criteria pass; no post-result threshold tuning", "pending_PRM098_execution"),
        ("P097-G09", "family applicability", "X006 B/C/L specialist and F/T sensitivity are reported separately", "pending_PRM098_execution"),
        ("P097-G10", "analytic redundancy controls", "X028 P11=S2 and homogeneity=1-contrast/2; X008 constriction=1-bottleneck", "passed_preregistration"),
        ("P097-G11", "existing-bank redundancy", "new outputs compared y-blind with XREG-v0.2 only after technical panel", "pending_later"),
        ("P097-G12", "no y", "performance read/fit/selection/promotion all zero", "passed_preregistration"),
        ("P097-G13", "protected assets", "NB-CURRENT/LEGACY-PY/original Excel/source geometry unchanged", "passed_preregistration"),
        ("P097-G14", "return gate", "PRM098 synthetic/panel results return to control tower before any full58 permit", "frozen"),
    ]
    gates = pd.DataFrame(gate_rows, columns=["gate_id", "gate_name", "requirement", "status"])
    gates.to_csv(TABLES / "PRM097_qualification_gate_registry.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    queue = pd.DataFrame([{
        "candidate_group_id": g,
        "current_state": "formula_and_test_contract_frozen",
        "next_work": "PRM098_bounded_synthetic_truth_cost_canary_and_representative_panel",
        "next_execution_scope": "synthetic fixtures then serial V64 cost canary; panel only after group gates",
        "execution_authorized_now": False,
        "full58_authorized": False,
        "y_authorized": False,
        "stop_and_return": resource_limits[g][2],
    } for g in GROUPS])
    queue.to_csv(TABLES / "PRM097_execute_or_stop_queue.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    later = pd.read_csv(INPUTS["PRM096_gates"])
    later["PRM097_status"] = "preserved_exact_unopened"
    later.to_csv(TABLES / "PRM097_later_y_gate_preservation.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    contract = {
        "work_id": "PRM-097",
        "title": "THIRD_WAVE_FORMULA_AND_SYNTHETIC_TRUTH_PREREGISTRATION_NO_EXECUTION",
        "created_at_kst": "2026-07-23T02:00:00+09:00",
        "status": "formula_and_test_contracts_frozen_no_execution",
        "candidate_groups": GROUPS,
        "output_schema_rows": len(roster),
        "formula_contracts": len(formulas),
        "synthetic_fixtures": len(fixtures),
        "representative_panel_cells": len(panel),
        "resolution_parameter_rows": len(resolution),
        "inputs": [{"name": k, "path": str(v.relative_to(ROOT)), "sha256": sha256(v)} for k, v in INPUTS.items()],
        "locks": {"candidate_calculation": 0, "full58_execution": 0, "performance_y_read": 0, "model_fit": 0, "feature_selection": 0, "feature_promotion": 0, "new_mask_or_slicing": 0, "NB_CURRENT_mutation": 0, "LEGACY_PY_mutation": 0, "original_Excel_mutation": 0},
        "next_work": "PRM-098_BOUNDED_THIRD_WAVE_SYNTHETIC_TRUTH_COST_CANARY_AND_REPRESENTATIVE_PANEL",
    }
    (CONTRACTS / "PRM-097_THIRD_WAVE_FORMULA_TEST_CONTRACT_20260723.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks = [
        ("six_groups", set(roster.candidate_group_id) == set(GROUPS), str(roster.candidate_group_id.nunique())),
        ("unique_outputs", roster.candidate_id.is_unique, str(len(roster))),
        ("formula_refs", set(roster.formula_id).issubset(set(formulas.formula_id)), str(roster.formula_id.nunique())),
        ("mandatory_fields", not roster.astype(str).apply(lambda s: s.str.strip().eq("")).any().any(), "no blank cells"),
        ("no_active", not roster.active_feature.any(), "0"),
        ("no_promoted", not roster.promoted.any(), "0"),
        ("no_y", not roster.y_evidence.any(), "0"),
        ("fixtures_cover_all", set(fixtures.candidate_group_id) == set(GROUPS), str(fixtures.candidate_group_id.nunique())),
        ("sources_cover_all", set(sources.candidate_group_id) == set(GROUPS), str(sources.candidate_group_id.nunique())),
        ("panel_36", len(panel) == 36, str(len(panel))),
        ("resolution_24", len(resolution) == 24, str(len(resolution))),
        ("all_execution_false", not panel.execution_authorized.any() and not resolution.execution_authorized.any() and not resources.execution_authorized.any() and not queue.execution_authorized_now.any(), "all false"),
        ("required_dependencies", deps.loc[deps.required_for_PRM098, "installed"].all(), deps.loc[deps.required_for_PRM098, ["module", "version"]].to_dict("records")),
        ("later_y_8", len(later) == 8, str(len(later))),
        ("contract_locks_zero", all(v == 0 for v in contract["locks"].values()), str(contract["locks"])),
    ]
    qa = pd.DataFrame([{"check_id": i, "status": "PASS" if ok else "FAIL", "detail": str(detail)} for i, ok, detail in checks])
    qa.to_csv(REPORTS / "PRM097_producer_QA.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    summary = {"work_id": "PRM-097", "status": "PASS" if qa.status.eq("PASS").all() else "FAIL", "checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}", "groups": len(GROUPS), "output_schema_rows": len(roster), "formula_contracts": len(formulas), "fixtures": len(fixtures), "panel_cells_not_executed": len(panel), "candidate_calculation_or_y_or_fit_or_selection_or_promotion": "0/0/0/0/0", "next_work": contract["next_work"]}
    (REPORTS / "PRM097_producer_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    if summary["status"] != "PASS":
        raise SystemExit(qa.loc[qa.status.eq("FAIL"), "check_id"].tolist())


if __name__ == "__main__":
    main()
