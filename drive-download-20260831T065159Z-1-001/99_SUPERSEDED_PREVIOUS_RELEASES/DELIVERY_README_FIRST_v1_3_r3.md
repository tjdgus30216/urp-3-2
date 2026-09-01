# URP4-1 전달 파일 안내 — ZIP을 받기 전에 먼저 읽어주세요

## 박사님께 실제로 전달할 핵심 파일

```text
URP4-1_FINAL_HANDOFF_20260801/             ← Google Drive 전달 폴더
├─ DELIVERY_README_FIRST_v1_3_r3.md        ← 지금 읽는 파일
├─ URP4-1_PROFESSOR_HANDOFF_20260802_v1_3_r3.zip
│  └─ 프로젝트 코드·설명·결과·검증 근거가 들어 있는 실제 제출물
├─ URP4-1_PROFESSOR_HANDOFF_20260802_v1_3_r3.zip.sha256
│  └─ ZIP이 손상되지 않았는지 확인하는 SHA-256 영수증
├─ URP4-1_GEOMETRY_REFERENCE_20260701_67FILES.zip
│  └─ 별도 보존한 전체 geometry 원본 67개(STL 34 + STP 33)
└─ COMPRESSION_SOURCE_20260802_11FILES/
   └─ 별도 보존한 압축시험 원본 Excel 11개
```

**처음에는 `v1_3_r3.zip` 하나만 내려받으면 됩니다.**  
geometry와 압축시험 원본은 대용량 원자료가 필요한 경우에만 추가로 받습니다.

## Google Drive 링크

- 전체 전달 폴더: <https://drive.google.com/drive/folders/1ofJz1N5ycdijVTuNtpeGn0xben08WWV0>
- 최종 ZIP: <https://drive.google.com/file/d/1WD1XOGKNWTNmRj6eUEN-bApx2s7GXmWN/view?usp=drivesdk>
- ZIP SHA-256: <https://drive.google.com/file/d/18NZZgAvdVMj3PYlIqO28d9U0rq0qslB3/view?usp=drivesdk>
- geometry 원본 67개: <https://drive.google.com/file/d/19yIGDRtUWQPRmaV3WyQvBa5S-QZgxpYh/view?usp=drivesdk>
- 압축시험 원본 11개 폴더: <https://drive.google.com/drive/folders/1XR1xMdQC9ePp_aWe-wsZB-kfYuGJRcmg>

현재 Drive 표시상 파일은 `not_shared`입니다. 박사님에게 보내기 전에 전체 전달 폴더 또는 필요한 파일에 Viewer 권한을 부여해야 합니다.

## ZIP을 풀고 처음 열 파일

```text
URP4/
├─ 00_READ_ME_FIRST/README_FIRST.md
│  └─ 한글 전체 안내와 파일 찾는 법
├─ 01_PROJECT_MAP_AND_LEDGER/URP4_1_HQ_PROJECT_MAP.html
│  └─ 전체 파이프라인과 현재 상태를 보는 HTML 지도
└─ 02_VERIFIED_CORE_HQ_NB_PY/00_RUNNABLE_HQ_AND_ENGINE/URP4_1_HQ.ipynb
   └─ 메인 실행 Notebook(HQ)
```

## 이 ZIP에 들어 있는 것

- 수정·구축한 HQ, `.py`, Import, slicing, 구조인자, Training·압축 데이터 파이프라인
- LEGACY-PY, NB-ORIG, NB-CURRENT, NB-DEV와 박사님 원본 Training/Generator의 read-only 사본
- C1 direct STEP, XREG-v2.7, Training, AI Lattice, B/C/L·Voronoi 대표 결과와 QA
- 후속 담당자가 계산을 재개할 수 있는 config, runtime lock, manifest, SHA와 runbook

## 현재 검증 범위

- C1: 801/801 slices, 800/800 overlays, LEGACY-PY 구조인자 40개, 독립 QA 9/9 PASS
- Training: 원본 9개 audit 완료, replay 1/9, numerical parity는 native crash로 차단 상태
- AI Lattice: exact x-y join 149개, 기술 파일럿 완료
- B/C/L·Voronoi: exact x-y join 167개, 기술 파일럿과 QA 완료

다만 최적 feature·최적 model·전체 imported STL·전체 역설계는 아직 과학적으로 확정되지 않았습니다.

## 파일 식별값

- 파일명: `URP4-1_PROFESSOR_HANDOFF_20260802_v1_3_r3.zip`
- Cutoff: `HANDOFF-CUTOFF-20260802-002`
- Schema: `PROJECT_SCHEMA v1.3`
- SHA-256: `153f1ece4de7ffb6926bafdbe7f83084992dc4a5a983a41519d2017a319ebdbe`
- 크기: `108,286,084 bytes`
- ZIP member: `1,142`

이 r3는 README와 전달 경로를 이해하기 쉽게 고친 packaging revision입니다. 연구 계산과 과학 결론은 r2에서 변경하지 않았습니다.
