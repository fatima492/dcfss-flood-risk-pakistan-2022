"""
09 - Verify the numbers quoted in the TEXT of the revised manuscript against the
result tables, and write MANUSCRIPT_TRACEABILITY.md. Every line is an assertion:
the script stops with an error if a quoted number is not reproduced.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
rd = lambda n, **k: pd.read_csv(T / n, **k)
checks = []

def check(claim, where, source, cond):
    assert bool(cond), f"NOT REPRODUCED: {claim}"
    checks.append((claim, where, source))

def close(a, b, tol): return abs(a - b) <= tol

sr = rd("T05_stage_results.csv"); S = lambda s: sr[sr.stage == s].set_index("region")
sh = rd("T01b_regional_shares_percent.csv", index_col=0)
raw = rd("T01_raw_data.csv", index_col=0)
order = lambda s, col="rank_WHD": "".join({"AJ&K": "A", "Balochistan": "B", "GB": "G", "ICT": "I", "KP": "K",
                                            "Punjab": "P", "Sindh": "S"}[r] for r in S(s).sort_values(col).index)

# ---- data ------------------------------------------------------------------------------------
check("National totals 1,545 deaths; 12,860 injured; 33,046,329 affected", "Sec. 6.1", "T01_raw_data.csv",
      list(raw.loc["Total"].astype(int))[:2] == [1545, 12860] and int(raw.loc["Total"].iloc[-1]) == 33046329)
check("Sindh: 44% deaths, 66% injured, 66% roads, 88% houses", "Abstract, Sec. 6.5, 9.1", "T01b",
      [round(sh.loc["Sindh", c]) for c in ("e1", "e2", "e3", "e5")] == [44, 66, 66, 88])
check("Punjab 30% of injuries; Balochistan 53% of livestock and 28% of affected population", "Abstract, Sec. 6.5",
      "T01b", round(sh.loc["Punjab", "e2"]) == 30 and round(sh.loc["Balochistan", "e6"]) == 53
      and round(sh.loc["Balochistan", "e7"]) == 28)
check("KP 28% of bridges; GB 17% of bridges", "Sec. 6.5", "T01b",
      round(sh.loc["KP", "e4"]) == 28 and round(sh.loc["GB", "e4"]) == 17)
check("Punjab has 21 times as many injured as Balochistan", "Sec. 6.7", "T01",
      round(raw.loc["Punjab"].iloc[1] / raw.loc["Balochistan"].iloc[1]) == 21)
rv = rd("T17_observed_revision_national_totals.csv").dropna()
rv["relative_revision"] = (rv.final_18Nov2022 - rv.snapshot_18Sep2022) / rv.snapshot_18Sep2022
check("Revisions between <0.1% and 23.3%, mean 12.3%, median 14.8%", "Sec. 6.3", "T17",
      round(100 * rv.relative_revision.max(), 1) == 23.3 and 100 * rv.relative_revision.min() < 0.1
      and close(100 * rv.relative_revision.mean(), 12.3, 0.05) and close(100 * rv.relative_revision.median(), 14.8, 0.05))

pv = rd("T30_data_provenance_check.csv"); pvr = rd("T30b_rankings_with_later_report.csv")
check("41 of 49 input values identical to NDMA SITREP No. 099 (20 Sep 2022); stage rankings identical with that report",
      "Sec. 6.1", "T30, T30b", int(pv.identical.sum()) == 41 and len(pv) == 49 and pvr.identical.all())

# ---- stage results -----------------------------------------------------------------------------
check("Stage rankings T1 SPKBAGI, T2 SPKBGAI, T3 SBPKAGI (WHD)", "Sec. 6.5, Tables 8-10", "T05",
      (order("T1"), order("T2"), order("T3")) == ("SPKBAGI", "SPKBGAI", "SBPKAGI"))
check("Sindh SSI 0.967 / 0.967 / 0.848; maximum of any other region 0.51", "Sec. 6.5, Conclusion", "T05",
      [round(S(s).loc["Sindh", "SSI_WHD"], 3) for s in ("T1", "T2", "T3")] == [0.967, 0.967, 0.848]
      and round(sr[sr.region != "Sindh"].SSI_WHD.max(), 2) == 0.51)
check("T1: Punjab 0.347, KP 0.298, Balochistan 0.283", "Sec. 6.5", "T05",
      [round(S("T1").loc[r, "SSI_WHD"], 3) for r in ("Punjab", "KP", "Balochistan")] == [0.347, 0.298, 0.283])
check("T2: Punjab 0.200, KP 0.146, Balochistan 0.084", "Sec. 6.5", "T05",
      [round(S("T2").loc[r, "SSI_WHD"], 3) for r in ("Punjab", "KP", "Balochistan")] == [0.200, 0.146, 0.084])
check("T3: Balochistan 0.508, Punjab 0.252, KP 0.160", "Sec. 6.5", "T05",
      [round(S("T3").loc[r, "SSI_WHD"], 3) for r in ("Balochistan", "Punjab", "KP")] == [0.508, 0.252, 0.160])
check("Worked example Punjab T1: d+ 0.6528, d- 0.3472; WED 0.6591/0.3588/0.3525; WHHD 0.6875/0.3819/0.3571; band [0.3125, 0.3819]",
      "Sec. 6.4, Fig. 1", "T05",
      np.allclose(S("T1").loc["Punjab", ["dplus_WHD", "dminus_WHD", "dplus_WED", "dminus_WED", "SSI_WED",
                                          "dplus_WHHD", "dminus_WHHD", "SSI_WHHD", "band_lower", "band_upper"]]
                  .astype(float), [0.6528, 0.3472, 0.6591, 0.3588, 0.3525, 0.6875, 0.3819, 0.3571, 0.3125, 0.3819], atol=6e-5))
check("Tiers at 10%: T1 Sindh | Punjab,KP,Balochistan | AJ&K | GB | ICT; T2 seven tiers; T3 AJ&K and GB share a tier",
      "Sec. 6.5", "T05", S("T1").tier.to_dict() == {"AJ&K": 3, "Balochistan": 2, "GB": 4, "ICT": 5, "KP": 2,
      "Punjab": 2, "Sindh": 1} and S("T2").tier.nunique() == 7 and S("T3").loc["AJ&K", "tier"] == S("T3").loc["GB", "tier"])
check("Only disagreement among distances: Balochistan/GB at T2 under WED", "Sec. 6.5", "T05",
      (order("T1", "rank_WED"), order("T3", "rank_WED")) == ("SPKBAGI", "SBPKAGI") and order("T2", "rank_WED") == "SPKGBAI"
      and all(order(s, "rank_WHHD") == order(s) for s in ("T1", "T2", "T3")))
K = json.loads((ROOT / "results" / "key_numbers_robustness.json").read_text(encoding="utf-8"))
check("Kendall W over nine distance/reference rules: 1.000 (T1, T3), 0.988 (T2)", "Sec. 6.5", "key_numbers_robustness.json",
      [round(K["kendall_w_distance_reference"][s], 3) for s in ("T1", "T2", "T3")] == [1.0, 0.988, 1.0])

# ---- ICT, static vs dynamic, emphasis -------------------------------------------------------------
ict = rd("T22_ICT_excluded.csv")
check("Order of the six regions preserved at every stage and distance when ICT is excluded; GB index 0 at T1",
      "Sec. 6.6, Table 11", "T22", ict.order_preserved.all()
      and close(ict[(ict.stage == "T1") & (ict.distance == "WHD")].SSI_GB.iloc[0], 0, 1e-9))
cmp_ = rd("T26_static_vs_dynamic_ranks.csv", index_col=0)
B = json.loads((ROOT / "results" / "key_numbers_benchmarks.json").read_text(encoding="utf-8"))
check("Static ranks differ from stage ranks for 5 / 3 / 2 regions; Spearman 0.857 / 0.893 / 0.964",
      "Abstract, Sec. 6.7, Conclusion", "T26",
      [int((cmp_[f"DCFSS {s}"] != cmp_["Static CFSS (all attributes)"]).sum()) for s in ("T1", "T2", "T3")] == [5, 3, 2]
      and [round(B["static_vs_stage_spearman"][s], 3) for s in ("T1", "T2", "T3")] == [0.857, 0.893, 0.964])
check("Balochistan overtakes KP at about 15% and Punjab at about 31% of the relief-to-recovery shift", "Sec. 6.7, Fig. 6",
      "T28", close(B["crossover_KP_Balochistan_t"][0] - 1, 0.15, 0.005) and close(B["crossover_Punjab_Balochistan_t"][0] - 1, 0.31, 0.005))
dy = rd("T08_dynamic_stage_emphasis.csv", index_col=0)
check("Early response: Punjab 2nd, Balochistan 3rd; Sindh first for every profile", "Sec. 6.7, Table 12", "T08",
      dy.loc["Punjab", "Early response | rank"] == 2 and dy.loc["Balochistan", "Early response | rank"] == 3
      and all(dy.loc["Sindh", c] == 1 for c in dy.columns if c.endswith("rank")))
al = rd("T08b_illustrative_proportional_shares.csv", index_col=0)
check("Proportional shares: Balochistan 14.5 / 5.8 / 28.7 %, Sindh 49.3 / 67.0 / 47.9 %", "Sec. 9.1", "T08b",
      list(al.loc["Balochistan"]) == [14.5, 5.8, 28.7] and list(al.loc["Sindh"]) == [49.3, 67.0, 47.9])

# ---- weights ----------------------------------------------------------------------------------------
wr = rd("T11_ranking_under_weight_schemes.csv")
check("Sindh first in 17 of 18 scheme-stage combinations; complete order unchanged in 14 of 18", "Sec. 7.1", "T11",
      int((wr.Sindh == 1).sum()) == 17 and int((wr.n_changed == 0).sum()) == 14 and len(wr) == 18)
ws = rd("T10_weight_schemes.csv", index_col=0)
check("CRITIC gives 61% of the recovery-stage weight to livestock; entropy's largest weight is houses", "Sec. 7.1", "T10",
      round(100 * ws.loc["CRITIC", "e6"] / ws.loc["CRITIC", ["e5", "e6", "e7"]].sum()) == 61
      and ws.loc["Entropy"].idxmax() == "e5" and ws.loc["CRITIC"].idxmax() == "e6")
oat = rd("T12_weights_one_at_a_time.csv")
check("+-20% single-weight changes: no ranking change; +-50%: 3 of 18 cases change", "Sec. 7.1", "T12",
      oat[oat.factor.isin([0.8, 1.2])].n_changed.sum() == 0 and len(oat[oat.factor.isin([0.5, 1.5])]) == 18
      and int((oat[oat.factor.isin([0.5, 1.5])].n_changed > 0).sum()) == 3)
st = rd("T13_weight_stability_intervals.csv").set_index(["stage", "attribute"])
check("Stability: deaths at T1 up to 0.709 (baseline 0.625); bridges at T2 up to 0.190 (baseline 0.111); livestock at T3 up to 0.524",
      "Sec. 7.1, 7.5, Table 14", "T13", close(st.loc[("T1", "e1"), "stage_weight_high"], 0.709, 6e-4)
      and close(st.loc[("T2", "e4"), "stage_weight_high"], 0.190, 6e-4) and close(st.loc[("T3", "e6"), "stage_weight_high"], 0.524, 6e-4))
mw = rd("T14_weights_monte_carlo.csv").set_index(["scenario", "stage"])
check("Weights +-20%: complete ranking preserved with probability >= 0.998; +-50%: 0.80 / 0.87 / 1.00", "Abstract-level claim, Sec. 7.1, Conclusion",
      "T14", mw.loc["local +-20%"].P_full_order_unchanged.min() >= 0.998
      and [round(mw.loc[("local +-50%", s), "P_full_order_unchanged"], 2) for s in ("T1", "T2", "T3")] == [0.80, 0.87, 1.00])
check("Uniform weights: Sindh first with probability 1.00 / 1.00 / 0.78", "Sec. 7.1", "T14",
      [round(mw.loc[("global (uniform simplex)", s), "P_top1_unchanged"], 2) for s in ("T1", "T2", "T3")] == [1.0, 1.0, 0.78])
acc = rd("T14b_rank_acceptability_weights_global_T2.csv", index_col=0)
check("Uniform weights at T2: KP second with probability 0.63, Punjab 0.35; ICT always last, AJ&K never above 5th", "Sec. 7.1, Fig. 7a",
      "T14b", round(acc.loc["KP", "rank2"], 2) == 0.63 and round(acc.loc["Punjab", "rank2"], 2) == 0.35
      and acc.loc["ICT", "rank7"] == 1 and acc.loc["AJ&K", ["rank1", "rank2", "rank3", "rank4"]].sum() == 0)

# ---- tolerance -----------------------------------------------------------------------------------------
tol = rd("T15_tolerance_sensitivity.csv")
check("Rankings identical for every tolerance 0-30% under each distance", "Abstract, Sec. 7.2", "T15",
      all(tol[(tol.stage == s) & (tol.distance == k)][["AJ&K", "Balochistan", "GB", "ICT", "KP", "Punjab", "Sindh"]]
          .drop_duplicates().shape[0] == 1 for s in ("T1", "T2", "T3") for k in ("WED", "WHD", "WHHD")))
ct = rd("T07_critical_tolerances.csv")
g = lambda s, a, b: float(ct[(ct.stage == s) & (ct.higher == a) & (ct.lower == b)].critical_tolerance.iloc[0])
check("Critical tolerances: KP/Balochistan 2.6%, Punjab/KP 7.6% (T1); minimum 15.6% at T2; AJ&K/GB 7.4% at T3", "Sec. 7.2, Table 17",
      "T07", close(100 * g("T1", "KP", "Balochistan"), 2.55, 0.05) and f'{100 * g("T1", "KP", "Balochistan"):.1f}' == "2.6")
check("Critical tolerance values (detail)", "Sec. 7.2", "T07",
      close(100 * g("T1", "Punjab", "KP"), 7.6, 0.06) and close(100 * ct[ct.stage == "T2"].critical_tolerance.min(), 15.6, 0.06)
      and close(100 * g("T3", "AJ&K", "GB"), 7.4, 0.06)
      and 100 * ct[(ct.stage == "T1") & ~ct.lower.isin(["KP", "Balochistan"])].critical_tolerance.min() > 38
      and 100 * ct[(ct.stage == "T3") & (ct.lower != "GB")].critical_tolerance.min() >= 22)
tr = rd("T16_priority_tiers_by_tolerance.csv").set_index(["stage", "delta"])
check("Punjab and KP merge at T2 from 20% and at T3 from 25%; Sindh alone in tier 1 up to 30%", "Sec. 7.2, Table 16", "T16",
      tr.loc[("T2", 0.15), "KP"] != tr.loc[("T2", 0.15), "Punjab"] and tr.loc[("T2", 0.20), "KP"] == tr.loc[("T2", 0.20), "Punjab"]
      and tr.loc[("T3", 0.20), "KP"] != tr.loc[("T3", 0.20), "Punjab"] and tr.loc[("T3", 0.25), "KP"] == tr.loc[("T3", 0.25), "Punjab"]
      and all((tr.loc[(s, 0.30)].drop("n_tiers") == 1).sum() == 1 and tr.loc[(s, 0.30), "Sindh"] == 1 for s in ("T1", "T2", "T3")))
het = rd("T18_heterogeneous_tolerance.csv"); het = het[het.distance == "WHD"]
base_t = {s: "|".join(str(int(S(s).loc[r, "tier"])) for r in ["AJ&K", "Balochistan", "GB", "ICT", "KP", "Punjab", "Sindh"]) for s in ("T1", "T2", "T3")}
check("Indicator-specific tolerances: same rankings and tiers as uniform 10%", "Sec. 7.2", "T18",
      het.n_changed_vs_baseline.sum() == 0 and all(het[het.stage == s].tiers.iloc[0] == base_t[s] for s in base_t))
md = rd("T19_data_perturbation_monte_carlo.csv").set_index(["delta", "stage"])
check("Data +-10%: ranking preserved with probability 0.71 / 1.00 / 0.99; Sindh always first; Punjab stays 2nd at T1 with 0.98",
      "Sec. 7.2, Table 15", "T19", [round(md.loc[(0.10, s), "P_full_order_unchanged"], 2) for s in ("T1", "T2", "T3")] == [0.71, 1.0, 0.99]
      and md.P_top1_unchanged.min() == 1 and round(md.loc[(0.10, "T1"), "P_keeps_rank_Punjab"], 2) == 0.98)

# ---- stage structure, normalisation ------------------------------------------------------------------------
ss = rd("T20_stage_structure_sensitivity.csv"); ss = ss[ss.variant != "Baseline"]
ss17 = ss[~((ss.variant == "Disjoint stages") & (ss.stage != "T2"))]
check("Stage structure: 17 variants, Sindh always first, 6 unchanged, rho >= 0.89 in all but one (0.775)", "Sec. 7.3, Table 18",
      "T20", len(ss17) == 17 and ss17.top1_same.all() and int((ss17.n_changed == 0).sum()) == 6
      and int((ss17.spearman < 0.89).sum()) == 1 and close(ss17.spearman.min(), 0.775, 6e-4))
nr = rd("T21_normalisation_sensitivity.csv")
check("Four normalisation rules give identical stage rankings", "Abstract, Sec. 7.4", "T21", nr.n_changed.sum() == 0)

# ---- benchmarks ----------------------------------------------------------------------------------------------
ag = rd("T25_benchmark_agreement.csv").set_index(["stage", "method"])
check("SAW, TOPSIS, VIKOR: rho = 1 at T2 and T3; TOPSIS and VIKOR rho = 0.893 at T1; SAW rho = 1 at T1", "Abstract, Sec. 8.2",
      "T25", all(ag.loc[(s, m), "spearman_vs_DCFSS_WHD"] == 1 for s in ("T2", "T3") for m in ("SAW", "TOPSIS", "VIKOR"))
      and all(close(ag.loc[("T1", m), "spearman_vs_DCFSS_WHD"], 0.893, 6e-4) for m in ("TOPSIS", "VIKOR"))
      and ag.loc[("T1", "SAW"), "spearman_vs_DCFSS_WHD"] == 1)
check("Kendall W over eight methods 0.959 / 0.987 / 1.000; VIKOR conditions hold for Sindh at every stage", "Sec. 8.2",
      "key_numbers_benchmarks.json", [round(B["kendall_w_methods"][s], 3) for s in ("T1", "T2", "T3")] == [0.959, 0.987, 1.0]
      and all(B["vikor_conditions"][s]["C1"] and B["vikor_conditions"][s]["C2"] for s in ("T1", "T2", "T3")))
ds = rd("T27_crisp_dynamic_soft_set_baseline.csv"); d5 = ds[ds.threshold == 0.5].set_index("stage")
check("Crisp dynamic soft set, threshold 0.50: 6 / 5 / 5 regions tied at zero; 2 / 3 / 3 rank levels", "Sec. 8.1, Table 19", "T27",
      list(d5.regions_tied_at_zero) == [6, 5, 5] and list(d5.distinct_rank_levels) == [2, 3, 3])

# ---- write traceability file -------------------------------------------------------------------------------------
lines = ["# Manuscript traceability", "",
         "Each statement below is quoted in the revised manuscript and is asserted by "
         "`code/09_verify_manuscript_numbers.py` against the result tables. The script fails if any statement is not reproduced.", "",
         "| # | Statement in the manuscript | Location | Result file |", "|---:|---|---|---|"]
for i, (c, w, s) in enumerate(checks, 1):
    lines.append(f"| {i} | {c} | {w} | `{s}` |")
lines += ["", "## Tables and figures", "",
          "| Manuscript item | Produced by | Result file |", "|---|---|---|",
          "| Table 4 (input data) | 02 | `T01_raw_data.csv`, `latex/tab_raw.tex` |",
          "| Table 5 (weights) | 02 | `T04_stage_weights.csv` |",
          "| Table 6 (revision of national totals) | 03 | `T17_observed_revision_national_totals.csv` |",
          "| Table 7 (severity memberships) | 02 | `T02_severity_membership.csv` |",
          "| Tables 8-10 (stage results) | 02 | `T05_stage_results.csv` |",
          "| Table 11 (ICT excluded) | 03 | `T22_ICT_excluded.csv` |",
          "| Table 12 (static vs stage ranks, stage emphasis) | 02, 04 | `T26_...csv`, `T08_...csv` |",
          "| Table 13 (weighting schemes) | 03 | `T10_...csv`, `T11_...csv` |",
          "| Table 14 (weight stability intervals) | 03 | `T13_...csv` |",
          "| Table 15 (Monte Carlo) | 03 | `T14_...csv`, `T19_...csv` |",
          "| Table 16 (tiers by tolerance) | 03 | `T16_...csv` |",
          "| Table 17 (critical tolerances) | 02 | `T07_critical_tolerances.csv` |",
          "| Table 18 (stage structure) | 03 | `T20_...csv` |",
          "| Table 19 (crisp dynamic soft set) | 04 | `T27_...csv` |",
          "| Table 20 (benchmarks) | 04 | `T24_...csv`, `T25_...csv` |",
          "| Table 21 (running time) | 05 | `T29_scalability.csv` |",
          "| Table C1 (cubic values) | 02 | `T03_cubic_values.csv` |",
          "| Fig. 1 (workflow) | 06 | `figures/Fig_workflow.png` |",
          "| Fig. 3 (stage structure and weights) | 06 | `figures/Fig_stage_structure.png` |",
          "| Fig. 4 (stage severity index) | 06 | `figures/Fig_stage_severity_index.png` |",
          "| Fig. 5 (rank shifts) | 06 | `figures/Fig_rank_shifts.png` |",
          "| Fig. 6 (stage-emphasis path) | 06 | `figures/Fig_stage_emphasis_path.png` |",
          "| Fig. 7 (rank acceptability) | 06 | `figures/Fig_rank_acceptability.png` |",
          "| Fig. 8 (stability curves) | 06 | `figures/Fig_stability_curves.png` |",
          "| Fig. 9 (benchmark ranks) | 06 | `figures/Fig_benchmark_ranks.png` |",
          "", "Figure 2 (ERCC/DG ECHO map) is not computed; it is supplied with the manuscript."]
(ROOT / "MANUSCRIPT_TRACEABILITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"All {len(checks)} statements quoted in the manuscript are reproduced by the result tables.")
