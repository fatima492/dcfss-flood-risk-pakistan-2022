"""
dcfss.core
==========
Core computations of the Dynamic Cubic Fuzzy Soft Set (DCFSS) decision framework.

Notation (matches the revised manuscript)
-----------------------------------------
u in U            alternatives (regions), n = |U|
eps in E          attributes (parameters)
tau in T          stages (time / context index)
A_tau             active attribute set at stage tau
mu                crisp (reference) severity membership in [0, 1]
[xi, zeta]        interval-valued membership (lower, upper)
delta             relative interval tolerance
Theta_plus        maximal-severity reference  ([1, 1], 1)
Theta_minus       no-loss reference           ([0, 0], 0)
w_tau(eps)        stage weights (positive, summing to 1 over A_tau)

All functions are pure NumPy and have O(|T| * n * m) cost.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

import numpy as np
import pandas as pd

DISTANCES = ("WED", "WHD", "WHHD")


# ----------------------------------------------------------------------------
# Configuration / data loading
# ----------------------------------------------------------------------------
@dataclass
class Problem:
    """A DCFSS decision problem: raw data + attribute/stage structure."""
    alternatives: List[str]
    attributes: List[str]                 # attribute ids, e.g. ["e1", ..., "e7"]
    labels: Dict[str, str]                # id -> human readable label
    types: Dict[str, str]                 # id -> "loss" | "capacity"
    weights: Dict[str, float]             # global (un-normalised) weights
    stages: Dict[str, List[str]]          # stage id -> active attribute ids
    stage_labels: Dict[str, str]
    X: np.ndarray                         # raw data, shape (n, m)
    tolerance: float | Dict[str, float] = 0.10
    normalisation: str = "minmax"
    profiles: Dict[str, List[float]] = field(default_factory=dict)
    name: str = ""

    @property
    def n(self) -> int:
        return len(self.alternatives)

    @property
    def m(self) -> int:
        return len(self.attributes)

    def col(self, attr: str) -> int:
        return self.attributes.index(attr)

    def w_vector(self) -> np.ndarray:
        return np.array([self.weights[a] for a in self.attributes], dtype=float)

    def delta_vector(self, tolerance=None) -> np.ndarray:
        t = self.tolerance if tolerance is None else tolerance
        if isinstance(t, Mapping):
            return np.array([float(t[a]) for a in self.attributes])
        return np.full(self.m, float(t))


def load_problem(config_path: str | Path) -> Problem:
    """Load a problem from a JSON configuration file (see data/config_*.json)."""
    config_path = Path(config_path)
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    df = pd.read_csv(config_path.parent / cfg["data_file"])
    attrs = list(cfg["attributes"].keys())
    X = df[[cfg["attributes"][a]["column"] for a in attrs]].to_numpy(dtype=float)
    if np.isnan(X).any():
        raise ValueError("Missing values in data: deactivate the attribute for "
                         "the affected stage or impute before running.")
    return Problem(
        alternatives=df[cfg["id_column"]].astype(str).tolist(),
        attributes=attrs,
        labels={a: cfg["attributes"][a]["label"] for a in attrs},
        types={a: cfg["attributes"][a].get("type", "loss") for a in attrs},
        weights={a: float(cfg["attributes"][a]["weight"]) for a in attrs},
        stages={s: list(v["active"]) for s, v in cfg["stages"].items()},
        stage_labels={s: v.get("label", s) for s, v in cfg["stages"].items()},
        X=X,
        tolerance=cfg.get("tolerance", 0.10),
        normalisation=cfg.get("normalisation", "minmax"),
        profiles=cfg.get("stage_emphasis_profiles", {}),
        name=cfg.get("name", ""),
    )


# ----------------------------------------------------------------------------
# Step 1 - orientation and normalisation (severity membership)
# ----------------------------------------------------------------------------
def severity_membership(X: np.ndarray, types: Sequence[str],
                        method: str = "minmax") -> np.ndarray:
    """Map raw indicators to severity memberships mu in [0, 1].

    After this step 1 always denotes the most severe observed condition:
    * loss-type attributes (deaths, damage, ...): larger raw value -> larger mu
    * capacity-type attributes (relief coverage, ...): larger raw value -> smaller mu

    method: "minmax" (baseline), "max", "sum", "vector".
    Columns with zero range map to 0 (no discrimination).
    """
    X = np.asarray(X, dtype=float)
    mu = np.zeros_like(X)
    for j in range(X.shape[1]):
        x = X[:, j]
        if method == "minmax":
            rng = x.max() - x.min()
            v = (x - x.min()) / rng if rng > 0 else np.zeros_like(x)
            if types[j] == "capacity":
                v = 1.0 - v if rng > 0 else v
        elif method == "max":
            v = x / x.max() if x.max() > 0 else np.zeros_like(x)
            if types[j] == "capacity":
                v = 1.0 - v
        elif method == "sum":
            v = x / x.sum() if x.sum() > 0 else np.zeros_like(x)
            if types[j] == "capacity":
                v = (1.0 - v) / max(len(x) - 1, 1)
        elif method == "vector":
            nrm = np.sqrt((x ** 2).sum())
            v = x / nrm if nrm > 0 else np.zeros_like(x)
            if types[j] == "capacity":
                v = 1.0 - v
        else:
            raise ValueError(f"unknown normalisation '{method}'")
        mu[:, j] = v
    return mu


# ----------------------------------------------------------------------------
# Step 2 - cubic fuzzy values ([xi, zeta], mu)
# ----------------------------------------------------------------------------
def cubic_values(mu: np.ndarray, delta) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Internal cubic values: xi = max(0,(1-delta)mu), zeta = min(1,(1+delta)mu)."""
    mu = np.asarray(mu, dtype=float)
    d = np.broadcast_to(np.asarray(delta, dtype=float), mu.shape)
    lower = np.clip((1.0 - d) * mu, 0.0, 1.0)
    upper = np.clip((1.0 + d) * mu, 0.0, 1.0)
    return lower, upper, mu


# ----------------------------------------------------------------------------
# Step 3 - stage weights
# ----------------------------------------------------------------------------
def stage_weights(w: np.ndarray, active_idx: Sequence[int]) -> np.ndarray:
    """Weights restricted to the active set and renormalised to sum to one."""
    ws = np.asarray(w, dtype=float)[list(active_idx)]
    if (ws <= 0).any():
        raise ValueError("stage weights must be strictly positive")
    return ws / ws.sum()


# ----------------------------------------------------------------------------
# Step 4 - distances
# ----------------------------------------------------------------------------
def _components(L, U, M, ref):
    """Absolute component differences to a reference cubic value/array."""
    if np.isscalar(ref):
        rl = ru = rm = float(ref)
    else:
        rl, ru, rm = ref
    return np.abs(L - rl), np.abs(U - ru), np.abs(M - rm)


def alt_distances(L, U, M, w, ref) -> Dict[str, np.ndarray]:
    """Alternative-wise weighted distances to a reference (one value per row).

    L, U, M : arrays (n, k) restricted to the k active attributes
    w       : stage weights, shape (k,), positive, sum 1
    ref     : scalar theta (reference ([theta, theta], theta)) or a tuple of
              arrays (L_ref, U_ref, M_ref) of shape (n, k) or (k,)
    """
    a, b, c = _components(L, U, M, ref)
    wed = np.sqrt(((a ** 2 + b ** 2 + c ** 2) * w).sum(axis=1) / 3.0)
    whd = ((a + b + c) * w).sum(axis=1) / 3.0
    whhd = (np.maximum(np.maximum(a, b), c) * w).sum(axis=1)
    return {"WED": wed, "WHD": whd, "WHHD": whhd}


def set_distances(F, G, w) -> Dict[str, float]:
    """Stage-level distances between two cubic fuzzy soft sets F, G.

    F, G : tuples (L, U, M) with arrays of shape (n, k).
    Relation to the alternative-wise distances d(u):
        D_WED^2 = mean_u d_WED(u)^2,  D_WHD = mean_u d_WHD(u),  D_WHHD = mean_u d_WHHD(u)
    """
    d = alt_distances(F[0], F[1], F[2], w, G)
    return {"WED": float(np.sqrt(np.mean(d["WED"] ** 2))),
            "WHD": float(np.mean(d["WHD"])),
            "WHHD": float(np.mean(d["WHHD"]))}


# ----------------------------------------------------------------------------
# Step 5 - stage severity index and ranking
# ----------------------------------------------------------------------------
def rank_desc(score: np.ndarray, decimals: int = 10) -> np.ndarray:
    """Competition ranking, 1 = largest score. Ties share the smallest rank.
    Scores are rounded to `decimals` places so that values that differ only by
    floating-point noise are treated as tied."""
    from scipy.stats import rankdata
    s = np.round(np.asarray(score, dtype=float), decimals)
    return rankdata(-s, method="min").astype(int)


def rank_asc(score: np.ndarray, decimals: int = 10) -> np.ndarray:
    return rank_desc(-np.asarray(score, dtype=float), decimals)


def stage_evaluation(mu: np.ndarray, w_global: np.ndarray, active_idx: Sequence[int],
                     delta) -> Dict[str, object]:
    """Evaluate one stage. Returns distances to both references, the stage
    severity index (SSI) for the three distances, ranks, and the uncertainty band."""
    idx = list(active_idx)
    w = stage_weights(w_global, idx)
    d = np.broadcast_to(np.asarray(delta, dtype=float), (mu.shape[1],))[idx]
    L, U, M = cubic_values(mu[:, idx], d)
    d_plus = alt_distances(L, U, M, w, 1.0)    # to maximal-severity reference
    d_minus = alt_distances(L, U, M, w, 0.0)   # to no-loss reference
    ssi, rank = {}, {}
    for k in DISTANCES:
        den = d_plus[k] + d_minus[k]
        ssi[k] = np.divide(d_minus[k], den, out=np.zeros_like(den), where=den > 0)
        rank[k] = rank_desc(ssi[k])
    band_lo = (L * w).sum(axis=1)
    band_mid = (M * w).sum(axis=1)
    band_hi = (U * w).sum(axis=1)
    return {"weights": w, "L": L, "U": U, "M": M,
            "d_plus": d_plus, "d_minus": d_minus,
            "ssi": ssi, "rank": rank,
            "rank_dplus": {k: rank_asc(d_plus[k]) for k in DISTANCES},
            "rank_dminus": {k: rank_desc(d_minus[k]) for k in DISTANCES},
            "band": (band_lo, band_mid, band_hi)}


def evaluate(problem: Problem, *, weights: np.ndarray | None = None,
             tolerance=None, normalisation: str | None = None,
             stages: Mapping[str, Iterable[str]] | None = None,
             X: np.ndarray | None = None) -> Dict[str, Dict[str, object]]:
    """Run the full DCFSS evaluation for every stage of a problem."""
    Xd = problem.X if X is None else X
    types = [problem.types[a] for a in problem.attributes]
    mu = severity_membership(Xd, types, normalisation or problem.normalisation)
    w = problem.w_vector() if weights is None else np.asarray(weights, dtype=float)
    delta = problem.delta_vector(tolerance)
    st = problem.stages if stages is None else stages
    out = {}
    for s, active in st.items():
        idx = [problem.col(a) for a in active]
        out[s] = stage_evaluation(mu, w, idx, delta)
        out[s]["active"] = list(active)
    out["_mu"] = mu
    return out


# ----------------------------------------------------------------------------
# Uncertainty tiers and critical tolerance
# ----------------------------------------------------------------------------
def priority_tiers(band_lo: np.ndarray, band_mid: np.ndarray,
                   band_hi: np.ndarray) -> np.ndarray:
    """Group alternatives into priority tiers.

    Alternatives are sorted by the central score. Two consecutive alternatives
    belong to the same tier when their uncertainty bands overlap, i.e. when the
    lower bound of the higher one does not exceed the upper bound of the lower
    one. Tier 1 is the highest priority. Alternatives with identical degenerate
    bands (e.g. all-zero profiles) share a tier.
    """
    order = np.argsort(-band_mid, kind="stable")
    tiers = np.empty(len(order), dtype=int)
    t = 1
    tiers[order[0]] = t
    for a, b in zip(order[:-1], order[1:]):
        separated = band_lo[a] > band_hi[b] + 1e-12
        if separated:
            t += 1
        tiers[b] = t
    return tiers


def critical_tolerance(mu_hi: np.ndarray, mu_lo: np.ndarray, w: np.ndarray,
                       tol: float = 1e-9) -> float:
    """Largest uniform tolerance delta for which alternative 'hi' remains
    robustly separated from 'lo':  sum w (1-delta) mu_hi  >  sum w min(1,(1+delta) mu_lo).
    Solved by bisection (the gap is monotone decreasing in delta).
    Without capping the closed form is (s_hi - s_lo) / (s_hi + s_lo)."""
    def gap(d):
        return ((1 - d) * mu_hi * w).sum() - (np.minimum(1.0, (1 + d) * mu_lo) * w).sum()
    if gap(0.0) <= 0:
        return 0.0
    lo, hi = 0.0, 1.0
    if gap(hi) > 0:
        return 1.0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if gap(mid) > 0:
            lo = mid
        else:
            hi = mid
    return lo


# ----------------------------------------------------------------------------
# Cross-stage (dynamic) aggregation
# ----------------------------------------------------------------------------
def dynamic_index(stage_scores: Mapping[str, np.ndarray], lam: Sequence[float]) -> np.ndarray:
    """Stage-emphasis aggregate  Psi_lambda(u) = sum_tau lambda_tau * Psi_tau(u)."""
    lam = np.asarray(lam, dtype=float)
    lam = lam / lam.sum()
    keys = list(stage_scores.keys())
    return sum(l * np.asarray(stage_scores[k]) for l, k in zip(lam, keys))


# ----------------------------------------------------------------------------
# Rank agreement statistics
# ----------------------------------------------------------------------------
def spearman(r1, r2) -> float:
    from scipy.stats import spearmanr
    rho = spearmanr(r1, r2).correlation
    return float(rho)


def kendall(r1, r2) -> float:
    from scipy.stats import kendalltau
    return float(kendalltau(r1, r2).correlation)


def kendall_w(rank_matrix: np.ndarray) -> float:
    """Kendall's coefficient of concordance W for a (k rankings x n items) matrix
    (no tie correction; ties are rare here and make W slightly conservative)."""
    R = np.asarray(rank_matrix, dtype=float)
    k, n = R.shape
    Rs = R.sum(axis=0)
    S = ((Rs - Rs.mean()) ** 2).sum()
    return float(12.0 * S / (k ** 2 * (n ** 3 - n)))
