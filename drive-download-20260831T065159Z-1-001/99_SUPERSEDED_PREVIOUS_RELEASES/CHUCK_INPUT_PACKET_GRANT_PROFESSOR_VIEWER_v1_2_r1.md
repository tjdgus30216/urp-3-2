# Chuck Input Packet — 교수님 Viewer 권한 부여

## 왜 필요한가

Drive 업로드와 원격 파일 존재·크기 검증은 완료됐지만, 현재 전달 폴더와 파일은 `not_shared`입니다. 보안상 자동 공개하지 않았습니다.

## Chuck이 할 일

1. 아래 전달 root를 엽니다.
   - https://drive.google.com/drive/folders/1ofJz1N5ycdijVTuNtpeGn0xben08WWV0
2. 교수님 Google 계정 이메일에 **Viewer** 권한을 줍니다.
3. 하위 `COMPRESSION_SOURCE_20260802_11FILES` 폴더도 권한이 상속되는지 확인합니다.
4. 교수님께는 우선 아래 ZIP 링크 하나와 `DELIVERY_README_FIRST_v1_2_r1.md`를 보냅니다.
   - https://drive.google.com/file/d/12In-zPZjqJ-KLCop4NfN2gJHB-EpkQ21/view?usp=drivesdk

## 완료 기준

- 교수님 계정에서 ZIP을 다운로드할 수 있음.
- 압축 원본 Excel 폴더를 열 수 있음.
- 링크를 웹 공개로 전환하지 않고 지정 계정 Viewer로 전달함.
