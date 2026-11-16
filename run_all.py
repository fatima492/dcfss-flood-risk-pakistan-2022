#!/usr/bin/env python3
"""
Regenerate every table and figure of the revised manuscript from the raw data.

    python run_all.py            # full run (about 8-10 minutes, dominated by the Monte Carlo analysis)
    python run_all.py --quick    # skips the robustness Monte Carlo (script 03) and the timing benchmark (05)

Outputs are written to results/tables (CSV), results/latex (table bodies used in
the manuscript), results/figures (PNG, 600 dpi), results/tool_output and
results/DCFSS_results.xlsx. A log is written to results/run_log.txt.
"""
import subprocess, sys, time, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
quick = "--quick" in sys.argv
steps = [("01_reproduce_original_submission.py", []), ("02_main_analysis.py", []),
         ("03_robustness.py", []), ("04_benchmarks.py", []), ("05_scalability.py", []),
         ("06_figures.py", []), ("07_latex_tables.py", []),
         ("10_data_provenance_check.py", []), ("08_results_workbook.py", []),
         ("09_verify_manuscript_numbers.py", []),
         ("dcfss_tool.py", ["--config", str(ROOT / "data" / "config_pakistan2022.json"),
                            "--out", str(ROOT / "results" / "tool_output")])]
if quick:
    steps = [s for s in steps if not s[0].startswith(("03", "05", "09"))]
for d in ("tables", "latex", "figures"):
    (ROOT / "results" / d).mkdir(parents=True, exist_ok=True)
log = open(ROOT / "results" / "run_log.txt", "w", encoding="utf-8")
env = dict(os.environ, PYTHONPATH=str(CODE), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")   # same behaviour on Windows
t_all = time.time()
for script, args in steps:
    t0 = time.time()
    print(f"[run_all] {script} ...", flush=True)
    r = subprocess.run([sys.executable, str(CODE / script), *args], cwd=CODE, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    log.write(f"\n{'=' * 78}\n{script}  (exit {r.returncode}, {time.time() - t0:.1f} s)\n{'=' * 78}\n")
    log.write(r.stdout + ("\nSTDERR:\n" + r.stderr if r.stderr.strip() else ""))
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(f"[run_all] FAILED in {script}")
    print(f"           done in {time.time() - t0:.1f} s")
r = subprocess.run([sys.executable, "-m", "pytest", str(CODE / "tests"), "-q"], cwd=ROOT, env=env,
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
log.write("\n" + "=" * 78 + "\nunit tests\n" + "=" * 78 + "\n" + r.stdout + r.stderr)
print("[run_all] unit tests:", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:])
log.write(f"\nTotal time: {time.time() - t_all:.1f} s\n"); log.close()
print(f"[run_all] finished in {time.time() - t_all:.1f} s; see results/")
