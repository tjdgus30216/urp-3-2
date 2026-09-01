import pandas as pd
import numpy as np
import os

# === 사용자 입력 ===
inp_folder = input("INP 파일들이 들어 있는 폴더 경로를 입력하세요: ").strip().replace('\\', '/')
save_folder = input("엑셀 결과 파일들을 저장할 폴더 경로를 입력하세요: ").strip().replace('\\', '/')
os.makedirs(save_folder, exist_ok=True)

# INP 파일 목록
inp_files = [f for f in os.listdir(inp_folder) if f.lower().endswith(".inp")]

if not inp_files:
    print("INP 파일이 없습니다.")
else:
    for inp_file in inp_files:
        inp_path = os.path.join(inp_folder, inp_file)
        base_name = os.path.splitext(inp_file)[0]
        output_excel_path = os.path.join(save_folder, f"{base_name}_normalized.xlsx")
        output_inp_path = os.path.join(save_folder, f"{base_name}_Normalized.inp")

        X_list, Y_list, Z_list = [], [], []
        node_lines = []
        pre_lines = []
        post_lines = []
        start_reading = False

        with open(inp_path, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line_strip = line.strip()
            if line_strip.startswith("*NODE"):
                start_reading = True
                continue
            if line_strip.startswith("*ELEMENT"):
                # ✅ "*ELEMENT" 주석 포함 보존 (i-1부터 저장)
                post_lines = lines[i - 1:] if i > 0 else lines[i:]
                break
            if not start_reading:
                pre_lines.append(line)
            elif line_strip.startswith("**") or line_strip == "":
                continue
            else:
                parts = line_strip.split(",")
                if len(parts) >= 4:
                    node_lines.append(line)
                    X_list.append(float(parts[1]))
                    Y_list.append(float(parts[2]))
                    Z_list.append(float(parts[3]))

        X = np.array(X_list)
        Y = np.array(Y_list)
        Z = np.array(Z_list)

        # 중심점 및 길이 계산
        x_center = (np.max(X) + np.min(X)) / 2
        y_center = (np.max(Y) + np.min(Y)) / 2
        z_center = (np.max(Z) + np.min(Z)) / 2

        x_len = np.max(X) - np.min(X)
        y_len = np.max(Y) - np.min(Y)
        z_len = np.max(Z) - np.min(Z)

        # 정규화
        X_norm = (X - x_center) / x_len
        Y_norm = (Y - y_center) / y_len
        Z_norm = (Z - z_center) / z_len

        # === 정규화된 INP 저장 ===
        with open(output_inp_path, 'w') as f:
            for line in pre_lines:
                f.write(line)
            f.write("*NODE, NSET=NALL\n")
            for idx, line in enumerate(node_lines):
                parts = line.strip().split(",")
                if len(parts) >= 4 and idx < len(X_norm):
                    node_id = parts[0].strip()
                    f.write(f"{node_id},{X_norm[idx]:.9f},{Y_norm[idx]:.9f},{Z_norm[idx]:.9f}\n")
            for line in post_lines:
                f.write(line)

        # === 엑셀 저장 ===
        with pd.ExcelWriter(output_excel_path) as writer:
            pd.DataFrame({'X': X_norm, 'Y': Y_norm, 'Z': Z_norm}).to_excel(writer, sheet_name='Normalized XYZ', index=False)

            # Global Range
            mask_global = (np.abs(X_norm) <= 0.5) & (np.abs(Y_norm) <= 0.5) & (np.abs(Z_norm) <= 0.5)
            Xg, Yg, Zg = X_norm[mask_global], Y_norm[mask_global], Z_norm[mask_global]
            XYg = np.sqrt(Xg**2 + Yg**2)
            YZg = np.sqrt(Yg**2 + Zg**2)
            XZg = np.sqrt(Xg**2 + Zg**2)
            XYZg = np.sqrt(Xg**2 + Yg**2 + Zg**2)

            global_stats = {
                'Mean': [np.abs(Xg).mean(), np.abs(Yg).mean(), np.abs(Zg).mean(), XYg.mean(), YZg.mean(), XZg.mean(), XYZg.mean()],
                'Stdev': [np.abs(Xg).std(), np.abs(Yg).std(), np.abs(Zg).std(), XYg.std(), YZg.std(), XZg.std(), XYZg.std()]
            }
            pd.DataFrame(global_stats, index=['X', 'Y', 'Z', 'XY', 'YZ', 'XZ', 'XYZ']).to_excel(writer, sheet_name='Global Range')

            # Local Range
            mask_local = (np.abs(X_norm) <= 0.1) & (np.abs(Y_norm) <= 0.1) & (np.abs(Z_norm) <= 0.1)
            Xl, Yl, Zl = X_norm[mask_local], Y_norm[mask_local], Z_norm[mask_local]
            XYl = np.sqrt(Xl**2 + Yl**2)
            YZl = np.sqrt(Yl**2 + Zl**2)
            XZl = np.sqrt(Xl**2 + Zl**2)
            XYZl = np.sqrt(Xl**2 + Yl**2 + Zl**2)

            local_stats = {
                'Mean': [np.abs(Xl).mean(), np.abs(Yl).mean(), np.abs(Zl).mean(), XYl.mean(), YZl.mean(), XZl.mean(), XYZl.mean()],
                'Stdev': [np.abs(Xl).std(), np.abs(Yl).std(), np.abs(Zl).std(), XYl.std(), YZl.std(), XZl.std(), XYZl.std()]
            }
            pd.DataFrame(local_stats, index=['X', 'Y', 'Z', 'XY', 'YZ', 'XZ', 'XYZ']).to_excel(writer, sheet_name='Local Range')

            # Center and Length
            info_df = pd.DataFrame({
                'X': [x_center, x_len],
                'Y': [y_center, y_len],
                'Z': [z_center, z_len]
            }, index=['Center', 'Length'])
            info_df.to_excel(writer, sheet_name='Center and Length')

        print(f"[완료] {inp_file} → {os.path.basename(output_excel_path)}, {os.path.basename(output_inp_path)}")
