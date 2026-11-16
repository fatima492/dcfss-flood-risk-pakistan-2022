"""
08 - Collect every result table (results/tables/*.csv) into one Excel workbook,
results/DCFSS_results.xlsx, with an index sheet describing each table.
"""
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "results" / "tables"
DESC = {
 "T00_": "Original submission Tables 6-9 recomputed and compared with the published values",
 "T00b": "Constant scale factors between the original and the revised distances (rankings identical)",
 "T01_": "Raw NDMA data with national totals (manuscript Table 4)",
 "T01b": "Regional shares of the national totals, per cent",
 "T02_": "Severity memberships after min-max normalisation (manuscript Table 7)",
 "T03_": "Cubic values, tolerance 10 % (manuscript Table C1)",
 "T04_": "Global and stage weights (manuscript Table 5)",
 "T05_": "Stage results: distances to both references, indices, ranks, bands, tiers (Tables 8-10)",
 "T05b": "Consistency of the ranking rules across distances and reference points",
 "T06_": "Stage ranks and rank shifts between stages",
 "T07_": "Critical tolerances of adjacent ranks (manuscript Table 17)",
 "T08_": "Stage-emphasis aggregate for four emphasis profiles (manuscript Table 12)",
 "T08b": "Illustrative proportional shares of a stage budget (Section 9.1)",
 "T09_": "Stage-level set distances of the case-study DCFSS to the two references",
 "T10_": "Weight vectors of the six weighting schemes (manuscript Table 13)",
 "T11_": "Stage rankings under the six weighting schemes (manuscript Table 13)",
 "T12_": "One-at-a-time weight changes of +-20 % and +-50 %",
 "T13_": "Weight stability intervals (manuscript Table 14)",
 "T14_": "Monte Carlo over weights: probability that rankings are preserved (Table 15a)",
 "T14b": "Rank acceptability matrices, weights perturbed (Fig. 7a)",
 "T15_": "Indices and ranks for tolerances 0-30 %",
 "T16_": "Priority tiers by tolerance (manuscript Table 16)",
 "T17_": "Observed revision of NDMA national totals, 18 Sep -> 18 Nov 2022 (manuscript Table 6)",
 "T18_": "Rankings and tiers with indicator-specific tolerances",
 "T19_": "Monte Carlo over reported data: probability that rankings are preserved (Table 15b)",
 "T19b": "Rank acceptability matrices, data perturbed (Fig. 7b)",
 "T20_": "Sensitivity to the stage structure (manuscript Table 18)",
 "T21_": "Sensitivity to the normalisation rule",
 "T22_": "Analysis with ICT excluded (manuscript Table 11)",
 "T22b": "Severity memberships with ICT excluded",
 "T23_": "Rankings under nine distance / reference rules",
 "T24_": "Benchmark methods: scores and ranks (manuscript Table 20, Fig. 9)",
 "T25_": "Benchmark methods: agreement with the DCFSS ranking",
 "T26_": "Static model versus stage ranks (manuscript Table 12, Fig. 5)",
 "T27_": "Crisp dynamic soft set baseline (manuscript Table 19)",
 "T28_": "Stage-emphasis path from impact to recovery (Fig. 6)",
 "T29_": "Running time versus problem size (manuscript Table 21)",
 "T30_": "Input data compared cell by cell with NDMA SITREP No. 099 of 20 September 2022",
 "T30b": "Stage rankings recomputed with the figures of NDMA SITREP No. 099",
}
files = sorted(TAB.glob("*.csv"))
out = ROOT / "results" / "DCFSS_results.xlsx"
index = []
with pd.ExcelWriter(out, engine="openpyxl") as xw:
    pd.DataFrame({"placeholder": []}).to_excel(xw, sheet_name="Index", index=False)
    for i, f in enumerate(files, start=1):
        sheet = f.stem[:31]
        pd.read_csv(f).to_excel(xw, sheet_name=sheet, index=False)
        key = f.stem[:4]
        index.append({"Sheet": sheet, "File": f"results/tables/{f.name}",
                      "Content": DESC.get(key, DESC.get(f.stem[:4].rstrip("_") + "_", ""))})
wb = load_workbook(out)
ws = wb["Index"]; ws.delete_rows(1, 2)
ws.append(["Sheet", "File", "Content"])
for r in index: ws.append([r["Sheet"], r["File"], r["Content"]])
for s in wb.worksheets:
    for c in s[1]:
        c.font = Font(name="Arial", bold=True); c.fill = PatternFill("solid", fgColor="D9E2F3")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for col in s.columns:
        width = max(len(str(c.value)) if c.value is not None else 0 for c in col[:60])
        s.column_dimensions[col[0].column_letter].width = min(max(10, width + 2), 60)
    s.freeze_panes = "A2"
wb.save(out)
print("written", out, "with", len(files), "tables")
