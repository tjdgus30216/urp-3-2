import os
import cv2
import numpy as np
import pandas as pd
import time
import cupy as cp
from threading import Semaphore

# GPU 설정
gpu_count = cp.cuda.runtime.getDeviceCount()
gpu_semaphores = {i: Semaphore(2) for i in range(gpu_count)}

def wait_until_memory_is_free(threshold_bytes=3 * 1024**3, device_id=0, max_retries=300):
    retry = 0
    while retry < max_retries:
        with cp.cuda.Device(device_id):
            free_bytes, _ = cp.cuda.Device(device_id).mem_info
            if free_bytes > threshold_bytes:
                return True
        time.sleep(0.1)
        retry += 1
    return False

def sum_array(area_label):
    return np.array([sum(sublist) for sublist in area_label])

def sum_array_edge(edge_label):
    return np.array([np.nansum(sublist) if isinstance(sublist, list) and len(sublist) > 0 else 1e-6 for sublist in edge_label])

def labeling(area_list, color_coordinate, white_labels, cnt):
    area_label = [[] for _ in range(1, cnt)]
    for k, coordinate in enumerate(color_coordinate):
        x, y = int(coordinate[0]), int(coordinate[1])
        if 0 <= y < white_labels.shape[0] and 0 <= x < white_labels.shape[1]:
            label = white_labels[y, x] - 1
            if 0 <= label < len(area_label):
                area_label[label].append(area_list[k])
    return area_label

def find_nonzero_safe(mask):
    coords = cv2.findNonZero(mask)
    if coords is None:
        return np.empty((0, 2), dtype=int), []
    return coords.reshape(-1, 2), mask[mask > 0]

def calc_perimeter_to_area(mask_red, mask_purple):
    combined_mask = cv2.bitwise_or(mask_red, mask_purple)
    num_labels, labels = cv2.connectedComponents(combined_mask)
    pta_list = []
    for i in range(1, num_labels):
        mask_i = (labels == i).astype(np.uint8) * 255
        area = cv2.countNonZero(mask_i)
        if area == 0:
            continue
        contours, _ = cv2.findContours(mask_i, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            perimeter = cv2.arcLength(contours[0], True)
            pta = perimeter / area
            pta_list.append((pta, area))
    if pta_list:
        vals, weights = zip(*pta_list)
        return np.array(vals), np.array(weights)
    else:
        return np.array([]), np.array([])

def get_contact_edge_length(mask_a, mask_b, length_per_pixel):
    kernel = np.ones((3,3), np.uint8)
    a_dil = cv2.dilate(mask_a, kernel, iterations=1)
    contact = cv2.bitwise_and(a_dil, mask_b)
    return np.count_nonzero(contact) * length_per_pixel

def process_file(file, width, height, volume_fraction, total_pixel, device_id):
    print(f"[경로 시작] {file} (GPU{device_id})")
    with gpu_semaphores[device_id]:
        wait_until_memory_is_free(device_id=device_id)

        image = cv2.imread(file)
        if image is None:
            return None
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        x_pixel, y_pixel = image.shape[:2]
        area_per_pixel = width**2 / (x_pixel * y_pixel)
        length_per_pixel = width / x_pixel
        unit_length_per_pixel = width / total_pixel

        mask_red = cv2.inRange(img_gray, 76, 76)
        mask_blue = cv2.inRange(img_gray, 29, 29)
        mask_purple = cv2.inRange(img_gray, 105, 105)
        mask_all = cv2.inRange(img_gray, 29, 105)

        cnt, white_labels, _, _ = cv2.connectedComponentsWithStats(mask_all)

        red = []
        blue = []
        purple = []
        arclength1 = []
        arclength2 = []
        for label in range(1, cnt):
            label_mask = (white_labels == label).astype(np.uint8) * 255
            label_red = cv2.bitwise_and(mask_red, label_mask)
            label_blue = cv2.bitwise_and(mask_blue, label_mask)
            label_purp = cv2.bitwise_and(mask_purple, label_mask)
            area_red = cv2.countNonZero(label_red) * area_per_pixel
            area_blue = cv2.countNonZero(label_blue) * area_per_pixel
            area_purp = cv2.countNonZero(label_purp) * area_per_pixel
            red.append(area_red)
            blue.append(area_blue)
            purple.append(area_purp)
            arclength1.append(get_contact_edge_length(label_red, label_purp, length_per_pixel))
            arclength2.append(get_contact_edge_length(label_blue, label_purp, length_per_pixel))
        red = np.array(red)
        blue = np.array(blue)
        purple = np.array(purple)
        arclength1 = np.array(arclength1)
        arclength2 = np.array(arclength2)

        weight = ((red + blue + 2 * purple) * height) / 2

        # ✅ angle, curvature 계산 로직 수정
        angle = np.full_like(red, 90.0, dtype=float)
        curvature = np.zeros_like(red, dtype=float)

        both_mask = (arclength1 > 1e-6) & (arclength2 > 1e-6)
        angle[both_mask] = np.arctan((height * 2) / (
            (red[both_mask] / arclength1[both_mask] + blue[both_mask] / arclength2[both_mask])
        )) * 180 / np.pi
        curvature[both_mask] = (
            (red[both_mask] / arclength1[both_mask] + blue[both_mask] / arclength2[both_mask]) / (2 * height)
        )

        red_only_mask = (arclength1 > 1e-6) & (arclength2 <= 1e-6)
        angle[red_only_mask] = np.arctan((height * 2) / (red[red_only_mask] / arclength1[red_only_mask])) * 180 / np.pi
        curvature[red_only_mask] = (red[red_only_mask] / arclength1[red_only_mask]) / (2 * height)

        blue_only_mask = (arclength1 <= 1e-6) & (arclength2 > 1e-6)
        angle[blue_only_mask] = np.arctan((height * 2) / (blue[blue_only_mask] / arclength2[blue_only_mask])) * 180 / np.pi
        curvature[blue_only_mask] = (blue[blue_only_mask] / arclength2[blue_only_mask]) / (2 * height)
        # 둘 다 없음은 angle=90, curvature=0 유지

        mass_ori = purple / (0.5 * red + 0.5 * blue + purple)
        thickness = np.sqrt(red + purple)

        # Perimeter-to-Area (라벨별, weight=area)
        pta_vals, pta_weights = calc_perimeter_to_area(mask_red, mask_purple)

        return {
            'angle': (angle, weight),
            'thickness': (thickness, weight),
            'massori': (mass_ori, weight),
            'curvature': (curvature, weight),
            'pta': (pta_vals, pta_weights)
        }

def weighted_avg_std(values, weights):
    avg = np.sum(values * weights) / np.sum(weights)
    std = np.sqrt(np.sum(weights * (values - avg)**2) / np.sum(weights))
    return avg, std

def process_all(folder, width, height, volume_fraction, total_pixel):
    file_list = sorted(
        [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".png")],
        key=lambda x: int(''.join(filter(str.isdigit, os.path.splitext(os.path.basename(x))[0]))))
    results = []
    for i, file in enumerate(file_list):
        result = process_file(file, width, height, volume_fraction, total_pixel, device_id=i % gpu_count)
        if result:
            results.append(result)
    return results

def save_results(results, save_root, path):
    summary = {}
    for key in ['angle', 'thickness', 'massori', 'curvature', 'pta']:
        all_vals, all_weights = [], []
        for r in results:
            v, w = r[key]
            all_vals.append(v)
            all_weights.append(w)
        if all_vals and np.concatenate(all_vals).size > 0:
            vcat = np.concatenate(all_vals)
            wcat = np.concatenate(all_weights)
            summary[key] = weighted_avg_std(vcat, wcat)
        else:
            summary[key] = (0, 0)

    df_summary = pd.DataFrame(
        [[k, f"{avg:.4f}", f"{std:.4f}"] for k, (avg, std) in summary.items()],
        columns=['Parameter', 'Weighted Avg', 'Weighted Std']
    )

    folder_name = os.path.basename(os.path.normpath(path))
    output_file = os.path.join(save_root, f"{folder_name}_summary.xlsx")

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='summary', index=False)
        for key in ['angle', 'thickness', 'massori', 'curvature', 'pta']:
            all_vals, all_weights = [], []
            for r in results:
                v, w = r[key]
                all_vals.append(v)
                all_weights.append(w)
            vcat = np.concatenate(all_vals)
            wcat = np.concatenate(all_weights)
            if vcat.size == 0:
                continue
            wcat_normalized = wcat / wcat.sum()
            df_dist = pd.DataFrame({
                'Value': vcat,
                'Weight Factor': wcat_normalized
            })
            df_dist.to_excel(writer, sheet_name=key, index=False)
            bin_edges = np.linspace(vcat.min(), vcat.max(), 21)
            bins = pd.cut(vcat, bins=bin_edges, include_lowest=True, right=False)
            dist_list = []
            for bin_range in bins.categories:
                idx = bins == bin_range
                mean_val = np.mean(vcat[idx]) if np.any(idx) else 0
                sum_weight = np.sum(wcat[idx]) if np.any(idx) else 0
                label_str = f"[{bin_range.left:.2f}, {bin_range.right:.2f})"
                dist_list.append([label_str, mean_val, sum_weight / wcat.sum()])
            df_bin = pd.DataFrame(dist_list, columns=['Range', 'Mean Value', 'Normalized Sum Weight'])
            df_bin.to_excel(writer, sheet_name=f'{key}_20bin', index=False)

    print(f"\n✅ 저장 완료: {output_file}")

if __name__ == '__main__':
    save_root = input("엑셀 저장 경로를 입력하세요 (예: C:/results): ").strip().replace('\\', '/')
    os.makedirs(save_root, exist_ok=True)
    parent_folders = []
    while True:
        folder = input("분석할 경로 입력 (종료: 'q') : ").strip()
        if folder.lower() == 'q':
            break
        parent_folders.append(folder.replace('\\', '/'))

    width = int(input("Width (예: 40): "))
    height = float(input("Height (예: 0.05): "))
    vf = float(input("Volume fraction (예: 0.3): "))
    total_pixel = int(input("길이 당 픽셀 수 입력 (예: 1000): "))
    t0 = time.time()

    for path in parent_folders:
        print(f"\n[경로 시작] {path}")
        input_path = os.path.join(path, 'colorcombine')
        results = process_all(input_path, width, height, vf, total_pixel)
        save_results(results, save_root, path)

    print(f"\n⏱️ 전체 경로 처리 완료. 총 소요 시간: {time.time() - t0:.2f}초")
