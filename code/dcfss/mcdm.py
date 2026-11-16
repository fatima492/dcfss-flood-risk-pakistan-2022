"""
dcfss.mcdm
==========
Benchmark multi-criteria methods and objective weighting schemes used for the
comparative analysis. All benchmarks receive the SAME severity-oriented,
min-max normalised matrix mu (n x k) and the SAME stage weights w (k,) as the
DCFSS model, so that differences in ranking are attributable to the
aggregation rule alone. Rank 1 always denotes the highest severity / priority.
"""
from __future__ import annotations

import numpy as np

from .core import rank_asc, rank_desc


# ----------------------------------------------------------------------------
# Benchmarks
# ----------------------------------------------------------------------------
def saw(mu: np.ndarray, w: np.ndarray):
    """Simple additive weighting (weighted linear aggregation)."""
    score = (mu * w).sum(axis=1)
    return score, rank_desc(score)


def topsis(mu: np.ndarray, w: np.ndarray, vector_normalise: bool = False):
    """TOPSIS (Hwang & Yoon 1981) on the severity matrix.

    The 'ideal' point of the severity ordering is the column-wise maximum
    (most severe), the anti-ideal the column-wise minimum; closeness C in [0,1]
    is high for severe alternatives.
    vector_normalise=True applies the classical vector normalisation first.
    """
    R = mu.copy()
    if vector_normalise:
        nrm = np.sqrt((R ** 2).sum(axis=0))
        nrm[nrm == 0] = 1.0
        R = R / nrm
    V = R * w
    v_pos, v_neg = V.max(axis=0), V.min(axis=0)
    s_pos = np.sqrt(((V - v_pos) ** 2).sum(axis=1))
    s_neg = np.sqrt(((V - v_neg) ** 2).sum(axis=1))
    den = s_pos + s_neg
    C = np.divide(s_neg, den, out=np.zeros_like(den), where=den > 0)
    return C, rank_desc(C)


def vikor(mu: np.ndarray, w: np.ndarray, v: float = 0.5):
    """VIKOR (Opricovic & Tzeng 2004) on the severity matrix.

    f* = column maximum (most severe), f- = column minimum.
    S = group utility, R = individual regret, Q = compromise index.
    Smallest Q = closest to the most-severe profile = rank 1.
    Returns Q, ranks, and a dict with S, R and the two acceptability conditions.
    """
    f_star, f_minus = mu.max(axis=0), mu.min(axis=0)
    rng = f_star - f_minus
    rng[rng == 0] = 1.0
    D = (f_star - mu) / rng * w
    S, R = D.sum(axis=1), D.max(axis=1)
    def _n(x):
        r = x.max() - x.min()
        return (x - x.min()) / r if r > 0 else np.zeros_like(x)
    Q = v * _n(S) + (1 - v) * _n(R)
    ranks = rank_asc(Q)
    order = np.argsort(Q, kind="stable")
    n = len(Q)
    dq = 1.0 / (n - 1)
    c1 = bool(Q[order[1]] - Q[order[0]] >= dq)                  # acceptable advantage
    c2 = bool(order[0] in (np.argmin(S), np.argmin(R)))         # acceptable stability
    return Q, ranks, {"S": S, "R": R, "C1_advantage": c1, "C2_stability": c2, "DQ": dq}


def crisp_dynamic_soft_set(mu: np.ndarray, w: np.ndarray, threshold: float = 0.5):
    """Classical (crisp) dynamic soft set baseline.

    F_tau(eps) = {u : mu(eps, u) >= threshold}; the weighted choice value of u
    is the total weight of the parameters whose approximate set contains u.
    """
    member = (mu >= threshold).astype(float)
    score = (member * w).sum(axis=1)
    return score, rank_desc(score), member


# ----------------------------------------------------------------------------
# Weighting schemes
# ----------------------------------------------------------------------------
def entropy_weights(X: np.ndarray) -> np.ndarray:
    """Shannon entropy weights from non-negative raw data (0*ln 0 := 0)."""
    X = np.asarray(X, dtype=float)
    n = X.shape[0]
    col = X.sum(axis=0)
    col[col == 0] = 1.0
    P = X / col
    with np.errstate(divide="ignore", invalid="ignore"):
        plogp = np.where(P > 0, P * np.log(P), 0.0)
    e = -plogp.sum(axis=0) / np.log(n)
    d = 1.0 - e
    return d / d.sum()


def critic_weights(mu: np.ndarray) -> np.ndarray:
    """CRITIC weights (Diakoulaki et al. 1995) from the normalised matrix."""
    sd = mu.std(axis=0, ddof=1)
    corr = np.corrcoef(mu, rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0)
    info = sd * (1.0 - corr).sum(axis=0)
    return info / info.sum()


def roc_weights_from_scores(w: np.ndarray) -> np.ndarray:
    """Rank-order-centroid weights (Barron & Barrett 1996) using only the
    ORDER of importance implied by a weight vector; tied attributes share the
    mean of the ROC weights of the positions they occupy."""
    w = np.asarray(w, dtype=float)
    m = len(w)
    roc = np.array([sum(1.0 / k for k in range(i, m + 1)) / m for i in range(1, m + 1)])
    order = np.argsort(-w, kind="stable")
    out = np.empty(m)
    i = 0
    while i < m:
        j = i
        while j + 1 < m and np.isclose(w[order[j + 1]], w[order[i]]):
            j += 1
        out[order[i:j + 1]] = roc[i:j + 1].mean()
        i = j + 1
    return out / out.sum()
