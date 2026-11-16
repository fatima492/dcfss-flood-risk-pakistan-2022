# Manuscript traceability

Each statement below is quoted in the revised manuscript and is asserted by `code/09_verify_manuscript_numbers.py` against the result tables. The script fails if any statement is not reproduced.

| # | Statement in the manuscript | Location | Result file |
|---:|---|---|---|
| 1 | National totals 1,545 deaths; 12,860 injured; 33,046,329 affected | Sec. 6.1 | `T01_raw_data.csv` |
| 2 | Sindh: 44% deaths, 66% injured, 66% roads, 88% houses | Abstract, Sec. 6.5, 9.1 | `T01b` |
| 3 | Punjab 30% of injuries; Balochistan 53% of livestock and 28% of affected population | Abstract, Sec. 6.5 | `T01b` |
| 4 | KP 28% of bridges; GB 17% of bridges | Sec. 6.5 | `T01b` |
| 5 | Punjab has 21 times as many injured as Balochistan | Sec. 6.7 | `T01` |
| 6 | Revisions between <0.1% and 23.3%, mean 12.3%, median 14.8% | Sec. 6.3 | `T17` |
| 7 | 41 of 49 input values identical to NDMA SITREP No. 099 (20 Sep 2022); stage rankings identical with that report | Sec. 6.1 | `T30, T30b` |
| 8 | Stage rankings T1 SPKBAGI, T2 SPKBGAI, T3 SBPKAGI (WHD) | Sec. 6.5, Tables 8-10 | `T05` |
| 9 | Sindh SSI 0.967 / 0.967 / 0.848; maximum of any other region 0.51 | Sec. 6.5, Conclusion | `T05` |
| 10 | T1: Punjab 0.347, KP 0.298, Balochistan 0.283 | Sec. 6.5 | `T05` |
| 11 | T2: Punjab 0.200, KP 0.146, Balochistan 0.084 | Sec. 6.5 | `T05` |
| 12 | T3: Balochistan 0.508, Punjab 0.252, KP 0.160 | Sec. 6.5 | `T05` |
| 13 | Worked example Punjab T1: d+ 0.6528, d- 0.3472; WED 0.6591/0.3588/0.3525; WHHD 0.6875/0.3819/0.3571; band [0.3125, 0.3819] | Sec. 6.4, Fig. 1 | `T05` |
| 14 | Tiers at 10%: T1 Sindh | Punjab,KP,Balochistan | AJ&K | GB | ICT; T2 seven tiers; T3 AJ&K and GB share a tier | Sec. 6.5 | `T05` |
| 15 | Only disagreement among distances: Balochistan/GB at T2 under WED | Sec. 6.5 | `T05` |
| 16 | Kendall W over nine distance/reference rules: 1.000 (T1, T3), 0.988 (T2) | Sec. 6.5 | `key_numbers_robustness.json` |
| 17 | Order of the six regions preserved at every stage and distance when ICT is excluded; GB index 0 at T1 | Sec. 6.6, Table 11 | `T22` |
| 18 | Static ranks differ from stage ranks for 5 / 3 / 2 regions; Spearman 0.857 / 0.893 / 0.964 | Abstract, Sec. 6.7, Conclusion | `T26` |
| 19 | Balochistan overtakes KP at about 15% and Punjab at about 31% of the relief-to-recovery shift | Sec. 6.7, Fig. 6 | `T28` |
| 20 | Early response: Punjab 2nd, Balochistan 3rd; Sindh first for every profile | Sec. 6.7, Table 12 | `T08` |
| 21 | Proportional shares: Balochistan 14.5 / 5.8 / 28.7 %, Sindh 49.3 / 67.0 / 47.9 % | Sec. 9.1 | `T08b` |
| 22 | Sindh first in 17 of 18 scheme-stage combinations; complete order unchanged in 14 of 18 | Sec. 7.1 | `T11` |
| 23 | CRITIC gives 61% of the recovery-stage weight to livestock; entropy's largest weight is houses | Sec. 7.1 | `T10` |
| 24 | +-20% single-weight changes: no ranking change; +-50%: 3 of 18 cases change | Sec. 7.1 | `T12` |
| 25 | Stability: deaths at T1 up to 0.709 (baseline 0.625); bridges at T2 up to 0.190 (baseline 0.111); livestock at T3 up to 0.524 | Sec. 7.1, 7.5, Table 14 | `T13` |
| 26 | Weights +-20%: complete ranking preserved with probability >= 0.998; +-50%: 0.80 / 0.87 / 1.00 | Abstract-level claim, Sec. 7.1, Conclusion | `T14` |
| 27 | Uniform weights: Sindh first with probability 1.00 / 1.00 / 0.78 | Sec. 7.1 | `T14` |
| 28 | Uniform weights at T2: KP second with probability 0.63, Punjab 0.35; ICT always last, AJ&K never above 5th | Sec. 7.1, Fig. 7a | `T14b` |
| 29 | Rankings identical for every tolerance 0-30% under each distance | Abstract, Sec. 7.2 | `T15` |
| 30 | Critical tolerances: KP/Balochistan 2.6%, Punjab/KP 7.6% (T1); minimum 15.6% at T2; AJ&K/GB 7.4% at T3 | Sec. 7.2, Table 17 | `T07` |
| 31 | Critical tolerance values (detail) | Sec. 7.2 | `T07` |
| 32 | Punjab and KP merge at T2 from 20% and at T3 from 25%; Sindh alone in tier 1 up to 30% | Sec. 7.2, Table 16 | `T16` |
| 33 | Indicator-specific tolerances: same rankings and tiers as uniform 10% | Sec. 7.2 | `T18` |
| 34 | Data +-10%: ranking preserved with probability 0.71 / 1.00 / 0.99; Sindh always first; Punjab stays 2nd at T1 with 0.98 | Sec. 7.2, Table 15 | `T19` |
| 35 | Stage structure: 17 variants, Sindh always first, 6 unchanged, rho >= 0.89 in all but one (0.775) | Sec. 7.3, Table 18 | `T20` |
| 36 | Four normalisation rules give identical stage rankings | Abstract, Sec. 7.4 | `T21` |
| 37 | SAW, TOPSIS, VIKOR: rho = 1 at T2 and T3; TOPSIS and VIKOR rho = 0.893 at T1; SAW rho = 1 at T1 | Abstract, Sec. 8.2 | `T25` |
| 38 | Kendall W over eight methods 0.959 / 0.987 / 1.000; VIKOR conditions hold for Sindh at every stage | Sec. 8.2 | `key_numbers_benchmarks.json` |
| 39 | Crisp dynamic soft set, threshold 0.50: 6 / 5 / 5 regions tied at zero; 2 / 3 / 3 rank levels | Sec. 8.1, Table 19 | `T27` |

## Tables and figures

| Manuscript item | Produced by | Result file |
|---|---|---|
| Table 4 (input data) | 02 | `T01_raw_data.csv`, `latex/tab_raw.tex` |
| Table 5 (weights) | 02 | `T04_stage_weights.csv` |
| Table 6 (revision of national totals) | 03 | `T17_observed_revision_national_totals.csv` |
| Table 7 (severity memberships) | 02 | `T02_severity_membership.csv` |
| Tables 8-10 (stage results) | 02 | `T05_stage_results.csv` |
| Table 11 (ICT excluded) | 03 | `T22_ICT_excluded.csv` |
| Table 12 (static vs stage ranks, stage emphasis) | 02, 04 | `T26_...csv`, `T08_...csv` |
| Table 13 (weighting schemes) | 03 | `T10_...csv`, `T11_...csv` |
| Table 14 (weight stability intervals) | 03 | `T13_...csv` |
| Table 15 (Monte Carlo) | 03 | `T14_...csv`, `T19_...csv` |
| Table 16 (tiers by tolerance) | 03 | `T16_...csv` |
| Table 17 (critical tolerances) | 02 | `T07_critical_tolerances.csv` |
| Table 18 (stage structure) | 03 | `T20_...csv` |
| Table 19 (crisp dynamic soft set) | 04 | `T27_...csv` |
| Table 20 (benchmarks) | 04 | `T24_...csv`, `T25_...csv` |
| Table 21 (running time) | 05 | `T29_scalability.csv` |
| Table C1 (cubic values) | 02 | `T03_cubic_values.csv` |
| Fig. 1 (workflow) | 06 | `figures/Fig_workflow.png` |
| Fig. 3 (stage structure and weights) | 06 | `figures/Fig_stage_structure.png` |
| Fig. 4 (stage severity index) | 06 | `figures/Fig_stage_severity_index.png` |
| Fig. 5 (rank shifts) | 06 | `figures/Fig_rank_shifts.png` |
| Fig. 6 (stage-emphasis path) | 06 | `figures/Fig_stage_emphasis_path.png` |
| Fig. 7 (rank acceptability) | 06 | `figures/Fig_rank_acceptability.png` |
| Fig. 8 (stability curves) | 06 | `figures/Fig_stability_curves.png` |
| Fig. 9 (benchmark ranks) | 06 | `figures/Fig_benchmark_ranks.png` |

Figure 2 (ERCC/DG ECHO map) is not computed; it is supplied with the manuscript.
