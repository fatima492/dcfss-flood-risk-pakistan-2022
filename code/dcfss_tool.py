#!/usr/bin/env python3
"""
dcfss_tool.py - command-line decision-support tool for the DCFSS framework.

Usage
-----
    python dcfss_tool.py
    python dcfss_tool.py --config my_event.json --tolerance 0.15 --out report_dir

Without arguments (for example when the file is opened in IDLE and run with F5) the tool
analyses the 2022 Pakistan case study (data/config_pakistan2022.json) and writes the report
to results/tool_output.

The tool needs only (i) a CSV table of indicators per region and (ii) a small
JSON file naming the indicators, their weights and the indicators that are
active in each stage (see data/config_pakistan2022.json and tool/USER_GUIDE.md).
No knowledge of fuzzy mathematics is required to read the output:

    priority_report.md   plain-language briefing per stage
    stage_<id>.csv       index, rank, uncertainty band and tier per region
"""
import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))   # find the dcfss package from any working directory
from dcfss import load_problem, evaluate, priority_tiers, critical_tolerance, dynamic_index, rank_desc


ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "data" / "config_pakistan2022.json"),
                    help="JSON configuration file (default: the 2022 Pakistan case study)")
    ap.add_argument("--out", default=str(ROOT / "results" / "tool_output"),
                    help="output directory (default: results/tool_output)")
    ap.add_argument("--tolerance", type=float, default=None,
                    help="relative reporting tolerance (overrides the configuration), e.g. 0.10")
    ap.add_argument("--distance", choices=["WHD", "WED", "WHHD"], default="WHD")
    args = ap.parse_args()

    P = load_problem(args.config)
    tol = P.tolerance if args.tolerance is None else args.tolerance
    res = evaluate(P, tolerance=tol)
    mu = res["_mu"]
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    R = P.alternatives
    tol_txt = f"{100 * tol:.0f} %" if not isinstance(tol, dict) else "attribute-specific"
    lines = [f"# DCFSS priority report", "", f"**Event:** {P.name}  ",
             f"**Regions:** {P.n}  |  **Indicators:** {P.m}  |  **Reporting tolerance:** {tol_txt}  |  "
             f"**Distance:** {args.distance}", "",
             "Index = stage severity index (0 = no reported loss, 1 = worst observed on every active indicator). "
             "Regions in the same tier cannot be told apart once the reporting tolerance is taken into account; "
             "treat them as equal priority.", ""]
    for s, active in P.stages.items():
        e = res[s]; lo, mid, hi = e["band"]; tiers = priority_tiers(lo, mid, hi)
        df = pd.DataFrame({"region": R, "index": e["ssi"][args.distance], "rank": e["rank"][args.distance],
                           "band_lower": lo, "band_upper": hi, "tier": tiers}).sort_values("rank")
        df.round(4).to_csv(out / f"stage_{s}.csv", index=False)
        idx = [P.col(a) for a in active]
        lines += [f"## Stage {s}: {P.stage_labels[s]}", "",
                  "Active indicators (stage weight): " +
                  ", ".join(f"{P.labels[a]} ({w:.2f})" for a, w in zip(active, e["weights"])), "",
                  "| Rank | Region | Index | Band | Tier |", "|---:|---|---:|---|---:|"]
        for _, r in df.iterrows():
            lines.append(f"| {int(r['rank'])} | {r.region} | {r['index']:.3f} | "
                         f"{r.band_lower:.3f} to {r.band_upper:.3f} | {int(r.tier)} |")
        order = np.argsort(-mid, kind="stable")
        notes = []
        for a, b in zip(order[:-1], order[1:]):
            if mid[b] <= 0:
                continue
            d = critical_tolerance(mu[a, idx], mu[b, idx], e["weights"])
            if d <= (tol if not isinstance(tol, dict) else 0.10):
                notes.append(f"{R[a]} and {R[b]} are separated only if reporting error is below {100*d:.1f} %")
        lines += ["", "Robustness note: " + ("; ".join(notes) + "." if notes else
                  "all adjacent ranks are separated at the stated tolerance."), ""]
    if P.profiles:
        scores = {s: res[s]["ssi"][args.distance] for s in P.stages}
        lines += ["## Stage-emphasis aggregate", "",
                  "| Profile (weights on stages) | " + " | ".join(R) + " |",
                  "|---|" + "---:|" * P.n]
        for name, lam in P.profiles.items():
            v = dynamic_index(scores, lam); rk = rank_desc(v)
            lines.append(f"| {name} ({', '.join(f'{x:.2f}' for x in lam)}) | " +
                         " | ".join(f"{v[i]:.3f} (#{rk[i]})" for i in range(P.n)) + " |")
        lines.append("")
    (out / "priority_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nWritten to {out.resolve()}")


if __name__ == "__main__":
    main()
