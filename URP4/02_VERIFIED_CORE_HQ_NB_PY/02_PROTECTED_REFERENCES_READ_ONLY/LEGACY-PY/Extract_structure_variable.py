import math
import re
import statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime

import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.utils.cell import range_boundaries


# =========================================================
# 1) 경로 설정
# =========================================================
INPUT_PATH = Path(r"C:\Users\김민겸\OneDrive - SKKU\1. Metal metamaterial\Ntop-Structural Variable\5x5x5 Node-Strut Data.xlsx")

# 결과 파일명 뒤에 현재 날짜+시간 추가
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PATH = INPUT_PATH.with_name(INPUT_PATH.stem + f"_Summary_{TIMESTAMP}.xlsx")


# =========================================================
# 2) 설정값
# =========================================================
DATA_START_ROW = 4
MAX_STRUT_SLOTS = 17           # Strut1 ~ Strut17까지만 출력
COORD_KEY_DECIMALS = 6         # 좌표 매칭용 반올림 자리수
ANGLE_DECIMALS = 6
LENGTH_DECIMALS = 6
SUMMARY_DECIMALS = 6
L_OVER_D_COL = 14              # N열: l/d
L_OVER_D_DECIMALS = 6

# "Strut?-No." 컬럼에 무엇을 넣을지:
#   "total_count" -> 해당 node에 연결된 총 strut 개수
#   "index"       -> 1,2,3... 세트 번호
STRUT_NO_MODE = "total_count"


# =========================================================
# 3) 유틸 함수
# =========================================================
def to_float(v):
    """셀 값을 float로 변환 (실패 시 None)"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return None
        s = s.replace("−", "-").replace("–", "-").replace("—", "-")
        s = s.replace(",", "")
        if s.startswith("="):
            return None
        try:
            return float(s)
        except Exception:
            return None
    return None


def split_excel_args(arg_text):
    """Excel 함수 인자를 top-level comma/semicolon 기준으로 분리한다."""
    args = []
    buf = []
    depth = 0
    in_string = False

    for ch in arg_text:
        if ch == '"':
            in_string = not in_string
            buf.append(ch)
            continue

        if not in_string:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch in [",", ";"] and depth == 0:
                args.append("".join(buf).strip())
                buf = []
                continue

        buf.append(ch)

    if buf or arg_text.strip() == "":
        args.append("".join(buf).strip())

    return args


def strip_outer_parentheses(expr):
    """전체 식을 감싸는 바깥 괄호만 제거한다."""
    expr = expr.strip()
    while expr.startswith("(") and expr.endswith(")"):
        depth = 0
        valid = True
        for i, ch in enumerate(expr):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i != len(expr) - 1:
                    valid = False
                    break
        if valid:
            expr = expr[1:-1].strip()
        else:
            break
    return expr


def get_numeric_cell(ws_values, ws_formula, row, col, _visited=None):
    """
    셀의 숫자 값을 안전하게 읽는다.

    핵심 수정:
    - openpyxl의 data_only=True는 Excel 수식의 cached value가 없으면 None을 반환한다.
    - 따라서 N열 l/d가 함수/수식이면 값이 비어 나올 수 있다.
    - 이 함수는 cached value가 없을 때 data_only=False에서 수식 문자열을 읽어 직접 계산한다.

    지원 예시:
    - =K4/M4
    - =ROUND(K4/M4, 6)
    - =SQRT((E4-H4)^2+(F4-I4)^2+(G4-J4)^2)/M4
    - =IFERROR(K4/M4, "")
    - =SUM(A1:A3), =AVERAGE(A1:A3)
    """
    if _visited is None:
        _visited = set()

    # 1) cached value 우선
    v = to_float(ws_values.cell(row, col).value)
    if v is not None:
        return v

    if ws_formula is None:
        return None

    raw = ws_formula.cell(row, col).value
    if raw is None:
        return None

    # 2) 수식이 아니라 일반 숫자/문자 숫자면 그대로 변환
    direct = to_float(raw)
    if direct is not None:
        return direct

    # 3) 수식이면 직접 계산
    if isinstance(raw, str) and raw.startswith("="):
        coord = ws_formula.cell(row, col).coordinate
        if coord in _visited:
            return None
        _visited.add(coord)
        return evaluate_excel_expr(raw[1:], ws_values, ws_formula, _visited)

    return None


def evaluate_excel_expr(expr, ws_values, ws_formula, _visited=None):
    """
    openpyxl이 계산하지 못한 Excel 수식을 제한적으로 직접 계산한다.
    N열 l/d가 함수 형태로 들어가 있을 때 값을 읽기 위한 보완 계산기이다.
    """
    if _visited is None:
        _visited = set()

    if expr is None:
        return None

    expr = str(expr).strip()
    if expr.startswith("="):
        expr = expr[1:].strip()

    if expr == "":
        return None

    # Excel 표기 정리
    expr = expr.replace("$", "")
    expr = expr.replace("^", "**")
    expr = expr.replace("_xlfn.", "")
    expr = expr.replace("@", "")
    expr = expr.replace("TRUE", "1").replace("FALSE", "0")
    expr = strip_outer_parentheses(expr)

    # 문자열 빈 값 처리
    if expr in ['""', "''"]:
        return None

    # 다른 시트 참조는 여기서는 처리하지 않음
    if "!" in expr:
        return None

    # 전체가 숫자인 경우
    direct = to_float(expr)
    if direct is not None:
        return direct

    # IFERROR(primary, fallback)
    m = re.match(r"^IFERROR\((.*)\)$", expr, flags=re.IGNORECASE)
    if m:
        args = split_excel_args(m.group(1))
        if len(args) >= 1:
            primary = evaluate_excel_expr(args[0], ws_values, ws_formula, _visited.copy())
            if primary is not None and math.isfinite(primary):
                return primary
            if len(args) >= 2:
                return evaluate_excel_expr(args[1], ws_values, ws_formula, _visited.copy())
        return None

    # IF(condition, true_value, false_value)
    m = re.match(r"^IF\((.*)\)$", expr, flags=re.IGNORECASE)
    if m:
        args = split_excel_args(m.group(1))
        if len(args) >= 2:
            cond = evaluate_excel_condition(args[0], ws_values, ws_formula, _visited.copy())
            if cond:
                return evaluate_excel_expr(args[1], ws_values, ws_formula, _visited.copy())
            if len(args) >= 3:
                return evaluate_excel_expr(args[2], ws_values, ws_formula, _visited.copy())
        return None

    # Excel 함수명을 Python 함수명으로 변환
    func_map = {
        "SQRT": "sqrt",
        "ABS": "abs",
        "POWER": "power",
        "SUM": "sum_",
        "AVERAGE": "average",
        "AVERAGEA": "average",
        "MIN": "min",
        "MAX": "max",
        "ROUND": "round",
        "ROUNDDOWN": "rounddown",
        "ROUNDUP": "roundup",
        "PI": "pi",
    }
    for excel_name, py_name in func_map.items():
        expr = re.sub(rf"\b{excel_name}\s*\(", f"{py_name}(", expr, flags=re.IGNORECASE)

    # 범위 참조 A1:B3를 [값, 값, ...]로 치환
    range_pattern = re.compile(r"(?<![A-Za-z0-9_])([A-Z]{1,3}[0-9]{1,7}:[A-Z]{1,3}[0-9]{1,7})(?![A-Za-z0-9_])", re.IGNORECASE)

    def replace_range(match):
        range_ref = match.group(1).upper()
        try:
            min_col, min_row, max_col, max_row = range_boundaries(range_ref)
            vals = []
            for rr in range(min_row, max_row + 1):
                for cc in range(min_col, max_col + 1):
                    val = get_numeric_cell(ws_values, ws_formula, rr, cc, _visited.copy())
                    if val is not None:
                        vals.append(float(val))
            return str(vals)
        except Exception:
            raise ValueError(f"Cannot evaluate range: {range_ref}")

    # 단일 셀 참조 A1을 숫자로 치환
    cell_ref_pattern = re.compile(r"(?<![A-Za-z0-9_])([A-Z]{1,3}[0-9]{1,7})(?![A-Za-z0-9_])", re.IGNORECASE)

    def replace_cell(match):
        ref = match.group(1).upper()
        try:
            # openpyxl coordinate -> row/col
            col_letters = re.match(r"([A-Z]{1,3})([0-9]{1,7})", ref).group(1)
            row_num = int(re.match(r"([A-Z]{1,3})([0-9]{1,7})", ref).group(2))
            col_num = 0
            for ch in col_letters:
                col_num = col_num * 26 + (ord(ch) - ord("A") + 1)
            val = get_numeric_cell(ws_values, ws_formula, row_num, col_num, _visited.copy())
            if val is None:
                raise ValueError(f"Cannot evaluate cell reference: {ref}")
            return str(float(val))
        except Exception:
            raise ValueError(f"Cannot evaluate cell reference: {ref}")

    try:
        expr2 = range_pattern.sub(replace_range, expr)
        expr2 = cell_ref_pattern.sub(replace_cell, expr2)

        # Excel 비교 연산자 보정
        expr2 = expr2.replace("<>", "!=")
        expr2 = re.sub(r"(?<![<>=!])=(?!=)", "==", expr2)

        def sum_(*args):
            vals = []
            for a in args:
                if isinstance(a, (list, tuple)):
                    vals.extend(a)
                elif a is not None:
                    vals.append(a)
            return sum(vals)

        def average(*args):
            vals = []
            for a in args:
                if isinstance(a, (list, tuple)):
                    vals.extend(a)
                elif a is not None:
                    vals.append(a)
            vals = [float(x) for x in vals if x is not None]
            if len(vals) == 0:
                return None
            return sum(vals) / len(vals)

        def power(a, b):
            return float(a) ** float(b)

        def rounddown(a, nd=0):
            factor = 10 ** int(nd)
            return math.floor(float(a) * factor) / factor

        def roundup(a, nd=0):
            factor = 10 ** int(nd)
            return math.ceil(float(a) * factor) / factor

        env = {
            "sqrt": math.sqrt,
            "abs": abs,
            "min": min,
            "max": max,
            "sum_": sum_,
            "average": average,
            "round": round,
            "rounddown": rounddown,
            "roundup": roundup,
            "power": power,
            "pi": math.pi,
        }

        # 안전성 검사: 허용된 문자/함수명만 남겨서 eval
        if re.search(r"[^0-9eE+\-*/()., \[\]_<>=!a-zA-Z]", expr2):
            return None

        val = eval(expr2, {"__builtins__": {}}, env)
        return to_float(val)
    except Exception:
        return None


def evaluate_excel_condition(expr, ws_values, ws_formula, _visited=None):
    """IF 조건식 계산용 보조 함수."""
    val = evaluate_excel_expr(expr, ws_values, ws_formula, _visited)
    if val is not None:
        return bool(val)
    return False


def key3(x, y, z, nd=COORD_KEY_DECIMALS):
    return (round(float(x), nd), round(float(y), nd), round(float(z), nd))


def canonical_strut_key(k1, k2):
    """
    같은 strut가 방향만 반대로 중복 입력된 경우를 제거하기 위한 key.
    예: A-B와 B-A를 동일 strut로 처리.
    """
    return tuple(sorted([k1, k2]))


def round_or_none(v, nd=SUMMARY_DECIMALS):
    if v is None:
        return None
    return round(float(v), nd)


def mean_or_none(values):
    vals = [v for v in values if v is not None]
    if len(vals) == 0:
        return None
    return statistics.mean(vals)


def stdev_or_none(values):
    """
    Excel STDEV.S와 유사하게 sample standard deviation 사용.
    데이터가 1개 이하이면 0으로 반환.
    """
    vals = [v for v in values if v is not None]
    if len(vals) <= 1:
        return 0
    return statistics.stdev(vals)


def weighted_mean_or_none(values, weights):
    pairs = [
        (v, w)
        for v, w in zip(values, weights)
        if v is not None and w is not None and w > 0
    ]
    if len(pairs) == 0:
        return None

    total_w = sum(w for _, w in pairs)
    if total_w == 0:
        return None

    return sum(v * w for v, w in pairs) / total_w


def weighted_stdev_or_none(values, weights):
    """
    Length weighted standard deviation.
    가중 분산 = sum(w*(x-mean)^2) / sum(w)
    """
    pairs = [
        (v, w)
        for v, w in zip(values, weights)
        if v is not None and w is not None and w > 0
    ]
    if len(pairs) <= 1:
        return 0

    total_w = sum(w for _, w in pairs)
    if total_w == 0:
        return None

    w_mean = sum(v * w for v, w in pairs) / total_w
    w_var = sum(w * (v - w_mean) ** 2 for v, w in pairs) / total_w
    return math.sqrt(w_var)


def count_triplet_rows(ws, cols, start_row=DATA_START_ROW):
    """
    지정한 3개 컬럼에 대해, 데이터가 존재하는 행 개수(완전한 triplet 기준)를 카운트
    cols: (col1, col2, col3) 1-indexed
    """
    c1, c2, c3 = cols
    cnt = 0
    for r in range(start_row, ws.max_row + 1):
        v1 = to_float(ws.cell(r, c1).value)
        v2 = to_float(ws.cell(r, c2).value)
        v3 = to_float(ws.cell(r, c3).value)
        if v1 is not None and v2 is not None and v3 is not None:
            cnt += 1
    return cnt


def compute_strut_length_and_angles(p1, p2):
    """
    p1=(x1,y1,z1), p2=(x2,y2,z2)

    length = sqrt(dx^2 + dy^2 + dz^2)

    angle_z = asin(abs(dz) / L)
            = XY 평면 대비 Z 방향 기울기

    angle_x = asin(abs(dx) / L)
            = YZ 평면 대비 X 방향 기울기

    angle_y = asin(abs(dy) / L)
            = XZ 평면 대비 Y 방향 기울기
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]

    L = math.sqrt(dx * dx + dy * dy + dz * dz)

    if L == 0:
        return 0, None, None, None

    def axis_angle(axis_delta):
        ratio = abs(axis_delta) / L
        ratio = max(0.0, min(1.0, ratio))
        return round(math.degrees(math.asin(ratio)), ANGLE_DECIMALS)

    angle_x = axis_angle(dx)
    angle_y = axis_angle(dy)
    angle_z = axis_angle(dz)

    return round(L, LENGTH_DECIMALS), angle_z, angle_x, angle_y


def set_basic_style(ws, max_col):
    # 헤더 스타일
    for c in range(1, max_col + 1):
        cell = ws.cell(1, c)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # 열 너비 대략 조정
    widths = {
        1: 8,   # No.
        2: 12,  # Node-x
        3: 12,  # Node-y
        4: 12,  # Node-z
    }

    for c in range(5, max_col + 1):
        mod = (c - 5) % 3
        if mod == 0:
            widths[c] = 14
        elif mod == 1:
            widths[c] = 13
        else:
            widths[c] = 10

    for c, w in widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    # 추가 컬럼이 생겨도 보기 좋게 기본 너비 적용
    for c in range(1, ws.max_column + 1):
        if c not in widths:
            ws.column_dimensions[get_column_letter(c)].width = 34

    ws.freeze_panes = "A2"


def set_summary_style(ws):
    for c in range(1, ws.max_column + 1):
        cell = ws.cell(1, c)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    widths = {
        1: 28,  # 모델명
        2: 12,  # Node 개수
        3: 12,  # Strut 개수

        4: 24,
        5: 24,

        6: 22,
        7: 22,

        8: 34,
        9: 34,

        10: 22,
        11: 22,

        12: 34,
        13: 34,

        14: 34,
        15: 34,

        16: 34,
        17: 34,

        18: 34,
        19: 34,

        20: 34,
        21: 34,
        22: 34,
        23: 34,
        24: 34,
        25: 34,
    }

    for c, w in widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    for c in range(1, ws.max_column + 1):
        if c not in widths:
            ws.column_dimensions[get_column_letter(c)].width = 34

    for r in range(2, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            ws.cell(r, c).alignment = Alignment(horizontal="center", vertical="center")

    ws.freeze_panes = "A2"


# =========================================================
# 4) 데이터 읽기 함수
# =========================================================
def read_nodes_from_sheet(ws):
    """
    Import 시트의 B,C,D열(4행부터)에서 Node 목록 읽기
    반환: list of dict(row, x,y,z,key)
    """
    nodes = []

    for r in range(DATA_START_ROW, ws.max_row + 1):
        x = to_float(ws.cell(r, 2).value)  # B
        y = to_float(ws.cell(r, 3).value)  # C
        z = to_float(ws.cell(r, 4).value)  # D

        if x is None or y is None or z is None:
            continue

        nodes.append({
            "src_row": r,
            "x": x,
            "y": y,
            "z": z,
            "key": key3(x, y, z)
        })

    return nodes


def read_struts_from_sheet(ws, ws_formula=None):
    """
    Import 시트의 E:F:G / H:I:J (4행부터)에서 Strut 목록을 읽는다.
    같은 행의 N열 l/d 값을 해당 strut의 속성으로 함께 저장한다.
    반환: list of dict(row, p1, p2, length, l_over_d, angle_z, angle_x, angle_y)
    """
    struts = []
    skipped_incomplete = 0
    skipped_zero = 0

    for r in range(DATA_START_ROW, ws.max_row + 1):
        x1 = to_float(ws.cell(r, 5).value)   # E
        y1 = to_float(ws.cell(r, 6).value)   # F
        z1 = to_float(ws.cell(r, 7).value)   # G

        x2 = to_float(ws.cell(r, 8).value)   # H
        y2 = to_float(ws.cell(r, 9).value)   # I
        z2 = to_float(ws.cell(r, 10).value)  # J

        # 같은 행의 N열 l/d 값
        l_over_d = get_numeric_cell(ws, ws_formula, r, L_OVER_D_COL)

        # 완전 빈 행은 skip
        if all(v is None for v in (x1, y1, z1, x2, y2, z2)):
            continue

        # 불완전 행 skip
        if any(v is None for v in (x1, y1, z1, x2, y2, z2)):
            skipped_incomplete += 1
            continue

        p1 = (x1, y1, z1)
        p2 = (x2, y2, z2)

        L, angle_z, angle_x, angle_y = compute_strut_length_and_angles(p1, p2)

        if L == 0:
            skipped_zero += 1
            continue

        k1 = key3(*p1)
        k2 = key3(*p2)

        struts.append({
            "src_row": r,
            "p1": p1,
            "p2": p2,

            "k1": k1,
            "k2": k2,
            "unique_key": canonical_strut_key(k1, k2),

            "length": L,
            "l_over_d": round(float(l_over_d), L_OVER_D_DECIMALS) if l_over_d is not None else None,

            # 기존 코드에서 사용하던 angle은 Z 방향 angle로 유지
            "angle": angle_z,
            "angle_z": angle_z,

            # 새로 추가된 X/Y 방향 angle
            "angle_x": angle_x,
            "angle_y": angle_y,
        })

    return struts, skipped_incomplete, skipped_zero


def get_unique_struts(struts):
    """
    중복되지 않은 strut만 반환.
    동일한 양 끝 node 조합을 갖는 strut는 1개로 처리.
    """
    unique = {}

    for s in struts:
        if s["unique_key"] not in unique:
            unique[s["unique_key"]] = s

    return list(unique.values())


def compute_weighted_global_angle_stats(unique_struts, angle_key):
    """
    중복되지 않은 strut 기준 Global angle weighted AVG/STDEV 계산.
    angle_key: "angle_z", "angle_x", "angle_y"
    """
    angles = [
        s[angle_key]
        for s in unique_struts
        if s.get(angle_key) is not None and s.get("length") is not None and s["length"] > 0
    ]

    weights = [
        s["length"]
        for s in unique_struts
        if s.get(angle_key) is not None and s.get("length") is not None and s["length"] > 0
    ]

    avg = weighted_mean_or_none(angles, weights)
    stdev = weighted_stdev_or_none(angles, weights)

    return avg, stdev


def compute_node_weighted_angle_stats(nodes, node_to_struts, angle_key):
    """
    각 Node에서 연결된 strut angle을 length weighted average로 계산한 뒤,
    Node 전체에서 AVG/STDEV 계산.
    angle_key: "angle_z", "angle_x", "angle_y"
    """
    node_angle_weighted_avgs = []

    for node in nodes:
        connected = node_to_struts.get(node["key"], [])

        angles = [
            s[angle_key]
            for s in connected
            if s.get(angle_key) is not None and s.get("length") is not None and s["length"] > 0
        ]

        weights = [
            s["length"]
            for s in connected
            if s.get(angle_key) is not None and s.get("length") is not None and s["length"] > 0
        ]

        if len(angles) == 0:
            continue

        node_w_avg = weighted_mean_or_none(angles, weights)

        if node_w_avg is not None:
            node_angle_weighted_avgs.append(node_w_avg)

    avg = mean_or_none(node_angle_weighted_avgs)
    stdev = stdev_or_none(node_angle_weighted_avgs)

    return avg, stdev


def read_global_l_over_d_values_from_sheet(ws, ws_formula=None):
    """
    Global l/d 계산용 데이터.
    N열 4행부터 숫자로 읽히는 모든 l/d 값을 직접 수집한다.
    이 값은 unique strut 처리와 무관하게 원본 N열 데이터 그대로 사용한다.
    """
    values = []
    for r in range(DATA_START_ROW, ws.max_row + 1):
        v = get_numeric_cell(ws, ws_formula, r, L_OVER_D_COL)
        if v is not None:
            values.append(v)
    return values


def compute_node_l_over_d_stats(nodes, node_to_struts):
    """
    Node l/d 계산 방식:
    1) 하나의 node에 연결된 strut들의 l/d 값을 모음
    2) 해당 node 내부에서 l/d 평균을 계산
    3) 모든 node의 l/d 평균값들을 모아 전체 AVG/STDEV 계산
    Length의 Node 계산 방식과 동일한 흐름이다.
    """
    node_l_over_d_avgs = []

    for node in nodes:
        connected = node_to_struts.get(node["key"], [])
        l_over_d_values = [
            s["l_over_d"]
            for s in connected
            if s.get("l_over_d") is not None
        ]

        if len(l_over_d_values) == 0:
            continue

        node_l_over_d_avgs.append(statistics.mean(l_over_d_values))

    avg = mean_or_none(node_l_over_d_avgs)
    stdev = stdev_or_none(node_l_over_d_avgs)

    return avg, stdev, len(node_l_over_d_avgs)


def compute_summary_metrics(nodes, struts, node_to_struts, global_l_over_d_values=None):
    """
    Summary 시트 D~Y열에 들어갈 통계 계산.

    D,E: Global: Strut No. at Nodes-AVG, STDEV
    F,G: Global: Length - AVG, STDEV

    H,I: Global: Angle-Z (weighted with length)-AVG, STDEV
    J,K: Node: Length - AVG, STDEV
    L,M: Node: Angle-Z (weighted with length)-AVG, STDEV

    N,O: Global: l/d AVG, STDEV
    P,Q: Node: l/d AVG, STDEV

    R,S: Global: Angle-X (weighted with length)-AVG, STDEV
    T,U: Node: Angle-X (weighted with length)-AVG, STDEV

    V,W: Global: Angle-Y (weighted with length)-AVG, STDEV
    X,Y: Node: Angle-Y (weighted with length)-AVG, STDEV
    """

    # -----------------------------------------------------
    # D,E열
    # Node에서의 Strut 개수 평균 및 표준편차
    # -----------------------------------------------------
    strut_no_at_nodes = []

    for node in nodes:
        connected = node_to_struts.get(node["key"], [])
        strut_no_at_nodes.append(len(connected))

    global_strut_no_avg = mean_or_none(strut_no_at_nodes)
    global_strut_no_stdev = stdev_or_none(strut_no_at_nodes)

    # -----------------------------------------------------
    # 중복되지 않은 strut 기준 데이터
    # -----------------------------------------------------
    unique_struts = get_unique_struts(struts)

    unique_lengths = [
        s["length"]
        for s in unique_struts
        if s.get("length") is not None
    ]

    # -----------------------------------------------------
    # F,G열
    # 중복되지 않은 Strut들의 Length 평균 및 표준편차
    # -----------------------------------------------------
    global_length_avg = mean_or_none(unique_lengths)
    global_length_stdev = stdev_or_none(unique_lengths)

    # -----------------------------------------------------
    # H,I열
    # 중복되지 않은 Strut들의 Angle-Z를 Length로 가중 평균/표준편차
    # -----------------------------------------------------
    global_angle_z_weighted_avg, global_angle_z_weighted_stdev = compute_weighted_global_angle_stats(
        unique_struts,
        "angle_z"
    )

    # -----------------------------------------------------
    # J,K열
    # 각 Node에서 연결된 Strut Length 평균 계산 후,
    # Node 전체에서 그 값들의 평균 및 표준편차
    # -----------------------------------------------------
    node_length_avgs = []

    for node in nodes:
        connected = node_to_struts.get(node["key"], [])
        lengths = [
            s["length"]
            for s in connected
            if s.get("length") is not None
        ]

        if len(lengths) == 0:
            continue

        node_length_avgs.append(statistics.mean(lengths))

    node_length_avg = mean_or_none(node_length_avgs)
    node_length_stdev = stdev_or_none(node_length_avgs)

    # -----------------------------------------------------
    # L,M열
    # 각 Node에서 연결된 Strut Angle-Z를 Length 가중 평균으로 계산 후,
    # Node 전체에서 그 값들의 평균 및 표준편차
    # -----------------------------------------------------
    node_angle_z_weighted_avg, node_angle_z_weighted_stdev = compute_node_weighted_angle_stats(
        nodes,
        node_to_struts,
        "angle_z"
    )

    # -----------------------------------------------------
    # N,O열
    # Global l/d AVG/STDEV
    # - 원본 N열 4행부터 존재하는 모든 숫자 데이터를 그대로 사용
    # -----------------------------------------------------
    if global_l_over_d_values is None:
        global_l_over_d_values = [
            s["l_over_d"]
            for s in struts
            if s.get("l_over_d") is not None
        ]

    global_l_over_d_avg = mean_or_none(global_l_over_d_values)
    global_l_over_d_stdev = stdev_or_none(global_l_over_d_values)

    # -----------------------------------------------------
    # P,Q열
    # Node l/d AVG/STDEV
    # -----------------------------------------------------
    node_l_over_d_avg, node_l_over_d_stdev, node_l_over_d_valid_node_count = compute_node_l_over_d_stats(
        nodes,
        node_to_struts
    )

    # -----------------------------------------------------
    # R,S열
    # Global Angle-X weighted AVG/STDEV
    # -----------------------------------------------------
    global_angle_x_weighted_avg, global_angle_x_weighted_stdev = compute_weighted_global_angle_stats(
        unique_struts,
        "angle_x"
    )

    # -----------------------------------------------------
    # T,U열
    # Node Angle-X weighted AVG/STDEV
    # -----------------------------------------------------
    node_angle_x_weighted_avg, node_angle_x_weighted_stdev = compute_node_weighted_angle_stats(
        nodes,
        node_to_struts,
        "angle_x"
    )

    # -----------------------------------------------------
    # V,W열
    # Global Angle-Y weighted AVG/STDEV
    # -----------------------------------------------------
    global_angle_y_weighted_avg, global_angle_y_weighted_stdev = compute_weighted_global_angle_stats(
        unique_struts,
        "angle_y"
    )

    # -----------------------------------------------------
    # X,Y열
    # Node Angle-Y weighted AVG/STDEV
    # -----------------------------------------------------
    node_angle_y_weighted_avg, node_angle_y_weighted_stdev = compute_node_weighted_angle_stats(
        nodes,
        node_to_struts,
        "angle_y"
    )

    return {
        "global_strut_no_avg": round_or_none(global_strut_no_avg),
        "global_strut_no_stdev": round_or_none(global_strut_no_stdev),

        "global_length_avg": round_or_none(global_length_avg),
        "global_length_stdev": round_or_none(global_length_stdev),

        "global_angle_z_weighted_avg": round_or_none(global_angle_z_weighted_avg),
        "global_angle_z_weighted_stdev": round_or_none(global_angle_z_weighted_stdev),

        "node_length_avg": round_or_none(node_length_avg),
        "node_length_stdev": round_or_none(node_length_stdev),

        "node_angle_z_weighted_avg": round_or_none(node_angle_z_weighted_avg),
        "node_angle_z_weighted_stdev": round_or_none(node_angle_z_weighted_stdev),

        "global_l_over_d_avg": round_or_none(global_l_over_d_avg),
        "global_l_over_d_stdev": round_or_none(global_l_over_d_stdev),

        "node_l_over_d_avg": round_or_none(node_l_over_d_avg),
        "node_l_over_d_stdev": round_or_none(node_l_over_d_stdev),
        "node_l_over_d_valid_node_count": node_l_over_d_valid_node_count,
        "global_l_over_d_count": len(global_l_over_d_values),

        "global_angle_x_weighted_avg": round_or_none(global_angle_x_weighted_avg),
        "global_angle_x_weighted_stdev": round_or_none(global_angle_x_weighted_stdev),

        "node_angle_x_weighted_avg": round_or_none(node_angle_x_weighted_avg),
        "node_angle_x_weighted_stdev": round_or_none(node_angle_x_weighted_stdev),

        "global_angle_y_weighted_avg": round_or_none(global_angle_y_weighted_avg),
        "global_angle_y_weighted_stdev": round_or_none(global_angle_y_weighted_stdev),

        "node_angle_y_weighted_avg": round_or_none(node_angle_y_weighted_avg),
        "node_angle_y_weighted_stdev": round_or_none(node_angle_y_weighted_stdev),

        "unique_strut_count": len(unique_struts),
    }


# =========================================================
# 5) 메인 처리
# =========================================================
def main():
    if not INPUT_PATH.exists():
        print(f"[오류] 파일이 없습니다:\n{INPUT_PATH}")
        return

    # data_only=True: Excel cached value 읽기
    # data_only=False: N열 l/d가 수식인데 cached value가 비어 있을 때 단순 수식 보완 계산용
    try:
        wb_in = openpyxl.load_workbook(INPUT_PATH, data_only=True)
        wb_formula = openpyxl.load_workbook(INPUT_PATH, data_only=False)
    except PermissionError:
        print("[권한 오류] Import 엑셀 파일이 열려 있으면 닫고 다시 실행하세요.")
        return
    except Exception as e:
        print(f"[오류] 파일 열기 실패: {e}")
        return

    # 출력 워크북 생성
    wb_out = openpyxl.Workbook()

    # 기본 시트 제거
    default_ws = wb_out.active
    wb_out.remove(default_ws)

    # -----------------------------------------------------
    # Summary 시트 생성
    # -----------------------------------------------------
    ws_summary = wb_out.create_sheet("Summary")

    summary_headers = [
        "모델명",
        "Node 개수",
        "Strut 개수",

        "Global: Strut No. at Nodes-AVG",
        "Global: Strut No. at Nodes-STDEV",

        "Global: Length - AVG",
        "Global: Length - STDEV",

        "Global: Angle-Z (weighted with length)-AVG",
        "Global: Angle-Z (weighted with length)-STDEV",

        "Node: Length - AVG",
        "Node: Length - STDEV",

        "Node: Angle-Z (weighted with length)-AVG",
        "Node: Angle-Z (weighted with length)-STDEV",

        "Global: l/d AVG",
        "Global: l/d STDEV",

        "Node: l/d AVG",
        "Node: l/d STDEV",

        "Global: Angle-X (weighted with length)-AVG",
        "Global: Angle-X (weighted with length)-STDEV",

        "Node: Angle-X (weighted with length)-AVG",
        "Node: Angle-X (weighted with length)-STDEV",

        "Global: Angle-Y (weighted with length)-AVG",
        "Global: Angle-Y (weighted with length)-STDEV",

        "Node: Angle-Y (weighted with length)-AVG",
        "Node: Angle-Y (weighted with length)-STDEV",
    ]

    for col_idx, h in enumerate(summary_headers, start=1):
        ws_summary.cell(1, col_idx).value = h

    summary_row = 2

    # -----------------------------------------------------
    # 각 시트 처리
    # -----------------------------------------------------
    for sheet_name in wb_in.sheetnames:
        ws_in = wb_in[sheet_name]
        ws_formula = wb_formula[sheet_name] if sheet_name in wb_formula.sheetnames else None

        # Summary 카운트
        node_count_summary = count_triplet_rows(ws_in, (2, 3, 4), DATA_START_ROW)   # B,C,D
        strut_count_summary = count_triplet_rows(ws_in, (5, 6, 7), DATA_START_ROW)  # E,F,G

        # 실제 데이터 읽기
        nodes = read_nodes_from_sheet(ws_in)
        struts, skipped_incomplete, skipped_zero = read_struts_from_sheet(ws_in, ws_formula)

        # Global l/d는 원본 N열 4행부터 존재하는 모든 숫자 데이터를 직접 사용
        global_l_over_d_values = read_global_l_over_d_values_from_sheet(ws_in, ws_formula)

        # Node key -> connected struts 목록 매핑
        node_to_struts = defaultdict(list)

        for s in struts:
            node_to_struts[s["k1"]].append(s)
            node_to_struts[s["k2"]].append(s)

        # Summary 추가 통계 계산
        metrics = compute_summary_metrics(nodes, struts, node_to_struts, global_l_over_d_values)

        # Summary A~U 작성
        ws_summary.cell(summary_row, 1).value = sheet_name
        ws_summary.cell(summary_row, 2).value = node_count_summary
        ws_summary.cell(summary_row, 3).value = strut_count_summary

        ws_summary.cell(summary_row, 4).value = metrics["global_strut_no_avg"]
        ws_summary.cell(summary_row, 5).value = metrics["global_strut_no_stdev"]

        ws_summary.cell(summary_row, 6).value = metrics["global_length_avg"]
        ws_summary.cell(summary_row, 7).value = metrics["global_length_stdev"]

        ws_summary.cell(summary_row, 8).value = metrics["global_angle_z_weighted_avg"]
        ws_summary.cell(summary_row, 9).value = metrics["global_angle_z_weighted_stdev"]

        ws_summary.cell(summary_row, 10).value = metrics["node_length_avg"]
        ws_summary.cell(summary_row, 11).value = metrics["node_length_stdev"]

        ws_summary.cell(summary_row, 12).value = metrics["node_angle_z_weighted_avg"]
        ws_summary.cell(summary_row, 13).value = metrics["node_angle_z_weighted_stdev"]

        ws_summary.cell(summary_row, 14).value = metrics["global_l_over_d_avg"]
        ws_summary.cell(summary_row, 15).value = metrics["global_l_over_d_stdev"]

        ws_summary.cell(summary_row, 16).value = metrics["node_l_over_d_avg"]
        ws_summary.cell(summary_row, 17).value = metrics["node_l_over_d_stdev"]

        ws_summary.cell(summary_row, 18).value = metrics["global_angle_x_weighted_avg"]
        ws_summary.cell(summary_row, 19).value = metrics["global_angle_x_weighted_stdev"]

        ws_summary.cell(summary_row, 20).value = metrics["node_angle_x_weighted_avg"]
        ws_summary.cell(summary_row, 21).value = metrics["node_angle_x_weighted_stdev"]

        ws_summary.cell(summary_row, 22).value = metrics["global_angle_y_weighted_avg"]
        ws_summary.cell(summary_row, 23).value = metrics["global_angle_y_weighted_stdev"]

        ws_summary.cell(summary_row, 24).value = metrics["node_angle_y_weighted_avg"]
        ws_summary.cell(summary_row, 25).value = metrics["node_angle_y_weighted_stdev"]

        summary_row += 1

        # -----------------------------------------------------
        # 출력 시트 생성
        # 기존 상세 시트 구조는 그대로 유지
        # -----------------------------------------------------
        ws_out = wb_out.create_sheet(sheet_name)

        headers = ["No.", "Node-x", "Node-y", "Node-z"]

        for i in range(1, MAX_STRUT_SLOTS + 1):
            headers += [
                f"Strut{i}-length",
                f"Strut{i}-angle",
                f"Strut{i}-No."
            ]

        for col_idx, h in enumerate(headers, start=1):
            ws_out.cell(1, col_idx).value = h

        # 데이터 작성
        max_connected_found = 0
        truncation_count = 0

        for idx, node in enumerate(nodes, start=1):
            r_out = idx + 1

            # A~D
            ws_out.cell(r_out, 1).value = idx
            ws_out.cell(r_out, 2).value = node["x"]
            ws_out.cell(r_out, 3).value = node["y"]
            ws_out.cell(r_out, 4).value = node["z"]

            connected = node_to_struts.get(node["key"], [])
            total_connected = len(connected)
            max_connected_found = max(max_connected_found, total_connected)

            if total_connected > MAX_STRUT_SLOTS:
                truncation_count += 1

            # 연결된 strut 정보 기록
            # 기존 상세 시트 angle은 Z-direction angle 유지
            for j, s in enumerate(connected[:MAX_STRUT_SLOTS], start=1):
                base_col = 5 + (j - 1) * 3

                ws_out.cell(r_out, base_col).value = s["length"]
                ws_out.cell(r_out, base_col + 1).value = s["angle_z"]

                if STRUT_NO_MODE == "total_count":
                    ws_out.cell(r_out, base_col + 2).value = total_connected
                else:
                    ws_out.cell(r_out, base_col + 2).value = j

        # 샘플별 시트 서식
        set_basic_style(ws_out, max_col=len(headers))

        # 콘솔 로그
        print(
            f"[{sheet_name}] "
            f"Nodes={len(nodes)}, "
            f"Struts(valid)={len(struts)}, "
            f"Unique Struts={metrics['unique_strut_count']}, "
            f"Global l/d n={metrics['global_l_over_d_count']}, "
            f"Node l/d valid nodes={metrics['node_l_over_d_valid_node_count']}, "
            f"Skipped(incomplete)={skipped_incomplete}, "
            f"Skipped(zero)={skipped_zero}, "
            f"Max connected per node={max_connected_found}, "
            f"Truncated nodes={truncation_count}"
        )

    # Summary 시트 서식
    set_summary_style(ws_summary)

    # 저장
    try:
        wb_out.save(OUTPUT_PATH)
        print(f"\n완료: {OUTPUT_PATH}")
    except PermissionError:
        print("[권한 오류] 저장할 파일이 열려 있으면 닫고 다시 실행하세요.")
    finally:
        wb_in.close()
        wb_formula.close()
        wb_out.close()


if __name__ == "__main__":
    main()