# URP4-1 모든 파일 트리와 개별 설명

이 문서는 ZIP 안의 **모든 파일을 상대경로 트리로 한 번씩 나열하고, 각 파일의 역할을 한국어로 설명**합니다.
ID와 alias는 추적성을 위해 유지하며, 가능한 경우 바로 뒤 괄호 설명에 뜻을 적었습니다.
`SOURCE_CUTOFF_SNAPSHOT/`과 `attempts/`는 과거 상태·실패 이력이며 현재 상태가 아닙니다.

## 전수성 요약

- 설명 대상 파일: **1,147개**
- 고유 상대경로: **1,147개**
- 검색·필터용 표: `ALL_FILES_DESCRIPTION_INDEX_KO.csv`
- 누락·중복 QA: `ALL_FILES_DESCRIPTION_QA.json`

### 상태별 파일 수

- `current_package_member_or_evidence`: 1,096개
- `historical_cutoff_snapshot`: 22개
- `historical_or_quarantined`: 3개
- `optional_demo_not_scientific_authority`: 3개
- `protected_reference_read_only`: 23개

### 최상위 폴더별 파일 수

- `00_READ_ME_FIRST`: 9개
- `01_PROJECT_MAP_AND_LEDGER`: 26개
- `02_VERIFIED_CORE_HQ_NB_PY`: 647개
- `03_CONFIG_RUNTIME_AND_COMMANDS`: 11개
- `04_REFERENCE_INPUTS`: 23개
- `05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE`: 90개
- `06_TRAINING_EVIDENCE`: 159개
- `07_COMPRESSION_DATA_AND_PILOT`: 123개
- `08_OPTIONAL_UI_DEMO`: 3개
- `09_LIMITATIONS_AND_RESUME`: 5개
- `10_MANIFEST_SHA256_AND_QA`: 29개
- `SOURCE_CUTOFF_SNAPSHOT`: 22개

## 전체 파일 트리

```text
URP4/ — URP4-1 박사님 제출·재개 패키지 루트
├─ 00_READ_ME_FIRST/ — 박사님이 먼저 읽는 안내, alias 풀이, 알고리즘·전체 파일 목록
│  ├─ ALGORITHM_AND_RESULT_GUIDE_KO.txt — 수정·구축한 알고리즘과 활용 결과를 한국어로 요약한 안내
│  ├─ ALGORITHM_FILE_INDEX.csv — 재개에 유효한 알고리즘 파일별 경로·SHA·역할·실행 등급 목록
│  ├─ ALGORITHM_PIPELINE_INDEX.csv — 파이프라인별 목적·입력·출력·entrypoint·근거·재개 행동 목록
│  ├─ ALL_FILES_DESCRIPTION_INDEX_KO.csv — 모든 파일의 상대경로·유형·상태·한국어 설명을 검색·필터하는 표
│  ├─ ALL_FILES_DESCRIPTION_QA.json — 00_READ_ME_FIRST 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  ├─ FINAL_SUBMISSION_REPORT.md — 00_READ_ME_FIRST 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  ├─ MERGE_PACKET.md — 00_READ_ME_FIRST 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  ├─ README_ALL_FILES_TREE_AND_DESCRIPTION_KO.md — ZIP 안 모든 파일의 상대경로를 트리로 나열하고 각 파일을 설명한 전수 목록
│  └─ README_FIRST.md — 박사님용 한국어 첫 안내서: 읽는 순서, alias 뜻, 현재 가능한 기능과 한계
├─ 01_PROJECT_MAP_AND_LEDGER/ — 프로젝트 전체 지도, 현재 상태 schema, 작업·근거 원장
│  ├─ CLAIM_AND_LIMITATION_LEDGER.csv — 01_PROJECT_MAP_AND_LEDGER 폴더의 계산값·registry·manifest·QA 표
│  ├─ CONTEXT_AND_DECISION_LINEAGE.md — 01_PROJECT_MAP_AND_LEDGER 폴더의 설명·보고·계약·의사결정 문서
│  ├─ CONTEXT_LINEAGE_REGISTER.csv — 01_PROJECT_MAP_AND_LEDGER 폴더의 계산값·registry·manifest·QA 표
│  ├─ EVIDENCE_INDEX.csv — 작업 결론을 실제 근거 파일·SHA-256과 연결한 인덱스
│  ├─ FILE_ALIAS_AND_PATH_INDEX.csv — HQ·Notebook·원본 파일의 alias와 실제 원본 경로·SHA 연결표
│  ├─ FINAL_SUBMISSION_REPORT.md — 01_PROJECT_MAP_AND_LEDGER 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  ├─ HANDOFF_CUTOFF_MANIFEST.json — cutoff에서 공식 근거로 등록한 파일·SHA·상태 manifest
│  ├─ HQ_CELL_IMPLEMENTATION_MAP.csv — 01_PROJECT_MAP_AND_LEDGER 폴더의 계산값·registry·manifest·QA 표
│  ├─ HQ_NOTEBOOK_CELL_TREE.csv — 01_PROJECT_MAP_AND_LEDGER 폴더의 계산값·registry·manifest·QA 표
│  ├─ MANIFEST_SCOPE_AND_REVISION_MAP.csv — 01_PROJECT_MAP_AND_LEDGER 입력·출력·경로·SHA-256을 고정한 manifest
│  ├─ MERGE_PACKET.md — 01_PROJECT_MAP_AND_LEDGER 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  ├─ OPEN_GATES.csv — 현재 미완료·차단·다음 통과 조건 목록
│  ├─ OPEN_ISSUES_AND_NEXT_GATES.md — 01_PROJECT_MAP_AND_LEDGER 폴더의 설명·보고·계약·의사결정 문서
│  ├─ PACKAGE_VIEW_MANIFEST.json — 01_PROJECT_MAP_AND_LEDGER 입력·출력·경로·SHA-256을 고정한 manifest
│  ├─ PROJECT_SCHEMA.json — 현재 프로젝트 상태를 기계가 읽는 single source of status truth
│  ├─ PYTHON_MODULE_AUDIT.csv — 01_PROJECT_MAP_AND_LEDGER 폴더의 계산값·registry·manifest·QA 표
│  ├─ RECONCILIATION_DISCREPANCIES.csv — 01_PROJECT_MAP_AND_LEDGER 폴더의 계산값·registry·manifest·QA 표
│  ├─ REPRODUCTION_AND_RESUME_GUIDE.md — 01_PROJECT_MAP_AND_LEDGER 폴더의 설명·보고·계약·의사결정 문서
│  ├─ SOURCE_CUTOFF_MANIFEST.json — 01_PROJECT_MAP_AND_LEDGER 입력·출력·경로·SHA-256을 고정한 manifest
│  ├─ SUBMISSION_REQUIREMENTS_CHECKLIST.csv — 01_PROJECT_MAP_AND_LEDGER 폴더의 계산값·registry·manifest·QA 표
│  ├─ URP4_1_HQ_21CELL_RAW_FLOW.svg — 01_PROJECT_MAP_AND_LEDGER 폴더의 벡터 다이어그램·도식
│  ├─ URP4_1_HQ_PROJECT_MAP.html — 브라우저에서 보는 전체 파이프라인·상태·근거 연결 지도
│  ├─ URP4_1_HQ_PROJECT_MAP.md — 전체 파이프라인·상태·근거 연결 지도의 Markdown 버전
│  ├─ URP4_1_HQ_PROJECT_MAP.svg — 01_PROJECT_MAP_AND_LEDGER 폴더의 벡터 다이어그램·도식
│  ├─ URP4_1_MASTER_HANDOFF_LEDGER.xlsx — 박사님과 후속 담당자가 필터·검색하는 프로젝트 종합 원장
│  └─ WORK_PACKAGE_LEDGER.csv — 작업별 실행·과학·Notebook 통합·release 상태 원장
├─ 02_VERIFIED_CORE_HQ_NB_PY/ — 메인 HQ Notebook, Python 엔진, 보호 원본, 재개 snapshot
│  ├─ 00_RUNNABLE_HQ_AND_ENGINE/ — 00_RUNNABLE_HQ_AND_ENGINE 관련 코드·입력·결과·검증 자료
│  │  ├─ config/ — config 관련 코드·입력·결과·검증 자료
│  │  │  └─ HQ_BLUEPRINT_V0_2_STAGE_REGISTRY.json — config 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  ├─ configs/ — configs 관련 코드·입력·결과·검증 자료
│  │  │  ├─ default.json — configs 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  ├─ training_future_run_skeleton.json — configs 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  └─ training_method_availability.csv — configs 폴더의 계산값·registry·manifest·QA 표
│  │  ├─ docs/ — docs 관련 코드·입력·결과·검증 자료
│  │  │  ├─ submission_audit/ — submission_audit 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ URP4-1_HQ_GLOBAL_DEBUG_VALIDATION_AND_SUBMISSION_AUDIT_20260728.md — submission_audit 폴더의 설명·보고·계약·의사결정 문서
│  │  │  │  ├─ URP4-1_HQ_INCOMPLETE_WORK_QUEUE_20260728.csv — submission_audit 폴더의 계산값·registry·manifest·QA 표
│  │  │  │  └─ URP4-1_HQ_SUBMISSION_REQUIREMENTS_CHECKLIST_20260728.csv — submission_audit 폴더의 계산값·registry·manifest·QA 표
│  │  │  ├─ HQ-INTAKE-001_AUDIT_REPORT_20260728.md — docs 폴더의 설명·보고·계약·의사결정 문서
│  │  │  ├─ HQ_SUBMISSION_READINESS_20260728.md — docs 폴더의 설명·보고·계약·의사결정 문서
│  │  │  ├─ URP4-1_HQ_CONTROLLER_POLICY_20260728.csv — docs 폴더의 계산값·registry·manifest·QA 표
│  │  │  ├─ URP4-1_HQ_FINALIZATION_REPORT_20260728.md — docs 폴더의 설명·보고·계약·의사결정 문서
│  │  │  ├─ URP4-1_HQ_INTAKE_AUDIT_20260728.csv — docs 폴더의 계산값·registry·manifest·QA 표
│  │  │  ├─ URP4-1_HQ_INTEGRATION_MANIFEST_20260728.csv — docs 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │  ├─ URP4-1_HQ_MODULE_AUDIT_20260728.csv — docs 폴더의 계산값·registry·manifest·QA 표
│  │  │  └─ URP4-1_HQ_SIDECHAT_CONFLICT_RESOLUTION_20260728.csv — docs 폴더의 계산값·registry·manifest·QA 표
│  │  ├─ tests/ — tests 관련 코드·입력·결과·검증 자료
│  │  │  ├─ fixtures/ — fixtures 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ generated_controlled_box_N40.stl — fixtures 검증·예제에 사용하는 geometry 파일(STL)
│  │  │  │  ├─ L28_UBCCz_VF30_imported.stl — fixtures 검증·예제에 사용하는 geometry 파일(STL)
│  │  │  │  ├─ L28_UBCCz_VF30_original.stp — fixtures 검증·예제에 사용하는 geometry 파일(STP)
│  │  │  │  └─ README.md — fixtures 폴더의 설명·보고·계약·의사결정 문서
│  │  │  ├─ audit_deliverable.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ controller_contract.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ full_descriptor_smoke.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ resume_generated_fixture_descriptor.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ resume_voxel_smoke.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  └─ smoke_hq.py — 프로젝트 작업의 python_source 근거 파일
│  │  ├─ urp4/ — urp4 관련 코드·입력·결과·검증 자료
│  │  │  ├─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ schemas/ — schemas 관련 코드·입력·결과·검증 자료
│  │  │  │  │  │  └─ urp4_contracts_v0_1.schema.json — schemas 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ canonical.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ ids.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ README.md — v0_1 폴더의 설명·보고·계약·의사결정 문서
│  │  │  │  │  └─ validation.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ descriptor_service/ — descriptor_service 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ component.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ config.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ formula.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ geometry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ pipeline.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ pixel.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ population.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ qa.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ run139.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ service.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ slicing.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ generators/ — generators 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ lattice_typeab/ — lattice_typeab 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ descriptors.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ exporters.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ graph.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ plugin.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  └─ type_b.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ tpms_multiwall/ — tpms_multiwall 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ exporters.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ fields.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ masking.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ plugin.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  └─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ voxel/ — voxel 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ exporters.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ kernel.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ plugin.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  ├─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  │  └─ source_kernel.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ geometry_io/ — geometry_io 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ routing.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ stl_import.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ v0_2/ — v0_2 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ step_import.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ v0_3/ — v0_3 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ source_preflight.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ v0_4/ — v0_4 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ imported_winding.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ v0_5/ — v0_5 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ generated_normalization.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ hq/ — hq 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ controller.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ engine.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ imported_pipeline.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ v0_2/ — v0_2 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ runtime.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ v0_3/ — v0_3 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ generated_n40_development.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ route_policy/ — route_policy 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ controller.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  ├─ training/ — training 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ p1_adapter_v0_1/ — p1_adapter_v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ adapters.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ p1_exec_layer_v0_1/ — p1_exec_layer_v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ builders.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ estimators.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ ledger.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ permit.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ policy.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ source_audit.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  ├─ v0_2/ — v0_2 관련 코드·입력·결과·검증 자료
│  │  │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  ├─ policy.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  │  └─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  ├─ README_RUN.md — 00_RUNNABLE_HQ_AND_ENGINE 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ URP4_1_HQ.ipynb — 메인 실행 Notebook(HQ): 전체 pipeline 설정·단계·실행 순서를 제어
│  │  └─ URP4_1_HQ_BLUEPRINT_v0_2.ipynb — 향후 21-cell 전체 HQ 구조를 정의한 설계 Notebook
│  ├─ 01_EXPERIMENTAL_TRAINING_ADAPTER/ — 01_EXPERIMENTAL_TRAINING_ADAPTER 관련 코드·입력·결과·검증 자료
│  │  ├─ adapter_v0_1_1/ — adapter_v0_1_1 관련 코드·입력·결과·검증 자료
│  │  │  ├─ implementation/ — implementation 관련 코드·입력·결과·검증 자료
│  │  │  │  ├─ __init__.py — implementation 폴더의 Python 실행·계산·검증 스크립트
│  │  │  │  ├─ branches.py — implementation 폴더의 Python 실행·계산·검증 스크립트
│  │  │  │  ├─ contracts.py — TRAIN-PARITY-003A 작업의 v1.1 authoritative evidence 근거 파일
│  │  │  │  ├─ hashing.py — implementation 폴더의 Python 실행·계산·검증 스크립트
│  │  │  │  ├─ instrumentation.py — implementation 폴더의 Python 실행·계산·검증 스크립트
│  │  │  │  ├─ ledgers.py — TRAIN-PARITY-002A, TRAIN-PARITY-003A 작업의 v1.1 authoritative evidence 근거 파일
│  │  │  │  ├─ no_fit_guard.py — implementation 폴더의 Python 실행·계산·검증 스크립트
│  │  │  │  └─ source_exact_runtime.py — implementation 폴더의 Python 실행·계산·검증 스크립트
│  │  │  └─ __init__.py — adapter_v0_1_1 폴더의 Python 실행·계산·검증 스크립트
│  │  └─ source_reference_runner.py — 01_EXPERIMENTAL_TRAINING_ADAPTER 폴더의 Python 실행·계산·검증 스크립트
│  ├─ 02_PROTECTED_REFERENCES_READ_ONLY/ — 02_PROTECTED_REFERENCES_READ_ONLY 관련 코드·입력·결과·검증 자료
│  │  ├─ LEGACY-PY/ — LEGACY-PY(박사님·조교님이 사용하던 검증 레거시 Python 코드)
│  │  │  ├─ 1._parameter_rawdata_0726.py — 읽기 전용 보호 원본: 프로젝트 작업의 python_source 근거 파일. 관련 ID: LEGACY-PY(박사님·조교님이 사용하던 검증 레거시 Python 코드)
│  │  │  ├─ 2._Parameter_result_0727.py — 읽기 전용 보호 원본: 프로젝트 작업의 protected_asset, python_source 근거 파일. 관련 ID: LEGACY-PY(박사님·조교님이 사용하던 검증 레거시 Python 코드)
│  │  │  ├─ 3._parameter_angle_all_0727.py — 읽기 전용 보호 원본: 프로젝트 작업의 protected_asset, python_source 근거 파일. 관련 ID: LEGACY-PY(박사님·조교님이 사용하던 검증 레거시 Python 코드)
│  │  │  ├─ Curvature_Extraction_New.py — 읽기 전용 보호 원본: 프로젝트 작업의 python_source 근거 파일. 관련 ID: LEGACY-PY(박사님·조교님이 사용하던 검증 레거시 Python 코드)
│  │  │  ├─ Extract_structure_variable.py — 읽기 전용 보호 원본: 프로젝트 작업의 python_source 근거 파일. 관련 ID: LEGACY-PY(박사님·조교님이 사용하던 검증 레거시 Python 코드)
│  │  │  └─ Parameter_distribution_New.py — 읽기 전용 보호 원본: 프로젝트 작업의 python_source 근거 파일. 관련 ID: LEGACY-PY(박사님·조교님이 사용하던 검증 레거시 Python 코드)
│  │  ├─ NB-CURRENT/ — NB-CURRENT(LEGACY-PY를 통합한 박사님 승인 기준 Notebook)
│  │  │  └─ R06V2_integrated_legacy_candidate_v0_2.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: NB-CURRENT(LEGACY-PY를 통합한 박사님 승인 기준 Notebook)
│  │  ├─ NB-DEV/ — NB-DEV(Import route controller 개발·검증용 Notebook)
│  │  │  └─ NB_DEV_v0_6_ROUTE_VALID_004_IMPORT_POLICY.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: NB-DEV(Import route controller 개발·검증용 Notebook)
│  │  ├─ NB-ORIG/ — NB-ORIG(처음 받은 원본 통합 Notebook)
│  │  │  └─ Model_generator_260506_descriptor_v5_boundary_symmetry_perfboost.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source, protected_asset 근거 파일. 관련 ID: NB-ORIG(처음 받은 원본 통합 Notebook)
│  │  ├─ PROFESSOR_GENERATORS/ — PROFESSOR_GENERATORS(박사님 제공 generator 원본(과거 내부 alias 유지))
│  │  │  ├─ Multiwall_model_generator_VF50.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_GENERATORS(박사님 제공 generator 원본(과거 내부 alias 유지))
│  │  │  ├─ README.md — 읽기 전용 보호 원본: PROFESSOR_GENERATORS 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: PROFESSOR_GENERATORS(박사님 제공 generator 원본(과거 내부 alias 유지))
│  │  │  ├─ source_manifest_20260716.csv — 읽기 전용 보호 원본: PROFESSOR_GENERATORS 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: PROFESSOR_GENERATORS(박사님 제공 generator 원본(과거 내부 alias 유지))
│  │  │  └─ Type A+B Gen. Image slicing.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_GENERATORS(박사님 제공 generator 원본(과거 내부 alias 유지))
│  │  └─ PROFESSOR_TRAINING/ — PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Total data_260503.xlsx — 읽기 전용 보호 원본: PROFESSOR_TRAINING 폴더의 Excel 입력·원장·결과 workbook. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Training_260418-1st method - New feature.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Training_260418-1st method.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Training_260419-2nd method - New feature - Good. vibration.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Training_260419-2nd method.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Training_260420-3rd method - New feature - Good. h.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Training_260420-3rd method.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Training_260503_Ensemble-4th method.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     ├─ Training_260508_Alltogether-5th method.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  │     └─ Training_260508_Alltogether-5th_method_FIXED.ipynb — 읽기 전용 보호 원본: 프로젝트 작업의 notebook_source 근거 파일. 관련 ID: PROFESSOR_TRAINING(박사님 제공 Training 1–5 원본(과거 내부 alias 유지))
│  ├─ 03_RESUMABLE_PROJECT_SNAPSHOT/ — 03_RESUMABLE_PROJECT_SNAPSHOT 관련 코드·입력·결과·검증 자료
│  │  ├─ configs/ — configs 관련 코드·입력·결과·검증 자료
│  │  │  ├─ default.json — configs 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  ├─ training_future_run_skeleton.json — configs 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  └─ training_method_availability.csv — configs 폴더의 계산값·registry·manifest·QA 표
│  │  ├─ experiments/ — experiments 관련 코드·입력·결과·검증 자료
│  │  │  └─ lab_001_xy_connection_20260626/ — lab_001_xy_connection_20260626 관련 코드·입력·결과·검증 자료
│  │  │     ├─ data/ — data 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ processed/ — processed 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ n40_all58_20260715/ — n40_all58_20260715 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ stl/ — stl 관련 코드·입력·결과·검증 자료
│  │  │     │  │        ├─ B3__a272cdb922__N40.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │  │        ├─ C1__7755dda7d0__N40.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │  │        ├─ F1__0dff3c1b13__N40.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │  │        └─ L1__412f5bec5e__N40.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │  └─ raw/ — raw 관련 코드·입력·결과·검증 자료
│  │  │     │     └─ notion_reference_models_20260701/ — notion_reference_models_20260701 관련 코드·입력·결과·검증 자료
│  │  │     │        ├─ stl/ — stl 관련 코드·입력·결과·검증 자료
│  │  │     │        │  ├─ B1-Basic_Cubic-SC5.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │        │  ├─ B3-Basic_Cubic-BCC_Lattice.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │        │  ├─ C1-Cubic_truss_lattice-SC-FCC.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │        │  ├─ F1-Foam-Kelvin_foam.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │        │  ├─ L1-Truss Lattice-Octahedron_lattice_New.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │        │  └─ L7-Truss_Lattice-3D_chiral_metamaterial.stl — stl 검증·예제에 사용하는 geometry 파일(STL)
│  │  │     │        └─ stp/ — stp 관련 코드·입력·결과·검증 자료
│  │  │     │           ├─ B1-Basic_Cubic-SC5.stp — stp 검증·예제에 사용하는 geometry 파일(STP)
│  │  │     │           ├─ B3-Basic_Cubic-BCC_Lattice.stp — stp 검증·예제에 사용하는 geometry 파일(STP)
│  │  │     │           ├─ C1-Cubic_truss_lattice-SC-FCC.stp — stp 검증·예제에 사용하는 geometry 파일(STP)
│  │  │     │           ├─ F1-Foam-Kelvin_foam.stp — stp 검증·예제에 사용하는 geometry 파일(STP)
│  │  │     │           ├─ L1-Truss Lattice-Octahedron_lattice_New.stp — stp 검증·예제에 사용하는 geometry 파일(STP)
│  │  │     │           └─ L7-Truss_Lattice-3D_chiral_metamaterial.stp — stp 검증·예제에 사용하는 geometry 파일(STP)
│  │  │     ├─ factories/ — factories 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ IMSTL-006/ — IMSTL-006 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ IMSTL-006_SMALL_GENERALIZATION_v0_1_20260728.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     ├─ IMSTL-006_SMALL_GENERALIZATION_v0_2_20260728.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     └─ IMSTL-006_SMALL_GENERALIZATION_v0_3_SELECTED_GATE_20260728.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ IMSTL-007/ — IMSTL-007 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ IMSTL-007_F1_RESOLUTION_PIXEL_PHASE_v0_1_20260728.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     └─ IMSTL-007_F1_RESOLUTION_PIXEL_PHASE_v0_2_SHORTPATH_20260728.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ IMSTL-008/ — IMSTL-008 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ IMSTL-008_F1_FULL_P1000_Z801_NONREGRESSION_v0_1_20260728.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     └─ IMSTL-008_F1_FULL_P1000_Z801_NONREGRESSION_v0_2_20260728.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-097/ — PRM-097 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-097_THIRD_WAVE_FORMULA_TEST_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-098/ — PRM-098 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-098_BOUNDED_EXECUTION_PERMIT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-099/ — PRM-099 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ PRM-099_FULL58_PERMIT_DECISION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     └─ PRM099_FULL58_SIX_OUTPUT_CONFIG_20260723.json — contracts 실행 조건을 재현하기 위한 frozen configuration
│  │  │     │  ├─ PRM-101/ — PRM-101 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-101_XREG_V0_3_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-102/ — PRM-102 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-102_BC_RAW_TABLE_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-103/ — PRM-103 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-103_XREG_V0_4_BC_COHORT_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-104/ — PRM-104 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-104_OVERLAY_PHASE_PROFILE_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-105/ — PRM-105 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-105_XREG_V0_5_OVERLAY_PHASE_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-106/ — PRM-106 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-106_PROFILE_DYNAMICS_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-107/ — PRM-107 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-107_XREG_V0_6_PROFILE_DYNAMICS_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-108/ — PRM-108 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-108_AXIAL_DISTRIBUTION_SYMMETRY_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-109/ — PRM-109 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-109_XREG_V0_7_AXIAL_SYMMETRY_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-110/ — PRM-110 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-110_AXIAL_SHAPE_ENTROPY_BC_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-111/ — PRM-111 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-111_XREG_V0_8_AXIAL_SHAPE_ENTROPY_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-112/ — PRM-112 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-112_AXIAL_WEIGHTED_QUANTILE_LOCATION_B_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-113/ — PRM-113 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-113_XREG_V0_9_WEIGHTED_QUANTILE_LOCATION_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-114/ — PRM-114 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-114_OVERLAY_COMPONENT_INEQUALITY_CONCENTRATION_BC_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-115/ — PRM-115 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-115_XREG_V1_0_COMPONENT_INEQUALITY_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-116/ — PRM-116 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-116_COMPONENT_FILTER_SENSITIVITY_BC_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-117/ — PRM-117 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-117_XREG_V1_1_COMPONENT_FILTER_SENSITIVITY_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-118/ — PRM-118 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-118_SLICE_COMPONENT_FILTER_SENSITIVITY_BC_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-119/ — PRM-119 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-119_XREG_V1_2_SLICE_COMPONENT_FILTER_SENSITIVITY_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-120/ — PRM-120 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-120_OVERLAY_PAIR_COMPONENT_COMPOSITION_BC_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-121/ — PRM-121 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-121_XREG_V1_3_OVERLAY_PAIR_COMPONENT_COMPOSITION_CONSOLIDATION_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ PRM-122/ — PRM-122 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  │     └─ PRM-122_PROFILE_JUMP_AND_TURN_BC_BATCH_CONTRACT_20260723.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  └─ TOUR-C001/ — TOUR-C001 관련 코드·입력·결과·검증 자료
│  │  │     │     └─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │        ├─ PRM-069_SLICE005_RETURN_INTAKE_20260722.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │        ├─ PRM-070_SLICE005_CONVERGENCE_CONTROL_PREREG_20260722.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │        ├─ TOUR-C001_T4R_SLICE_001_T8_T9_CONVERGENCE_PREREGISTRATION_20260720.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │        ├─ TOUR-C001_T4R_SLICE_003A_MATCHED_SOURCE_FIVE_MODEL_PREREGISTRATION_20260720.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │        └─ TOUR-C001_T4R_SLICE_004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION_20260720.json — contracts 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     ├─ reports/ — reports 관련 코드·입력·결과·검증 자료
│  │  │     │  └─ tables/ — tables 관련 코드·입력·결과·검증 자료
│  │  │     │     ├─ CINT-02_golden_panel_input_manifest_20260718.csv — tables 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │     │     ├─ CINT-02_legacy_source_adapter_registry_20260718.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ IMSTL-006-20260728-002_selected_slice_gate_detail.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ IMSTL-008-20260728-002_f1_run139_scalar_result.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ IMSTL-008-20260728-002_family_nonregression.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ IMSTL-008-20260728-002_independent_scalar_replay.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ IMSTL-008-20260728-002_selected_mask_replay.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM101_unified_redundancy_block_registry.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM101_unified_redundancy_edge_registry.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM101_xreg_v0_3_candidate_bank.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM101_xreg_v0_3_values_long.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM101_xreg_v0_3_values_wide.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM149_unified_redundancy_block_registry.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM149_unified_redundancy_edge_registry.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM149_xreg_v2_7_candidate_bank.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     ├─ PRM149_xreg_v2_7_values_long.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     │     └─ R09-20260715_final_canonical_geometry_registry.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │     ├─ results/ — results 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ I008_F1/ — I008_F1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ IMSTL-008-20260728-002/ — IMSTL-008-20260728-002 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ DECISION_PACKET.json — IMSTL-008-20260728-002 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     ├─ IMSTL_008_F1_FULL_P1000_Z801_NONREGRESSION_REPORT_20260728.md — IMSTL-008-20260728-002 폴더의 설명·보고·계약·의사결정 문서
│  │  │     │  │     ├─ INDEPENDENT_QA.json — IMSTL-008-20260728-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     ├─ MERGE_PACKET.md — IMSTL-008-20260728-002 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  │  │     │  │     ├─ PRODUCER_SUMMARY.json — IMSTL-008-20260728-002 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     ├─ PROTECTED_ASSET_POST_AUDIT.csv — IMSTL-008-20260728-002 폴더의 계산값·registry·manifest·QA 표
│  │  │     │  │     └─ PROTECTED_ASSET_PRE_AUDIT.csv — IMSTL-008-20260728-002 폴더의 계산값·registry·manifest·QA 표
│  │  │     │  ├─ IMSTL-006_SMALL_GENERALIZATION/ — IMSTL-006_SMALL_GENERALIZATION 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ IMSTL-006-20260728-001/ — IMSTL-006-20260728-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ IMSTL-006-20260728-002/ — IMSTL-006-20260728-002 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ DECISION_PACKET.json — IMSTL-006-20260728-002 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     ├─ IMSTL_006_SMALL_GENERALIZATION_REPORT_20260728.md — IMSTL-006-20260728-002 폴더의 설명·보고·계약·의사결정 문서
│  │  │     │  │     ├─ INDEPENDENT_QA.json — IMSTL-006-20260728-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     ├─ PRODUCER_QA.json — IMSTL-006-20260728-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     └─ SELECTED_GATE_PACKET.json — IMSTL-006-20260728-002 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ IMSTL-007_F1_RESOLUTION_PIXEL_PHASE/ — IMSTL-007_F1_RESOLUTION_PIXEL_PHASE 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ IMSTL-007-20260728-001/ — IMSTL-007-20260728-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ figures/ — figures 관련 코드·입력·결과·검증 자료
│  │  │     │  │     │  ├─ F1_z0000_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     │  ├─ F1_z0001_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     │  ├─ F1_z0100_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     │  ├─ F1_z0200_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     │  ├─ F1_z0400_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     │  ├─ F1_z0600_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     │  ├─ F1_z0700_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     │  ├─ F1_z0799_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     │  └─ F1_z0800_resolution_phase_grid.png — figures 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ DECISION_PACKET.json — IMSTL-007-20260728-001 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     ├─ PRODUCER_QA.json — IMSTL-007-20260728-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     └─ QUARANTINE.json — 과거 실패·대체·격리 이력(현재 canonical 아님): IMSTL-007-20260728-001 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ POSTRUN-GATE-001/ — POSTRUN-GATE-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ POSTRUN-GATE-001-20260801-001/ — POSTRUN-GATE-001-20260801-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ C1_INDEPENDENT_QA_RESULT.json — POSTRUN-GATE-001-20260801-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     ├─ CLAIM_AND_STATUS_LEDGER.csv — STRICT-STEP-026 작업의 v1.1 authoritative evidence 근거 파일
│  │  │     │  │     ├─ MERGE_PACKET.md — POSTRUN-GATE-001-20260801-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  │  │     │  │     ├─ NEXT_GATE_RECOMMENDATION.md — POSTRUN-GATE-001-20260801-001 폴더의 설명·보고·계약·의사결정 문서
│  │  │     │  │     ├─ REPORT.md — POSTRUN-GATE-001-20260801-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  │     │  │     ├─ TRAIN_REPLAY_LIFECYCLE_AWARE_QA_V2.json — POSTRUN-GATE-001-20260801-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     └─ TRAIN_REPLAY_QA_FAILURE_DISPOSITION.csv — POSTRUN-GATE-001-20260801-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  ├─ ROUTE-VALID-001/ — ROUTE-VALID-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ ROUTE-VALID-001-20260729-001/ — ROUTE-VALID-001-20260729-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ C1_ZMID_P1000_IMPORTED_STL_ROUTE_C.png — ROUTE-VALID-001-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ INDEPENDENT_QA.json — ROUTE-VALID-001-20260729-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     ├─ REPORT.md — ROUTE-VALID-001-20260729-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  │     │  │     └─ ROUTE_VALID_001_C1_PACKET.json — ROUTE-VALID-001-20260729-001 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ ROUTE-VALID-002/ — ROUTE-VALID-002 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ ROUTE-VALID-002-20260729-001/ — ROUTE-VALID-002-20260729-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ B1_ZMID_P1000_ROUTE_A.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ B1_ZMID_P1000_ROUTE_B.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ B1_ZMID_P1000_ROUTE_C.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ B1_ZMID_P500_ROUTE_A.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ B1_ZMID_P500_ROUTE_B.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ B1_ZMID_P500_ROUTE_C.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ INDEPENDENT_QA.json — ROUTE-VALID-002-20260729-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     ├─ L7_ZMID_P1000_ROUTE_A.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ L7_ZMID_P1000_ROUTE_B.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ L7_ZMID_P1000_ROUTE_C.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ L7_ZMID_P500_ROUTE_A.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ L7_ZMID_P500_ROUTE_B.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ L7_ZMID_P500_ROUTE_C.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ MERGE_PACKET.md — ROUTE-VALID-002-20260729-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  │  │     │  │     ├─ REPORT.md — ROUTE-VALID-002-20260729-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  │     │  │     └─ ROUTE_VALID_002_PACKET.json — ROUTE-VALID-002-20260729-001 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ ROUTE-VALID-003/ — ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │  ├─ ROUTE-VALID-003-20260729-001/ — ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │  │  └─ COMMON_RASTER_CONTRACT.json — ROUTE-VALID-003-20260729-001 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │  └─ ROUTE-VALID-003-20260729-002/ — ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     ├─ figures/ — ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AB_worst_01_z0400_P750_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AB_worst_02_z0400_P750_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AB_worst_03_z0400_P1000_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AB_worst_04_z0400_P1000_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AB_worst_05_z0400_P1500_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AB_worst_06_z0400_P1500_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AC_worst_01_z0400_P500_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AC_worst_02_z0400_P500_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AC_worst_03_z0400_P750_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AC_worst_04_z0400_P750_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  ├─ AC_worst_05_z0400_P1000_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     │  └─ AC_worst_06_z0400_P1000_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     ├─ COMMON_RASTER_CONTRACT.json — ROUTE-VALID-003-20260729-002 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     ├─ INDEPENDENT_QA.json — ROUTE-VALID-003-20260729-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     ├─ MERGE_PACKET.md — ROUTE-VALID-003-20260729-002 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     ├─ OUTPUT_MANIFEST.csv — ROUTE-VALID-003-20260729-002 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     ├─ PRODUCER_PACKET.json — ROUTE-VALID-003-20260729-002 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     ├─ REPORT.md — ROUTE-VALID-003-20260729-002 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  │     └─ ROUTE_VALID_003_PACKET.json — ROUTE-VALID-003-20260729-002 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │     │  ├─ ROUTE-VALID-004/ — ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  │  └─ ROUTE-VALID-004-20260729-001/ — ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  │     ├─ FINAL_OUTPUT_MANIFEST.csv — ROUTE-VALID-004-20260729-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  │     ├─ INDEPENDENT_QA.json — ROUTE-VALID-004-20260729-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  │     ├─ MERGE_PACKET.md — ROUTE-VALID-004-20260729-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  │     ├─ OUTPUT_MANIFEST.csv — ROUTE-VALID-004-20260729-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  │     ├─ POLICY_CONTRACT.json — ROUTE-VALID-004-20260729-001 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  │     ├─ PROTECTED_ASSET_RECHECK.csv — ROUTE-VALID-004-20260729-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  │     └─ REPORT.md — ROUTE-VALID-004-20260729-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  │     │  └─ STRICT-STEP-026/ — STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     ├─ STRICT-STEP-026-20260731-001/ — STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  ├─ anchor_pngs/ — STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  ├─ overlay_0199_0200.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  ├─ overlay_0399_0400.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  ├─ overlay_0599_0600.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  ├─ overlay_0799_0800.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  ├─ slice_0000.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  ├─ slice_0200.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  ├─ slice_0400.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  ├─ slice_0600.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  │  └─ slice_0800.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  ├─ CONTRACT_MANIFEST.json — STRICT-STEP-026-20260731-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  ├─ direct_legacy_scalar_table.csv — STRICT-STEP-026 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  ├─ INDEPENDENT_QA.json — STRICT-STEP-026-20260731-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  ├─ overlay_png_manifest.csv — STRICT-STEP-026-20260731-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  ├─ RUN_STATE.json — STRICT-STEP-026 작업의 terminal_snapshot_v1_1_r2 근거 파일. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     │  └─ slice_png_manifest.csv — STRICT-STEP-026-20260731-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │     └─ worker_logs/ — STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │        ├─ STRICT-STEP-026-20260731-001.stderr.log — worker_logs 폴더의 실행 로그. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     │        └─ STRICT-STEP-026-20260731-001.stdout.log — worker_logs 폴더의 실행 로그. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │     ├─ resume_evidence/ — resume_evidence 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ I007_F1/ — I007_F1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ IMSTL-007-20260728-002/ — IMSTL-007-20260728-002 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ DECISION_PACKET.json — IMSTL-007-20260728-002 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     ├─ INDEPENDENT_QA.json — IMSTL-007-20260728-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     ├─ OUTPUT_MANIFEST.csv — IMSTL-007-20260728-002 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │     │  │     ├─ PRODUCER_QA.json — IMSTL-007-20260728-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     └─ REPORT.md — IMSTL-007-20260728-002 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  │     │  ├─ IMSTL-006_SMALL_GENERALIZATION/ — IMSTL-006_SMALL_GENERALIZATION 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ IMSTL-006-20260728-002/ — IMSTL-006-20260728-002 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ DECISION_PACKET.json — IMSTL-006-20260728-002 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │     ├─ IMSTL_006_SMALL_GENERALIZATION_REPORT_20260728.md — IMSTL-006-20260728-002 폴더의 설명·보고·계약·의사결정 문서
│  │  │     │  │     ├─ INDEPENDENT_QA.json — IMSTL-006-20260728-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     ├─ PRODUCER_QA.json — IMSTL-006-20260728-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     └─ SELECTED_GATE_PACKET.json — IMSTL-006-20260728-002 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  ├─ ROUTE-VALID-001/ — ROUTE-VALID-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │  └─ ROUTE-VALID-001-20260729-001/ — ROUTE-VALID-001-20260729-001 관련 코드·입력·결과·검증 자료
│  │  │     │  │     ├─ C1_ZMID_P1000_IMPORTED_STL_ROUTE_C.png — ROUTE-VALID-001-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │  │     ├─ INDEPENDENT_QA.json — ROUTE-VALID-001-20260729-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │  │     ├─ REPORT.md — ROUTE-VALID-001-20260729-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  │     │  │     └─ ROUTE_VALID_001_C1_PACKET.json — ROUTE-VALID-001-20260729-001 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  └─ ROUTE-VALID-002/ — ROUTE-VALID-002 관련 코드·입력·결과·검증 자료
│  │  │     │     └─ ROUTE-VALID-002-20260729-001/ — ROUTE-VALID-002-20260729-001 관련 코드·입력·결과·검증 자료
│  │  │     │        ├─ B1_ZMID_P1000_ROUTE_A.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ B1_ZMID_P1000_ROUTE_B.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ B1_ZMID_P1000_ROUTE_C.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ B1_ZMID_P500_ROUTE_A.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ B1_ZMID_P500_ROUTE_B.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ B1_ZMID_P500_ROUTE_C.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ INDEPENDENT_QA.json — ROUTE-VALID-002-20260729-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │     │        ├─ L7_ZMID_P1000_ROUTE_A.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ L7_ZMID_P1000_ROUTE_B.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ L7_ZMID_P1000_ROUTE_C.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ L7_ZMID_P500_ROUTE_A.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ L7_ZMID_P500_ROUTE_B.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ L7_ZMID_P500_ROUTE_C.png — ROUTE-VALID-002-20260729-001 작업의 slice·overlay·진단·결과 시각 자료
│  │  │     │        ├─ MERGE_PACKET.md — ROUTE-VALID-002-20260729-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  │  │     │        ├─ REPORT.md — ROUTE-VALID-002-20260729-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  │     │        └─ ROUTE_VALID_002_PACKET.json — ROUTE-VALID-002-20260729-001 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     └─ scripts/ — scripts 관련 코드·입력·결과·검증 자료
│  │  │        ├─ IMSTL_006_independent_qa.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 독립 QA/회귀검증. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ IMSTL_006_small_generalization_factory.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 계산 실행/후보 생성. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ IMSTL_007_f1_resolution_pixel_phase_diagnosis.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 감사·진단·비교. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ IMSTL_007_independent_qa.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 독립 QA/회귀검증. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ IMSTL_008_f1_full_p1000_z801_nonregression.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 계산 지원/변환. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ IMSTL_008_independent_qa.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 독립 QA/회귀검증. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ NB_INTEGRATE_001_build_development_notebook.py — IMPORT_CONTROLLER_INTEGRATION 파이프라인의 계산 지원/변환. Fail-closed source/route controller integration and its regression QA
│  │  │        ├─ NB_INTEGRATE_001_controller_smoke.py — IMPORT_CONTROLLER_INTEGRATION 파이프라인의 계산 지원/변환. Fail-closed source/route controller integration and its regression QA
│  │  │        ├─ NB_INTEGRATE_001_finalize.py — IMPORT_CONTROLLER_INTEGRATION 파이프라인의 결과·manifest 봉인/동기화. Fail-closed source/route controller integration and its regression QA
│  │  │        ├─ NB_INTEGRATE_001_independent_regression_qa.py — IMPORT_CONTROLLER_INTEGRATION 파이프라인의 계산 지원/변환. Fail-closed source/route controller integration and its regression QA
│  │  │        ├─ NB_INTEGRATE_001_notebook_static_qa.py — IMPORT_CONTROLLER_INTEGRATION 파이프라인의 계산 지원/변환. Fail-closed source/route controller integration and its regression QA
│  │  │        ├─ PRM069_SLICE005_return_intake_audit.py — RESOLUTION_OPTIMIZATION 파이프라인의 감사·진단·비교. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ PRM069_SLICE005_return_postmerge_QA.py — RESOLUTION_OPTIMIZATION 파이프라인의 결과·manifest 봉인/동기화. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ PRM070_SLICE005_convergence_control.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ PRM070_SLICE005_independent_control_QA.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ PRM070_SLICE005_postmerge_sync_QA.py — RESOLUTION_OPTIMIZATION 파이프라인의 결과·manifest 봉인/동기화. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ PRM097_finalize_manifest.py — scripts 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │        ├─ PRM097_freeze_third_wave_formula_contracts.py — SLICE004_AND_XREG 파이프라인의 실행 계약·사전등록. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM097_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM097_make_preregistration_figure.py — SLICE004_AND_XREG 파이프라인의 실행 계약·사전등록. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM097_postmerge_sync_QA.py — SLICE004_AND_XREG 파이프라인의 결과·manifest 봉인/동기화. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_C1_mask_alias_audit.py — SLICE004_AND_XREG 파이프라인의 감사·진단·비교. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_finalize_evidence.py — SLICE004_AND_XREG 파이프라인의 결과·manifest 봉인/동기화. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_finalize_manifest.py — scripts 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │        ├─ PRM098_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_materialize_V192_panel_masks.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_postmerge_sync_QA.py — SLICE004_AND_XREG 파이프라인의 결과·manifest 봉인/동기화. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_preflight_and_permit.py — SLICE004_AND_XREG 파이프라인의 실행 계약·사전등록. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_run_cell.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_run_cost_canary.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_run_progressive_panel.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_run_synthetic_truth.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_technical_gate_analysis.py — SLICE004_AND_XREG 파이프라인의 감사·진단·비교. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM098_third_wave_formula_library.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM099_finalize_manifest.py — scripts 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │        ├─ PRM099_independent_permit_QA.py — SLICE004_AND_XREG 파이프라인의 실행 계약·사전등록. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM099_postmerge_sync_QA.py — SLICE004_AND_XREG 파이프라인의 결과·manifest 봉인/동기화. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM099_prepare_full58_permit_decision.py — SLICE004_AND_XREG 파이프라인의 실행 계약·사전등록. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM099_render_permit_review.py — SLICE004_AND_XREG 파이프라인의 실행 계약·사전등록. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM099_third_wave_full58_runner.py — SLICE004_AND_XREG 파이프라인의 계산 실행/후보 생성. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM100_execute_serial_cells.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM100_finalize_manifest.py — scripts 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │        ├─ PRM100_independent_xonly_QA.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM100_postmerge_sync_QA.py — SLICE004_AND_XREG 파이프라인의 결과·manifest 봉인/동기화. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM100_render_xonly_review.py — SLICE004_AND_XREG 파이프라인의 감사·진단·비교. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM100_xonly_technical_review.py — SLICE004_AND_XREG 파이프라인의 감사·진단·비교. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM101_consolidate_xreg_v0_3.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM101_finalize_manifest.py — scripts 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │        ├─ PRM101_independent_consolidation_QA.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM101_postmerge_sync_QA.py — SLICE004_AND_XREG 파이프라인의 결과·manifest 봉인/동기화. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM102_bc_raw_table_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM102_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM102_postmerge_sync_QA.py — SLICE004_AND_XREG 파이프라인의 결과·manifest 봉인/동기화. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM103_consolidate_bc_cohort_xreg_v0_4.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM103_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM104_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM104_overlay_phase_profile_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM105_consolidate_overlay_phase_xreg_v0_5.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM105_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM106_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM106_profile_dynamics_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM107_consolidate_profile_dynamics_xreg_v0_6.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM107_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM108_axial_distribution_symmetry_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM108_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM109_consolidate_axial_symmetry_xreg_v0_7.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM109_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM110_axial_shape_entropy_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM110_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM111_consolidate_axial_shape_entropy_xreg_v0_8.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM111_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM112_axial_weighted_quantile_location_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM112_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM113_consolidate_weighted_quantile_location_xreg_v0_9.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM113_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM114_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM114_overlay_component_inequality_concentration_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM115_consolidate_component_inequality_xreg_v1_0.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM115_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM116_component_filter_sensitivity_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM116_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM117_consolidate_component_filter_sensitivity_xreg_v1_1.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM117_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM118_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM118_slice_component_filter_sensitivity_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM119_consolidate_slice_component_filter_sensitivity_xreg_v1_2.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM119_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM120_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM120_overlay_pair_component_composition_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM121_consolidate_overlay_pair_component_composition_xreg_v1_3.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM121_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM122_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM122_profile_jump_and_turn_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM123_consolidate_profile_jump_turn_xreg_v1_4.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM123_finalize_and_independent_QA.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM124_overlay_phase_balance_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM124_overlay_phase_balance_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM125_consolidate_overlay_phase_balance_xreg_v1_5.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM125_finalize_and_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM126_overlay_component_density_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM126_overlay_component_density_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM127_consolidate_overlay_component_density_xreg_v1_6.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM127_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM128_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM128_overlay_phase_cross_correlation_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM129_consolidate_phase_cross_correlation_xreg_v1_7.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM129_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM130_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM130_overlay_fraction_quantile_batch.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM131_consolidate_overlay_fraction_quantile_xreg_v1_8.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM132_137_fast_batch_autopilot.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM132_137_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM138_143_fast_batch_autopilot.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM138_143_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM144_149_fast_batch_autopilot.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ PRM144_149_independent_qa.py — SLICE004_AND_XREG 파이프라인의 독립 QA/회귀검증. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ R09_SLICE005_R2_repair_aggregate_verification.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_B3_coarse_canary_analyze.py — RESOLUTION_OPTIMIZATION 파이프라인의 감사·진단·비교. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_B3_coarse_canary_control_review.py — RESOLUTION_OPTIMIZATION 파이프라인의 감사·진단·비교. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_B3_coarse_canary_final_preregistration.py — RESOLUTION_OPTIMIZATION 파이프라인의 실행 계약·사전등록. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_B3_coarse_canary_independent_QA.py — RESOLUTION_OPTIMIZATION 파이프라인의 독립 QA/회귀검증. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_B3_coarse_canary_official_sync_QA.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_B3_coarse_canary_preregistration.py — RESOLUTION_OPTIMIZATION 파이프라인의 실행 계약·사전등록. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_B3_coarse_canary_repair_preregistration.py — RESOLUTION_OPTIMIZATION 파이프라인의 실행 계약·사전등록. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_B3_coarse_canary_worker.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_build_labpc_gdrive_factory.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 실행/후보 생성. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_build_labpc_usb_factory.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 실행/후보 생성. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_labpc_collect.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_labpc_common.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_labpc_doctor.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_labpc_runner.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 실행/후보 생성. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_labpc_usb_prep_official_sync_QA.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_labpc_verify.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_labpc_worker.py — RESOLUTION_OPTIMIZATION 파이프라인의 계산 지원/변환. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_official_sync_audit.py — RESOLUTION_OPTIMIZATION 파이프라인의 감사·진단·비교. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_strict_convergence_control_review.py — RESOLUTION_OPTIMIZATION 파이프라인의 감사·진단·비교. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_strict_convergence_independent_QA.py — RESOLUTION_OPTIMIZATION 파이프라인의 독립 QA/회귀검증. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ R09_SLICE_005_strict_convergence_preregistration_noexec.py — RESOLUTION_OPTIMIZATION 파이프라인의 실행 계약·사전등록. Pixel resolution and slice-count/spacing convergence factory; continuation-only
│  │  │        ├─ ROUTE_VALID_001_independent_qa.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 독립 QA/회귀검증. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_001_source_eligibility_and_c1_three_route.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 계산 지원/변환. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_002_b1_l7_cross_family_selected_slice.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 계산 지원/변환. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_002_independent_qa.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 독립 QA/회귀검증. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_003_f1_step_reference_pixel_phase.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 계산 지원/변환. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_003_finalize.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 결과·manifest 봉인/동기화. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_003_independent_qa.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 독립 QA/회귀검증. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_003A_brep_curve_raster_adapter_probe.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 감사·진단·비교. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_003A_f1_z400_targeted_attribution_replay.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 계산 지원/변환. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_003A_finalize.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 결과·manifest 봉인/동기화. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_003A_independent_qa.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 독립 QA/회귀검증. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_004_independent_policy_qa.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 계산 지원/변환. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ ROUTE_VALID_004_route_policy_and_nb_integration_gate.py — IMPORTED_STL_AND_ROUTE_VALIDATION 파이프라인의 계산 지원/변환. Imported-STL winding route, F1 stress tests and STEP/tessellation/STL comparison tools
│  │  │        ├─ STRICT_GEOM_006_phase_a_face_rasterizer_fixtures.py — DIRECT_STEP_C1 파이프라인의 계산 지원/변환. Original STEP B-rep slicing and direct LEGACY-PY 40-scalar reproduction for C1
│  │  │        ├─ STRICT_STEP_007_overlay_trace_execution.py — DIRECT_STEP_C1 파이프라인의 계산 실행/후보 생성. Original STEP B-rep slicing and direct LEGACY-PY 40-scalar reproduction for C1
│  │  │        ├─ STRICT_STEP_021_b3_route_a_z801_raw_primitives.py — DIRECT_STEP_C1 파이프라인의 계산 지원/변환. Original STEP B-rep slicing and direct LEGACY-PY 40-scalar reproduction for C1
│  │  │        ├─ STRICT_STEP_026_c1_direct_legacy_py_xonly.py — DIRECT_STEP_C1 파이프라인의 계산 실행/후보 생성. Original STEP B-rep slicing and direct LEGACY-PY 40-scalar reproduction for C1
│  │  │        ├─ STRICT_STEP_026_c1_independent_qa.py — DIRECT_STEP_C1 파이프라인의 독립 QA/회귀검증. Original STEP B-rep slicing and direct LEGACY-PY 40-scalar reproduction for C1
│  │  │        ├─ test_NB_INTEGRATE_001_route_policy.py — IMPORT_CONTROLLER_INTEGRATION 파이프라인의 독립 QA/회귀검증. Fail-closed source/route controller integration and its regression QA
│  │  │        ├─ TOUR_C001_T4R_SLICE_001_t8_t9_legacy_detail_convergence.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ TOUR_C001_T4R_SLICE_003A_matched_source_five_model_audit.py — SLICE004_AND_XREG 파이프라인의 감사·진단·비교. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        ├─ TOUR_C001_T4R_SLICE_004_all58_source_matched_exact_extraction.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  │        └─ TOUR_C001_T4R_SLICE_004_independent_QA_and_manifest.py — scripts 입력·출력·경로·SHA-256을 고정한 manifest
│  │  ├─ outputs/ — outputs 관련 코드·입력·결과·검증 자료
│  │  │  ├─ IMSTL008/ — IMSTL008 관련 코드·입력·결과·검증 자료
│  │  │  │  └─ IMSTL-008-20260728-002/ — IMSTL-008-20260728-002 관련 코드·입력·결과·검증 자료
│  │  │  │     └─ HQ-d7324dbb123f_20260728_212157_198620/ — HQ-d7324dbb123f_20260728_212157_198620 관련 코드·입력·결과·검증 자료
│  │  │  │        ├─ descriptor/ — descriptor 관련 코드·입력·결과·검증 자료
│  │  │  │        │  ├─ images/ — images 관련 코드·입력·결과·검증 자료
│  │  │  │        │  │  ├─ masks/ — masks 관련 코드·입력·결과·검증 자료
│  │  │  │        │  │  └─ overlays/ — overlays 관련 코드·입력·결과·검증 자료
│  │  │  │        │  ├─ tables/ — tables 관련 코드·입력·결과·검증 자료
│  │  │  │        │  │  ├─ overlay_component_table.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │  │        │  │  ├─ overlay_pixel_table.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │  │        │  │  ├─ slice_component_table.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │  │        │  │  └─ slice_pixel_count_table.csv — tables 폴더의 계산값·registry·manifest·QA 표
│  │  │  │        │  └─ qa.json — descriptor 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  │  │        ├─ descriptor_result.csv — HQ-d7324dbb123f_20260728_212157_198620 폴더의 계산값·registry·manifest·QA 표
│  │  │  │        ├─ descriptor_result.xlsx — HQ-d7324dbb123f_20260728_212157_198620 폴더의 Excel 입력·원장·결과 workbook
│  │  │  │        ├─ frozen_run_config.json — HQ-d7324dbb123f_20260728_212157_198620 실행 조건을 재현하기 위한 frozen configuration
│  │  │  │        ├─ geometry_preflight.json — HQ-d7324dbb123f_20260728_212157_198620 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  │        ├─ input_geometry_manifest.json — HQ-d7324dbb123f_20260728_212157_198620 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │  │        ├─ output_manifest.csv — HQ-d7324dbb123f_20260728_212157_198620 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │  │        ├─ run_manifest.json — HQ-d7324dbb123f_20260728_212157_198620 입력·출력·경로·SHA-256을 고정한 manifest
│  │  │  │        ├─ run_status.json — HQ-d7324dbb123f_20260728_212157_198620 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  │        ├─ training_required_input_schema.json — HQ-d7324dbb123f_20260728_212157_198620 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  │        └─ x_only_readiness.json — HQ-d7324dbb123f_20260728_212157_198620 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │  └─ URP4-1/ — URP4-1 관련 코드·입력·결과·검증 자료
│  │  │     ├─ 2._Parameter_result_0727.py — 프로젝트 작업의 protected_asset, python_source 근거 파일
│  │  │     ├─ 3._parameter_angle_all_0727.py — 프로젝트 작업의 protected_asset, python_source 근거 파일
│  │  │     └─ 압축+열+진동+구조인자_260212.xlsx — 프로젝트 작업의 protected_asset 근거 파일
│  │  ├─ URP4-1_DELIVERABLE/ — URP4-1_DELIVERABLE 관련 코드·입력·결과·검증 자료
│  │  │  └─ urp4/ — urp4 관련 코드·입력·결과·검증 자료
│  │  │     ├─ contracts/ — contracts 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ schemas/ — schemas 관련 코드·입력·결과·검증 자료
│  │  │     │  │  │  └─ urp4_contracts_v0_1.schema.json — schemas 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ canonical.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ ids.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ README.md — v0_1 폴더의 설명·보고·계약·의사결정 문서
│  │  │     │  │  └─ validation.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     ├─ descriptor_service/ — descriptor_service 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ component.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ config.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ formula.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ geometry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ pipeline.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ pixel.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ population.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ qa.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ run139.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ service.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ slicing.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     ├─ generators/ — generators 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ lattice_typeab/ — lattice_typeab 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ descriptors.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ exporters.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ graph.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ plugin.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  └─ type_b.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ tpms_multiwall/ — tpms_multiwall 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ exporters.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ fields.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ masking.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ plugin.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  └─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ voxel/ — voxel 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ exporters.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ kernel.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ plugin.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  ├─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  │  └─ source_kernel.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     ├─ geometry_io/ — geometry_io 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ routing.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ stl_import.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ v0_2/ — v0_2 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ step_import.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ v0_3/ — v0_3 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ source_preflight.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ v0_4/ — v0_4 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ imported_winding.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ v0_5/ — v0_5 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ generated_normalization.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     ├─ hq/ — hq 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ controller.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ engine.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ imported_pipeline.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ v0_2/ — v0_2 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ runtime.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ v0_3/ — v0_3 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ generated_n40_development.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     ├─ route_policy/ — route_policy 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ controller.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     ├─ training/ — training 관련 코드·입력·결과·검증 자료
│  │  │     │  ├─ p1_adapter_v0_1/ — p1_adapter_v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ adapters.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ p1_exec_layer_v0_1/ — p1_exec_layer_v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ builders.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ estimators.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ ledger.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ permit.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ v0_1/ — v0_1 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ contracts.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ policy.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ source_audit.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  ├─ v0_2/ — v0_2 관련 코드·입력·결과·검증 자료
│  │  │     │  │  ├─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ models.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  ├─ policy.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  │  └─ registry.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     │  └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  │     └─ __init__.py — 프로젝트 작업의 python_source 근거 파일
│  │  ├─ 00_VERIFY_RESUMABLE_HANDOFF.py — 압축 해제본에서 경로·필수 파일·SHA를 계산 없이 확인하는 read-only 검증기
│  │  ├─ RAW_SLICE_TABLE_MANIFEST.csv — 03_RESUMABLE_PROJECT_SNAPSHOT 입력·출력·경로·SHA-256을 고정한 manifest
│  │  ├─ RAW_SLICE_TABLES_XREG_V2_7.zip — 03_RESUMABLE_PROJECT_SNAPSHOT 폴더의 무결성 검증된 묶음 자산
│  │  ├─ README_HQ_ENGINE.md — 03_RESUMABLE_PROJECT_SNAPSHOT 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ RESUME_RUNBOOK.md — 후속 담당자가 기존 결과를 덮어쓰지 않고 계산을 재개하는 절차
│  │  ├─ URP4_1_HQ.ipynb — 메인 실행 Notebook(HQ): 전체 pipeline 설정·단계·실행 순서를 제어
│  │  └─ URP4_1_HQ_BLUEPRINT_v0_2.ipynb — 향후 21-cell 전체 HQ 구조를 정의한 설계 Notebook
│  └─ 00_PRIOR_CORE_RELEASE_RECEIPT.json — 02_VERIFIED_CORE_HQ_NB_PY 폴더의 설정·manifest·상태·QA 기계 판독 파일
├─ 03_CONFIG_RUNTIME_AND_COMMANDS/ — KMK312·Python 환경, 실행 명령, 휴대형 경로 설정
│  ├─ CANONICAL_RUNTIME.json — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  ├─ COMMANDS_AND_PATH_LENGTH.md — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 설명·보고·계약·의사결정 문서
│  ├─ ENVIRONMENT_LOCK_SHA256.json — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  ├─ KMK312_CONDA_EXPLICIT_LOCK.txt — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 텍스트 안내·로그·환경 정보
│  ├─ KMK312_CONDA_META_LOCK.json — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  ├─ KMK312_PIP_FREEZE.txt — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 텍스트 안내·로그·환경 정보
│  ├─ PORTABLE_PATH_MAP.json — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  ├─ README_PORTABLE_REPRODUCTION.md — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 설명·보고·계약·의사결정 문서
│  ├─ README_RUN_SOURCE.md — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 설명·보고·계약·의사결정 문서
│  ├─ VERIFY_READ_ONLY.cmd — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 Windows 명령 실행 launcher
│  └─ VERIFY_READ_ONLY.ps1 — 03_CONFIG_RUNTIME_AND_COMMANDS 폴더의 PowerShell 실행·검증 스크립트
├─ 04_REFERENCE_INPUTS/ — 참조 Excel, 압축시험 원본, geometry 외부 자산 포인터
│  ├─ alias_registry/ — alias_registry 관련 코드·입력·결과·검증 자료
│  │  └─ URP4-1_file_alias_registry_20260709_UPDATED.xlsx — alias_registry 폴더의 Excel 입력·원장·결과 workbook
│  ├─ doctor_compression_data_20260731/ — doctor_compression_data_20260731 관련 코드·입력·결과·검증 자료
│  │  ├─ 01_structural_factors/ — 01_structural_factors 관련 코드·입력·결과·검증 자료
│  │  │  └─ Structural_Factors_All.xlsx — 01_structural_factors 폴더의 Excel 입력·원장·결과 workbook
│  │  ├─ 02_reference_strut_sources/ — 02_reference_strut_sources 관련 코드·입력·결과·검증 자료
│  │  │  ├─ AI lattice_1-150_30 mm_merge.xlsx — 02_reference_strut_sources 폴더의 Excel 입력·원장·결과 workbook
│  │  │  ├─ B, C, L model_30 mm_merge.xlsx — 02_reference_strut_sources 폴더의 Excel 입력·원장·결과 workbook
│  │  │  └─ Voronoi_30 mm_merge.xlsx — 02_reference_strut_sources 폴더의 Excel 입력·원장·결과 workbook
│  │  ├─ 03_ai_lattice_summaries/ — 03_ai_lattice_summaries 관련 코드·입력·결과·검증 자료
│  │  │  ├─ Ai-Lattice_(1-50)_summary (1).xlsx — 03_ai_lattice_summaries 폴더의 Excel 입력·원장·결과 workbook
│  │  │  ├─ Ai-Lattice_(101-150)_summary.xlsx — 03_ai_lattice_summaries 폴더의 Excel 입력·원장·결과 workbook
│  │  │  └─ Ai-Lattice_(51-100)_summary.xlsx — 03_ai_lattice_summaries 폴더의 Excel 입력·원장·결과 workbook
│  │  ├─ 04_bcl_summaries_pending/ — 04_bcl_summaries_pending 관련 코드·입력·결과·검증 자료
│  │  │  └─ README.md — 04_bcl_summaries_pending 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ 05_voronoi_summaries_pending/ — 05_voronoi_summaries_pending 관련 코드·입력·결과·검증 자료
│  │  │  └─ README.md — 05_voronoi_summaries_pending 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ FILE_MANIFEST.csv — doctor_compression_data_20260731 입력·출력·경로·SHA-256을 고정한 manifest
│  │  └─ README.md — doctor_compression_data_20260731 폴더의 설명·보고·계약·의사결정 문서
│  ├─ doctor_compression_data_20260802/ — doctor_compression_data_20260802 관련 코드·입력·결과·검증 자료
│  │  ├─ small_reference_summaries/ — small_reference_summaries 관련 코드·입력·결과·검증 자료
│  │  │  ├─ Compression_VF30_Summary.xlsx — small_reference_summaries 폴더의 Excel 입력·원장·결과 workbook
│  │  │  ├─ Compression_VF45_Summary.xlsx — small_reference_summaries 폴더의 Excel 입력·원장·결과 workbook
│  │  │  ├─ Compression_VF60_Summary.xlsx — small_reference_summaries 폴더의 Excel 입력·원장·결과 workbook
│  │  │  └─ Voronoi_Summary.xlsx — small_reference_summaries 폴더의 Excel 입력·원장·결과 workbook
│  │  ├─ README.md — doctor_compression_data_20260802 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ SOURCE_MANIFEST.csv — doctor_compression_data_20260802 입력·출력·경로·SHA-256을 고정한 manifest
│  │  └─ SOURCE_MANIFEST.json — doctor_compression_data_20260802 입력·출력·경로·SHA-256을 고정한 manifest
│  ├─ geometry_drive_asset_pointer_only/ — geometry_drive_asset_pointer_only 관련 코드·입력·결과·검증 자료
│  │  ├─ R09_reference_model_manifest.csv — geometry_drive_asset_pointer_only 입력·출력·경로·SHA-256을 고정한 manifest
│  │  ├─ R09_reference_model_manifest.json — geometry_drive_asset_pointer_only 입력·출력·경로·SHA-256을 고정한 manifest
│  │  └─ README.md — geometry_drive_asset_pointer_only 폴더의 설명·보고·계약·의사결정 문서
│  └─ legacy_reference/ — legacy_reference 관련 코드·입력·결과·검증 자료
│     └─ 압축+열+진동+구조인자_260212.xlsx — 프로젝트 작업의 protected_asset 근거 파일
├─ 05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE/ — geometry·slicing·구조인자 후보은행과 검증 근거
│  ├─ HQ-GEOM-002/ — HQ-GEOM-002 관련 코드·입력·결과·검증 자료
│  │  ├─ HQ_GEOM_002_VERSIONED_DEVELOPMENT_ROUTE_REPORT_20260728.md — HQ-GEOM-002 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ INDEPENDENT_QA.json — HQ-GEOM-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  ├─ MERGE_PACKET.md — HQ-GEOM-002 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  │  ├─ PRODUCER_SUMMARY.json — HQ-GEOM-002 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  │  └─ PROTECTED_ASSET_AUDIT.csv — HQ-GEOM-002 폴더의 계산값·registry·manifest·QA 표
│  ├─ HQ-GEOM-003/ — HQ-GEOM-003 관련 코드·입력·결과·검증 자료
│  │  ├─ CHUCK_INPUT_PACKET_TOPOLOGY_POLICY_20260728.md — HQ-GEOM-003 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ HQ_GEOM_003_LATTICE_TPMS_TOPOLOGY_EXCEPTION_PREREGISTRATION_REPORT_20260728.md — HQ-GEOM-003 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ INDEPENDENT_PREREG_QA.json — HQ-GEOM-003 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  ├─ MERGE_PACKET.md — HQ-GEOM-003 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  │  ├─ PROTECTED_ASSET_AUDIT.csv — HQ-GEOM-003 폴더의 계산값·registry·manifest·QA 표
│  │  ├─ REPORT.md — HQ-GEOM-003 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  └─ TOPOLOGY_EXCEPTION_CONTRACT.json — HQ-GEOM-003 폴더의 설정·manifest·상태·QA 기계 판독 파일
│  ├─ L28-DESCVAL/ — L28-DESCVAL 관련 코드·입력·결과·검증 자료
│  │  ├─ INDEPENDENT_QA_REPORT.json — L28-DESCVAL 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  ├─ INDEPENDENT_QA_REPORT.md — L28-DESCVAL 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  ├─ L28_ANOMALY_SHORTLIST.md — L28-DESCVAL 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ L28_ARCHIVAL_AUDIT_REPORT.md — L28-DESCVAL 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  ├─ L28_FINAL_DESCRIPTOR_READINESS_REPORT.md — L28-DESCVAL 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  ├─ L28_STATISTICAL_FLAG_INTERPRETATION_ADDENDUM.md — L28-DESCVAL 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ PACKAGE_MANIFEST.json — L28-DESCVAL 입력·출력·경로·SHA-256을 고정한 manifest
│  │  ├─ PHASE1_QA.json — L28-DESCVAL 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  └─ PHASE2_3_QA.json — L28-DESCVAL 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  ├─ LINK_TARGETS_R2/ — LINK_TARGETS_R2 관련 코드·입력·결과·검증 자료
│  │  ├─ HQ-GEOM-003-20260728-001_policy_options.csv — LINK_TARGETS_R2 폴더의 계산값·registry·manifest·QA 표
│  │  ├─ HQ-GEOM-003-20260728-001_source_topology_evidence.csv — LINK_TARGETS_R2 폴더의 계산값·registry·manifest·QA 표
│  │  ├─ PRM144_149_fast_batch_autopilot.py — SLICE004_AND_XREG 파이프라인의 계산 지원/변환. 58-model raw-table extraction plus no-y descriptor candidate/XREG construction and QA
│  │  ├─ PRM144_149_independent_QA.csv — LINK_TARGETS_R2 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  ├─ ROUTE-VALID-004-20260729-001_fail_closed_fallback.csv — LINK_TARGETS_R2 폴더의 계산값·registry·manifest·QA 표. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  └─ ROUTE-VALID-004-20260729-001_source_type_route_policy.csv — LINK_TARGETS_R2 폴더의 계산값·registry·manifest·QA 표. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  ├─ NB-INTEGRATE-001/ — NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  ├─ FIXTURE_TEST_OUTPUT.txt — NB-INTEGRATE-001 폴더의 텍스트 안내·로그·환경 정보. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  ├─ INDEPENDENT_QA.csv — NB-INTEGRATE-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  ├─ INDEPENDENT_QA.json — NB-INTEGRATE-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  ├─ MERGE_PACKET.md — NB-INTEGRATE-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  ├─ NOTEBOOK_STATIC_QA.json — NB-INTEGRATE-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  ├─ OUTPUT_MANIFEST.csv — NB-INTEGRATE-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  ├─ PROTECTED_ASSET_RECHECK.csv — NB-INTEGRATE-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  ├─ REPORT.md — NB-INTEGRATE-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  │  └─ RUNTIME_PATH_DISCOVERY_CORRECTION.md — NB-INTEGRATE-001 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: NB-INTEGRATE-001(source type별 Import route controller 개발·QA 작업)
│  ├─ POSTRUN-GATE-001/ — POSTRUN-GATE-001 관련 코드·입력·결과·검증 자료
│  │  ├─ C1_INDEPENDENT_QA_RESULT.json — POSTRUN-GATE-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  ├─ CLAIM_AND_STATUS_LEDGER.csv — STRICT-STEP-026 작업의 v1.1 authoritative evidence 근거 파일
│  │  ├─ MERGE_PACKET.md — POSTRUN-GATE-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
│  │  ├─ NEXT_GATE_RECOMMENDATION.md — POSTRUN-GATE-001 폴더의 설명·보고·계약·의사결정 문서
│  │  ├─ REPORT.md — POSTRUN-GATE-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서
│  │  ├─ TRAIN_REPLAY_LIFECYCLE_AWARE_QA_V2.json — POSTRUN-GATE-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  │  └─ TRAIN_REPLAY_QA_FAILURE_DISPOSITION.csv — POSTRUN-GATE-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  ├─ ROUTE-VALID-003/ — ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  ├─ figures/ — ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AB_worst_01_z0400_P750_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AB_worst_02_z0400_P750_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AB_worst_03_z0400_P1000_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AB_worst_04_z0400_P1000_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AB_worst_05_z0400_P1500_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AB_worst_06_z0400_P1500_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AC_worst_01_z0400_P500_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AC_worst_02_z0400_P500_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AC_worst_03_z0400_P750_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AC_worst_04_z0400_P750_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  ├─ AC_worst_05_z0400_P1000_P50X.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  │  └─ AC_worst_06_z0400_P1000_P00.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  ├─ COMMON_RASTER_CONTRACT.json — ROUTE-VALID-003 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  ├─ INDEPENDENT_QA.json — ROUTE-VALID-003 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  ├─ MERGE_PACKET.md — ROUTE-VALID-003 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  ├─ OUTPUT_MANIFEST.csv — ROUTE-VALID-003 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  ├─ PRODUCER_PACKET.json — ROUTE-VALID-003 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  ├─ REPORT.md — ROUTE-VALID-003 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  │  └─ ROUTE_VALID_003_PACKET.json — ROUTE-VALID-003 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-003(STEP·tessellation·imported STL selected-slice 비교 작업)
│  ├─ ROUTE-VALID-004/ — ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  ├─ FINAL_OUTPUT_MANIFEST.csv — ROUTE-VALID-004 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  ├─ INDEPENDENT_QA.json — ROUTE-VALID-004 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  ├─ MERGE_PACKET.md — ROUTE-VALID-004 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  ├─ OUTPUT_MANIFEST.csv — ROUTE-VALID-004 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  ├─ POLICY_CONTRACT.json — ROUTE-VALID-004 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  ├─ PROTECTED_ASSET_RECHECK.csv — ROUTE-VALID-004 폴더의 계산값·registry·manifest·QA 표. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  │  └─ REPORT.md — ROUTE-VALID-004 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: ROUTE-VALID-004(source type별 허용·차단 route 정책 결정 작업)
│  ├─ STRICT-STEP-026/ — STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  ├─ anchor_pngs/ — STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  ├─ overlay_0199_0200.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  ├─ overlay_0399_0400.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  ├─ overlay_0599_0600.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  ├─ overlay_0799_0800.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  ├─ slice_0000.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  ├─ slice_0200.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  ├─ slice_0400.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  ├─ slice_0600.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  │  └─ slice_0800.png — anchor_pngs 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  ├─ CONTRACT_MANIFEST.json — STRICT-STEP-026 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  ├─ direct_legacy_scalar_table.csv — STRICT-STEP-026 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  ├─ INDEPENDENT_QA.json — STRICT-STEP-026 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  ├─ overlay_png_manifest.csv — STRICT-STEP-026 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  ├─ RUN_STATE.json — STRICT-STEP-026 작업의 terminal_snapshot_v1_1_r2 근거 파일. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  │  └─ slice_png_manifest.csv — STRICT-STEP-026 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: STRICT-STEP-026(C1 원본 STEP direct slicing·구조인자 40개 계산 작업)
│  ├─ XREG-v2.7/ — XREG-v2.7(구조인자 후보은행(기존 구조인자 + 새로 추가한 구조인자 후보 542개))
│  │  ├─ PRM149_unified_redundancy_block_registry.csv — XREG-v2.7 폴더의 계산값·registry·manifest·QA 표. 관련 ID: XREG-v2.7(구조인자 후보은행(기존 구조인자 + 새로 추가한 구조인자 후보 542개))
│  │  ├─ PRM149_unified_redundancy_edge_registry.csv — XREG-v2.7 폴더의 계산값·registry·manifest·QA 표. 관련 ID: XREG-v2.7(구조인자 후보은행(기존 구조인자 + 새로 추가한 구조인자 후보 542개))
│  │  ├─ PRM149_xreg_v2_7_candidate_bank.csv — XREG-v2.7 폴더의 계산값·registry·manifest·QA 표. 관련 ID: XREG-v2.7(구조인자 후보은행(기존 구조인자 + 새로 추가한 구조인자 후보 542개))
│  │  └─ PRM149_xreg_v2_7_values_long.csv — XREG-v2.7 폴더의 계산값·registry·manifest·QA 표. 관련 ID: XREG-v2.7(구조인자 후보은행(기존 구조인자 + 새로 추가한 구조인자 후보 542개))
│  ├─ R09-20260720-TOUR-C001_T4R_SLICE_004_ALL58_SOURCE_MATCHED_EXACT_EXTRACTION_REPORT_20260720.md — 05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE 폴더의 설명·보고·계약·의사결정 문서
│  └─ R09-20260723-PRM144_149_BATCH_AUTOPILOT_REPORT.md — 05_DESCRIPTOR_XREG_GEOMETRY_EVIDENCE 작업의 목적·실행 결과·해석 경계를 기록한 보고서
├─ 06_TRAINING_EVIDENCE/ — Training 1–5 audit·replay·parity 근거
│  ├─ TRAIN-AUDIT-001/ — TRAIN-AUDIT-001(박사님 제공 Training Notebook 9개 구조·입출력 감사)
│  │  ├─ MERGE_PACKET.md — TRAIN-AUDIT-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: TRAIN-AUDIT-001(박사님 제공 Training Notebook 9개 구조·입출력 감사)
│  │  ├─ NEXT_ACTION_RECOMMENDATION.md — TRAIN-AUDIT-001 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: TRAIN-AUDIT-001(박사님 제공 Training Notebook 9개 구조·입출력 감사)
│  │  ├─ REPORT.md — TRAIN-AUDIT-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-AUDIT-001(박사님 제공 Training Notebook 9개 구조·입출력 감사)
│  │  ├─ TRAINING_EXISTING_EVIDENCE_INDEX.csv — TRAIN-AUDIT-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-AUDIT-001(박사님 제공 Training Notebook 9개 구조·입출력 감사)
│  │  ├─ TRAINING_FIRST_UNFINISHED_GATE.md — TRAIN-AUDIT-001 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: TRAIN-AUDIT-001(박사님 제공 Training Notebook 9개 구조·입출력 감사)
│  │  ├─ TRAINING_NINE_NOTEBOOK_STATUS_MATRIX.csv — TRAIN-AUDIT-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-AUDIT-001(박사님 제공 Training Notebook 9개 구조·입출력 감사)
│  │  └─ TRAINING_SOURCE_AND_MODULE_LINEAGE.csv — TRAIN-AUDIT-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-AUDIT-001(박사님 제공 Training Notebook 9개 구조·입출력 감사)
│  ├─ TRAIN-PARITY-001/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ ADAPTER_GAP_AND_READINESS_MATRIX.csv — TRAIN-PARITY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ CONTROLLED_PARITY_EXECUTION_PREREQUISITES.md — TRAIN-PARITY-001 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ DATASET_AND_GROUP_PARITY_CONTRACT.csv — TRAIN-PARITY-001 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ DETERMINISM_AND_RANDOMNESS_REGISTER.csv — TRAIN-PARITY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ FEATURE_METHOD_MODEL_PARITY_CONTRACT.csv — TRAIN-PARITY-001 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ FOLD_MANIFEST_SCHEMA.csv — TRAIN-PARITY-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ FROZEN_SOURCE_EXECUTION_CONTRACT.json — TRAIN-PARITY-001 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ MERGE_PACKET.md — TRAIN-PARITY-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PREDICTION_METRIC_TOLERANCE_REGISTRY.csv — TRAIN-PARITY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ REPORT.md — TRAIN-PARITY-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ SOURCE_ADAPTER_LINEAGE_MATRIX.csv — TRAIN-PARITY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  └─ TARGET_ELIGIBILITY_AND_HOLD_POLICY.csv — TRAIN-PARITY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  ├─ TRAIN-PARITY-002/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ artifacts/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ COLUMN_IDENTITY_LEDGER.csv — TRAIN-PARITY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ DATASET_MANIFEST.json — artifacts 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ METRIC_LEDGER_EMPTY.csv — TRAIN-PARITY-002, TRAIN-PARITY-002A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ PREDICTION_LEDGER_EMPTY.csv — TRAIN-PARITY-002, TRAIN-PARITY-002A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ ROW_IDENTITY_LEDGER.csv — TRAIN-PARITY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ SHARED_FOLD_MANIFEST.csv — artifacts 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ SHARED_FOLD_MANIFEST.meta.json — artifacts 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  └─ TARGET_SAMPLE_LEDGER.csv — TRAIN-PARITY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ implementation/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ __init__.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ contracts.py — TRAIN-PARITY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ extractor.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ folds.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ guards.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ hashing.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ ledgers.py — TRAIN-PARITY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ observability.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ source_ast.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  └─ stage_graph.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ DATASET_EXTRACTOR_QA.csv — TRAIN-PARITY-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ GROUP_AND_FOLD_MANIFEST_QA.csv — TRAIN-PARITY-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ IMPLEMENTATION_MANIFEST.json — TRAIN-PARITY-002 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ INDEPENDENT_QA.json — TRAIN-PARITY-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ independent_qa.py — TRAIN-PARITY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ MERGE_PACKET.md — TRAIN-PARITY-002 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ NEGATIVE_FAIL_CLOSED_QA.csv — TRAIN-PARITY-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ NO_FIT_PROOF.json — TRAIN-PARITY-002 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ OBSERVABILITY_EVENT_SCHEMA.csv — TRAIN-PARITY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PREDICTION_METRIC_LEDGER_SCHEMA.csv — TRAIN-PARITY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PROTECTED_ASSET_HASH_AUDIT.csv — TRAIN-PARITY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ REPORT.md — TRAIN-PARITY-002 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ run_no_fit_implementation.py — TRAIN-PARITY-002 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ SOURCE_FUNCTION_LINEAGE.csv — TRAIN-PARITY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  └─ STAGE_GRAPH_COVERAGE.csv — TRAIN-PARITY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  ├─ TRAIN-PARITY-002A/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ artifacts/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ FIXTURE_OBSERVABILITY_EVENTS.jsonl — artifacts 폴더의 연구 패키지 보조 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ METRIC_LEDGER_EMPTY.csv — TRAIN-PARITY-002, TRAIN-PARITY-002A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  └─ PREDICTION_LEDGER_EMPTY.csv — TRAIN-PARITY-002, TRAIN-PARITY-002A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ implementation/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ __init__.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ branches.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ contracts.py — TRAIN-PARITY-002A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ hashing.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ instrumentation.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ ledgers.py — TRAIN-PARITY-002A, TRAIN-PARITY-003A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ no_fit_guard.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  └─ source_exact_runtime.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ BRANCH_IMPLEMENTATION_STATUS.csv — TRAIN-PARITY-002A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ BRANCH_STAGE_AND_OBJECTIVE_MATRIX.csv — TRAIN-PARITY-002A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ IMPLEMENTATION_MANIFEST.json — TRAIN-PARITY-002A 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ INDEPENDENT_QA.json — TRAIN-PARITY-002A 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ independent_qa.py — TRAIN-PARITY-002A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ MERGE_PACKET.md — TRAIN-PARITY-002A 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ NO_FIT_PROOF.json — TRAIN-PARITY-002A 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ NONDETERMINISM_AND_FALLBACK_INSTRUMENTATION.csv — TRAIN-PARITY-002A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PROTECTED_ASSET_HASH_AUDIT.csv — TRAIN-PARITY-002A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ REPORT.md — TRAIN-PARITY-002A 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ run_static_fixture_batch.py — TRAIN-PARITY-002A 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ SOURCE_TO_ADAPTER_NUMERICAL_LINEAGE.csv — TRAIN-PARITY-002A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  └─ STATIC_AND_FIXTURE_QA.csv — TRAIN-PARITY-002A 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  ├─ TRAIN-PARITY-003/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ build_preregistration_packet.py — TRAIN-PARITY-003 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ BUILD_STATE.json — TRAIN-PARITY-003 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ CONTROLLED_EXECUTION_CONTRACT.json — TRAIN-PARITY-003 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ EXECUTION_PERMIT_DRAFT.json — TRAIN-PARITY-003 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ FAIL_CLOSED_STOP_CONDITIONS.csv — TRAIN-PARITY-003 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ independent_preregistration_qa.py — TRAIN-PARITY-003 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ MERGE_PACKET.md — TRAIN-PARITY-003 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PREREGISTRATION_QA.json — TRAIN-PARITY-003 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ REPORT.md — TRAIN-PARITY-003 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ RESOURCE_AND_RUNTIME_ESTIMATE.csv — TRAIN-PARITY-003 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ SENTINEL_TARGET_SELECTION.csv — TRAIN-PARITY-003 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ SOURCE_REFERENCE_ADAPTER_BINDING.csv — TRAIN-PARITY-003 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  └─ STAGE_PARITY_LEDGER_SCHEMA.csv — TRAIN-PARITY-003 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  ├─ TRAIN-PARITY-003A/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ adapter_v0_1_1/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ implementation/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  │  ├─ __init__.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  │  ├─ branches.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  │  ├─ contracts.py — TRAIN-PARITY-003A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  │  ├─ hashing.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  │  ├─ instrumentation.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  │  ├─ ledgers.py — TRAIN-PARITY-002A, TRAIN-PARITY-003A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  │  ├─ no_fit_guard.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  │  └─ source_exact_runtime.py — implementation 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  └─ __init__.py — adapter_v0_1_1 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ ADAPTER_BRANCH_NO_FIT_QA.csv — TRAIN-PARITY-003A 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ ADAPTER_V0_1_1_CHANGE_MANIFEST.json — TRAIN-PARITY-003A 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ AFFECTED_CONTRACT_QA.json — TRAIN-PARITY-003A 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ build_train_parity_003a.py — TRAIN-PARITY-003A 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ EXECUTION_PERMIT.json — TRAIN-PARITY-003A 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ FIT_PREDICT_COUNTERS.json — TRAIN-PARITY-003A 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ FOLD_POLICY_REBIND_QA.csv — TRAIN-PARITY-003A 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ INDEPENDENT_QA.json — TRAIN-PARITY-003A 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ independent_qa.py — TRAIN-PARITY-003A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ INDEPENDENT_QA_EXECUTION_ATTEMPT_LOG.json — TRAIN-PARITY-003A 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ MERGE_PACKET.md — TRAIN-PARITY-003A 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PREDECESSOR_POLICY_SUPERSESSION.csv — TRAIN-PARITY-003A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PREREGISTRATION_READJUDICATION.json — TRAIN-PARITY-003A 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ REPLAY_REFIT_HOLD_PROVENANCE.csv — TRAIN-PARITY-003A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ REPORT.md — TRAIN-PARITY-003A 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ run_affected_contract_qa.py — TRAIN-PARITY-003A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ source_reference_runner.py — TRAIN-PARITY-003A 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ SOURCE_REFERENCE_RUNNER_PREFLIGHT.csv — TRAIN-PARITY-003A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ TARGET_HEADER_AND_VALUE_HASH_PROOF.csv — TRAIN-PARITY-003A 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ TARGET_IDENTITY_CROSSWALK_V0_2.csv — TRAIN-PARITY-003A 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ TARGET_POLICY_NEGATIVE_QA.csv — TRAIN-PARITY-003A 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  └─ TRAIN_TARGET_POLICY_V0_2.json — TRAIN-PARITY-003A 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  ├─ TRAIN-PARITY-004/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ logs/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ source.stderr.log — 프로젝트 작업의 python_source 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  └─ source.stdout.log — 프로젝트 작업의 python_source 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ qa/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  └─ PREFLIGHT.csv — qa 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ source_reference/ — TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ stage_P0_dataset.json — source_reference 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ stage_P1_split.json — source_reference 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ stage_P2_preprocessing.json — source_reference 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  ├─ stage_P3_features.json — source_reference 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  │  └─ stage_P4_contract_pre_fit.json — TRAIN-PARITY-004 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ ADAPTER_EXECUTION_MANIFEST.json — TRAIN-PARITY-004 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ ADAPTER_PREDICTION_LEDGER.csv — TRAIN-PARITY-004 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ CHECKPOINT_AND_RESUME_MANIFEST.json — TRAIN-PARITY-004 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ EXECUTION_AUTHORIZATION.json — TRAIN-PARITY-004 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ FIRST_MISMATCH_REPORT.md — TRAIN-PARITY-004 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ INDEPENDENT_QA.json — TRAIN-PARITY-004 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ MERGE_PACKET.md — TRAIN-PARITY-004 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ METRIC_COMPARISON.csv — TRAIN-PARITY-004 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PREDICTION_COMPARISON.csv — TRAIN-PARITY-004 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PRODUCER_FINAL_STATE.json — TRAIN-PARITY-004 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ PROTECTED_ASSET_HASH_AUDIT.csv — TRAIN-PARITY-004 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ REPORT.md — TRAIN-PARITY-004 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ RUNTIME_ENVIRONMENT.json — TRAIN-PARITY-004 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ SOURCE_EXECUTION_MANIFEST.json — TRAIN-PARITY-004 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  ├─ SOURCE_PREDICTION_LEDGER.csv — TRAIN-PARITY-004 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  │  └─ STAGE_PARITY_LEDGER.csv — TRAIN-PARITY-004 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-PARITY(Training 원본 branch와 adapter의 수치 동등성 검증 작업군)
│  └─ TRAIN-REPLAY-001/ — TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ model_comparison/ — TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     │  ├─ final_refit_summary.csv — TRAIN-REPLAY-001 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     │  └─ final_summary_merged.csv — TRAIN-REPLAY-001 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ actual_input_manifest.csv — TRAIN-REPLAY-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ cell_execution_status.csv — TRAIN-REPLAY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ extracted_training_contract.json — TRAIN-REPLAY-001 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ generated_output_manifest.csv — TRAIN-REPLAY-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ independent_qa.json — TRAIN-REPLAY-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ independent_qa_checks.csv — TRAIN-REPLAY-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ MERGE_PACKET.md — TRAIN-REPLAY-001 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ prediction_and_metric_inventory.csv — TRAIN-REPLAY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ replay_state.json — TRAIN-REPLAY-001 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ REPORT.md — TRAIN-REPLAY-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ runtime_environment.json — TRAIN-REPLAY-001 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     ├─ TRAIN-2ND-NEWFEATURE_EXECUTED_ISOLATED.ipynb — TRAIN-REPLAY-001 폴더의 Jupyter Notebook. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
│     └─ warnings_and_errors.md — TRAIN-REPLAY-001 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: TRAIN-REPLAY-001(Training 원본 Notebook 실행 재현 작업)
├─ 07_COMPRESSION_DATA_AND_PILOT/ — AI Lattice·B/C/L·Voronoi 압축 데이터 파이프라인과 결과
│  ├─ COMP-FACTORY-001/ — COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ ai_lattice_x_wide.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ ai_lattice_xy_all150_trace.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ ai_lattice_xy_eligible149.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ ai_lattice_y_long.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ ai_lattice_y_wide.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ excluded_non_model_rows.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ feature_registry.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ INDEPENDENT_QA.csv — COMP-FACTORY-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ INDEPENDENT_QA_SUMMARY.json — COMP-FACTORY-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ MANIFEST.json — COMP-FACTORY-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ producer_QA.csv — COMP-FACTORY-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ REPORT.md — COMP-FACTORY-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ row_registry.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  ├─ source_audit.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  │  └─ target_registry.csv — COMP-FACTORY-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  ├─ COMP-FACTORY-002/ — COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ figures/ — COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  │  ├─ f1_yx.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  │  ├─ f2_r2.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  │  └─ f3_block.png — figures 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ feature_redundancy_edges.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ feature_selection_frequency.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ feature_x_only_census.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ fold_local_feature_selection.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ INDEPENDENT_QA.csv — COMP-FACTORY-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ INDEPENDENT_QA_SUMMARY.json — COMP-FACTORY-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ MANIFEST.json — COMP-FACTORY-002 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ method_execution_details.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ metrics.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ nearest_neighbor_collision_audit.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ oof_predictions.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ outer_fold_registry.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ producer_QA.csv — COMP-FACTORY-002 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ REPORT.md — COMP-FACTORY-002 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ source_hash_audit.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ target_screening_summary.csv — COMP-FACTORY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ target_y_census.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  ├─ target_y_redundancy_edges.csv — COMP-FACTORY-002 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  │  └─ target_y_source_block_summary.csv — COMP-FACTORY-002 작업의 v1.1 authoritative evidence 근거 파일. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
│  ├─ COMP-FACTORY-003_BCL_VORONOI_INTAKE/ — COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ cell_lineage.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ feature_registry.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ independent_QA.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ independent_QA.json — COMP-FACTORY-003_BCL_VORONOI_INTAKE 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ MANIFEST.json — COMP-FACTORY-003_BCL_VORONOI_INTAKE 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ performance_y_wide_all.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ producer_QA.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ REPORT.md — COMP-FACTORY-003_BCL_VORONOI_INTAKE 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ row_registry.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ source_audit.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ structural_x_wide_relevant.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  ├─ target_registry.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  │  └─ xy_eligible_exact_join.csv — COMP-FACTORY-003_BCL_VORONOI_INTAKE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업)
│  ├─ COMP-FACTORY-004_BCL/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ best_target_y_vs_oof_prediction.png — COMP-FACTORY-004_BCL 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ feature_redundancy_edges.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ feature_selection_frequency.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ feature_x_only_census.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ fold_local_feature_selection.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ independent_QA.csv — COMP-FACTORY-004_BCL 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ independent_QA.json — COMP-FACTORY-004_BCL 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ independent_QA_v2.csv — COMP-FACTORY-004_BCL 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ independent_QA_v2.json — COMP-FACTORY-004_BCL 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ MANIFEST.json — COMP-FACTORY-004_BCL 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ method_execution_details.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ metrics.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ oof_predictions.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ outer_fold_registry.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ producer_QA.csv — COMP-FACTORY-004_BCL 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ REPORT.md — COMP-FACTORY-004_BCL 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ source_hash_audit.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ target_screening_pooled_r2.png — COMP-FACTORY-004_BCL 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ target_screening_summary.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ WARNING_AND_LIMITATION_REGISTER.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  └─ WARNING_AND_LIMITATION_REGISTER_v2.csv — COMP-FACTORY-004_BCL 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  ├─ COMP-FACTORY-004_HANDOFF/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ MERGE_PACKET.md — COMP-FACTORY-004_HANDOFF 작업의 QA·채택 범위·남은 제한을 요약한 merge packet. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ REPORT.md — COMP-FACTORY-004_HANDOFF 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  └─ RESULT_INDEX.csv — COMP-FACTORY-004_HANDOFF 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  ├─ COMP-FACTORY-004_PIPELINE_SOURCE/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ project_snapshot/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │  └─ experiments/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │     └─ lab_001_xy_connection_20260626/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        ├─ data/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  ├─ processed/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │  └─ COMP-FACTORY-003/ — COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │     └─ COMP-FACTORY-003-BCL-VORONOI-20260802-001/ — COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ cell_lineage.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ feature_registry.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ independent_QA.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ independent_QA.json — COMP-FACTORY-003-BCL-VORONOI-20260802-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ MANIFEST.json — COMP-FACTORY-003-BCL-VORONOI-20260802-001 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ performance_y_wide_all.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ producer_QA.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ REPORT.md — COMP-FACTORY-003-BCL-VORONOI-20260802-001 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ row_registry.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ source_audit.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ structural_x_wide_relevant.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        ├─ target_registry.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  │        └─ xy_eligible_exact_join.csv — COMP-FACTORY-003-BCL-VORONOI-20260802-001 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-003(B/C/L·Voronoi 압축 데이터 인입·crosswalk 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  └─ raw/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │     └─ doctor_compression_data_20260731/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │        └─ 01_structural_factors/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │           └─ Structural_Factors_All.xlsx — 01_structural_factors 폴더의 Excel 입력·원장·결과 workbook. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        ├─ factories/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │  └─ COMP-FACTORY-001/ — COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │     ├─ config/ — COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │     │  └─ compression_groups_v0_2.json — config 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │     ├─ FACTORY_STATUS.json — COMP-FACTORY-001 폴더의 설정·manifest·상태·QA 기계 판독 파일. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        │     └─ README.md — COMP-FACTORY-001 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업); COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │        └─ scripts/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │           ├─ COMP002_ai_lattice_fs4_pilot.py — scripts 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │           ├─ COMP003_xlsx_structure_probe.py — scripts 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │           ├─ COMP004_bcl_voronoi_independent_qa.py — scripts 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │           ├─ COMP004_bcl_voronoi_intake.py — scripts 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │           ├─ COMP005_multigroup_fs4_pilot.py — scripts 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │           ├─ COMP005_multigroup_independent_qa.py — scripts 폴더의 Python 실행·계산·검증 스크립트. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  │           └─ COMP006_artifact_output_validation.mjs — scripts 폴더의 연구 패키지 보조 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ PIPELINE_REPRODUCTION_GUIDE.md — COMP-FACTORY-004_PIPELINE_SOURCE 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  └─ SOURCE_CODE_SHA256.csv — COMP-FACTORY-004_PIPELINE_SOURCE 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  ├─ COMP-FACTORY-004_VORONOI/ — COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ best_target_y_vs_oof_prediction.png — COMP-FACTORY-004_VORONOI 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ feature_redundancy_edges.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ feature_selection_frequency.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ feature_x_only_census.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ fold_local_feature_selection.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ independent_QA.csv — COMP-FACTORY-004_VORONOI 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ independent_QA.json — COMP-FACTORY-004_VORONOI 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ independent_QA_v2.csv — COMP-FACTORY-004_VORONOI 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ independent_QA_v2.json — COMP-FACTORY-004_VORONOI 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ MANIFEST.json — COMP-FACTORY-004_VORONOI 입력·출력·경로·SHA-256을 고정한 manifest. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ method_execution_details.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ metrics.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ oof_predictions.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ outer_fold_registry.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ producer_QA.csv — COMP-FACTORY-004_VORONOI 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ REPORT.md — COMP-FACTORY-004_VORONOI 작업의 목적·실행 결과·해석 경계를 기록한 보고서. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ source_hash_audit.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ target_screening_pooled_r2.png — COMP-FACTORY-004_VORONOI 작업의 slice·overlay·진단·결과 시각 자료. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ target_screening_summary.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  ├─ WARNING_AND_LIMITATION_REGISTER.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  │  └─ WARNING_AND_LIMITATION_REGISTER_v2.csv — COMP-FACTORY-004_VORONOI 폴더의 계산값·registry·manifest·QA 표. 관련 ID: COMP-FACTORY-004(B/C/L·Voronoi grouped Feature Selection technical pilot)
│  ├─ COMP-FACTORY-001_HANDOFF.md — 07_COMPRESSION_DATA_AND_PILOT 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: COMP-FACTORY-001(AI Lattice 압축 데이터 인입·정합 작업)
│  └─ COMP-FACTORY-002_HANDOFF.md — 07_COMPRESSION_DATA_AND_PILOT 폴더의 설명·보고·계약·의사결정 문서. 관련 ID: COMP-FACTORY-002(AI Lattice 네 가지 Feature Selection technical pilot)
├─ 08_OPTIONAL_UI_DEMO/ — 선택적 UI·역설계 demo 자료; 과학적 검증 결과가 아님
│  ├─ README_BOUNDARY.md — 08_OPTIONAL_UI_DEMO 폴더의 설명·보고·계약·의사결정 문서
│  ├─ UI_FACTORY_003_PROFESSOR_COLD_START_ACCEPTANCE_20260731.md — 08_OPTIONAL_UI_DEMO 폴더의 설명·보고·계약·의사결정 문서
│  └─ URP4-1_FACTORY_v1_3.zip — 08_OPTIONAL_UI_DEMO 폴더의 무결성 검증된 묶음 자산
├─ 09_LIMITATIONS_AND_RESUME/ — 미완료·차단·다음 gate와 과거 연구 기록
│  ├─ AI_START_HERE_SOURCE_POINTER.md — 09_LIMITATIONS_AND_RESUME 폴더의 설명·보고·계약·의사결정 문서
│  ├─ KNOWN_LIMITATIONS_AND_BLOCKERS.md — 제출 시점의 과학적 미완료·차단·금지 주장과 다음 gate
│  ├─ R09_blackbox_decision_register_20260703.md — 09_LIMITATIONS_AND_RESUME 폴더의 설명·보고·계약·의사결정 문서
│  ├─ URP4-1_PROFESSOR_PROJECT_ROADMAP_20260629.md — 09_LIMITATIONS_AND_RESUME 폴더의 설명·보고·계약·의사결정 문서
│  └─ URP4-1_ROADMAP.md — 09_LIMITATIONS_AND_RESUME 폴더의 설명·보고·계약·의사결정 문서
├─ 10_MANIFEST_SHA256_AND_QA/ — 파일 SHA-256, package manifest, 독립 QA와 과거 packaging 시도
│  ├─ attempts/ — 과거 packaging 실패·대체 시도 보존 폴더; 현재 canonical 아님
│  │  └─ INDEPENDENT_CONTENT_QA_ATTEMPT_001_FAIL.json — 과거 실패·대체·격리 이력(현재 canonical 아님): attempts 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  ├─ MASTER_LEDGER_PREVIEWS/ — MASTER_LEDGER_PREVIEWS 관련 코드·입력·결과·검증 자료
│  │  ├─ 00_README_after.png — MASTER_LEDGER_PREVIEWS 작업의 slice·overlay·진단·결과 시각 자료
│  │  ├─ 00_README_v1_2.png — MASTER_LEDGER_PREVIEWS 작업의 slice·overlay·진단·결과 시각 자료
│  │  ├─ 02_TRACK_STATUS_after.png — MASTER_LEDGER_PREVIEWS 작업의 slice·overlay·진단·결과 시각 자료
│  │  ├─ 02_TRACK_STATUS_v1_2.png — MASTER_LEDGER_PREVIEWS 작업의 slice·overlay·진단·결과 시각 자료
│  │  ├─ 11_REQUIREMENTS_after.png — MASTER_LEDGER_PREVIEWS 작업의 slice·overlay·진단·결과 시각 자료
│  │  └─ 11_REQUIREMENTS_v1_2.png — MASTER_LEDGER_PREVIEWS 작업의 slice·overlay·진단·결과 시각 자료
│  ├─ CLAIM_AND_LIMITATION_LEDGER.csv — 10_MANIFEST_SHA256_AND_QA 폴더의 계산값·registry·manifest·QA 표
│  ├─ DRIVE_DELIVERY_CONTRACT.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ INCLUDED_EXCLUDED_FILE_MANIFEST.csv — 10_MANIFEST_SHA256_AND_QA 입력·출력·경로·SHA-256을 고정한 manifest
│  ├─ INDEPENDENT_CONTENT_QA.json — 10_MANIFEST_SHA256_AND_QA 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  ├─ MANIFEST_SCOPE_AND_REVISION_MAP.csv — 10_MANIFEST_SHA256_AND_QA 입력·출력·경로·SHA-256을 고정한 manifest
│  ├─ MASTER_LEDGER_VISUAL_AND_FORMULA_QA.json — 10_MANIFEST_SHA256_AND_QA 결과의 독립 재검사·무결성·계약 통과 여부를 기록한 QA 파일
│  ├─ PACKAGE_CONTENT_SHA256.csv — 패키지 파일별 SHA-256과 byte 수를 기록한 무결성 목록
│  ├─ PACKAGE_MEMBER_MANIFEST.csv — 최종 ZIP member별 상대경로·크기·SHA-256 manifest
│  ├─ PACKAGE_REVISION_v1_1_r2.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ PACKAGE_REVISION_v1_2_r1.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ PACKAGE_REVISION_v1_3_R1.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ PACKAGE_REVISION_v1_3_R2.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ PACKAGE_REVISION_v1_3_R3.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ PACKAGE_REVISION_v1_4_R1.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ PACKAGE_REVISION_v1_4_R2.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ PROTECTED_ASSET_SNAPSHOT.csv — 10_MANIFEST_SHA256_AND_QA 폴더의 계산값·registry·manifest·QA 표
│  ├─ R2_PREREGISTRATION.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ R2_REPAIR_SCOPE.csv — 10_MANIFEST_SHA256_AND_QA 폴더의 계산값·registry·manifest·QA 표
│  ├─ REPRODUCTION_AND_RESUME_GUIDE.md — 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  ├─ SUBMISSION_REQUIREMENTS_CHECKLIST.csv — 10_MANIFEST_SHA256_AND_QA 폴더의 계산값·registry·manifest·QA 표
│  ├─ SUPERSEDED_OR_QUARANTINED_ATTEMPTS.md — 과거 실패·대체·격리 이력(현재 canonical 아님): 10_MANIFEST_SHA256_AND_QA 폴더의 설명·보고·계약·의사결정 문서
│  └─ verify_package_read_only.py — 10_MANIFEST_SHA256_AND_QA 폴더의 Python 실행·계산·검증 스크립트
└─ SOURCE_CUTOFF_SNAPSHOT/ — 과거 cutoff 상태 보존본; 현재 상태 authority가 아님
   ├─ CLAIM_AND_LIMITATION_LEDGER.csv — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 계산값·registry·manifest·QA 표
   ├─ CONTEXT_AND_DECISION_LINEAGE.md — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 설명·보고·계약·의사결정 문서
   ├─ CONTEXT_LINEAGE_REGISTER.csv — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 계산값·registry·manifest·QA 표
   ├─ EVIDENCE_INDEX.csv — 과거 cutoff 보존본(현재 상태 아님): 작업 결론을 실제 근거 파일·SHA-256과 연결한 인덱스
   ├─ FILE_ALIAS_AND_PATH_INDEX.csv — 과거 cutoff 보존본(현재 상태 아님): HQ·Notebook·원본 파일의 alias와 실제 원본 경로·SHA 연결표
   ├─ FINAL_SUBMISSION_REPORT.md — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 작업의 목적·실행 결과·해석 경계를 기록한 보고서
   ├─ HQ_CELL_IMPLEMENTATION_MAP.csv — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 계산값·registry·manifest·QA 표
   ├─ HQ_NOTEBOOK_CELL_TREE.csv — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 계산값·registry·manifest·QA 표
   ├─ MERGE_PACKET.md — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 작업의 QA·채택 범위·남은 제한을 요약한 merge packet
   ├─ OPEN_GATES.csv — 과거 cutoff 보존본(현재 상태 아님): 현재 미완료·차단·다음 통과 조건 목록
   ├─ OPEN_ISSUES_AND_NEXT_GATES.md — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 설명·보고·계약·의사결정 문서
   ├─ PROJECT_SCHEMA.json — 과거 cutoff 보존본(현재 상태 아님): 현재 프로젝트 상태를 기계가 읽는 single source of status truth
   ├─ PYTHON_MODULE_AUDIT.csv — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 계산값·registry·manifest·QA 표
   ├─ RECONCILIATION_DISCREPANCIES.csv — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 계산값·registry·manifest·QA 표
   ├─ REPRODUCTION_AND_RESUME_GUIDE.md — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 설명·보고·계약·의사결정 문서
   ├─ SUBMISSION_REQUIREMENTS_CHECKLIST.csv — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 계산값·registry·manifest·QA 표
   ├─ URP4_1_HQ_21CELL_RAW_FLOW.svg — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 벡터 다이어그램·도식
   ├─ URP4_1_HQ_PROJECT_MAP.html — 과거 cutoff 보존본(현재 상태 아님): 브라우저에서 보는 전체 파이프라인·상태·근거 연결 지도
   ├─ URP4_1_HQ_PROJECT_MAP.md — 과거 cutoff 보존본(현재 상태 아님): 전체 파이프라인·상태·근거 연결 지도의 Markdown 버전
   ├─ URP4_1_HQ_PROJECT_MAP.svg — 과거 cutoff 보존본(현재 상태 아님): SOURCE_CUTOFF_SNAPSHOT 폴더의 벡터 다이어그램·도식
   ├─ URP4_1_MASTER_HANDOFF_LEDGER.xlsx — 과거 cutoff 보존본(현재 상태 아님): 박사님과 후속 담당자가 필터·검색하는 프로젝트 종합 원장
   └─ WORK_PACKAGE_LEDGER.csv — 과거 cutoff 보존본(현재 상태 아님): 작업별 실행·과학·Notebook 통합·release 상태 원장
```
