# URP4-1 박사님 제출·인수인계 — final submission report v1.4-r2

- Cutoff: `HANDOFF-CUTOFF-20260802-002`
- Schema: `PROJECT_SCHEMA v1.3`
- Package revision: `v1.4-r2`
- Active run: none
- Packaging action: algorithm/resume curation only; no research calculation rerun

## 박사님 요구사항 대응

- 수정·구축 알고리즘: HQ/engine, Direct STEP C1, imported-STL/route validation, XREG, resolution, Training adapter, compression pilot source를 포함했다.
- 간단한 파일 설명: `ALGORITHM_AND_RESULT_GUIDE_KO.txt`, `ALGORITHM_PIPELINE_INDEX.csv`, `ALGORITHM_FILE_INDEX.csv`에 기능·입출력·상태·경로를 기록했다.
- 전수 파일 설명: `README_ALL_FILES_TREE_AND_DESCRIPTION_KO.md`와 `ALL_FILES_DESCRIPTION_INDEX_KO.csv`에 ZIP 내부 모든 파일의 상대경로·한국어 설명을 기록했고 `ALL_FILES_DESCRIPTION_QA.json`으로 누락·중복을 검사했다.
- 활용 결과 데이터: C1, XREG-v2.7, Training, AI Lattice, B/C/L, Voronoi의 대표 결과·QA를 포함했다.
- 재개성: `03_RESUMABLE_PROJECT_SNAPSHOT`에 원래 프로젝트 상대경로, 최소 geometry, frozen raw table, accepted evidence와 read-only verifier를 보존했다.

## Bounded current results

- C1 direct STEP: 801/801 slices, 800/800 overlays, 40 scalar x, independent QA 9/9.
- Training: 9/9 source audit, 1/9 replay, exact numerical parity blocked by native source runtime crash.
- AI Lattice: 149 exact joins and technical four-method pilot; no feature/model promotion.
- B/C/L: 137 exact joins, 8,768 grouped OOF predictions, QA-v2 10/10 PASS_WITH_WARNINGS.
- Voronoi: 30 exact joins, 1,920 grouped OOF predictions, QA-v2 10/10 PASS_WITH_WARNINGS.
- XREG-v2.7: 542 no-y candidates, all unselected.

## Deliberately excluded

- cache, pyc, checkpoint, superseded/failed bulk outputs, transient full PNG streams.
- full 67-file geometry archive and large protected compression workbooks are delivered separately by Drive link/SHA instead of being duplicated.

## Claim boundary

This is a reproducible technical research handoff. It is not universal geometry qualification, successful Training numerical parity, a validated best feature/model, or validated y-based inverse design.

## Terminology correction

- 새 제출 파일명과 현재 설명은 `박사님/DOCTOR`를 사용한다.
- 과거 인덱스·원본 경로의 `professor_*`, `PROFESSOR_GENERATORS`, `PROFESSOR_TRAINING`은 추적성을 위해 유지한 역사적 alias이며 실제 제공자·수신자는 박사님이다.
- v1.4-r2는 문해력·전수 파일 설명과 QA 버전 표기를 보완한 packaging revision이며 새 연구 계산을 수행하지 않았다.
