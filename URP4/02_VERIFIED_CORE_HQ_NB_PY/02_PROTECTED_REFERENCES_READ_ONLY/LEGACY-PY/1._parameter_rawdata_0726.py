import os
import re
import cv2
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from multiprocessing import Manager, cpu_count
from operator import itemgetter

def get_slice_list(path):
    file_names = os.listdir(path)
    slice_png_list = []
    
    for file_name in file_names:
        match = re.match(r'^slice_(\d+)', file_name)
        if match:
            slice_png_list.append(os.path.join(path, file_name))

    slice_png_list.sort(key=lambda x: int(re.match(r'^slice_(\d+)', os.path.basename(x)).group(1)))
    for list_item in slice_png_list: # 'list'는 파이썬 내장 함수 이름이므로 'list_item'으로 변경
        list_item = list_item.replace('\\','/')

    return slice_png_list

# append_area_list 함수는 현재 코드에서 직접 호출되지 않으며,
# 전역 변수 'path'와 'slicearea'를 사용하므로 이 함수가 호출되는 위치와 맥락을
# 명확히 하는 것이 좋습니다. 현재 상태로는 오류 가능성이 있습니다.
# 이 코드에서는 호출되지 않으므로 그대로 두겠습니다.
def append_area_list(area_list) :
    if path.endswith('-x') or path.endswith('_x') or path.endswith('-z') or path.endswith('_z') :
        area_list.append([str(slicearea[0])+' mm^2', " ", " ", " "," "])
    if path.endswith('-xy') or path.endswith('_xy') : 
        area_list.append([str(slicearea[1])+' mm^2', " ", " ", " "," "])            
    if path.endswith('-xyz') or path.endswith('_xyz') : 
        area_list.append([str(slicearea[2])+' mm^2', " ", " ", " "," "])

def area_per_pixel_direction(path, slicearea, total_size):
    """
    주어진 경로의 접미사를 기반으로 픽셀당 면적을 계산합니다.
    total_size가 0이거나 경로 접미사가 인식되지 않으면 ValueError를 발생시킵니다.
    """
    if total_size == 0:
        raise ValueError(f"total_size는 0이 될 수 없습니다. 경로: {path}")

    if path.endswith('-x') or path.endswith('_x') or path.endswith('-z') or path.endswith('_z') :
        return slicearea[0]/total_size
    elif path.endswith('-xy') or path.endswith('_xy') : 
        return slicearea[1]/total_size
    elif path.endswith('-xyz') or path.endswith('_xyz') : 
        return slicearea[2]/total_size
    else:
        # 어떤 조건에도 해당하지 않는 경우
        raise ValueError(f"면적 계산을 위한 경로 접미사가 인식되지 않습니다: {path}")

def extract_numbers(name):
    return list(map(int, re.findall(r'\d+', name)))

def process_images(i, path_lists, output_folder, slicearea, parent_folder):
    if i + 1 < len(path_lists):
        image1_path = path_lists[i]
        image2_path = path_lists[i + 1]

        image1 = cv2.imread(image1_path)
        image2 = cv2.imread(image2_path)

        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        overlap_mask = cv2.bitwise_and(gray1, gray2)
        image1_only_mask = cv2.bitwise_and(gray1, cv2.bitwise_not(gray2))
        image2_only_mask = cv2.bitwise_and(gray2, cv2.bitwise_not(gray1))

        combined_image = np.zeros_like(image1)
        combined_image[np.where(overlap_mask > 0)] = [255, 0, 255]  # 보라색
        combined_image[np.where(image1_only_mask > 0)] = [0, 0, 255]  # 빨간색
        combined_image[np.where(image2_only_mask > 0)] = [255, 0, 0]  # 파란색

        combine_name = f"combine_image_{i+1}-{i+2}"
        output_path = output_folder + '/' + combine_name + '.png'

        print(output_path)

        cv2.imwrite(output_path, combined_image)

        height, width = combined_image.shape[:2]
        width_height = [width, height]
        total_size = width * height

        isolate_count = []

        isolated_color_result(combined_image, isolate_count)

        red_pixels = np.sum(isolate_count[0][1])
        blue_pixels = np.sum(isolate_count[1][1])
        purple_pixels = np.sum(isolate_count[2][1])
        black_pixels = np.sum(isolate_count[3][1])

        pixel_count = [
            combine_name,
            width_height,
            total_size,
            red_pixels,
            blue_pixels,
            purple_pixels,
            black_pixels,
            isolate_count[0][0],
            isolate_count[0][1],
            isolate_count[1][0],
            isolate_count[1][1],
            isolate_count[2][0],
            isolate_count[2][1],
            isolate_count[3][0],
            isolate_count[3][1]
        ]
        
        # area_per_pixel_direction 호출 시 오류 처리
        try:
            area_per_pixel = area_per_pixel_direction(parent_folder, slicearea, total_size)
        except ValueError as e:
            print(f"Error calculating area_per_pixel for combined images ({parent_folder}): {e}")
            return None, None # 오류 발생 시 None 반환하여 메인 루프에서 처리

        colorarealist = [
            red_pixels * area_per_pixel,
            blue_pixels * area_per_pixel,
            purple_pixels * area_per_pixel,
            black_pixels * area_per_pixel
        ]
        average_area = [0, 0, 0, 0]

        for idx, count_data in enumerate(isolate_count): # 'i' 대신 'idx' 사용 (루프 변수 충돌 방지)
            if count_data[0] != 0:
                average_area[idx] = colorarealist[idx] / count_data[0]

        area_result = [
            combine_name,
            colorarealist[0],
            colorarealist[1],
            colorarealist[2],
            colorarealist[3],
            average_area[0],
            average_area[1],
            average_area[2],
            average_area[3]
        ]

        return pixel_count, area_result
    
# process_wb_image 함수 수정
def process_wb_image(file_path, current_path, slicearea, total_size): # path, slicearea, total_size 인자 추가
    isolate_count = []
    file_name = os.path.basename(file_path)
    img_color = cv2.imread(file_path)
    img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV) # 이미지 hsv 색상으로 변환
    
    color_list = [[0, 0, 255], [0, 0, 0]] # BGR 순서로 기입 (흰색, 검은색)

    for color in color_list:
        img_mask = cv2.inRange(img_hsv, np.array(color), np.array(color))
        cnt, _, stats, _ = cv2.connectedComponentsWithStats(img_mask)

        num = 0
        arealist = []
        for s in range(1, cnt):
            (_, _, _, _, area) = stats[s]

            if area < 2:  # 영역의 넓이가 2보다 작을 시에는 카운트 하지 않음
                continue

            num += 1
            arealist.append(area)

        isolate_count.append([num, arealist])
    
    WB_count = [file_name,
                isolate_count[0][0],
                isolate_count[0][1],
                isolate_count[1][0],
                isolate_count[1][1]]
    
    black_pixel = np.sum(isolate_count[1][1])
    white_pixel = np.sum(isolate_count[0][1])

    # 여기서 area_per_pixel_direction에 올바른 인자를 전달
    try:
        area_per_pixel = area_per_pixel_direction(current_path, slicearea, total_size) 
    except ValueError as e:
        print(f"Error calculating area_per_pixel for W&B image ({file_path}): {e}")
        # 오류 발생 시 기본값 또는 오류 처리 로직 (여기서는 0으로 설정)
        area_per_pixel = 0.0 # 에러가 나면 픽셀당 면적을 0으로 처리 (혹은 다른 방법으로 처리)

    colorarealist = [white_pixel * area_per_pixel, black_pixel * area_per_pixel]
    average_area = [0, 0]
    
    for idx, count_data in enumerate(isolate_count): # 'i' 대신 'idx' 사용
        if count_data[0] != 0:
            average_area[idx] = colorarealist[idx] / count_data[0]

    area_list = [file_name,
                 colorarealist[0],
                 colorarealist[1],
                 average_area[0],
                 average_area[1]]

    print(WB_count)
    print(area_list)
    return WB_count, area_list

def colorcombine(path, output_folder, slicearea):
    pixel_counts = []
    areas = []   
    # append_area_list(areas) # 'path'와 'slicearea'가 전역 변수여야 하므로 주석 처리
    
    os.makedirs(output_folder, exist_ok=True)
    path_lists = get_slice_list(path)

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_images, i, path_lists, output_folder, slicearea, path): i for i in range(0, len(path_lists) - 1)}
        for future in as_completed(futures):
            try:
                pixel_count, area_result = future.result()
                if pixel_count is not None and area_result is not None: # None이 아닌 경우에만 추가
                    pixel_counts.append(pixel_count)
                    areas.append(area_result)
            except Exception as e:
                print(f"Error processing images: {e}")
                    
    # Create a dataframe with pixel counts
    sheet_name = os.path.basename(path)
    # pixel_counts와 areas가 비어있을 경우에 대한 처리 추가
    if not pixel_counts:
        print(f"No pixel count data generated for {path}. Skipping sorting.")
        pixel_counts_sorted = []
    else:
        pixel_counts_sorted = sorted(pixel_counts, key=lambda x: list(map(int, re.findall(r'\d+', x[0]))))

    if not areas:
        print(f"No area data generated for {path}. Skipping sorting.")
        areas_sorted = []
    else:
        areas_sorted = sorted(areas, key=lambda x: list(map(int, re.findall(r'\d+', x[0]))))


    result = [sheet_name, pixel_counts_sorted, areas_sorted]

    return result

# isolated 영역 개수 세기 (Combined color에 대하여, red, blue, purple, black, 2픽셀이상 영역부터 카운트)
def isolated_color_result(combined_image, isolate_count):
    img_hsv = cv2.cvtColor(combined_image, cv2.COLOR_BGR2HSV) # 이미지 hsv 색상으로 변환
    # OpenCV HSV 색상 범위: H(0-179), S(0-255), V(0-255)
    # 빨간색 (HSV에서 H값이 0에 가까움, 179에 가까움)
    # 파란색 (H값이 120 근처)
    # 보라색 (H값이 대략 150 근처)
    # 검은색 (V값이 0)
    color_list = [[0, 255, 255], [120, 255, 255], [150, 255, 255], [0,0,0]] 

    for color in color_list :
        # 색상 범위 설정: 특정 HSV 값만 정확히 일치하는 마스크 생성
        # 실제 이미지의 색상은 정확히 한 값으로 떨어지지 않을 수 있으므로,
        # 약간의 범위를 주는 것이 더 강건할 수 있습니다. (예: cv2.inRange(img_hsv, lower_bound, upper_bound))
        # 현재 코드는 단일 값으로 마스크를 만듭니다.
        img_mask = cv2.inRange(img_hsv, np.array(color), np.array(color))

        cnt, _, stats, _ = cv2.connectedComponentsWithStats(img_mask)
        num = 0
        arealist = []
        for s in range(1, cnt):
            (_, _, _, _, area) = stats[s]

            if area < 2:  #영역의 넓이가 2보다 작을 시에는 카운트 하지 않음
                continue

            num += 1
            arealist.append(area)
        
       
        isolate_count.append([num, arealist])

# isolated 영역 개수 세기 (W&B 원본에 대하여, 2픽셀이상 영역부터 카운트)
# WBisolated_color_result 함수 수정
def WBisolated_color_result(path, slicearea, total_size):
    file_list = [os.path.join(path, filename) for filename in os.listdir(path) if filename.endswith('.png')]
    file_list = sorted(file_list, key=lambda x: int(''.join(filter(str.isdigit, os.path.splitext(os.path.basename(x))[0]))))
    WB_counts = []
    area_lists = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        # process_wb_image 함수 호출 시 path, slicearea, total_size 인자 전달
        futures = [executor.submit(process_wb_image, file_path, path, slicearea, total_size) for file_path in file_list]
        
        for future in futures:
            try:
                WB_count, area_list = future.result()
                WB_counts.append(WB_count)
                area_lists.append(area_list)
            except Exception as e:
                print(f"Error processing W&B image: {e}")

    # 데이터가 있을 경우에만 정렬 시도
    if WB_counts:
        WB_counts.sort(key=lambda x: list(map(int, re.findall(r'\d+', x[0]))))
    else:
        print(f"No WB count data generated for {path}. Skipping sorting.")

    if area_lists:
        area_lists.sort(key=lambda x: list(map(int, re.findall(r'\d+', x[0]))))
    else:
        print(f"No WB area data generated for {path}. Skipping sorting.")

    sheet_name = os.path.basename(path) + '_W&B'
    result = [sheet_name, WB_counts, area_lists]
    
    return result


def save_to_excel(data, WB_data, parent_folder):
    column_color_pixel = ['File Name', 'Width Height', 'Total Pixel', 'Red Pixel', 'Blue Pixel', 'Purple Pixel', 'Black Pixel', 
                          'Isolated Count Red', 'Isolated Pixel Red', 'Isolated Count Blue', 'Isolated Pixel Blue', 
                          'Isolated Count Purple', 'Isolated Pixel Purple', 'Isolated Count Black', 'Isolated Pixel Black']
    column_color_area = ['File Name','Total Red Area','Total Blue Area','Total Purple Area','Total Black Area',
                         'Average Red Area','Average Blue Area','Average Purple Area','Average Black Area']
    column_WB_pixel = ['File Name', 'White Isolated Count', 'White Isolated Pixels', 'Black Isolated Count', 'Black Isolated Pixels']
    column_WB_area  = ['File Name', 'Total white area','Total black area','average white area','average black area']

    color = sorted(data, key=itemgetter(0))
    WB = sorted(WB_data, key=itemgetter(0))

    # 데이터가 비어있을 경우 DataFrame 생성 시 오류 방지
    df_x = pd.DataFrame(color[0][1], columns=column_color_pixel) if color and color[0][1] else pd.DataFrame(columns=column_color_pixel)
    df_xy = pd.DataFrame(color[1][1], columns=column_color_pixel) if len(color) > 1 and color[1][1] else pd.DataFrame(columns=column_color_pixel)
    df_xyz = pd.DataFrame(color[2][1], columns=column_color_pixel) if len(color) > 2 and color[2][1] else pd.DataFrame(columns=column_color_pixel)
    df_z = pd.DataFrame(color[3][1], columns=column_color_pixel) if len(color) > 3 and color[3][1] else pd.DataFrame(columns=column_color_pixel)

    df_WB_x = pd.DataFrame(WB[0][1], columns=column_WB_pixel) if WB and WB[0][1] else pd.DataFrame(columns=column_WB_pixel)
    df_WB_xy = pd.DataFrame(WB[1][1], columns=column_WB_pixel) if len(WB) > 1 and WB[1][1] else pd.DataFrame(columns=column_WB_pixel)
    df_WB_xyz = pd.DataFrame(WB[2][1], columns=column_WB_pixel) if len(WB) > 2 and WB[2][1] else pd.DataFrame(columns=column_WB_pixel)
    df_WB_z = pd.DataFrame(WB[3][1], columns=column_WB_pixel) if len(WB) > 3 and WB[3][1] else pd.DataFrame(columns=column_WB_pixel)

    df_area_x = pd.DataFrame(color[0][2], columns=column_color_area) if color and color[0][2] else pd.DataFrame(columns=column_color_area)
    df_area_xy = pd.DataFrame(color[1][2], columns=column_color_area) if len(color) > 1 and color[1][2] else pd.DataFrame(columns=column_color_area)
    df_area_xyz = pd.DataFrame(color[2][2], columns=column_color_area) if len(color) > 2 and color[2][2] else pd.DataFrame(columns=column_color_area)
    df_area_z = pd.DataFrame(color[3][2], columns=column_color_area) if len(color) > 3 and color[3][2] else pd.DataFrame(columns=column_color_area)

    df_area_WB_x = pd.DataFrame(WB[0][2], columns=column_WB_area) if WB and WB[0][2] else pd.DataFrame(columns=column_WB_area)
    df_area_WB_xy = pd.DataFrame(WB[1][2], columns=column_WB_area) if len(WB) > 1 and WB[1][2] else pd.DataFrame(columns=column_WB_area)
    df_area_WB_xyz = pd.DataFrame(WB[2][2], columns=column_WB_area) if len(WB) > 2 and WB[2][2] else pd.DataFrame(columns=column_WB_area)
    df_area_WB_z = pd.DataFrame(WB[3][2], columns=column_WB_area) if len(WB) > 3 and WB[3][2] else pd.DataFrame(columns=column_WB_area)

    excel_rawdata = os.path.join(parent_folder, os.path.basename(parent_folder)+'_rawdata.xlsx')
    excel_area = os.path.join(parent_folder, os.path.basename(parent_folder)+'_area.xlsx')

    with pd.ExcelWriter(excel_rawdata) as writer:
        if not df_x.empty: df_x.to_excel(writer, sheet_name=color[0][0], index=False)
        if not df_xy.empty: df_xy.to_excel(writer, sheet_name=color[1][0], index=False)
        if not df_xyz.empty: df_xyz.to_excel(writer, sheet_name=color[2][0], index=False)
        if not df_z.empty: df_z.to_excel(writer, sheet_name=color[3][0], index=False)

        if not df_WB_x.empty: df_WB_x.to_excel(writer, sheet_name=WB[0][0], index=False)
        if not df_WB_xy.empty: df_WB_xy.to_excel(writer, sheet_name=WB[1][0], index=False)
        if not df_WB_xyz.empty: df_WB_xyz.to_excel(writer, sheet_name=WB[2][0], index=False)
        if not df_WB_z.empty: df_WB_z.to_excel(writer, sheet_name=WB[3][0], index=False)

    with pd.ExcelWriter(excel_area) as writer:
        if not df_area_x.empty: df_area_x.to_excel(writer, sheet_name=color[0][0], index=False)
        if not df_area_xy.empty: df_area_xy.to_excel(writer, sheet_name=color[1][0], index=False)
        if not df_area_xyz.empty: df_area_xyz.to_excel(writer, sheet_name=color[2][0], index=False)
        if not df_area_z.empty: df_area_z.to_excel(writer, sheet_name=color[3][0], index=False)

        if not df_area_WB_x.empty: df_area_WB_x.to_excel(writer, sheet_name=WB[0][0], index=False)
        if not df_area_WB_xy.empty: df_area_WB_xy.to_excel(writer, sheet_name=WB[1][0], index=False)
        if not df_area_WB_xyz.empty: df_area_WB_xyz.to_excel(writer, sheet_name=WB[2][0], index=False)
        if not df_area_WB_z.empty: df_area_WB_z.to_excel(writer, sheet_name=WB[3][0], index=False)

if __name__ == '__main__':
    folder_paths = []
    while True:
        folder = input(r"경로를 입력하세요 (종료하려면 'q' 입력): ")
        if folder.lower() == 'q':
            break
        folder = folder.replace('\\','/')
        folder_paths.append(folder)

    slicearea = [int(input(f"{axis} 방향 슬라이스의 넓이 (e.g. x-1600, xy-3364, xyz-4802): ")) for axis in ['x, z', 'xy', 'xyz']]
    pixel = int(input("가로 방향 픽셀 수 (e.g. 1000): "))
    total_size = pixel * pixel

    # --- 1. 상위폴더 기준 그룹화 ---
    grouped_paths = defaultdict(list)
    for full_path in folder_paths:
        group_key = os.path.dirname(full_path)  # 한 단계 상위 폴더 기준 그룹
        grouped_paths[group_key].append(full_path)

    # --- 2. 그룹별로 계산 후 상위폴더에 엑셀 저장 ---
    for group_folder, subfolder_list in grouped_paths.items():
        try:
            data = []
            WB_data = []
            print(f"\n📁 그룹 처리: {group_folder}")

            for path in subfolder_list:
                path = path.replace('\\','/')
                print(f"  → 처리 대상: {path}")
                output_folder = os.path.join(path, 'colorcombine').replace('\\','/')
                
                color_result = colorcombine(path, output_folder, slicearea)
                if color_result:
                    data.append(color_result)
                else:
                    print(f"    ⚠️ colorcombine 결과 없음: {path}")

                try:
                    wb_result = WBisolated_color_result(path, slicearea, total_size)
                    if wb_result:
                        WB_data.append(wb_result)
                    else:
                        print(f"    ⚠️ WBisolated_color_result 결과 없음: {path}")
                except ValueError as ve:
                    print(f"    ❌ ValueError: {ve} ({path})")
                except Exception as e:
                    print(f"    ❌ 예외 발생: {e} ({path})")

            if data or WB_data:
                # --- 3. 상위폴더에 엑셀 저장 ---
                save_to_excel(data, WB_data, group_folder)
                print(f"  ✅ 저장 완료: {group_folder}")
            else:
                print(f"  ⚠️ 저장할 데이터 없음: {group_folder}")

        except Exception as e:
            print(f"❌ 그룹 처리 중 오류 발생: {group_folder} | {e}")
            input("계속하려면 Enter...")