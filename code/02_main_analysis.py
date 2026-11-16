"""
02 - Main DCFSS analysis of the Pakistan 2022 flood data.

Produces: normalised severity memberships, cubic values, stage weights,
distances to both references, stage severity indices (SSI), stage rankings,
uncertainty bands, priority tiers, critical tolerances, regional shares of the
national totals, the worked example, and the dynamic (stage-emphasis) aggregate.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from dcfss import (load_problem, evaluate, priority_tiers, critical_tolerance,
                   dynamic_index, rank_desc, set_distances, cubic_values, DISTANCES)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"
P = load_problem(ROOT / "data" / "config_pakistan2022.json")
R = P.alternatives
res = evaluate(P)
mu = res["_mu"]
KEY = {}          # key numbers quoted in the manuscript text

# --- T01 raw data and regional shares ---------------------------------------
raw = pd.DataFrame(P.X, index=R, columns=[P.labels[a] for a in P.attributes])
raw.loc["Total"] = raw.sum()
raw.to_csv(OUT / "T01_raw_data.csv")
share = pd.DataFrame(100 * P.X / P.X.sum(axis=0), index=R, columns=P.attributes).round(1)
share.to_csv(OUT / "T01b_regional_shares_percent.csv")
KEY["shares_percent"] = share.to_dict()
KEY["totals"] = dict(zip(P.attributes, P.X.sum(axis=0).tolist()))

# --- T02 severity memberships, T03 cubic values ------------------------------
pd.DataFrame(mu, index=R, columns=P.attributes).round(6).to_csv(OUT / "T02_severity_membership.csv")
L, U, M = cubic_values(mu, P.delta_vector())
cub = pd.DataFrame({a: [f"([{L[i,j]:.4f}, {U[i,j]:.4f}], {M[i,j]:.4f})" for i in range(P.n)]
                    for j, a in enumerate(P.attributes)}, index=R)
cub.to_csv(OUT / "T03_cubic_values.csv")

# --- T04 weights -------------------------------------------------------------
wrows = []
for s in P.stages:
    for a, w in zip(P.stages[s], res[s]["weights"]):
        wrows.append({"stage": s, "attribute": a, "label": P.labels[a],
                      "global_weight": P.weights[a], "stage_weight": round(float(w), 4)})
pd.DataFrame(wrows).to_csv(OUT / "T04_stage_weights.csv", index=False)

# --- T05 stage results --------------------------------------------------------
rows = []
for s in P.stages:
    e = res[s]
    lo, mid, hi = e["band"]
    tiers = priority_tiers(lo, mid, hi)
    for i, r in enumerate(R):
        row = {"stage": s, "region": r}
        for k in DISTANCES:
            row[f"dplus_{k}"] = e["d_plus"][k][i]
            row[f"dminus_{k}"] = e["d_minus"][k][i]
            row[f"SSI_{k}"] = e["ssi"][k][i]
            row[f"rank_{k}"] = int(e["rank"][k][i])
            row[f"rank_dplus_only_{k}"] = int(e["rank_dplus"][k][i])
        row.update({"band_lower": lo[i], "band_central": mid[i], "band_upper": hi[i],
                    "tier": int(tiers[i])})
        rows.append(row)
stage_df = pd.DataFrame(rows)
stage_df.round(6).to_csv(OUT / "T05_stage_results.csv", index=False)

# consistency of rankings across distances and between single- and two-reference rules
cons = []
for s in P.stages:
    e = res[s]
    base = e["rank"]["WHD"]
    cons.append({"stage": s,
                 "WED_equals_WHD": bool((e["rank"]["WED"] == base).all()),
                 "WHHD_equals_WHD": bool((e["rank"]["WHHD"] == base).all()),
                 **{f"dplus_only_equals_SSI_{k}": bool((e["rank_dplus"][k] == e["rank"][k]).all())
                    for k in DISTANCES},
                 "WHD_dplus_plus_dminus_equals_1": bool(np.allclose(e["d_plus"]["WHD"] + e["d_minus"]["WHD"], 1))})
cons = pd.DataFrame(cons)
cons.to_csv(OUT / "T05b_ranking_consistency.csv", index=False)

# --- T06 rank matrix and stage shifts ----------------------------------------
rk = pd.DataFrame({s: res[s]["rank"]["WHD"] for s in P.stages}, index=R)
rk["shift_T1_to_T2"] = rk["T1"] - rk["T2"]
rk["shift_T2_to_T3"] = rk["T2"] - rk["T3"]
rk["shift_T1_to_T3"] = rk["T1"] - rk["T3"]
rk.to_csv(OUT / "T06_stage_ranks_and_shifts.csv")

# --- T07 critical tolerances between adjacent ranks ---------------------------
crit = []
for s in P.stages:
    idx = [P.col(a) for a in P.stages[s]]
    w = res[s]["weights"]
    mid = res[s]["band"][1]
    order = np.argsort(-mid, kind="stable")
    for a, b in zip(order[:-1], order[1:]):
        dstar = critical_tolerance(mu[a, idx], mu[b, idx], w)
        closed = (mid[a] - mid[b]) / (mid[a] + mid[b]) if (mid[a] + mid[b]) > 0 else np.nan
        crit.append({"stage": s, "higher": R[a], "lower": R[b],
                     "score_higher": mid[a], "score_lower": mid[b],
                     "critical_tolerance": dstar, "closed_form_uncapped": closed,
                     "separated_at_10pct": bool(dstar > 0.10)})
crit = pd.DataFrame(crit)
crit.round(6).to_csv(OUT / "T07_critical_tolerances.csv", index=False)

# --- T08 dynamic (stage-emphasis) aggregate -----------------------------------
stage_scores = {s: res[s]["ssi"]["WHD"] for s in P.stages}
dyn = pd.DataFrame(index=R)
for name, lam in P.profiles.items():
    v = dynamic_index(stage_scores, lam)
    dyn[f"{name} | index"] = v
    dyn[f"{name} | rank"] = rank_desc(v)
dyn.round(6).to_csv(OUT / "T08_dynamic_stage_emphasis.csv")

# --- T08b illustrative proportional shares of a stage budget ---------------------
alloc = pd.DataFrame({s: 100 * res[s]["ssi"]["WHD"] / res[s]["ssi"]["WHD"].sum() for s in P.stages}, index=R)
alloc.round(1).to_csv(OUT / "T08b_illustrative_proportional_shares.csv")
KEY["proportional_shares_percent"] = alloc.round(1).to_dict()

# --- T09 stage-level set distances to the two references ----------------------
setd = []
for s in P.stages:
    e = res[s]
    F = (e["L"], e["U"], e["M"])
    one = (np.ones_like(e["L"]),) * 3
    zero = (np.zeros_like(e["L"]),) * 3
    dp, dm = set_distances(F, one, e["weights"]), set_distances(F, zero, e["weights"])
    setd.append({"stage": s, **{f"D_plus_{k}": dp[k] for k in DISTANCES},
                 **{f"D_minus_{k}": dm[k] for k in DISTANCES}})
pd.DataFrame(setd).round(6).to_csv(OUT / "T09_stage_level_set_distances.csv", index=False)

# --- worked example (Punjab at T1) --------------------------------------------
i = R.index("Punjab"); s = "T1"; idx = [P.col(a) for a in P.stages[s]]
e = res[s]
ex = {"region": "Punjab", "stage": s,
      "raw": {a: float(P.X[i, P.col(a)]) for a in P.stages[s]},
      "min": {a: float(P.X[:, P.col(a)].min()) for a in P.stages[s]},
      "max": {a: float(P.X[:, P.col(a)].max()) for a in P.stages[s]},
      "mu": {a: float(mu[i, P.col(a)]) for a in P.stages[s]},
      "L": e["L"][i].tolist(), "U": e["U"][i].tolist(),
      "stage_weights": e["weights"].tolist(),
      "d_plus": {k: float(e["d_plus"][k][i]) for k in DISTANCES},
      "d_minus": {k: float(e["d_minus"][k][i]) for k in DISTANCES},
      "SSI": {k: float(e["ssi"][k][i]) for k in DISTANCES},
      "rank": {k: int(e["rank"][k][i]) for k in DISTANCES},
      "band": [float(b[i]) for b in e["band"]]}
KEY["worked_example"] = ex
KEY["stage_ranking_WHD"] = {s: [R[j] for j in np.argsort(res[s]["rank"]["WHD"])] for s in P.stages}
KEY["tiers"] = {s: stage_df[stage_df.stage == s].set_index("region")["tier"].to_dict() for s in P.stages}
(ROOT / "results" / "key_numbers_main.json").write_text(json.dumps(KEY, indent=2), encoding="utf-8")

# --- console summary ----------------------------------------------------------
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40)
print("Severity memberships\n", pd.DataFrame(mu, index=R, columns=P.attributes).round(4))
for s in P.stages:
    d = stage_df[stage_df.stage == s].set_index("region")
    print(f"\n=== {s} ({P.stage_labels[s]}), active {P.stages[s]}, weights {np.round(res[s]['weights'],4)}")
    print(d[["dplus_WED","dminus_WED","SSI_WED","rank_WED","dplus_WHD","dminus_WHD","SSI_WHD","rank_WHD",
             "dplus_WHHD","dminus_WHHD","SSI_WHHD","rank_WHHD","band_lower","band_upper","tier"]].round(4))
print("\nConsistency\n", cons.T)
print("\nRanks and shifts\n", rk)
print("\nCritical tolerances\n", crit.round(4))
print("\nDynamic aggregate\n", dyn.round(4))
print("\nShares (%)\n", share)
print("\nProportional stage shares (%)\n", alloc.round(1))
print("\nWorked example\n", json.dumps(ex, indent=1))
