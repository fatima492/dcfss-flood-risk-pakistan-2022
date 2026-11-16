# DCFSS: stage-wise flood severity assessment with dynamic cubic fuzzy soft sets

Code, data, results and tools for the article

> F. Razaq, M. Saeed, M. H. Saeed, M. Salman Habib, M. Ullah. *Time-varying flood disaster risk analysis using dynamic cubic fuzzy soft sets: A case study of Pakistan 2022.* Natural Hazards (under review).

This repository regenerates every number, table and figure of the article from the raw data, and provides two tools for practitioners: a command-line tool and a formula-driven Excel calculator.

## Quick start

```bash
git clone https://github.com/fatima492/dcfss-flood-risk-pakistan-2022.git
cd dcfss-flood-risk-pakistan-2022
pip install -r requirements.txt
python run_all.py            # full run, about 8-10 minutes on one core
python run_all.py --quick    # about 30 seconds; skips the Monte Carlo robustness analysis and the timing benchmark
```

**Windows / IDLE.** Open `run_all.py` in IDLE and press F5, or open any single script in `code/` and press F5: every script runs without arguments. `code/dcfss_tool.py` without arguments analyses the case study and writes `results/tool_output/priority_report.md`; pass `--config my_event.json` to analyse another event (see `tool/USER_GUIDE.md`). The scripts are numbered in the order in which they depend on each other, so after a change in `data/` run them in that order, or simply run `run_all.py`.

Tested with Python 3.13, NumPy 2.5, pandas 3.0, SciPy 1.18, Matplotlib 3.11, openpyxl 3.1. Monte Carlo experiments use the fixed seed 20221118, so results are identical from run to run. Running times in `T29_scalability.csv` depend on the machine.

## Contents

| Path | Content |
|---|---|
| `data/ndma_pakistan_floods_2022_snapshot.csv` | Input data: 7 regions x 7 loss indicators, NDMA cumulative figures 14 June - 18 September 2022 (manuscript Table 4) |
| `data/ndma_national_totals_revision.csv` | National totals on 18 September and 18 November 2022, used to justify the interval tolerance (manuscript Table 6) |
| `data/ndma_sitrep_099_2022-09-20.csv` | Cumulative regional figures of NDMA Monsoon 2022 Daily SITREP No. 099 (20 September 2022), transcribed from the report, used for the provenance check |
| `data/config_pakistan2022.json` | Indicators, types, weights, stage definitions, tolerance, stage-emphasis profiles |
| `data/DATA_DICTIONARY.md` | Variables, units, sources and known data caveats |
| `code/dcfss/` | Reference implementation: `core.py` (normalisation, cubic values, distances, severity index, tiers, critical tolerance, dynamic aggregate), `mcdm.py` (SAW, TOPSIS, VIKOR, crisp dynamic soft set; entropy, CRITIC and ROC weights) |
| `code/01_...py` to `code/10_...py` | Analysis scripts, one per part of the paper (see below) |
| `code/assets/` | Icon font used for the pictograms of Figs. 1 and 3 (Font Awesome Free 6; font SIL OFL 1.1, icons CC BY 4.0) with its licence |
| `code/dcfss_tool.py` | Command-line decision-support tool for any event (see `tool/USER_GUIDE.md`) |
| `code/tests/test_core.py` | Unit tests: metric axioms on random inputs, containment monotonicity, index properties, regression values |
| `results/tables/` | 55 CSV result tables (`T00` to `T30`) |
| `results/DCFSS_results.xlsx` | The same tables in one workbook with an index sheet |
| `results/latex/` | Table bodies exactly as inlined in `sn-article.tex` |
| `results/figures/` | Figures of the manuscript (PNG, 600 dpi) |
| `results/key_numbers_*.json` | Numbers quoted in the text of the manuscript |
| `results/tool_output/` | Output of the command-line tool for the case study |
| `results/run_log.txt` | Console log of the last full run |
| `tool/DCFSS_Calculator.xlsx` | Formula-driven spreadsheet calculator (no programming needed) |
| `tool/build_calculator.py` | Script that builds the calculator |
| `tool/USER_GUIDE.md` | Step-by-step guide for practitioners |
| `LICENSE`, `CITATION.cff` | Licence of the code and citation metadata |
| `MANUSCRIPT_TRACEABILITY.md` | Map from each table, figure and quoted number of the manuscript to the script and result file that produces it |

## Scripts

| Script | Purpose | Manuscript |
|---|---|---|
| `01_reproduce_original_submission.py` | Recomputes Tables 6-9 of the original submission (maximum deviation from the published values 0.0001) and shows that the revised, normalised distances are a constant multiple of the original ones in each stage, so all original rankings are preserved | Response to reviewers |
| `02_main_analysis.py` | Normalisation, cubic values, stage weights, distances, stage severity index, ranks, bands, tiers, critical tolerances, stage-emphasis aggregate, worked example | Sections 6.1-6.7; Tables 4, 5, 7-10, 12, 17, C1 |
| `03_robustness.py` | Weights (six schemes, one-at-a-time, stability intervals, Monte Carlo), tolerance (0-30 %, indicator-specific, Monte Carlo on the data), stage structure, normalisation, ICT exclusion, distance and reference rules | Section 7; Tables 6, 11, 13-16, 18 |
| `04_benchmarks.py` | SAW, TOPSIS, VIKOR, entropy-TOPSIS; static cubic model; crisp dynamic soft set; stage-emphasis path | Sections 6.7 and 8; Tables 12, 19, 20 |
| `05_scalability.py` | Running time versus problem size | Section 9.4; Table 21 |
| `06_figures.py` | All computed figures | Figs. 1, 3-9 |
| `07_latex_tables.py` | LaTeX table bodies | all result tables |
| `08_results_workbook.py` | Excel workbook of all result tables | - |
| `09_verify_manuscript_numbers.py` | Asserts the numbers quoted in the text of the manuscript against the result tables and writes `MANUSCRIPT_TRACEABILITY.md` | whole text |
| `10_data_provenance_check.py` | Compares the input matrix cell by cell with NDMA SITREP No. 099 (20 September 2022) and recomputes the rankings with that report | Section 6.1 |

## Method in brief

1. **Orientation and normalisation.** Each indicator is rescaled to a severity membership in [0, 1] with 1 = most severe region (loss-type: (x - min)/(max - min); capacity-type: (max - x)/(max - min)).
2. **Cubic value.** `([max(0,(1-d)mu), min(1,(1+d)mu)], mu)` with relative tolerance `d` (baseline 10 %).
3. **Stage weights.** Global weights of the indicators active in a stage, rescaled to sum to one.
4. **Distances** of each region to the maximal-severity reference `([1,1],1)` (d+) and the no-loss reference `([0,0],0)` (d-): weighted Euclidean (WED), Hamming (WHD), Hausdorff-Hamming (WHHD).
5. **Stage severity index** `SSI = d- / (d+ + d-)`; rank 1 = most severe = highest priority.
6. **Uncertainty band and tiers.** Regions whose bands overlap share a priority tier; the critical tolerance of two adjacent regions is `(s_hi - s_lo)/(s_hi + s_lo)`.
7. **Stage-emphasis aggregate** `sum_tau lambda_tau * SSI_tau`.

## Figure files of the article

| Article | File in `results/figures/` |
|---|---|
| Fig. 1 | `Fig_workflow.png` |
| Fig. 3 | `Fig_stage_structure.png` |
| Fig. 4 | `Fig_stage_severity_index.png` |
| Fig. 5 | `Fig_rank_shifts.png` |
| Fig. 6 | `Fig_stage_emphasis_path.png` |
| Fig. 7 | `Fig_rank_acceptability.png` |
| Fig. 8 | `Fig_stability_curves.png` |
| Fig. 9 | `Fig_benchmark_ranks.png` |

All figures are written by `code/06_figures.py` as PNG files at 600 dpi. Figure 2 (ERCC/DG ECHO map of the 2022 floods) is not computed and is not part of this repository.

## Relation to the original submission

The original manuscript ranked regions by the distance to `([1,1],1)` computed with the factor `1/(3n)`, `n = 7`, and with weights that were not rescaled within each stage. The revised definitions use `1/3` for the alternative-level distances (no factor for the Hausdorff-type maximum) and stage weights that sum to one, which places all distances in [0, 1] and makes stages comparable. For each stage the revised distance equals the original one multiplied by a positive constant (`sqrt(n/W)`, `n/W` and `3n/W` for WED, WHD and WHHD, where `W` is the sum of the active global weights), so every ranking of the original submission is unchanged. Script 01 verifies this numerically.

## Weights

The baseline weights in `config_pakistan2022.json` are illustrative values assigned by the authors. They were not elicited from an expert panel and were not derived by a formal weighting method. Script 03 therefore tests the results against equal, entropy, CRITIC, rank-order-centroid and hybrid weights, one-at-a-time changes, stability intervals and Monte Carlo sampling of the whole weight space.

## Data source and licence

Input figures: National Disaster Management Authority (NDMA), Pakistan, as redistributed in the Kaggle dataset "Pakistan Flood 2022 Data by NDMA" (K. Hamsafar, 2022, https://www.kaggle.com/datasets/khairullahhamsafar/pakistan-flood-2022-data-by-ndma). The column totals equal the cumulative figures of the NDMA daily situation report of 18 September 2022. The matrix in `data/` is the one printed in Table 4 of the article. It was checked against a primary source: 41 of its 49 values are identical to NDMA Daily SITREP No. 099 of 20 September 2022, and the other eight differ as expected for a report issued two days later (script 10). Final national totals (18 November 2022) are taken from OCHA, Pakistan: 2022 Monsoon Floods - Situation Report No. 11, which reports the NDMA figures.

## Licence and citation

The source code is released under the MIT licence (`LICENSE`). The input figures are public NDMA data. The pictograms of Figs. 1 and 3 use the Font Awesome Free font bundled in `code/assets/` (font SIL OFL 1.1, icons CC BY 4.0). To cite this work, see `CITATION.cff`.
