"""
03 - Robustness and sensitivity analysis (Reviewer 2: comments 4-6, 8; Reviewer 4: comment 2).

A. Attribute weights      : alternative schemes, one-at-a-time changes, stability
                            intervals, Monte Carlo over the weight space.
B. Interval tolerance     : uniform delta in {0,...,30 %}, data-informed heterogeneous
                            delta, Monte Carlo perturbation of the raw data.
C. Stage structure        : leave-one-attribute-out, reassignment of shared attributes,
                            alternative stage mappings.
D. Normalisation          : min-max, max, sum, vector.
E. Trivial dominance      : exclusion of ICT (all-zero profile).
F. Distance / reference   : nine rankings per stage, Kendall's W.
G. Data revision          : observed revision of NDMA national totals (18 Sep -> 18 Nov 2022).
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from dcfss import (load_problem, evaluate, rank_desc, spearman, kendall, kendall_w,
                   priority_tiers, DISTANCES)
from dcfss.mcdm import entropy_weights, critic_weights, roc_weights_from_scores

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"
P = load_problem(ROOT / "data" / "config_pakistan2022.json")
R, S = P.alternatives, list(P.stages)
SEED, N_MC = 20221118, 10_000
rng = np.random.default_rng(SEED)
base = evaluate(P)
mu = base["_mu"]
w0 = P.w_vector()
BASE_RANK = {s: base[s]["rank"]["WHD"] for s in S}
KEY = {"seed": SEED, "n_mc": N_MC}

def ranks(res, dist="WHD"):
    return {s: res[s]["rank"][dist] for s in S}

def order_str(r):
    return " > ".join(R[j] for j in np.argsort(r, kind="stable"))

def compare(r, s):
    b = BASE_RANK[s]
    return {"spearman": spearman(b, r), "kendall": kendall(b, r),
            "n_changed": int((b != r).sum()), "top1_same": bool(np.argmin(r) == np.argmin(b)),
            "top3_same": set(np.argsort(r)[:3]) == set(np.argsort(b)[:3])}

# =============================================================================
# A. WEIGHTS
# =============================================================================
schemes = {
    "Author-assigned (baseline)": w0,
    "Equal": np.full(P.m, 1 / P.m),
    "Entropy": entropy_weights(P.X),
    "CRITIC": critic_weights(mu),
    "ROC (baseline order)": roc_weights_from_scores(w0),
}
schemes["Hybrid (baseline+entropy)"] = 0.5 * w0 / w0.sum() + 0.5 * schemes["Entropy"]
pd.DataFrame(schemes, index=P.attributes).T.round(6).to_csv(OUT / "T10_weight_schemes.csv")

rows = []
for name, w in schemes.items():
    res = evaluate(P, weights=w)
    for s in S:
        r = res[s]["rank"]["WHD"]
        rows.append({"scheme": name, "stage": s, **{reg: int(r[i]) for i, reg in enumerate(R)},
                     **compare(r, s), "order": order_str(r)})
wdf = pd.DataFrame(rows)
wdf.round(6).to_csv(OUT / "T11_ranking_under_weight_schemes.csv", index=False)

# one-at-a-time +-20 % and +-50 %
rows = []
for j, a in enumerate(P.attributes):
    for f in (0.5, 0.8, 1.2, 1.5):
        w = w0.copy(); w[j] *= f
        res = evaluate(P, weights=w)
        for s in S:
            if a in P.stages[s]:
                rows.append({"attribute": a, "factor": f, "stage": s, **compare(res[s]["rank"]["WHD"], s),
                             "order": order_str(res[s]["rank"]["WHD"])})
oat = pd.DataFrame(rows)
oat.round(6).to_csv(OUT / "T12_weights_one_at_a_time.csv", index=False)

# weight stability intervals: range of the multiplicative factor on one global weight
# for which the stage ranking stays identical to the baseline (grid 0.01 ... 20)
grid = np.concatenate([np.linspace(0.01, 1, 100), np.linspace(1.02, 20, 950)])
rows = []
for j, a in enumerate(P.attributes):
    for s in S:
        if a not in P.stages[s]:
            continue
        ok = []
        for f in grid:
            w = w0.copy(); w[j] *= f
            ok.append(bool((evaluate(P, weights=w)[s]["rank"]["WHD"] == BASE_RANK[s]).all()))
        ok = np.array(ok)
        i1 = int(np.argmin(np.abs(grid - 1.0)))
        lo = i1
        while lo > 0 and ok[lo - 1]: lo -= 1
        hi = i1
        while hi < len(grid) - 1 and ok[hi + 1]: hi += 1
        idx = [P.col(x) for x in P.stages[s]]
        def stage_w(f):
            w = w0.copy(); w[j] *= f
            return w[j] / w[idx].sum()
        rows.append({"stage": s, "attribute": a, "baseline_stage_weight": stage_w(1.0),
                     "factor_low": grid[lo], "factor_high": grid[hi],
                     "stage_weight_low": stage_w(grid[lo]), "stage_weight_high": stage_w(grid[hi]),
                     "open_low": lo == 0, "open_high": hi == len(grid) - 1})
stab = pd.DataFrame(rows)
stab.round(6).to_csv(OUT / "T13_weight_stability_intervals.csv", index=False)

# Monte Carlo over weights
def mc_weights(sampler, label):
    cnt = {s: np.zeros((P.n, P.n)) for s in S}
    same = {s: 0 for s in S}; top1 = {s: 0 for s in S}; top3 = {s: 0 for s in S}
    rho = {s: [] for s in S}
    for _ in range(N_MC):
        res = evaluate(P, weights=sampler())
        for s in S:
            r = res[s]["rank"]["WHD"]
            cnt[s][np.arange(P.n), r - 1] += 1
            c = compare(r, s)
            same[s] += c["n_changed"] == 0; top1[s] += c["top1_same"]; top3[s] += c["top3_same"]
            rho[s].append(c["spearman"])
    out = []
    for s in S:
        out.append({"scenario": label, "stage": s, "P_full_order_unchanged": same[s] / N_MC,
                    "P_top1_unchanged": top1[s] / N_MC, "P_top3_set_unchanged": top3[s] / N_MC,
                    "mean_spearman": float(np.mean(rho[s])), "min_spearman": float(np.min(rho[s])),
                    "p05_spearman": float(np.quantile(rho[s], 0.05))})
    return out, {s: cnt[s] / N_MC for s in S}

rows, ACC = [], {}
for p in (0.10, 0.20, 0.30, 0.50):
    o, acc = mc_weights(lambda p=p: w0 * (1 + rng.uniform(-p, p, P.m)), f"local +-{int(p*100)}%")
    rows += o; ACC[f"local{int(p*100)}"] = acc
o, acc = mc_weights(lambda: rng.dirichlet(np.ones(P.m)), "global (uniform simplex)")
rows += o; ACC["global"] = acc
mcw = pd.DataFrame(rows)
mcw.round(6).to_csv(OUT / "T14_weights_monte_carlo.csv", index=False)
for key in ("local30", "global"):
    for s in S:
        pd.DataFrame(ACC[key][s], index=R, columns=[f"rank{k}" for k in range(1, P.n + 1)]).round(6)\
          .to_csv(OUT / f"T14b_rank_acceptability_weights_{key}_{s}.csv")

# =============================================================================
# B. TOLERANCE
# =============================================================================
rows, tier_rows = [], []
for d in (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
    res = evaluate(P, tolerance=d)
    for s in S:
        lo, mid, hi = res[s]["band"]
        tiers = priority_tiers(lo, mid, hi)
        tier_rows.append({"delta": d, "stage": s, **{reg: int(tiers[i]) for i, reg in enumerate(R)},
                          "n_tiers": int(tiers.max())})
        for k in DISTANCES:
            r = res[s]["rank"][k]
            rows.append({"delta": d, "stage": s, "distance": k,
                         **{reg: int(r[i]) for i, reg in enumerate(R)},
                         "spearman_vs_baseline": spearman(BASE_RANK[s], r),
                         "n_changed": int((BASE_RANK[s] != r).sum()),
                         **{f"SSI_{reg}": float(res[s]["ssi"][k][i]) for i, reg in enumerate(R)}})
tol = pd.DataFrame(rows); tol.round(6).to_csv(OUT / "T15_tolerance_sensitivity.csv", index=False)
tiers_df = pd.DataFrame(tier_rows); tiers_df.to_csv(OUT / "T16_priority_tiers_by_tolerance.csv", index=False)

# observed revision of the national totals (data-informed tolerance)
rev = pd.read_csv(ROOT / "data" / "ndma_national_totals_revision.csv")
rev["relative_revision"] = (rev.final_18Nov2022 - rev.snapshot_18Sep2022) / rev.snapshot_18Sep2022
rev[["indicator", "attribute", "snapshot_18Sep2022", "final_18Nov2022", "relative_revision"]]\
    .round(6).to_csv(OUT / "T17_observed_revision_national_totals.csv", index=False)
rv = rev.dropna(subset=["relative_revision"])
KEY["revision"] = {"per_indicator": dict(zip(rv.attribute, rv.relative_revision.round(4))),
                   "mean": float(rv.relative_revision.mean()), "median": float(rv.relative_revision.median()),
                   "min": float(rv.relative_revision.min()), "max": float(rv.relative_revision.max())}
# check that the regional data sum to the snapshot totals
assert np.allclose(P.X.sum(axis=0), rev.snapshot_18Sep2022.to_numpy(dtype=float))

het = {a: max(float(r), 0.02) for a, r in zip(rv.attribute, rv.relative_revision)}
het["e7"] = 0.10      # no revised count published: baseline tolerance retained
res = evaluate(P, tolerance=het)
rows = []
for s in S:
    lo, mid, hi = res[s]["band"]; tiers = priority_tiers(lo, mid, hi)
    for k in DISTANCES:
        r = res[s]["rank"][k]
        rows.append({"stage": s, "distance": k, **{reg: int(r[i]) for i, reg in enumerate(R)},
                     "n_changed_vs_baseline": int((BASE_RANK[s] != r).sum()),
                     "tiers": "|".join(str(int(t)) for t in tiers)})
pd.DataFrame(rows).to_csv(OUT / "T18_heterogeneous_tolerance.csv", index=False)
KEY["heterogeneous_delta"] = het

# Monte Carlo perturbation of the raw data (reporting error)
rows, ACCD = [], {}
for d in (0.05, 0.10, 0.20, 0.30):
    cnt = {s: np.zeros((P.n, P.n)) for s in S}; same = {s: 0 for s in S}; rho = {s: [] for s in S}
    top1 = {s: 0 for s in S}
    for _ in range(N_MC):
        Xp = P.X * (1 + rng.uniform(-d, d, P.X.shape))
        res = evaluate(P, X=Xp, tolerance=d)
        for s in S:
            r = res[s]["rank"]["WHD"]
            cnt[s][np.arange(P.n), r - 1] += 1
            same[s] += int((r == BASE_RANK[s]).all()); rho[s].append(spearman(BASE_RANK[s], r))
            top1[s] += int(np.argmin(r) == np.argmin(BASE_RANK[s]))
    for s in S:
        acc = cnt[s] / N_MC
        ACCD[(d, s)] = acc
        rows.append({"delta": d, "stage": s, "P_full_order_unchanged": same[s] / N_MC,
                     "P_top1_unchanged": top1[s] / N_MC,
                     "mean_spearman": float(np.mean(rho[s])), "min_spearman": float(np.min(rho[s])),
                     **{f"P_keeps_rank_{reg}": float(acc[i, BASE_RANK[s][i] - 1]) for i, reg in enumerate(R)}})
        pd.DataFrame(acc, index=R, columns=[f"rank{k}" for k in range(1, P.n + 1)]).round(6)\
          .to_csv(OUT / f"T19b_rank_acceptability_data_delta{int(d*100)}_{s}.csv")
mcd = pd.DataFrame(rows); mcd.round(6).to_csv(OUT / "T19_data_perturbation_monte_carlo.csv", index=False)

# =============================================================================
# C. STAGE STRUCTURE
# =============================================================================
rows = []
def add(label, stages_alt):
    res = evaluate(P, stages=stages_alt)
    for s in stages_alt:
        r = res[s]["rank"]["WHD"]
        rows.append({"variant": label, "stage": s, "active": ",".join(stages_alt[s]),
                     **{reg: int(r[i]) for i, reg in enumerate(R)}, **compare(r, s), "order": order_str(r)})
add("Baseline", P.stages)
for s in S:                                   # leave-one-attribute-out
    for a in P.stages[s]:
        if len(P.stages[s]) > 1:
            alt = {s: [x for x in P.stages[s] if x != a]}
            add(f"{s} without {a}", alt)
add("e2 only in T1 (removed from T2)", {"T2": ["e3", "e4", "e5"]})
add("e2 only in T2 (removed from T1)", {"T1": ["e1"]})
add("e5 only in T2 (removed from T3)", {"T3": ["e6", "e7"]})
add("e5 only in T3 (removed from T2)", {"T2": ["e2", "e3", "e4"]})
add("e7 added to T1", {"T1": ["e1", "e2", "e7"]})
add("e7 added to T2", {"T2": ["e2", "e3", "e4", "e5", "e7"]})
add("e3,e4 added to T3", {"T3": ["e3", "e4", "e5", "e6", "e7"]})
add("Disjoint stages", {"T1": ["e1", "e2"], "T2": ["e3", "e4"], "T3": ["e5", "e6", "e7"]})
std = pd.DataFrame(rows); std.round(6).to_csv(OUT / "T20_stage_structure_sensitivity.csv", index=False)

# =============================================================================
# D. NORMALISATION   and   E. ICT EXCLUSION
# =============================================================================
rows = []
for meth in ("minmax", "max", "sum", "vector"):
    res = evaluate(P, normalisation=meth)
    for s in S:
        r = res[s]["rank"]["WHD"]
        rows.append({"normalisation": meth, "stage": s, **{reg: int(r[i]) for i, reg in enumerate(R)},
                     **compare(r, s)})
nrm = pd.DataFrame(rows); nrm.round(6).to_csv(OUT / "T21_normalisation_sensitivity.csv", index=False)

keep = [i for i, r in enumerate(R) if r != "ICT"]
import copy
P6 = copy.deepcopy(P); P6.alternatives = [R[i] for i in keep]; P6.X = P.X[keep]
res6 = evaluate(P6)
rows = []
for s in S:
    for k in DISTANCES:
        r6 = res6[s]["rank"][k]
        r7 = rank_desc(base[s]["ssi"][k][keep])          # baseline order restricted to the six regions
        rows.append({"stage": s, "distance": k, **{reg: int(r6[i]) for i, reg in enumerate(P6.alternatives)},
                     "order_preserved": bool((r6 == r7).all()), "spearman": spearman(r6, r7),
                     **{f"SSI_{reg}": float(res6[s]["ssi"][k][i]) for i, reg in enumerate(P6.alternatives)}})
ict = pd.DataFrame(rows); ict.round(6).to_csv(OUT / "T22_ICT_excluded.csv", index=False)
pd.DataFrame(res6["_mu"], index=P6.alternatives, columns=P.attributes).round(6)\
    .to_csv(OUT / "T22b_membership_ICT_excluded.csv")

# =============================================================================
# F. DISTANCE MEASURE AND REFERENCE POINT
# =============================================================================
rows = []
for s in S:
    mat, names = [], []
    for k in DISTANCES:
        for nm, r in (("SSI", base[s]["rank"][k]), ("d+ only", base[s]["rank_dplus"][k]),
                      ("d- only", base[s]["rank_dminus"][k])):
            mat.append(r); names.append(f"{k} / {nm}")
            rows.append({"stage": s, "rule": f"{k} / {nm}", **{reg: int(r[i]) for i, reg in enumerate(R)},
                         "spearman_vs_primary": spearman(BASE_RANK[s], r)})
    KEY.setdefault("kendall_w_distance_reference", {})[s] = kendall_w(np.array(mat))
pd.DataFrame(rows).round(6).to_csv(OUT / "T23_distance_and_reference_rules.csv", index=False)

# ---------------------------------------------------------------------------
KEY["weights"] = {k: np.round(v / v.sum(), 4).tolist() for k, v in schemes.items()}
KEY["mc_weights"] = mcw.round(4).to_dict(orient="records")
KEY["mc_data"] = mcd.round(4).to_dict(orient="records")
(ROOT / "results" / "key_numbers_robustness.json").write_text(json.dumps(KEY, indent=2, default=str), encoding="utf-8")

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_colwidth", 80)
print("WEIGHT SCHEMES\n", pd.DataFrame(schemes, index=P.attributes).T.round(4))
print("\nRANKING UNDER SCHEMES\n", wdf[["scheme","stage","spearman","n_changed","top1_same","top3_same","order"]].round(3).to_string(index=False))
print("\nOAT (changed only)\n", oat[oat.n_changed > 0].round(3).to_string(index=False))
print("\nSTABILITY INTERVALS\n", stab.round(3).to_string(index=False))
print("\nMC WEIGHTS\n", mcw.round(4).to_string(index=False))
print("\nTOLERANCE (rank changes)\n", tol[["delta","stage","distance","spearman_vs_baseline","n_changed"]+R].to_string(index=False))
print("\nTIERS\n", tiers_df.to_string(index=False))
print("\nREVISION\n", rev[["indicator","snapshot_18Sep2022","final_18Nov2022","relative_revision"]].round(4).to_string(index=False), "\n", KEY["revision"])
print("\nHETEROGENEOUS\n", pd.read_csv(OUT / "T18_heterogeneous_tolerance.csv").to_string(index=False))
print("\nMC DATA\n", mcd.round(4).to_string(index=False))
print("\nSTAGE STRUCTURE\n", std[["variant","stage","active","spearman","n_changed","top1_same","order"]].round(3).to_string(index=False))
print("\nNORMALISATION\n", nrm.round(3).to_string(index=False))
print("\nICT EXCLUDED\n", ict[["stage","distance","order_preserved","spearman"]+P6.alternatives].to_string(index=False))
print("\nKENDALL W\n", KEY["kendall_w_distance_reference"])
print(pd.read_csv(OUT / "T23_distance_and_reference_rules.csv").to_string(index=False))
