# URP4-1 교수님 전달본 v1.2-r1

## 먼저 열 파일

`URP4-1_PROFESSOR_HANDOFF_20260802_v1_2_r1.zip`

- Cutoff: `HANDOFF-CUTOFF-20260802-001`
- Schema: `PROJECT_SCHEMA v1.2`
- SHA-256: `d74597ca9361e5b528afda7b0d050a71e03cbec86d80b585b8feb2991e30a045`
- ZIP 내부 첫 문서: `URP4/00_READ_ME_FIRST/README_FIRST.md`

## 이번 revision에서 추가된 내용

- B/C/L exact x-y join 137개와 grouped OOF 8,768개.
- Voronoi exact x-y join 30개와 grouped OOF 1,920개.
- intake QA 15/15 PASS.
- 두 pilot의 QA-v2 각각 10/10 PASS_WITH_WARNINGS.
- 실제 실행 Python/Node 코드, 공통 의존 코드, frozen config, factory status, exact-join dataset, 실행·QA 방법.

## 별도 원본 데이터

2026-08-02 압축 원본 Excel 11개는 ZIP에 중복하지 않고 아래 폴더에 보존했습니다.

https://drive.google.com/drive/folders/1XR1xMdQC9ePp_aWe-wsZB-kfYuGJRcmg

폴더의 `SOURCE_MANIFEST.csv`로 파일명·크기·SHA-256을 확인합니다. 공유는 자동 공개하지 않았으므로 Chuck이 교수님 계정에 Viewer 권한을 부여해야 합니다.

## 주장 경계

이것은 재현 가능한 기술 인수인계본입니다. B/C/L·Voronoi 결과는 초기 기술 선별이며 최적 feature/model, production prediction, 성능 최적 구조 또는 검증된 역설계 성공을 의미하지 않습니다.
