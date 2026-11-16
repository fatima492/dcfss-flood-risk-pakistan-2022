"""
05 - Computational cost of the DCFSS evaluation (Reviewer 4, comment 5-i).

Times the complete pipeline (normalisation, cubic construction, distances to
both references, three indices, ranking) on synthetic problems of growing size.
The cost is linear in (number of stages) x (alternatives) x (attributes).
"""
from pathlib import Path
import time, platform, json
import numpy as np
import pandas as pd
from dcfss import severity_membership, stage_evaluation

ROOT = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(7)
rows = []
for n, m, T in [(7, 7, 3), (100, 10, 3), (1_000, 20, 6), (10_000, 20, 12),
                (100_000, 50, 12), (1_000_000, 50, 12)]:
    X = rng.gamma(0.6, 1000.0, size=(n, m))
    w = rng.uniform(0.5, 1.5, m)
    k = max(2, m // 3)
    stages = [sorted(rng.choice(m, size=k, replace=False).tolist()) for _ in range(T)]
    reps = 200 if n <= 100 else (20 if n <= 10_000 else 3)
    best = np.inf
    for _ in range(reps):
        t0 = time.perf_counter()
        mu = severity_membership(X, ["loss"] * m)
        for idx in stages:
            stage_evaluation(mu, w, idx, 0.10)
        best = min(best, time.perf_counter() - t0)
    rows.append({"alternatives_n": n, "attributes_m": m, "stages_T": T, "active_per_stage": k,
                 "cell_evaluations": n * k * T, "runtime_seconds": best,
                 "microseconds_per_cell": 1e6 * best / (n * k * T)})
df = pd.DataFrame(rows)
df.to_csv(ROOT / "results" / "tables" / "T29_scalability.csv", index=False)
meta = {"python": platform.python_version(), "numpy": np.__version__, "machine": platform.machine(),
        "processor": platform.processor() or "n/a", "note": "single core, best of repeated runs"}
(ROOT / "results" / "key_numbers_scalability.json").write_text(json.dumps(
    {"table": df.round(6).to_dict(orient="records"), "environment": meta}, indent=2), encoding="utf-8")
print(df.round(5).to_string(index=False)); print(meta)
