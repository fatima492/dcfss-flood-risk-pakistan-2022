"""
07 - LaTeX table bodies for the revised manuscript, generated from the result
tables so that every number printed in the paper is traceable to the code.
Output: results/latex/<name>.tex (the same text is inlined in sn-article.tex).
"""
from pathlib import Path
import json
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB, OUT = ROOT / "results" / "tables", ROOT / "results" / "latex"
OUT.mkdir(parents=True, exist_ok=True)
REG = ["AJ&K", "Balochistan", "GB", "ICT", "KP", "Punjab", "Sindh"]
UID = dict(zip(REG, [f"$u_{i}$" for i in range(1, 8)]))
tx = lambda s: str(s).replace("&", r"\&").replace("%", r"\%")
EPS = [rf"$\varepsilon_{j}$" for j in range(1, 8)]
STAGES = {"T1": "Impact stage ($T_1$)", "T2": "Relief stage ($T_2$)", "T3": "Recovery stage ($T_3$)"}

def write(name, lines):
    (OUT / f"{name}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

def f4(x): return f"{x:.4f}"
def f3(x): return f"{x:.3f}"
def intc(x): return f"{int(round(x)):,}".replace(",", "{,}")

# ---- raw data ---------------------------------------------------------------
raw = pd.read_csv(TAB / "T01_raw_data.csv", index_col=0)
sh = pd.read_csv(TAB / "T01b_regional_shares_percent.csv", index_col=0)
L = []
for r in REG:
    L.append(f"{UID[r]} & {tx(r)} & " + " & ".join(intc(v) for v in raw.loc[r]) + r" \\")
L.append(r"\midrule")
L.append(r"\multicolumn{2}{l}{National total} & " + " & ".join(intc(v) for v in raw.loc["Total"]) + r" \\")
L.append(r"\multicolumn{2}{l}{Largest regional share} & " +
         " & ".join(f"{tx(sh[c].idxmax())} {sh[c].max():.0f}\\%" for c in sh.columns) + r" \\")
write("tab_raw", L)

# ---- severity membership ----------------------------------------------------
mu = pd.read_csv(TAB / "T02_severity_membership.csv", index_col=0)
write("tab_mu", [f"{UID[r]} & {tx(r)} & " + " & ".join(f4(v) for v in mu.loc[r]) + r" \\" for r in REG])

# ---- cubic values (appendix) --------------------------------------------------
cub = pd.read_csv(TAB / "T03_cubic_values.csv", index_col=0)
L = []
for r in REG:
    cells = []
    for c in cub.columns:
        v = cub.loc[r, c]                    # "([a, b], m)"
        inner, m = v[1:-1].rsplit(", ", 1)
        cells.append(rf"$\begin{{matrix}}({inner},\\ {m})\end{{matrix}}$")
    L.append(f"{UID[r]} & {tx(r)} & " + " & ".join(cells) + r" \\[6pt]")
write("tab_cubic", L)

# ---- weights -----------------------------------------------------------------
w = pd.read_csv(TAB / "T04_stage_weights.csv")
glob = {f"e{j}": v for j, v in zip(range(1, 8), [0.25, 0.15, 0.10, 0.05, 0.15, 0.10, 0.20])}
L = ["Global weight $w(\\varepsilon)$ & " + " & ".join(f"{glob[f'e{j}']:.2f}" for j in range(1, 8)) + r" & 1.00 \\", r"\midrule"]
for s, lab in STAGES.items():
    d = w[w.stage == s].set_index("attribute")["stage_weight"]
    L.append(f"{lab}: $w_{{T_{s[1]}}}(\\varepsilon)$ & " +
             " & ".join(f4(d[f"e{j}"]) if f"e{j}" in d.index else "--" for j in range(1, 8)) + r" & 1.00 \\")
write("tab_weights", L)

# ---- revision of national totals -----------------------------------------------
rv = pd.read_csv(TAB / "T17_observed_revision_national_totals.csv")
rv["relative_revision"] = (rv.final_18Nov2022 - rv.snapshot_18Sep2022) / rv.snapshot_18Sep2022
names = ["Total deaths", "Total injured", "Roads damaged (km)", "Bridges damaged", "Houses damaged",
         "Livestock lost", "Affected population"]
L = []
for (_, r), nm, e in zip(rv.iterrows(), names, EPS):
    if pd.isna(r.final_18Nov2022):
        L.append(f"{e} & {nm} & {intc(r.snapshot_18Sep2022)} & about 33 million & n/a " + r"\\")
    else:
        L.append(f"{e} & {nm} & {intc(r.snapshot_18Sep2022)} & {intc(r.final_18Nov2022)} & "
                 f"{100*r.relative_revision:+.1f}\\% " + r"\\")
write("tab_revision", L)

# ---- stage results -------------------------------------------------------------
sr = pd.read_csv(TAB / "T05_stage_results.csv")
for s in STAGES:
    d = sr[sr.stage == s].set_index("region")
    L = []
    for r in REG:
        x = d.loc[r]
        L.append(f"{tx(r)} & " + " & ".join(
            f"{f4(x[f'dplus_{k}'])} & {f4(x[f'dminus_{k}'])} & {f4(x[f'SSI_{k}'])} & {int(x[f'rank_{k}'])}"
            for k in ("WED", "WHD", "WHHD")) +
            f" & [{f3(x.band_lower)}, {f3(x.band_upper)}] & {int(x.tier)}" + r" \\")
    write(f"tab_stage_{s}", L)

# ---- static vs stage ranks, stage-emphasis aggregate ----------------------------
c = pd.read_csv(TAB / "T26_static_vs_dynamic_ranks.csv", index_col=0)
dy = pd.read_csv(TAB / "T08_dynamic_stage_emphasis.csv", index_col=0)
L = []
for r in REG:
    def sh_(a, b):
        v = int(c.loc[r, a] - c.loc[r, b])        # positive = moved up in priority
        return "0" if v == 0 else f"${v:+d}$"
    L.append(f"{tx(r)} & {int(c.loc[r,'Static CFSS (all attributes)'])} & {int(c.loc[r,'DCFSS T1'])} & "
             f"{int(c.loc[r,'DCFSS T2'])} & {int(c.loc[r,'DCFSS T3'])} & "
             f"{sh_('DCFSS T1','DCFSS T3')} & " +
             " & ".join(f"{f3(dy.loc[r, p+' | index'])} ({int(dy.loc[r, p+' | rank'])})"
                        for p in ("Early response", "Balanced", "Transition", "Late recovery")) + r" \\")
write("tab_ranks_dynamic", L)

# ---- critical tolerances ---------------------------------------------------------
ct = pd.read_csv(TAB / "T07_critical_tolerances.csv")
L = []
for s in STAGES:
    d = ct[ct.stage == s]
    for k, (_, r) in enumerate(d.iterrows()):
        first = rf"\multirow{{{len(d)}}}{{*}}{{$T_{s[1]}$}}" if k == 0 else ""
        L.append(f"{first} & {k+1} / {k+2} & {tx(r.higher)} / {tx(r.lower)} & {f4(r.score_higher)} & {f4(r.score_lower)} & "
                 f"{100*r.critical_tolerance:.1f}\\% & {'yes' if r.separated_at_10pct else 'no'}" + r" \\")
    if s != "T3": L.append(r"\midrule")
write("tab_critical", L)

# ---- weight schemes ---------------------------------------------------------------
ws = pd.read_csv(TAB / "T10_weight_schemes.csv", index_col=0)
wr = pd.read_csv(TAB / "T11_ranking_under_weight_schemes.csv")
short = {"AJ&K": "A", "Balochistan": "B", "GB": "G", "ICT": "I", "KP": "K", "Punjab": "P", "Sindh": "S"}
def order_code(row): return "".join(short[r] for r in sorted(REG, key=lambda r: row[r]))
L = []
for nm in ws.index:
    v = ws.loc[nm] / ws.loc[nm].sum()
    cells = []
    for s in STAGES:
        row = wr[(wr.scheme == nm) & (wr.stage == s)].iloc[0]
        cells.append(f"{order_code(row)} & {row.spearman:.3f}")
    L.append(f"{tx(nm)} & " + " & ".join(f"{x:.3f}" for x in v) + " & " + " & ".join(cells) + r" \\")
write("tab_weight_schemes", L)

# ---- Monte Carlo summary ------------------------------------------------------------
mw = pd.read_csv(TAB / "T14_weights_monte_carlo.csv"); md = pd.read_csv(TAB / "T19_data_perturbation_monte_carlo.csv")
L = [r"\multicolumn{10}{l}{\textit{(a) Weights perturbed (data fixed)}} \\"]
lab = {"local +-10%": r"each weight $\pm10\%$", "local +-20%": r"each weight $\pm20\%$", "local +-30%": r"each weight $\pm30\%$",
       "local +-50%": r"each weight $\pm50\%$", "global (uniform simplex)": "any weights (uniform on simplex)"}
for sc in mw.scenario.unique():
    d = mw[mw.scenario == sc].set_index("stage")
    L.append(lab[sc] + " & " + " & ".join(
        f"{d.loc[s,'P_full_order_unchanged']:.3f} & {d.loc[s,'P_top1_unchanged']:.3f} & {d.loc[s,'mean_spearman']:.3f}"
        for s in STAGES) + r" \\")
L += [r"\midrule", r"\multicolumn{10}{l}{\textit{(b) Reported data perturbed (weights fixed)}} \\"]
for dl in md.delta.unique():
    d = md[md.delta == dl].set_index("stage")
    L.append(rf"each figure $\pm{int(dl*100)}\%$ & " + " & ".join(
        f"{d.loc[s,'P_full_order_unchanged']:.3f} & {d.loc[s,'P_top1_unchanged']:.3f} & {d.loc[s,'mean_spearman']:.3f}"
        for s in STAGES) + r" \\")
write("tab_montecarlo", L)

# ---- weight stability intervals --------------------------------------------------------
st = pd.read_csv(TAB / "T13_weight_stability_intervals.csv")
L = []
for s in STAGES:
    d = st[st.stage == s]
    for k, (_, r) in enumerate(d.iterrows()):
        first = rf"\multirow{{{len(d)}}}{{*}}{{$T_{s[1]}$}}" if k == 0 else ""
        lo = "0" if r.open_low else f3(r.stage_weight_low)
        hi = "1" if r.open_high else f3(r.stage_weight_high)
        L.append(f"{first} & $\\varepsilon_{r.attribute[1]}$ & {f3(r.baseline_stage_weight)} & [{lo}, {hi}]" + r" \\")
    if s != "T3": L.append(r"\midrule")
write("tab_stability", L)

# ---- tiers by tolerance ------------------------------------------------------------------
tr = pd.read_csv(TAB / "T16_priority_tiers_by_tolerance.csv")
L = []
for s in STAGES:
    d = tr[tr.stage == s]
    for k, (_, r) in enumerate(d.iterrows()):
        first = rf"\multirow{{{len(d)}}}{{*}}{{$T_{s[1]}$}}" if k == 0 else ""
        L.append(f"{first} & {int(r.delta*100)}\\% & " + " & ".join(str(int(r[x])) for x in REG) + f" & {int(r.n_tiers)}" + r" \\")
    if s != "T3": L.append(r"\midrule")
write("tab_tiers", L)

# ---- stage structure ------------------------------------------------------------------------
ss = pd.read_csv(TAB / "T20_stage_structure_sensitivity.csv")
ss = ss[ss.variant != "Baseline"]
def act(a): return ", ".join(rf"$\varepsilon_{x[1]}$" for x in a.split(","))
L = []
for _, r in ss.iterrows():
    if r.variant == "Disjoint stages" and r.stage != "T2":
        continue
    v = re.sub(r" \(removed from T\d\)", "", r.variant).replace("e3,e4", "e3, e4")   # short labels: one line per row
    for j in range(1, 8): v = v.replace(f"e{j}", rf"$\varepsilon_{j}$")
    for j in range(1, 4): v = v.replace(f"T{j}", rf"$T_{j}$")
    L.append(f"{v} & $T_{r.stage[1]}$ & {act(r.active)} & {order_code(r)} & {int(r.n_changed)} & {r.spearman:.3f}" + r" \\")
write("tab_stage_structure", L)

# ---- benchmarks --------------------------------------------------------------------------------
bm = pd.read_csv(TAB / "T24_benchmark_scores_and_ranks.csv"); ag = pd.read_csv(TAB / "T25_benchmark_agreement.csv")
meth = ["DCFSS-WHD", "DCFSS-WED", "DCFSS-WHHD", "SAW", "TOPSIS", "TOPSIS (vector norm.)", "VIKOR", "Entropy-TOPSIS"]
L = []
for mname in meth:
    cells = []
    for s in list(STAGES) + ["ALL"]:
        row = bm[(bm.stage == s) & (bm.method == mname)].iloc[0]
        a = ag[(ag.stage == s) & (ag.method == mname)].iloc[0]
        cells.append(f"{order_code(row)} & {a.spearman_vs_DCFSS_WHD:.3f}")
    L.append(f"{tx(mname)} & " + " & ".join(cells) + r" \\")
    if mname == "DCFSS-WHHD": L.append(r"\midrule")
write("tab_benchmarks", L)

# ---- crisp DSS -------------------------------------------------------------------------------------
ds = pd.read_csv(TAB / "T27_crisp_dynamic_soft_set_baseline.csv")
L = []
for thr in (0.25, 0.5):
    d = ds[ds.threshold == thr]
    for k, (_, r) in enumerate(d.iterrows()):
        first = rf"\multirow{{3}}{{*}}{{{thr:.2f}}}" if k == 0 else ""
        L.append(f"{first} & $T_{r.stage[1]}$ & " + " & ".join(str(int(r[x])) for x in REG) +
                 f" & {int(r.distinct_rank_levels)} & {int(r.regions_tied_at_zero)} & {r.spearman_vs_DCFSS:.3f}" + r" \\")
    if thr == 0.25: L.append(r"\midrule")
write("tab_crisp_dss", L)

# ---- ICT excluded -----------------------------------------------------------------------------------
ic = pd.read_csv(TAB / "T22_ICT_excluded.csv"); ic = ic[ic.distance == "WHD"]
L = []
for _, r in ic.iterrows():
    L.append(f"$T_{r.stage[1]}$ & " + " & ".join(f"{r['SSI_'+x]:.4f} ({int(r[x])})" for x in REG if x != "ICT") +
             f" & {'yes' if r.order_preserved else 'no'}" + r" \\")
write("tab_ict", L)

# ---- scalability ---------------------------------------------------------------------------------------
sc = pd.read_csv(TAB / "T29_scalability.csv")
L = []
for _, r in sc.iterrows():
    t = r.runtime_seconds
    ts = f"{1000*t:.1f} ms" if t < 1 else f"{t:.1f} s"
    L.append(f"{intc(r.alternatives_n)} & {int(r.attributes_m)} & {int(r.stages_T)} & {intc(r.cell_evaluations)} & {ts}" + r" \\")
write("tab_scalability", L)
print("LaTeX tables written:", sorted(p.name for p in OUT.glob("*.tex")))
