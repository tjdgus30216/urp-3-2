# 30K / 96 Profile 변경사항

1. 기본 workspace 경로를 `C:\Users\Administrator\Desktop\Minkyeom\AI-Voxel\Voxel generation`으로 변경.
2. 새 run은 `Result_YYYYMMDD_HHMMSS`로 자동 생성.
3. `N_CANDIDATE_STRUCTURES=30_000`, `N_LHS_SELECTED_STRUCTURES=96` 추가. 기존 `N_RANDOM_STRUCTURES`, `N_FINAL_SAMPLES`는 호환 alias.
4. 모든 workflow 출력 폴더를 Result 폴더 내부로 재배치.
5. 30k generation용 item checkpoint + aggregate log 25-item flush 적용.
6. 30k candidate parameter 전체는 CSV/Parquet 저장, Excel은 기본 5,000행 preview. `EXPORT_FULL_CANDIDATE_XLSX=True`로 full XLSX 선택 가능.
7. Descriptor-LHS preprocessing을 float32 column-wise scaling + randomized PCA로 변경. 30k x 수천 descriptor에서 full SVD 대비 메모리/속도 개선.
8. Descriptor selection model 저장 시 같은 대형 descriptor matrix를 즉시 재계산하지 않도록 cache-aware 저장 적용.
9. Validation notebook은 project contract의 최신 Result snapshot을 자동 사용.
10. Runtime/descriptor engine은 Bundle의 source `.py`를 Result 폴더에 복사해서 durable restart를 유지.
