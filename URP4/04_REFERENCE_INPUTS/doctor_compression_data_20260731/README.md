# Doctor compression data intake — 2026-07-31

status: raw_read_only
project: URP4-1
purpose: compression-first data intake

이 폴더는 2026-07-31 박사님에게 전달받은 Excel 원본의 프로젝트 보존 복사본이다.

## 폴더 구성

- `01_structural_factors/`
  - 320개 모델의 통합 구조인자 결과.
- `02_reference_strut_sources/`
  - 구조인자 계산의 참고 원료인 30 mm strut 시작점·끝점·반지름 표.
  - AI Lattice 150개, B/C/L 140개, Voronoi 30개.
- `03_ai_lattice_summaries/`
  - AI Lattice 1–150을 50개씩 나눈 신규 summary 파일.
  - `Raw data` 시트의 compression-y 149개 행을 확인했다.
  - AI092는 구조인자 행은 있으나 유효한 성능 행이 없어 명시적으로 결측 처리한다.
- `04_bcl_summaries_pending/`
  - B/C/L 압축 summary 원본 입고 대기 폴더.
- `05_voronoi_summaries_pending/`
  - Voronoi 압축 summary 원본 입고 대기 폴더.

## 보존 규칙

1. 파일명과 파일 바이트를 변경하지 않는다.
2. 계산·정규화·병합 결과는 `data/processed` 또는 versioned result 폴더에 별도로 만든다.
3. 원본 출처, 복사본 경로, 크기와 SHA-256은 `FILE_MANIFEST.csv`를 기준으로 확인한다.
4. 이 폴더의 파일은 NB-CURRENT, NB-ORIG, LEGACY-PY 또는 기존 공식 Excel을 대체하지 않는다.
5. 압축 성능 y 여부와 model-ID crosswalk는 별도 감사 후 확정한다.

## 현재 intake 상태

- AI Lattice: 원본 감사·정규화·x-y exact join·독립 QA 완료.
- B/C/L: summary 원본 입고 대기.
- Voronoi: summary 원본 입고 대기.
- 학습과 feature selection: 별도 사전등록 전까지 실행 금지.
