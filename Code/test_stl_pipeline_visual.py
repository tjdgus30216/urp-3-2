# -*- coding: utf-8 -*-
"""
STL 파이프라인을 실제 파일로 눈으로 확인하기 위한 테스트 스크립트입니다.
run_stl_batch_descriptor_extraction.py와 동일한 파이프라인을 돌리되, 추가로:
  - 실제 slice 이미지(이진화된 단면) PNG를 저장하고
  - 3-layer A/B/C 중첩(TSPE) 이미지를 저장하고 (grayscale 버전도 함께)
  - 핵심 구조인자 요약을 사람이 읽기 쉬운 형태로 출력/저장합니다.

사용법:
  1) 아래 CONFIG 값을 확인/수정합니다. 기본값은 요청하신 경로로 이미 설정되어 있습니다.
  2) 이 파일을 descriptor_library.py, Architected_Material_Descriptor_Exhaustive_v3.ipynb와
     같은 폴더에 둔 채로 실행합니다:  python test_stl_pipeline_visual.py
  3) 처음 실행할 때는 MAX_FILES를 1~2로 낮춰서 먼저 빠르게 확인해보시는 걸 권장합니다
     (exhaustive 모드는 파일 하나당 몇 분 정도 걸릴 수 있습니다).
  4) 결과는 OUTPUT_BASE_DIR\\Test_YYYYMMDD_HHMMSS\\<원본파일이름>\\ 아래:
       images/raw_slices/       -- 실제 이진화된 slice PNG (이번에 새로 추가된 시각 출력)
       images/triplets/         -- hard-TSPE A/B/C 중첩 이미지 (A=255,B=170,C=85 grayscale)
       images/soft_triplets/    -- grayscale 기반 soft-TSPE A/B/C RGB 합성 이미지
       reconstructed_from_slices.stl -- 슬라이싱 결과를 역으로 mesh 재구성한 STL (형상 sanity check용)
       features/descriptors_ALL.csv  -- 전체 구조인자
       summary.txt / summary.json    -- 핵심 구조인자 + 슬라이싱 QA(odd-row 등) 요약
     로 저장됩니다.

필요 패키지: requirements.txt 참고 (trimesh 필수, STEP을 쓰신다면 cadquery도 필요).
"""
from __future__ import annotations
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# ============================== CONFIG ==============================
STL_INPUT_DIR = r"C:\Users\김민겸\Desktop\Metal metamaterial\Descriptor extraction\STL file"
OUTPUT_BASE_DIR = r"C:\Users\김민겸\Desktop\Metal metamaterial\Descriptor extraction"
OUTPUT_PREFIX = "Test"

VOXEL_SIZE_MM = 0.20
TRIPLET_IMAGE_STRIDE = 1      # Test 폴더는 시각 확인용이므로 기본적으로 매 slice 이미지를 저장합니다.
RAW_SLICE_IMAGE_STRIDE = 1
MAX_RAW_SLICE_IMAGES = 300    # slice 수가 매우 많은 mesh에서 이미지가 과도하게 쌓이지 않도록 상한.
MAX_FILES = None              # 정수로 설정하면 처음 N개 파일만 처리(빠른 스모크 테스트용). None=전체.
# ======================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import trimesh  # noqa: F401
except ImportError:
    print("!!! 'trimesh' 패키지가 설치되어 있지 않습니다. STL/mesh 를 불러오려면 필요합니다.")
    print("    설치: pip install trimesh")
    print("    STEP(.stp/.step) 파일도 쓰신다면 추가로: pip install cadquery")
    raise SystemExit(1)

import stl_pipeline_driver as drv


def print_and_save_summary(workdir: Path, filename: str):
    summary = drv.summarize_key_descriptors(workdir)
    print(f"   핵심 구조인자 요약 ({filename}):")
    if not summary:
        print("     (descriptors_ALL.csv를 찾지 못했습니다 -- 위 에러 로그를 확인하세요)")
        return
    for k, v in summary.items():
        print(f"     {k}: {v}")
    (workdir / 'summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding='utf-8'
    )
    lines = [f"{k}: {v}" for k, v in summary.items()]
    (workdir / 'summary.txt').write_text('\n'.join(lines), encoding='utf-8')


def main():
    input_dir = Path(STL_INPUT_DIR)
    if not input_dir.is_dir():
        raise SystemExit(f"STL 입력 폴더를 찾을 수 없습니다: {input_dir}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(OUTPUT_BASE_DIR) / f"{OUTPUT_PREFIX}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"테스트 결과 저장 폴더: {output_dir}")

    nb_path = drv.find_notebook_path(SCRIPT_DIR)
    cells = drv.load_notebook_cells(nb_path)
    print(f"노트북 로드: {nb_path.name} ({len(cells)} cells)")

    files = drv.discover_input_files(input_dir)
    if not files:
        raise SystemExit(f"{input_dir} 안에 STL/STEP/OBJ/PLY 파일이 없습니다.")
    if MAX_FILES is not None:
        files = files[:MAX_FILES]
    print(f"처리할 파일 {len(files)}개: " + ", ".join(f.name for f in files))

    results = []
    for i, f in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {f.name} 처리 중 ...")
        workdir = output_dir / f.stem
        ok, elapsed, err = drv.run_pipeline_for_one_input(
            cells, f, workdir,
            config_overrides={
                'VOXEL_SIZE_MM': VOXEL_SIZE_MM,
                'TRIPLET_IMAGE_STRIDE': TRIPLET_IMAGE_STRIDE,
                'SAVE_TRIPLET_IMAGES': True,
            },
        )
        status = 'OK' if ok else 'FAILED'
        print(f"   -> {status}  ({elapsed:.1f}s)")
        results.append({'file': f.name, 'status': status, 'elapsed_sec': round(elapsed, 1),
                         'error': (err or '').splitlines()[-1] if err else '', 'workdir': str(workdir)})

        if ok:
            n_slices = drv.save_raw_slice_images(workdir, stride=RAW_SLICE_IMAGE_STRIDE,
                                                  max_slices=MAX_RAW_SLICE_IMAGES)
            print(f"   raw slice 이미지 {n_slices}장 저장: {workdir / 'images' / 'raw_slices'}")
            print(f"   TSPE A/B/C 중첩 이미지: {workdir / 'images' / 'triplets'}")
            print(f"   soft-TSPE(grayscale) 중첩 이미지: {workdir / 'images' / 'soft_triplets'}")
            print_and_save_summary(workdir, f.name)
        else:
            print(f"   에러 로그: {workdir / 'logs' / 'error.txt'}")

    import pandas as pd
    log_path = output_dir / 'test_run_log.csv'
    pd.DataFrame(results).to_csv(log_path, index=False)
    n_ok = sum(1 for r in results if r['status'] == 'OK')
    print(f"\n완료: {n_ok}/{len(files)} 성공. 실행 로그: {log_path}")
    print(f"각 파일의 images/raw_slices, images/triplets, images/soft_triplets, "
          f"summary.txt를 열어 결과를 확인하세요.")


if __name__ == '__main__':
    main()
