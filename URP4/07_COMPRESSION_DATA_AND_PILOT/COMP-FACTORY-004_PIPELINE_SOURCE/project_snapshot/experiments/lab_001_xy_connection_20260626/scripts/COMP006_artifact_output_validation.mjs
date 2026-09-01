import fs from "node:fs/promises";
import path from "node:path";
import { Workbook } from "@oai/artifact-tool";

const files = process.argv.slice(2);
if (!files.length) throw new Error("provide one or more CSV files");
const results = [];
for (const file of files) {
  const csvText = await fs.readFile(file, "utf8");
  const workbook = await Workbook.fromCSV(csvText, { sheetName: "Data" });
  const inspection = await workbook.inspect({
    kind: "sheet,region",
    sheetId: "Data",
    range: "A1:H8",
    include: "id,name,values,formulas",
    maxChars: 5000,
    tableMaxRows: 8,
    tableMaxCols: 8,
  });
  results.push({
    file: path.resolve(file),
    bytes: Buffer.byteLength(csvText, "utf8"),
    inspection,
  });
}
process.stdout.write(JSON.stringify(results, null, 2));
