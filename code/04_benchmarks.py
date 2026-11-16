"""
04 - Benchmark comparison and added value of the dynamic cubic model
     (Reviewer 2: comments 1, 7; Reviewer 4: comments 3, 8).

A. Established MCDM methods on the SAME normalised data and stage weights:
   SAW, TOPSIS (min-max data; classical vector-normalised variant), VIKOR,
   entropy-weighted TOPSIS.
B. Structural baselines:
   static cubic fuzzy soft set (single stage, all attributes),
   crisp dynamic soft set (threshold membership),
   versus the DCFSS stage-wise rankings and the stage-emphasis aggregate.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from dcfss import (load_problem, evaluate, rank_desc, spearman, kendall, kendall_w,
                   stage_weights, dynamic_index)
from dcfss.mcdm import saw, topsis, vikor, crisp_dynamic_soft_set, entropy_weights

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"
P = load_problem(ROOT / "data" / "config_pakistan2022.json")
R, S = P.alternatives, list(P.stages)
base = evaluate(P); mu = base["_mu"]; w0 = P.w_vector()
KEY = {}
stages = dict(P.stages); stages["ALL"] = list(P.attributes)       # ALL = static single-stage model
res_all = evaluate(P, stages=stages)

# ---- A. benchmark methods -----------------------------------------------------
rows, agree = [], []
went = entropy_weights(P.X)
for s, active in stages.items():
    idx = [P.col(a) for a in active]
    w = stage_weights(w0, idx); m = mu[:, idx]
    methods = {}
    methods["DCFSS-WHD"] = (res_all[s]["ssi"]["WHD"], res_all[s]["rank"]["WHD"])
    methods["DCFSS-WED"] = (res_all[s]["ssi"]["WED"], res_all[s]["rank"]["WED"])
    methods["DCFSS-WHHD"] = (res_all[s]["ssi"]["WHHD"], res_all[s]["rank"]["WHHD"])
    methods["SAW"] = saw(m, w)
    methods["TOPSIS"] = topsis(m, w)
    methods["TOPSIS (vector norm.)"] = topsis(P.X[:, idx], w, vector_normalise=True)
    q, rq, info = vikor(m, w)
    methods["VIKOR"] = (q, rq)
    methods["Entropy-TOPSIS"] = topsis(m, stage_weights(went, idx))
    KEY.setdefault("vikor_conditions", {})[s] = {"C1": info["C1_advantage"], "C2": info["C2_stability"],
                                                 "DQ": info["DQ"]}
    for name, (score, rk) in methods.items():
        rows.append({"stage": s, "method": name,
                     **{f"score_{reg}": float(score[i]) for i, reg in enumerate(R)},
                     **{reg: int(rk[i]) for i, reg in enumerate(R)}})
        agree.append({"stage": s, "method": name,
                      "spearman_vs_DCFSS_WHD": spearman(methods["DCFSS-WHD"][1], rk),
                      "kendall_vs_DCFSS_WHD": kendall(methods["DCFSS-WHD"][1], rk),
                      "n_rank_differences": int((methods["DCFSS-WHD"][1] != rk).sum()),
                      "order": " > ".join(R[j] for j in np.argsort(rk, kind="stable"))})
    KEY.setdefault("kendall_w_methods", {})[s] = kendall_w(np.array([v[1] for v in methods.values()]))
bm = pd.DataFrame(rows); bm.round(6).to_csv(OUT / "T24_benchmark_scores_and_ranks.csv", index=False)
ag = pd.DataFrame(agree); ag.round(6).to_csv(OUT / "T25_benchmark_agreement.csv", index=False)

# ---- B. structural baselines --------------------------------------------------
static_rank = res_all["ALL"]["rank"]["WHD"]
comp = pd.DataFrame(index=R)
comp["Static CFSS (all attributes)"] = static_rank
for s in S:
    comp[f"DCFSS {s}"] = base[s]["rank"]["WHD"]
for s in S:
    comp[f"DCFSS {s} - static"] = comp[f"DCFSS {s}"] - comp["Static CFSS (all attributes)"]
comp.to_csv(OUT / "T26_static_vs_dynamic_ranks.csv")
KEY["static_vs_stage_spearman"] = {s: spearman(static_rank, base[s]["rank"]["WHD"]) for s in S}
KEY["regions_whose_rank_differs_from_static"] = {
    s: [R[i] for i in range(P.n) if base[s]["rank"]["WHD"][i] != static_rank[i]] for s in S}

rows = []
for thr in (0.25, 0.5, 0.75):
    for s in S:
        idx = [P.col(a) for a in P.stages[s]]
        w = stage_weights(w0, idx)
        score, rk, member = crisp_dynamic_soft_set(mu[:, idx], w, thr)
        rows.append({"threshold": thr, "stage": s, **{reg: int(rk[i]) for i, reg in enumerate(R)},
                     **{f"choice_{reg}": float(score[i]) for i, reg in enumerate(R)},
                     "distinct_rank_levels": int(len(set(rk))),
                     "regions_tied_at_zero": int((score == 0).sum()),
                     "spearman_vs_DCFSS": spearman(base[s]["rank"]["WHD"], rk)})
dss = pd.DataFrame(rows); dss.round(6).to_csv(OUT / "T27_crisp_dynamic_soft_set_baseline.csv", index=False)
# distinct levels of the cubic model for comparison
KEY["distinct_levels"] = {"DCFSS": {s: int(len(set(base[s]["rank"]["WHD"]))) for s in S},
                          "crisp_DSS_thr0.5": {r["stage"]: r["distinct_rank_levels"]
                                               for _, r in dss[dss.threshold == 0.5].iterrows()}}

# ---- C. stage-emphasis path: (1,0,0) -> (0,1,0) -> (0,0,1) ---------------------
scores = {s: base[s]["ssi"]["WHD"] for s in S}
path = []
for t in np.linspace(0, 2, 201):
    lam = (1 - t, t, 0.0) if t <= 1 else (0.0, 2 - t, t - 1)
    v = dynamic_index(scores, np.maximum(lam, 0) + 0.0)
    path.append({"t": round(float(t), 2), "lam_T1": lam[0], "lam_T2": lam[1], "lam_T3": lam[2],
                 **{reg: float(v[i]) for i, reg in enumerate(R)},
                 **{f"rank_{reg}": int(rank_desc(v)[i]) for i, reg in enumerate(R)}})
path = pd.DataFrame(path); path.round(5).to_csv(OUT / "T28_stage_emphasis_path.csv", index=False)
# crossover Punjab / Balochistan along the path (linear interpolation on the T2->T3 leg)
a, b = "Punjab", "Balochistan"
diff = (path[a] - path[b]).to_numpy()
cross = [float(path.t[i] + (path.t[i+1]-path.t[i]) * diff[i] / (diff[i] - diff[i+1]))
         for i in range(len(diff) - 1) if diff[i] * diff[i+1] < 0]
KEY["crossover_Punjab_Balochistan_t"] = cross
# also KP / Balochistan
diff = (path["KP"] - path[b]).to_numpy()
KEY["crossover_KP_Balochistan_t"] = [float(path.t[i] + (path.t[i+1]-path.t[i]) * diff[i] / (diff[i] - diff[i+1]))
                                      for i in range(len(diff) - 1) if diff[i] * diff[i+1] < 0]
(ROOT / "results" / "key_numbers_benchmarks.json").write_text(json.dumps(KEY, indent=2), encoding="utf-8")

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_colwidth", 90)
print(bm[["stage", "method"] + R].to_string(index=False))
print(bm[["stage", "method"] + [f"score_{r}" for r in R]].round(4).to_string(index=False))
print(ag.round(4).to_string(index=False))
print("\nSTATIC vs DYNAMIC\n", comp)
print("\nCRISP DSS\n", dss.round(3).to_string(index=False))
print(json.dumps(KEY, indent=1))
