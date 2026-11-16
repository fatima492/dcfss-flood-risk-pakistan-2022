"""
01 - Reproduce the tables of the ORIGINAL submission (Tables 6-9) exactly.

The original manuscript computed, for each region u and stage tau,

    WED_old  = sqrt( (1/(3n)) * sum_{eps in A_tau} w_eps * (dL^2 + dU^2 + dM^2) )
    WHD_old  =        (1/(3n)) * sum_{eps in A_tau} w_eps * (dL + dU + dM)
    WHHD_old =        (1/(3n)) * sum_{eps in A_tau} w_eps * max(dL, dU, dM)

with n = 7 (number of regions), the GLOBAL weights (not renormalised within the
stage) and the reference ([1,1],1). This script regenerates those numbers and
checks them against the published values, then shows that the revised
(normalised) distances are a positive constant multiple of the old ones in each
stage, so every published ranking is preserved.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from dcfss import load_problem, severity_membership, cubic_values, evaluate, rank_asc

ROOT = Path(__file__).resolve().parents[1]
P = load_problem(ROOT / "data" / "config_pakistan2022.json")
OUT = ROOT / "results" / "tables"

# Published values (original manuscript, Tables 6-9), order: AJ&K ... Sindh
PUBLISHED = {
 "T1": {"WED": [0.2286,0.1782,0.2344,0.2390,0.1744,0.1576,0.0138],
        "WHD": [0.0546,0.0410,0.0560,0.0571,0.0401,0.0373,0.0019],
        "WHHD":[0.0183,0.0142,0.0187,0.0190,0.0139,0.0131,0.0019]},
 "T2": {"WED": [0.2533,0.2332,0.2443,0.2535,0.2217,0.2082,0.0146],
        "WHD": [0.0642,0.0589,0.0614,0.0643,0.0549,0.0514,0.0021],
        "WHHD":[0.0214,0.0198,0.0206,0.0214,0.0186,0.0176,0.0021]},
 "T3": {"WED": [0.2530,0.1544,0.2531,0.2535,0.2153,0.1937,0.0691],
        "WHD": [0.0642,0.0316,0.0642,0.0643,0.0540,0.0481,0.0098],
        "WHHD":[0.0214,0.0115,0.0214,0.0214,0.0183,0.0166,0.0046]},
 "ALL":{"WED": [0.3710,0.2639,0.3685,0.3779,0.2951,0.2820,0.0709],
        "WHD": [0.1401,0.0899,0.1387,0.1428,0.1082,0.1046,0.0123],
        "WHHD":[0.0468,0.0315,0.0463,0.0476,0.0372,0.0361,0.0071]},
}

types = [P.types[a] for a in P.attributes]
mu = severity_membership(P.X, types, "minmax")
L, U, M = cubic_values(mu, 0.10)
w = P.w_vector()
n = P.n
stages = dict(P.stages); stages["ALL"] = list(P.attributes)

rows, max_dev, OLD = [], 0.0, {}
for s, active in stages.items():
    idx = [P.col(a) for a in active]
    a, b, c = 1 - L[:, idx], 1 - U[:, idx], 1 - M[:, idx]
    ww = w[idx]                                   # global weights, NOT renormalised
    old = {"WED": np.sqrt(((a**2 + b**2 + c**2) * ww).sum(1) / (3 * n)),
           "WHD": ((a + b + c) * ww).sum(1) / (3 * n),
           "WHHD": (np.maximum(np.maximum(a, b), c) * ww).sum(1) / (3 * n)}
    OLD[s] = old
    for k, v in old.items():
        pub = np.array(PUBLISHED[s][k])
        dev = np.abs(v - pub).max()
        max_dev = max(max_dev, dev)
        for i, r in enumerate(P.alternatives):
            rows.append({"stage": s, "distance": k, "region": r,
                         "recomputed": round(float(v[i]), 4), "published": pub[i],
                         "abs_diff": round(float(abs(v[i] - pub[i])), 5),
                         "rank_recomputed": int(rank_asc(v)[i])})

df = pd.DataFrame(rows)
df.to_csv(OUT / "T00_reproduction_of_original_tables.csv", index=False)
print(f"Maximum |recomputed - published| over all 84 published scores: {max_dev:.5f}")
print("Scores differing by more than 0.00015 (rounding of published cubic values):")
print(df[df.abs_diff > 0.00015].to_string(index=False) if (df.abs_diff > 0.00015).any() else "  none")

# Relation between original and revised distances to the maximal-severity reference
res = evaluate(P)
print("\nScale factor revised/original distance to ([1,1],1) per stage (constant across regions):")
rel = []
for s in P.stages:
    idx = [P.col(a) for a in P.stages[s]]
    W = w[idx].sum()
    for k, fac in (("WED", np.sqrt(n / W)), ("WHD", n / W), ("WHHD", 3 * n / W)):
        new = res[s]["d_plus"][k]
        ratio = new / OLD[s][k]
        same_rank = bool((rank_asc(new) == rank_asc(OLD[s][k])).all())
        assert np.allclose(ratio, fac), (s, k, ratio)
        rel.append({"stage": s, "distance": k, "stage_weight_sum": W,
                    "theoretical_factor": round(float(fac), 4), "ranking_identical": same_rank})
rel = pd.DataFrame(rel)
rel.to_csv(OUT / "T00b_original_vs_revised_scale_factors.csv", index=False)
print(rel.to_string(index=False))
assert max_dev < 6e-4, "original tables not reproduced"
assert rel.ranking_identical.all()
print("\nOK: original Tables 6-9 reproduced; all original rankings preserved by the revised distances.")
