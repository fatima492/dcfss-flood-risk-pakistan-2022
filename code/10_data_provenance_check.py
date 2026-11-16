"""
10 - Provenance check of the input data against a primary NDMA source.

The case-study matrix (data/ndma_pakistan_floods_2022_snapshot.csv) is compared,
cell by cell, with the cumulative tables of NDMA Monsoon 2022 Daily SITREP
No. 099 dated 20 September 2022 (data/ndma_sitrep_099_2022-09-20.csv, transcribed
from the PDF of the report). The case-study totals correspond to the report of
18 September 2022 (No. 097), i.e. two days earlier, so cumulative figures are
expected to be equal or slightly lower.

NDMA footnotes in SITREP 099 that matter for the uncertainty analysis:
  * Balochistan livestock (500,000) is a tentative figure; 304,950 were confirmed.
  * PDMA Balochistan's tentative housing estimates (125,000 partially and 65,000
    fully damaged) differ from the tabulated figure.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
cols = ["deaths", "injured", "roads_km", "bridges", "houses", "livestock", "affected_population"]
a = pd.read_csv(ROOT / "data" / "ndma_pakistan_floods_2022_snapshot.csv").set_index("region")[cols]
b = pd.read_csv(ROOT / "data" / "ndma_sitrep_099_2022-09-20.csv").set_index("region")[cols]
assert list(a.index) == list(b.index)
# internal consistency of the transcription with the totals printed in SITREP 099
assert list(b.sum()) == [1569, 12860, 12716, 374, 2009794, 998407, 33046329]

diff = b - a
rows = []
for r in a.index:
    for c in cols:
        rows.append({"region": r, "indicator": c, "case_study_18Sep": int(a.loc[r, c]),
                     "sitrep099_20Sep": int(b.loc[r, c]), "difference": int(diff.loc[r, c]),
                     "relative_difference_pct": (round(100 * diff.loc[r, c] / a.loc[r, c], 2) if a.loc[r, c] else 0.0),
                     "identical": bool(diff.loc[r, c] == 0)})
out = pd.DataFrame(rows)
out.to_csv(ROOT / "results" / "tables" / "T30_data_provenance_check.csv", index=False)
n_same = int(out.identical.sum())
print(f"Cells identical to NDMA SITREP 099 (20 Sep 2022): {n_same} of {len(out)}")
print(out[~out.identical].to_string(index=False))
assert n_same == 41
# same ordering of regions on every indicator in both reports (ties ignored)
same_order = all((a[c].rank(method="min") == b[c].rank(method="min")).all() for c in cols)
print("Regional ordering identical on every indicator:", same_order)

# ---- do the stage rankings change when the later report is used? ------------------------------
from dcfss import load_problem, evaluate, spearman
P = load_problem(ROOT / "data" / "config_pakistan2022.json")
base = evaluate(P)
later = evaluate(P, X=b.loc[P.alternatives].to_numpy(dtype=float))
rk = []
for s in P.stages:
    r0, r1 = base[s]["rank"]["WHD"], later[s]["rank"]["WHD"]
    rk.append({"stage": s,
               "ranking_18Sep": " > ".join(P.alternatives[i] for i in np.argsort(r0, kind="stable")),
               "ranking_20Sep": " > ".join(P.alternatives[i] for i in np.argsort(r1, kind="stable")),
               "identical": bool((r0 == r1).all()), "spearman": spearman(r0, r1),
               "max_abs_change_in_SSI": float(np.abs(base[s]["ssi"]["WHD"] - later[s]["ssi"]["WHD"]).max())})
rk = pd.DataFrame(rk)
rk.round(4).to_csv(ROOT / "results" / "tables" / "T30b_rankings_with_later_report.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
print(rk.round(4).to_string(index=False))
