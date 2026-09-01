import cv2
import numpy as np
import cupy as cp
import os
import pandas as pd
import time
from math import atan, degrees
from collections import defaultdict

def color_divide(img_gray, lower, upper):
    mask = cv2.inRange(img_gray, lower, upper)
    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    labels_cp = cp.asarray(labels)
    area_list, coordinate = [], []
    for i in range(1, cnt):
        (x, y, w, h, area) = stats[i]
        indices = cp.where(labels_cp == i)
        y, x = indices[0][0], indices[1][0]
        coordinate.append([x.item(), y.item()])
        area_list.append(area)
    return coordinate, area_list

def labeling(value_list, coordinates, white_labels, cnt):
    labeled = [[] for _ in range(1, cnt)]
    for val, (x, y) in zip(value_list, coordinates):
        lbl = white_labels[y, x] - 1
        if 0 <= lbl < len(labeled):
            labeled[lbl].append(val)
    return labeled

def sum_array(label_list):
    return np.array([sum(sublist) for sublist in label_list])

def sum_array_edge(label_list):
    return np.array([np.nansum(sublist) if sublist else 100000 for sublist in label_list])

def labeling_perimeter_area(labels, cnt):
    perim_area = [[] for _ in range(1, cnt)]
    for label in range(1, cnt):
        mask = (labels == label).astype(np.uint8)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            area = cv2.countNonZero(mask)
            perimeter = cv2.arcLength(contours[0], True)
            if area > 0:
                perim_area[label - 1].append(perimeter / area)
    return perim_area

def get_contact_edge_length(mask_a, mask_b, length_per_pixel):
    kernel = np.ones((3,3), np.uint8)
    a_dil = cv2.dilate(mask_a, kernel, iterations=1)
    contact = cv2.bitwise_and(a_dil, mask_b)
    return np.count_nonzero(contact) * length_per_pixel

def massorientation_curvature(input_folder, area_per_pixel, height, length_per_pixel):
    mass_IP_list, mass_LIP_list, mass_LTP_list = [], [], []
    curv_IP_list, curv_LIP_list, curv_LTP_list = [], [], []
    angle_IP_list, angle_LIP_list, angle_LTP_list = [], [], []
    pta_IP_list, pta_LIP_list, pta_LTP_list = [], [], []

    file_list = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith('.png')],
                       key=lambda x: int(''.join(filter(str.isdigit, os.path.splitext(os.path.basename(x))[0]))))

    for file in file_list:
        print(file)
        img = cv2.imread(file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        mask_r = cv2.inRange(gray, 76, 76)
        mask_b = cv2.inRange(gray, 29, 29)
        mask_p = cv2.inRange(gray, 105, 105)

        cnt, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.inRange(gray, 29, 105))

        red = []
        blue = []
        purple = []
        arc1 = []
        arc2 = []
        for label in range(1, cnt):
            label_mask = (labels == label).astype(np.uint8) * 255
            label_red = cv2.bitwise_and(mask_r, label_mask)
            label_blue = cv2.bitwise_and(mask_b, label_mask)
            label_purp = cv2.bitwise_and(mask_p, label_mask)
            area_red = cv2.countNonZero(label_red) * area_per_pixel
            area_blue = cv2.countNonZero(label_blue) * area_per_pixel
            area_purp = cv2.countNonZero(label_purp) * area_per_pixel
            red.append(area_red)
            blue.append(area_blue)
            purple.append(area_purp)
            arc1.append(get_contact_edge_length(label_red, label_purp, length_per_pixel))
            arc2.append(get_contact_edge_length(label_blue, label_purp, length_per_pixel))
        red = np.array(red)
        blue = np.array(blue)
        purple = np.array(purple)
        arc1 = np.array(arc1)
        arc2 = np.array(arc2)

        areas = [np.sum(red), np.sum(blue), np.sum(purple)]
        total = 0.5*areas[0] + 0.5*areas[1] + areas[2]
        if total > 0:
            mass_LTP_list.append(areas[2] / total)
        curv_LTP_list.append((areas[0]**0.5 + areas[1]**0.5) / (2 * height))

        perim_area = []
        for label in range(1, cnt):
            label_mask = (labels == label).astype(np.uint8)
            contours, _ = cv2.findContours(label_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            area = cv2.countNonZero(label_mask)
            if contours and area > 0:
                perimeter = cv2.arcLength(contours[0], True)
                perim_area.append(perimeter / area)
        perim_area = np.array(perim_area)

        mass_ori = purple / (0.5 * red + 0.5 * blue + purple + 1e-9)

        # ✅ angle, curvature 개선된 계산
        angle = np.full_like(red, 90.0, dtype=float)
        curvature = np.zeros_like(red, dtype=float)
        for i in range(len(red)):
            if (red[i] == 0) and (blue[i] == 0):
                angle[i] = 90.0
                curvature[i] = 0.0
            else:
                term_red = (red[i] / arc1[i]) if (arc1[i] > 1e-6 and red[i] > 0) else 0.0
                term_blue = (blue[i] / arc2[i]) if (arc2[i] > 1e-6 and blue[i] > 0) else 0.0
                denom = term_red + term_blue
                if denom > 0:
                    angle[i] = np.degrees(np.arctan(height / denom))
                    curvature[i] = (term_red + term_blue) / (2 * height)
                else:
                    angle[i] = 90.0
                    curvature[i] = 0.0

        if mass_ori.size:
            mass_IP_list.extend(mass_ori)
            mass_LIP_list.append(np.mean(mass_ori))
        if curvature.size:
            curv_IP_list.extend(curvature)
            curv_LIP_list.append(np.mean(curvature))
        if angle.size:
            angle_IP_list.extend(angle)
            angle_LIP_list.append(np.mean(angle))
            angle_LTP_list.append(np.mean(angle))
        if perim_area.size:
            pta_IP_list.extend(perim_area)
            pta_LIP_list.append(np.mean(perim_area))
            pta_LTP_list.append(np.mean(perim_area))

    return (
        np.mean(mass_IP_list), np.std(mass_IP_list), np.mean(mass_LIP_list), np.std(mass_LIP_list), np.mean(mass_LTP_list), np.std(mass_LTP_list),
        np.mean(curv_IP_list), np.std(curv_IP_list), np.mean(curv_LIP_list), np.std(curv_LIP_list), np.mean(curv_LTP_list), np.std(curv_LTP_list),
        np.mean(angle_IP_list), np.std(angle_IP_list), np.mean(angle_LIP_list), np.std(angle_LIP_list), np.mean(angle_LTP_list), np.std(angle_LTP_list),
        np.mean(pta_IP_list), np.std(pta_IP_list), np.mean(pta_LIP_list), np.std(pta_LIP_list), np.mean(pta_LTP_list), np.std(pta_LTP_list)
    )

def thickness(path, area_per_pixel):
    file_list = sorted([os.path.join(path, f) for f in os.listdir(path) if f.endswith('.png')],
                       key=lambda x: int(''.join(filter(str.isdigit, os.path.splitext(os.path.basename(x))[0]))))
    IP_thickness, LTP_thickness, LIP_thickness = [], [], []
    for file_path in file_list:
        print(file_path)
        img_color = cv2.imread(file_path)
        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
        lower = (0, 0, 255)
        upper = (0, 0, 255)
        img_mask = cv2.inRange(img_hsv, lower, upper)
        cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(img_mask)
        arealist = []
        for s in range(1, cnt):
            (x, y, w, h, area) = stats[s]
            if area < 2:
                continue
            area = area * area_per_pixel
            arealist.append(area)
            IP_thickness.append(area)
        np_arealist = np.array(arealist)
        if np_arealist.size:
            LIP_thickness.append(np.mean(np_arealist))
        LTP_thickness.append(sum(arealist))
    return np.mean(IP_thickness), np.std(IP_thickness), np.mean(LIP_thickness), np.std(LIP_thickness), np.mean(LTP_thickness), np.std(LTP_thickness)

def user_input():
    paths = []
    while True:
        path = input("폴더 경로를 입력하세요 (종료하려면 'q'를 입력): ").replace('\\','/')
        if path.lower() == 'q': break
        paths.append(path)
    width = int(input("레이어의 한 변 길이 (e.g. 40): "))
    pixel = int(input("레이어의 한 변 Pixel (e.g. 1000): "))
    height = float(input("레이어의 높이 (e.g. 0.05): "))
    area_per_pixel = (width**2) / (pixel**2)
    length_per_pixel = width / pixel
    return paths, area_per_pixel, height, length_per_pixel

def process_one_path(path, area_per_pixel, height, length_per_pixel):
    path_colorcombine = path + '/colorcombine'
    print(f"{path} 처리 중 ...")
    thickness_result = thickness(path, area_per_pixel)
    mass_curv_result = massorientation_curvature(path_colorcombine, area_per_pixel, height, length_per_pixel)
    return path, thickness_result, mass_curv_result

def main():
    starttime = time.time()
    path_lists, area_per_pixel, height, length_per_pixel = user_input()
    grouped = defaultdict(list)
    for p in path_lists:
        parent = os.path.dirname(p.rstrip('/\\'))
        grouped[parent].append(p)

    for group_folder, subfolders in grouped.items():
        print(f"\n📁 상위폴더: {group_folder}")
        thickness_data, massori_data, curvature_data, angle_data, pta_data = [], [], [], [], []
        for path in subfolders:
            path, thickness_result, all_results = process_one_path(path, area_per_pixel, height, length_per_pixel)
            folder_name = os.path.basename(path.rstrip('/\\'))

            mass_vals   = all_results[0:6]
            curv_vals   = all_results[6:12]
            angle_vals  = all_results[12:18]
            pta_vals    = all_results[18:24]

            thickness_data.append([folder_name] + list(thickness_result))
            massori_data.append([folder_name] + list(mass_vals))
            curvature_data.append([folder_name] + list(curv_vals))
            angle_data.append([folder_name] + list(angle_vals))
            pta_data.append([folder_name] + list(pta_vals))

        column = ['File Name', 'IP-avg', 'IP-stdev', 'LIP-avg', 'LIP-stdev', 'LTP-avg', 'LTP-stdev']
        df_thickness = pd.DataFrame(thickness_data, columns=column)
        df_massori   = pd.DataFrame(massori_data, columns=column)
        df_curvature = pd.DataFrame(curvature_data, columns=column)
        df_angle     = pd.DataFrame(angle_data, columns=column)
        df_perim     = pd.DataFrame(pta_data, columns=column)

        excel_file = os.path.join(group_folder, f"Parameter_result_{os.path.basename(group_folder)}.xlsx")
        with pd.ExcelWriter(excel_file) as writer:
            df_thickness.to_excel(writer, sheet_name='Thickness', index=False)
            df_massori.to_excel(writer, sheet_name='Mass Orientation', index=False)
            df_curvature.to_excel(writer, sheet_name='Curvature', index=False)
            df_angle.to_excel(writer, sheet_name='Angle', index=False)
            df_perim.to_excel(writer, sheet_name='Perimeter-to-Area', index=False)
        print(f"  ✅ {excel_file} 저장 완료")
    print(f"\n전체 실행 시간: {time.time() - starttime:.2f}초")

if __name__ == "__main__":
    main()
