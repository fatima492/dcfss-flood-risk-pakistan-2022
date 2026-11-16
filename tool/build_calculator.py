"""
Builds tool/DCFSS_Calculator.xlsx - a formula-driven spreadsheet implementation
of the DCFSS procedure, pre-sized for Pakistan's seven administrative units and
seven indicators. All results are live formulas: changing an input (data,
weights, tolerance, stage activation, stage emphasis) recalculates every ranking.

Run:  python tool/build_calculator.py     (then open the file in Excel / LibreOffice)
"""
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "ndma_pakistan_floods_2022_snapshot.csv")
REG = df.region.tolist()
ATT = ["Total deaths", "Total injured", "Roads damaged (km)", "Bridges damaged", "Houses damaged",
       "Livestock lost", "Affected population"]
COLS = ["deaths", "injured", "roads_km", "bridges", "houses", "livestock", "affected_population"]
W = [0.25, 0.15, 0.10, 0.05, 0.15, 0.10, 0.20]
ACT = {"T1 Impact": [1, 1, 0, 0, 0, 0, 0], "T2 Relief": [0, 1, 1, 1, 1, 0, 0], "T3 Recovery": [0, 0, 0, 0, 1, 1, 1]}
n, m = 7, 7

F = "Arial"
f_norm, f_bold = Font(name=F, size=10), Font(name=F, size=10, bold=True)
f_title = Font(name=F, size=14, bold=True)
f_in = Font(name=F, size=10, color="0000FF")
f_link = Font(name=F, size=10, color="008000")
fill_in = PatternFill("solid", fgColor="FFFF00")
fill_hd = PatternFill("solid", fgColor="D9E2F3")
fill_res = PatternFill("solid", fgColor="E2EFDA")
thin = Side(style="thin", color="BFBFBF"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook()
# ------------------------------------------------------------------ Guide
g = wb.active; g.title = "Guide"
guide = [
 ("DCFSS Calculator - stage-wise flood severity and priority ranking", f_title),
 ("", f_norm),
 ("What this workbook does", f_bold),
 ("It turns a region-by-indicator loss table (for example one NDMA situation report) into stage-wise priority rankings "
  "for the Impact, Relief and Recovery stages, with an uncertainty band around every score.", f_norm),
 ("", f_norm),
 ("How to use it", f_bold),
 ("1. Go to sheet 'Inputs'. Yellow cells with blue text are the only cells you edit.", f_norm),
 ("2. Type the reported figures for each region. Rename regions or indicators if needed (seven of each).", f_norm),
 ("3. For each indicator choose 'loss' (larger value = worse, e.g. deaths) or 'capacity' (larger value = better, e.g. relief coverage).", f_norm),
 ("4. Enter the importance weight of each indicator (any positive numbers; they are rescaled automatically).", f_norm),
 ("5. Enter the reporting tolerance (0.10 means the reported figures may be wrong by about 10 %).", f_norm),
 ("6. In the stage table put 1 where an indicator matters for a stage and 0 where it does not.", f_norm),
 ("7. Read the rankings on sheet 'Results'. Sheet 'Calc' shows every intermediate step.", f_norm),
 ("", f_norm),
 ("How to read the results", f_bold),
 ("Severity index: 0 = no reported loss, 1 = worst region on every active indicator. Rank 1 = highest priority.", f_norm),
 ("Band: the range of the score if the reported figures are wrong by up to the tolerance.", f_norm),
 ("Tier: regions whose bands overlap share a tier and should be treated as equal priority.", f_norm),
 ("", f_norm),
 ("Colour code", f_bold),
 ("Yellow fill, blue text = input you may change.   Black = formula.   Green = value linked from another sheet.", f_norm),
 ("", f_norm),
 ("Source of the example data", f_bold),
 ("NDMA Pakistan, cumulative monsoon losses 14 June - 18 September 2022 (daily situation report of 18 September 2022), "
  "as distributed in the Kaggle dataset 'Pakistan Flood 2022 Data by NDMA'. Weights: illustrative baseline weights of the manuscript (Table 5), "
  "assigned by the authors; replace them with weights agreed by your agency.", f_norm),
 ("Method: revised manuscript, Sections 4-6. The same numbers are produced by code/dcfss_tool.py.", f_norm),
]
for i, (t, f) in enumerate(guide, start=1):
    c = g.cell(row=i, column=1, value=t); c.font = f; c.alignment = Alignment(wrap_text=True, vertical="top")
g.column_dimensions["A"].width = 125

# ------------------------------------------------------------------ Inputs
s = wb.create_sheet("Inputs")
s["A1"] = "Inputs (edit yellow cells only)"; s["A1"].font = f_title
s["A3"] = "Region"; s["A3"].font = f_bold; s["A3"].fill = fill_hd
R0, C0 = 4, 2                       # data block starts B4
for j, a in enumerate(ATT):
    c = s.cell(row=3, column=C0 + j, value=a); c.font = f_in; c.fill = fill_in; c.border = BOX
    c.alignment = Alignment(wrap_text=True, horizontal="center")
for i, r in enumerate(REG):
    c = s.cell(row=R0 + i, column=1, value=r); c.font = f_in; c.fill = fill_in; c.border = BOX
    for j, col in enumerate(COLS):
        c = s.cell(row=R0 + i, column=C0 + j, value=float(df.loc[i, col]))
        c.font = f_in; c.fill = fill_in; c.border = BOX; c.number_format = "#,##0"
rT = R0 + n                          # 11 totals
s.cell(row=rT, column=1, value="Total").font = f_bold
for j in range(m):
    L = CL(C0 + j)
    c = s.cell(row=rT, column=C0 + j, value=f"=SUM({L}{R0}:{L}{R0+n-1})"); c.font = f_bold; c.number_format = "#,##0"
rType, rW, rWn = 13, 14, 15
s.cell(row=rType, column=1, value="Type (loss / capacity)").font = f_bold
s.cell(row=rW, column=1, value="Weight (importance)").font = f_bold
s.cell(row=rWn, column=1, value="Weight, rescaled to sum 1").font = f_bold
for j in range(m):
    L = CL(C0 + j)
    c = s.cell(row=rType, column=C0 + j, value="loss"); c.font = f_in; c.fill = fill_in; c.border = BOX
    c = s.cell(row=rW, column=C0 + j, value=W[j]); c.font = f_in; c.fill = fill_in; c.border = BOX; c.number_format = "0.00"
    c = s.cell(row=rWn, column=C0 + j, value=f"={L}{rW}/SUM($B${rW}:$H${rW})"); c.font = f_norm; c.number_format = "0.0000"
rTol = 17
s.cell(row=rTol, column=1, value="Reporting tolerance (delta)").font = f_bold
c = s.cell(row=rTol, column=2, value=0.10); c.font = f_in; c.fill = fill_in; c.border = BOX; c.number_format = "0%"
s.cell(row=rTol, column=3, value="Baseline 10 %: order of magnitude of the revisions of NDMA national totals between "
       "18 Sep and 18 Nov 2022 (0-23 %, mean 12 %).").font = f_norm
rA = 20
s.cell(row=rA - 1, column=1, value="Stage activation (1 = indicator is active in the stage, 0 = not active)").font = f_bold
for k, (st, row) in enumerate(ACT.items()):
    s.cell(row=rA + k, column=1, value=st).font = f_bold
    for j in range(m):
        c = s.cell(row=rA + k, column=C0 + j, value=row[j]); c.font = f_in; c.fill = fill_in; c.border = BOX
rLam = 25
s.cell(row=rLam - 1, column=1, value="Stage emphasis for the combined index (any non-negative numbers)").font = f_bold
for k, (st, v) in enumerate(zip(ACT, [1, 1, 1])):
    s.cell(row=rLam + k, column=1, value=st).font = f_bold
    c = s.cell(row=rLam + k, column=2, value=v); c.font = f_in; c.fill = fill_in; c.border = BOX
s.cell(row=rLam, column=3, value="Example: 6, 3, 1 in the first days of the response; 1, 2, 7 during reconstruction.").font = f_norm
s.column_dimensions["A"].width = 30
for j in range(m): s.column_dimensions[CL(C0 + j)].width = 16
s.row_dimensions[3].height = 30

# ------------------------------------------------------------------ Calc
c_ = wb.create_sheet("Calc")
c_["A1"] = "Step-by-step calculation (formulas only - do not edit)"; c_["A1"].font = f_title
def header(row, title):
    c_.cell(row=row, column=1, value=title).font = f_bold
    for j in range(m):
        x = c_.cell(row=row, column=C0 + j, value=f"=Inputs!{CL(C0+j)}3"); x.font = f_link; x.fill = fill_hd
        x.alignment = Alignment(wrap_text=True, horizontal="center")
def block(row0, title, fn):
    header(row0, title)
    for i in range(n):
        x = c_.cell(row=row0 + 1 + i, column=1, value=f"=Inputs!A{R0+i}"); x.font = f_link
        for j in range(m):
            y = c_.cell(row=row0 + 1 + i, column=C0 + j, value=fn(i, j)); y.font = f_norm; y.number_format = "0.0000"
MU0, L0, U0 = 3, 13, 23             # header rows of the three blocks; data rows +1..+7
def mu_f(i, j):
    L = CL(C0 + j); x = f"Inputs!{L}{R0+i}"; rng = f"Inputs!{L}${R0}:{L}${R0+n-1}"
    return (f'=IF(MAX({rng})-MIN({rng})=0,0,IF(Inputs!{L}${rType}="capacity",'
            f'(MAX({rng})-{x})/(MAX({rng})-MIN({rng})),({x}-MIN({rng}))/(MAX({rng})-MIN({rng}))))')
block(MU0, "Step 1  Severity membership (mu): 1 = most severe region", mu_f)
block(L0, "Step 2a  Lower bound = max(0, (1 - delta) x mu)",
      lambda i, j: f"=MAX(0,(1-Inputs!$B${rTol})*{CL(C0+j)}{MU0+1+i})")
block(U0, "Step 2b  Upper bound = min(1, (1 + delta) x mu)",
      lambda i, j: f"=MIN(1,(1+Inputs!$B${rTol})*{CL(C0+j)}{MU0+1+i})")
SW0 = 33
header(SW0, "Step 3  Stage weights (active weights rescaled to sum 1)")
for k, st in enumerate(ACT):
    c_.cell(row=SW0 + 1 + k, column=1, value=f"=Inputs!A{rA+k}").font = f_link
    for j in range(m):
        L = CL(C0 + j)
        y = c_.cell(row=SW0 + 1 + k, column=C0 + j,
                    value=f"=Inputs!{L}{rA+k}*Inputs!{L}{rW}/SUMPRODUCT(Inputs!$B${rA+k}:$H${rA+k},Inputs!$B${rW}:$H${rW})")
        y.font = f_norm; y.number_format = "0.0000"
# Step 4-5 per stage
HDR = ["Region", "d+ WED", "d- WED", "SSI WED", "d+ WHD", "d- WHD", "SSI WHD", "d+ WHHD", "d- WHHD", "SSI WHHD",
       "Band lower", "Band centre", "Band upper", "Rank (WHD)", "Sort key"]
ST0 = {}
for k, st in enumerate(ACT):
    r0 = 39 + k * 11; ST0[st] = r0
    c_.cell(row=r0, column=1, value=f"Steps 4-5  Distances to the worst-case (d+) and no-loss (d-) references, stage: {st}").font = f_bold
    for q, h in enumerate(HDR):
        x = c_.cell(row=r0 + 1, column=1 + q, value=h); x.font = f_bold; x.fill = fill_hd
    ws = f"$B${SW0+1+k}:$H${SW0+1+k}"
    for i in range(n):
        r = r0 + 2 + i
        Lr, Ur, Mr = (f"$B${L0+1+i}:$H${L0+1+i}", f"$B${U0+1+i}:$H${U0+1+i}", f"$B${MU0+1+i}:$H${MU0+1+i}")
        vals = [f"=Inputs!A{R0+i}",
                f"=SQRT((SUMPRODUCT({ws},(1-{Lr})^2)+SUMPRODUCT({ws},(1-{Ur})^2)+SUMPRODUCT({ws},(1-{Mr})^2))/3)",
                f"=SQRT((SUMPRODUCT({ws},{Lr}^2)+SUMPRODUCT({ws},{Ur}^2)+SUMPRODUCT({ws},{Mr}^2))/3)",
                f"=IF(B{r}+C{r}=0,0,C{r}/(B{r}+C{r}))",
                f"=(SUMPRODUCT({ws},1-{Lr})+SUMPRODUCT({ws},1-{Ur})+SUMPRODUCT({ws},1-{Mr}))/3",
                f"=(SUMPRODUCT({ws},{Lr})+SUMPRODUCT({ws},{Ur})+SUMPRODUCT({ws},{Mr}))/3",
                f"=IF(E{r}+F{r}=0,0,F{r}/(E{r}+F{r}))",
                f"=SUMPRODUCT({ws},1-{Lr})",          # max component difference to ([1,1],1) is 1 - lower bound
                f"=SUMPRODUCT({ws},{Ur})",            # max component difference to ([0,0],0) is the upper bound
                f"=IF(H{r}+I{r}=0,0,I{r}/(H{r}+I{r}))",
                f"=SUMPRODUCT({ws},{Lr})", f"=SUMPRODUCT({ws},{Mr})", f"=SUMPRODUCT({ws},{Ur})",
                f"=RANK(G{r},$G${r0+2}:$G${r0+1+n},0)",
                f"=L{r}-ROW()*0.000000001"]
        for q, v in enumerate(vals):
            x = c_.cell(row=r, column=1 + q, value=v); x.font = f_link if q == 0 else f_norm
            if 0 < q < 13 or q == 14: x.number_format = "0.0000"
c_.column_dimensions["A"].width = 44
for q in range(2, 17): c_.column_dimensions[CL(q)].width = 13
c_.cell(row=72, column=1, value="Note: because lower <= reported <= upper for every cubic value, the largest component "
        "difference to ([1,1],1) is 1 - lower bound and to ([0,0],0) it is the upper bound (WHHD columns).").font = f_norm

# ------------------------------------------------------------------ Results
r_ = wb.create_sheet("Results")
r_["A1"] = "Results - stage-wise priority ranking"; r_["A1"].font = f_title
r_["A2"] = "Sorted from highest to lowest priority. Regions in the same tier have overlapping bands: treat them as equal priority."
r_["A2"].font = f_norm
RH = ["Priority", "Region", "Severity index (WHD)", "Band lower", "Band upper", "Tier", "Index (WED)", "Index (WHHD)"]
RES0 = {}
for k, st in enumerate(ACT):
    r0 = 4 + k * 11; RES0[st] = r0; c0 = ST0[st]
    x = r_.cell(row=r0, column=1, value=f"=Inputs!A{rA+k}"); x.font = f_bold
    for q, h in enumerate(RH):
        x = r_.cell(row=r0 + 1, column=1 + q, value=h); x.font = f_bold; x.fill = fill_res; x.border = BOX
        x.alignment = Alignment(wrap_text=True, horizontal="center")
    key = f"Calc!$O${c0+2}:$O${c0+1+n}"
    def pick(col, r): return f"=INDEX(Calc!${col}${c0+2}:${col}${c0+1+n},MATCH(LARGE({key},A{r}),{key},0))"
    for i in range(n):
        r = r0 + 2 + i
        vals = [i + 1, pick("A", r), pick("G", r), pick("K", r), pick("M", r),
                1 if i == 0 else f"=F{r-1}+IF(D{r-1}>E{r}+0.000000000001,1,0)",
                pick("D", r), pick("J", r)]
        for q, v in enumerate(vals):
            x = r_.cell(row=r, column=1 + q, value=v); x.font = f_norm; x.border = BOX
            if q in (2, 3, 4, 6, 7): x.number_format = "0.000"
rc = 4 + 3 * 11
r_.cell(row=rc, column=1, value="Combined index over stages (weighted by the stage emphasis on sheet 'Inputs')").font = f_bold
for q, h in enumerate(["Region", "Combined index", "Rank"]):
    x = r_.cell(row=rc + 1, column=1 + q, value=h); x.font = f_bold; x.fill = fill_res; x.border = BOX
lam = [f"Inputs!$B${rLam+k}" for k in range(3)]
for i in range(n):
    r = rc + 2 + i
    terms = "+".join(f"{lam[k]}*Calc!G{ST0[st]+2+i}" for k, st in enumerate(ACT))
    x = r_.cell(row=r, column=1, value=f"=Inputs!A{R0+i}"); x.font = f_link; x.border = BOX
    x = r_.cell(row=r, column=2, value=f"=({terms})/SUM(Inputs!$B${rLam}:$B${rLam+2})"); x.font = f_norm; x.number_format = "0.000"; x.border = BOX
    x = r_.cell(row=r, column=3, value=f"=RANK(B{r},$B${rc+2}:$B${rc+1+n},0)"); x.font = f_norm; x.border = BOX
r_.column_dimensions["A"].width = 12; r_.column_dimensions["B"].width = 18
for q in range(3, 9): r_.column_dimensions[CL(q)].width = 15
for st in RES0: r_.row_dimensions[RES0[st] + 1].height = 30

out = ROOT / "tool" / "DCFSS_Calculator.xlsx"
wb.save(out); print("saved", out)
