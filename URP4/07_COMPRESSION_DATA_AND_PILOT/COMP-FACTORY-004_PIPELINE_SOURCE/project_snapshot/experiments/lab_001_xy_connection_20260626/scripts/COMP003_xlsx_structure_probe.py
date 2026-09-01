from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def shared_strings(archive: zipfile.ZipFile, limit: int = 250_000) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in archive.namelist():
        return []
    values: list[str] = []
    with archive.open(name) as handle:
        for _, element in ET.iterparse(handle, events=("end",)):
            if element.tag == f"{{{NS_MAIN}}}si":
                values.append("".join(node.text or "" for node in element.iter(f"{{{NS_MAIN}}}t")))
                element.clear()
                if len(values) >= limit:
                    break
    return values


def cell_value(cell: ET.Element, strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value_node = cell.find(f"{{{NS_MAIN}}}v")
    inline = cell.find(f"{{{NS_MAIN}}}is")
    if inline is not None:
        return "".join(node.text or "" for node in inline.iter(f"{{{NS_MAIN}}}t"))
    if value_node is None or value_node.text is None:
        return ""
    raw = value_node.text
    if cell_type == "s":
        try:
            return strings[int(raw)]
        except (ValueError, IndexError):
            return f"<bad_shared_string:{raw}>"
    return raw


def inspect_workbook(path: Path, sample_rows: int) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rel_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rels = {
            node.attrib["Id"]: node.attrib["Target"]
            for node in rel_root.findall(f"{{{NS_PKG}}}Relationship")
        }
        strings = shared_strings(archive)
        sheets = []
        for sheet in workbook.find(f"{{{NS_MAIN}}}sheets") or []:
            rel_id = sheet.attrib[f"{{{NS_REL}}}id"]
            target = rels[rel_id].replace("\\", "/")
            if target.startswith("/"):
                xml_name = target.lstrip("/")
            elif target.startswith("xl/"):
                xml_name = target
            else:
                xml_name = f"xl/{target}"
            if xml_name not in names:
                sheets.append({"sheet": sheet.attrib["name"], "xml": xml_name, "status": "missing_xml"})
                continue
            dimension = ""
            row_samples: list[dict] = []
            row_count_seen = 0
            with archive.open(xml_name) as handle:
                for event, element in ET.iterparse(handle, events=("start", "end")):
                    if event == "start" and element.tag == f"{{{NS_MAIN}}}dimension":
                        dimension = element.attrib.get("ref", "")
                    if event == "end" and element.tag == f"{{{NS_MAIN}}}row":
                        row_count_seen += 1
                        if len(row_samples) < sample_rows:
                            values = {
                                cell.attrib.get("r", ""): cell_value(cell, strings)
                                for cell in element.findall(f"{{{NS_MAIN}}}c")
                            }
                            row_samples.append({"row": element.attrib.get("r", ""), "values": values})
                        element.clear()
                        if len(row_samples) >= sample_rows:
                            break
            sheets.append(
                {
                    "sheet": sheet.attrib["name"],
                    "xml": xml_name,
                    "dimension": dimension,
                    "sampled_physical_rows": row_count_seen,
                    "sample_rows": row_samples,
                }
            )
        return {
            "path": str(path),
            "bytes": path.stat().st_size,
            "shared_strings_loaded": len(strings),
            "sheets": sheets,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--sample-rows", type=int, default=8)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    results = [inspect_workbook(Path(item).resolve(), args.sample_rows) for item in args.files]
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = []
    for workbook in results:
        for sheet in workbook["sheets"]:
            rows.append(
                {
                    "path": workbook["path"],
                    "bytes": workbook["bytes"],
                    "sheet": sheet["sheet"],
                    "dimension": sheet.get("dimension", ""),
                    "sampled_physical_rows": sheet.get("sampled_physical_rows", ""),
                    "shared_strings_loaded": workbook["shared_strings_loaded"],
                    "sample_json": json.dumps(sheet.get("sample_rows", []), ensure_ascii=False),
                }
            )
    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
