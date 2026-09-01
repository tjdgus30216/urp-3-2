# Chuck Input Packet — generated Lattice/TPMS topology policy

## Why AI is blocked

The frozen generated sources are non-clean, but code cannot decide whether the laboratory considers that source valid, whether it should be regenerated, or whether a topology-changing repair is acceptable.

## Ask the doctor

> Lattice A와 TPMS Gyroid generated STL의 mesh topology를 read-only로 확인했는데, Lattice는 non-manifold edge 6,798개/연결 성분 8,392개, TPMS는 non-manifold edge 103개와 orientation conflict 73개가 있습니다. 기존 native slicer는 실행되지만, 새 40 mm N40 개발 경로에는 자동으로 넣지 않고 있습니다. 각 family에 대해 다음 중 어떤 방향이 맞을까요? ① generator에서 clean STL로 재생성, ② 원본 보존 후 검증된 mesh repair derivative 사용, ③ 이번 milestone에서 제외. 원래 파일을 그대로 exception으로 허용하는 것은 권장하지 않습니다.

## Required answer format

```text
Lattice A: regenerate / repair / exclude
TPMS Gyroid: regenerate / repair / exclude
If repair: permitted tool or method, if known
40 mm meaning: analysis coordinate only / physical geometry requirement / other
```

## Completion criterion

The two family-specific choices are recorded. AI will then build only the matching isolated, hash-bound validation task.
