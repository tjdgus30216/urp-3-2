# -*- coding: utf-8 -*-
"""
STL(/STEP/OBJ/PLY) 폴더를 일괄로 읽어 전체 exhaustive descriptor 파이프라인을 돌리고,
결과를 Result_<날짜_시간> 폴더에 저장합니다.

사용법:
  1) 아래 CONFIG 값(특히 STL_INPUT_DIR, OUTPUT_BASE_DIR)을 확인/수정합니다.
     기본값은 요청하신 경로로 이미 설정되어 있습니다.
  2) 이 파일을 descriptor_library.py, Architected_Material_Descriptor_Exhaustive_v3.ipynb와
     같은 폴더에 둔 채로 실행합니다:  python run_stl_batch_descriptor_extraction.py
  3) STL_INPUT_DIR 안의 모든 STL/STEP/OBJ/PLY 파일을 이름순으로 하나씩 처리합니다
     (파일 하나가 실패해도 나머지는 계속 진행됩니다).
  4) 결과는 OUTPUT_BASE_DIR\\Result_YYYYMMDD_HHMMSS\\ 아래,
       <원본파일이름>\\   -- 해당 파일의 전체 checkpoint/features/images (노트북과 동일 구조)
       MASTER_descriptors_ALL.csv  -- 모든 파일의 descriptor를 한 행씩 모은 통합 CSV
       batch_run_log.csv           -- 파일별 성공/실패, 처리 시간, 에러 메시지
     로 저장됩니다.

필요 패키지: requirements.txt 참고 (trimesh 필수, STEP을 쓰신다면 cadquery도 필요).
"""
from __future__ import annotations
import sys
import os
from pathlib import Path
from datetime import datetime

# ============================== CONFIG ==============================
STL_INPUT_DIR = r"C:\Users\김민겸\Desktop\Metal metamaterial\Descriptor extraction\STL file"
OUTPUT_BASE_DIR = r"C:\Users\김민겸\Desktop\Metal metamaterial\Descriptor extraction"
OUTPUT_PREFIX = "Result"

VOXEL_SIZE_MM = 0.20          # 구조의 최소 특징 크기(strut 두께 등)보다 3~5배는 작게 설정하세요.
TRIPLET_IMAGE_STRIDE = 5      # A/B/C 중첩 이미지 저장 간격(1=매 slice 저장, 값을 키우면 용량 절약).
                               # 이미지를 조밀하게 보고 싶으면 test_stl_pipeline_visual.py를 사용하세요.
# ======================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)  # .architected_descriptor_active_workdir.txt 포인터 파일 등이 여기 기준으로 쓰입니다.
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import trimesh  # noqa: F401
except ImportError:
    print("!!! 'trimesh' 패키지가 설치되어 있지 않습니다. STL/mesh 를 불러오려면 필요합니다.")
    print("    설치: pip install trimesh")
    print("    STEP(.stp/.step) 파일도 쓰신다면 추가로: pip install cadquery")
    raise SystemExit(1)

import stl_pipeline_driver as drv


def main():
    input_dir = Path(STL_INPUT_DIR)
    if not input_dir.is_dir():
        raise SystemExit(f"STL 입력 폴더를 찾을 수 없습니다: {input_dir}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(OUTPUT_BASE_DIR) / f"{OUTPUT_PREFIX}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"결과 저장 폴더: {output_dir}")

    nb_path = drv.find_notebook_path(SCRIPT_DIR)
    cells = drv.load_notebook_cells(nb_path)
    print(f"노트북 로드: {nb_path.name} ({len(cells)} cells)")

    files = drv.discover_input_files(input_dir)
    if not files:
        raise SystemExit(f"{input_dir} 안에 STL/STEP/OBJ/PLY 파일이 없습니다.")
    print(f"입력 파일 {len(files)}개 발견: " + ", ".join(f.name for f in files[:10]) +
          (" ..." if len(files) > 10 else ""))

    results = []
    for i, f in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {f.name} 처리 중 ...")
        workdir = output_dir / f.stem
        ok, elapsed, err = drv.run_pipeline_for_one_input(
            cells, f, workdir,
            config_overrides={
                'VOXEL_SIZE_MM': VOXEL_SIZE_MM,
                'TRIPLET_IMAGE_STRIDE': TRIPLET_IMAGE_STRIDE,
            },
        )
        status = 'OK' if ok else 'FAILED'
        print(f"   -> {status}  ({elapsed:.1f}s)")
        results.append({
            'file': f.name, 'status': status, 'elapsed_sec': round(elapsed, 1),
            'error': (err or '').splitlines()[-1] if err else '',
            'workdir': str(workdir),
        })

    import pandas as pd
    frames = []
    for r in results:
        p = Path(r['workdir']) / 'features' / 'descriptors_ALL.csv'
        if p.exists():
            df = pd.read_csv(p)
            df.insert(0, 'source_file', r['file'])
            frames.append(df)
    if frames:
        master = pd.concat(frames, ignore_index=True, sort=False)
        master_path = output_dir / 'MASTER_descriptors_ALL.csv'
        master.to_csv(master_path, index=False)
        print(f"\n통합 결과 저장: {master_path}  (shape={master.shape})")
    else:
        print("\n성공한 파일이 없어 MASTER_descriptors_ALL.csv를 만들지 못했습니다. "
              "batch_run_log.csv와 각 파일의 logs/error.txt를 확인하세요.")

    log_path = output_dir / 'batch_run_log.csv'
    pd.DataFrame(results).to_csv(log_path, index=False)
    n_ok = sum(1 for r in results if r['status'] == 'OK')
    print(f"완료: {n_ok}/{len(files)} 성공. 실행 로그: {log_path}")


if __name__ == '__main__':
    main()
