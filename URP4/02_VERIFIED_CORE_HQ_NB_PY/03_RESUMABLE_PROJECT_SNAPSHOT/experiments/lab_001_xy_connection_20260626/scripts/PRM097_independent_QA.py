from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "experiments" / "lab_001_xy_connection_20260626"
TABLES = LAB / "reports" / "tables"
FACTORY = LAB / "factories" / "PRM-097"
REPORTS = FACTORY / "reports"
CONTRACT = FACTORY / "contracts" / "PRM-097_THIRD_WAVE_FORMULA_TEST_CONTRACT_20260723.json"
GROUPS = {"LIT-X006", "LIT-X008", "LIT-X019", "LIT-X024", "LIT-X028", "LIT-X031"}
EXPECTED_OUTPUTS = {"LIT-X006": 14, "LIT-X008": 8, "LIT-X019": 7, "LIT-X024": 7, "LIT-X028": 30, "LIT-X031": 6}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name, dtype=str, keep_default_na=False)


def as_bool_false(series: pd.Series) -> bool:
    return series.astype(str).str.lower().isin({"false", "0", "no", ""}).all()


def validate(
    roster: pd.DataFrame,
    formulas: pd.DataFrame,
    panel: pd.DataFrame,
    resolution: pd.DataFrame,
    queue: pd.DataFrame,
    later: pd.DataFrame,
    contract: dict,
) -> dict[str, bool]:
    exact = "\n".join(formulas["exact_definition"].astype(str))
    x006 = "\n".join(formulas.loc[formulas.candidate_group_id.eq("LIT-X006"), "exact_definition"].astype(str))
    x008 = "\n".join(formulas.loc[formulas.candidate_group_id.eq("LIT-X008"), "exact_definition"].astype(str))
    x019 = roster.loc[roster.candidate_group_id.eq("LIT-X019")]
    x024 = "\n".join(formulas.loc[formulas.candidate_group_id.eq("LIT-X024"), "exact_definition"].astype(str))
    x028 = "\n".join(formulas.loc[formulas.candidate_group_id.eq("LIT-X028"), "exact_definition"].astype(str))
    x031 = "\n".join(formulas.loc[formulas.candidate_group_id.eq("LIT-X031"), "exact_definition"].astype(str))
    counts = roster.groupby("candidate_group_id").size().to_dict()
    flags = [c for c in ["active_feature", "promoted", "y_evidence"] if c in roster]
    return {
        "group_and_output_identity": set(counts) == GROUPS and counts == EXPECTED_OUTPUTS and roster.candidate_id.is_unique,
        "formula_reference_integrity": roster.formula_id.isin(set(formulas.formula_id)).all() and formulas.formula_id.is_unique,
        "mandatory_lineage_complete": not roster[["candidate_id", "candidate_group_id", "formula_id", "unit", "input_population", "source_lineage", "direct_or_derived", "status_label"]].eq("").any().any(),
        "x006_digital_graph_contract": all(t in x006 for t in ["26-neighbour", "no wrap", "no pruning", "pure closed chain"]),
        "x006_family_separation": roster.loc[roster.candidate_group_id.eq("LIT-X006"), "applicable_family"].eq("B|C|L primary; F|T sensitivity").all(),
        "x008_maximal_ball_not_edt_shortcut": "max_{c:" in x008 and "2*r(c)" in x008 and "EDT(c)*delta" in x008,
        "x019_matched_parent_identity": len(x019) == 7 and x019.source_lineage.str.contains("LIT-X001|geometric mean", regex=True).all() and x019.notes.str.contains("not a classical beam slenderness|three axis", case=False, regex=True).all(),
        "x024_discrete_ect_contract": all(t in x024 for t in ["26 normalized", "j=0..128", "connectivity=3", "fixed 40-mm"]),
        "x028_analytic_negative_control": all(t in x028 for t in ["P11", "S2", "1-contrast/2", "ln"]),
        "x031_antipodal_even_contract": all(t in x031 for t in ["n and -n", "l=2,4,6", "sph_harm_y", "PRM082"]) and roster.loc[roster.candidate_group_id.eq("LIT-X031"), "notes"].str.contains("odd l are excluded|second-rank fabric", regex=True).all(),
        "panel_and_resolution_counts": len(panel) == 36 and len(resolution) == 24,
        "all_execution_flags_false": as_bool_false(panel.execution_authorized) and as_bool_false(resolution.execution_authorized) and as_bool_false(queue.execution_authorized_now) and as_bool_false(queue.full58_authorized) and as_bool_false(queue.y_authorized),
        "feature_y_claim_flags_false": all(as_bool_false(roster[c]) for c in flags),
        "later_y_gate_exactly_preserved": len(later) == 8 and set(later.gate_id) == {f"P095-NS{i:02d}" for i in range(1, 9)} and later.PRM097_status.eq("preserved_exact_unopened").all(),
        "contract_locks_all_zero": all(int(v) == 0 for v in contract["locks"].values()),
    }


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    roster = read("PRM097_candidate_output_schema.csv")
    formulas = read("PRM097_formula_contract_registry.csv")
    fixtures = read("PRM097_synthetic_truth_fixture_registry.csv")
    sources = read("PRM097_primary_source_crosswalk.csv")
    panel = read("PRM097_representative_panel_scope.csv")
    resolution = read("PRM097_resolution_parameter_panel.csv")
    queue = read("PRM097_execute_or_stop_queue.csv")
    later = read("PRM097_later_y_gate_preservation.csv")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    checks = validate(roster, formulas, panel, resolution, queue, later, contract)
    checks.update({
        "input_hash_replay": all(sha256(ROOT / item["path"]) == item["sha256"] for item in contract["inputs"]),
        "fixture_scope": len(fixtures) == 22 and set(fixtures.candidate_group_id) == GROUPS and fixtures.fixture_id.is_unique,
        "source_scope_and_boundaries": set(sources.candidate_group_id) == GROUPS and sources.url.str.startswith("http").all() and sources.claim_boundary.str.contains("does not establish predictive utility").all(),
        "formula_count": len(formulas) == 17,
        "no_execution_artifacts": not any(FACTORY.rglob("*candidate_matrix*")) and not any(FACTORY.rglob("*model_result*")),
    })
    qa = pd.DataFrame([{"check_id": f"IQA-{i:02d}", "check": k, "status": "PASS" if v else "FAIL"} for i, (k, v) in enumerate(checks.items(), 1)])
    qa.to_csv(REPORTS / "PRM097_independent_QA.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    negative_cases = []
    def case(case_id: str, mutation: str, r=roster, f=formulas, p=panel, rs=resolution, q=queue, ly=later, c=contract, expected_key: str | None=None):
        result = validate(r, f, p, rs, q, ly, c)
        detected = expected_key is not None and not result.get(expected_key, True)
        negative_cases.append({"negative_fixture_id": case_id, "mutation": mutation, "expected_failed_check": expected_key, "status": "PASS" if detected else "FAIL"})

    r = roster.copy(); r.loc[1, "candidate_id"] = r.loc[0, "candidate_id"]; case("NEG-01", "duplicate candidate_id", r=r, expected_key="group_and_output_identity")
    r = roster.copy(); r.loc[0, "formula_id"] = "NO-SUCH-FORMULA"; case("NEG-02", "missing formula reference", r=r, expected_key="formula_reference_integrity")
    f = formulas.copy(); f.loc[f.formula_id.eq("X006-F01"), "exact_definition"] = "skeleton with pruning"; case("NEG-03", "X006 canonical pruning/no-wrap removed", f=f, expected_key="x006_digital_graph_contract")
    r = roster.copy(); idx = r.candidate_group_id.eq("LIT-X019").idxmax(); r.loc[idx, "source_lineage"] = "unmatched parent"; case("NEG-04", "X019 parent mismatch", r=r, expected_key="x019_matched_parent_identity")
    f = formulas.copy(); m=f.candidate_group_id.eq("LIT-X024"); f.loc[m, "exact_definition"] = f.loc[m, "exact_definition"].str.replace("26 normalized", "25 normalized", regex=False); case("NEG-05", "X024 direction count changed", f=f, expected_key="x024_discrete_ect_contract")
    f = formulas.copy(); m=f.candidate_group_id.eq("LIT-X028"); f.loc[m, "exact_definition"] = f.loc[m, "exact_definition"].str.replace("P11", "PXX", regex=False).str.replace("1-contrast/2", "unknown", regex=False); case("NEG-06", "X028 identities removed", f=f, expected_key="x028_analytic_negative_control")
    f = formulas.copy(); m=f.candidate_group_id.eq("LIT-X031"); f.loc[m, "exact_definition"] = f.loc[m, "exact_definition"].str.replace("l=2,4,6", "l=1,2,3", regex=False); case("NEG-07", "X031 odd harmonic bands", f=f, expected_key="x031_antipodal_even_contract")
    p = panel.copy(); p.loc[0, "execution_authorized"] = "True"; case("NEG-08", "panel execution authorization opened", p=p, expected_key="all_execution_flags_false")
    r = roster.copy(); r.loc[0, "y_evidence"] = "True"; case("NEG-09", "y evidence flag opened", r=r, expected_key="feature_y_claim_flags_false")
    c = json.loads(json.dumps(contract)); c["locks"]["candidate_calculation"] = 1; case("NEG-10", "candidate calculation lock opened", c=c, expected_key="contract_locks_all_zero")
    neg = pd.DataFrame(negative_cases)
    neg.to_csv(REPORTS / "PRM097_independent_negative_fixture_QA.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    summary = {
        "work_id": "PRM-097",
        "status": "PASS" if qa.status.eq("PASS").all() and neg.status.eq("PASS").all() else "FAIL",
        "independent_checks": f"{qa.status.eq('PASS').sum()}/{len(qa)}",
        "negative_fixtures": f"{neg.status.eq('PASS').sum()}/{len(neg)}",
        "scientific_execution": 0,
        "performance_y_read": 0,
    }
    (REPORTS / "PRM097_independent_QA_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    if summary["status"] != "PASS":
        raise SystemExit("independent QA failed")


if __name__ == "__main__":
    main()
