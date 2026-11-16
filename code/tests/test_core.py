"""Unit tests: metric properties of the three distances, index properties,
and regression values of the case study. Run with:  python -m pytest code/tests -q"""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dcfss import (load_problem, evaluate, alt_distances, set_distances, cubic_values,
                   critical_tolerance, rank_desc)
from dcfss.mcdm import saw, topsis, vikor, entropy_weights, roc_weights_from_scores

ROOT = Path(__file__).resolve().parents[2]
rng = np.random.default_rng(1)


def random_cubic(n, k):
    a, b, m = rng.uniform(0, 1, (3, n, k))
    return np.minimum(a, b), np.maximum(a, b), m


def test_metric_axioms_alternative_and_set_level():
    for _ in range(300):
        n, k = rng.integers(1, 6), rng.integers(1, 7)
        w = rng.uniform(0.05, 1, k); w /= w.sum()
        F, G, H = random_cubic(n, k), random_cubic(n, k), random_cubic(n, k)
        dFG, dGF = alt_distances(*F, w, G), alt_distances(*G, w, F)
        dFH, dHG, dFF = alt_distances(*F, w, H), alt_distances(*H, w, G), alt_distances(*F, w, F)
        for key in ("WED", "WHD", "WHHD"):
            assert (dFG[key] >= 0).all() and (dFG[key] <= 1 + 1e-12).all()      # boundedness
            assert np.allclose(dFF[key], 0)                                     # identity
            assert np.allclose(dFG[key], dGF[key])                              # symmetry
            assert (dFG[key] <= dFH[key] + dHG[key] + 1e-12).all()              # triangle inequality
        sFG, sFH, sHG = set_distances(F, G, w), set_distances(F, H, w), set_distances(H, G, w)
        for key in sFG:
            assert 0 <= sFG[key] <= 1 + 1e-12
            assert sFG[key] <= sFH[key] + sHG[key] + 1e-12


def test_containment_monotonicity():
    """F subset G subset H  =>  d(F,G) <= d(F,H) and d(G,H) <= d(F,H)."""
    for _ in range(200):
        n, k = 4, 5
        w = rng.uniform(0.05, 1, k); w /= w.sum()
        lows = np.sort(rng.uniform(0, 0.5, (3, n, k)), axis=0)[::-1]     # lower bounds decreasing F->H
        ups = np.sort(rng.uniform(0.5, 1, (3, n, k)), axis=0)            # upper bounds increasing
        mus = np.sort(rng.uniform(0, 1, (3, n, k)), axis=0)              # crisp grades increasing
        F, G, H = [(lows[i], ups[i], mus[i]) for i in range(3)]
        for key in ("WED", "WHD", "WHHD"):
            assert (alt_distances(*F, w, G)[key] <= alt_distances(*F, w, H)[key] + 1e-12).all()
            assert (alt_distances(*G, w, H)[key] <= alt_distances(*F, w, H)[key] + 1e-12).all()


def test_hamming_reference_complementarity_and_index_bounds():
    for _ in range(100):
        mu = rng.uniform(0, 1, (6, 4)); w = rng.uniform(0.1, 1, 4); w /= w.sum()
        L, U, M = cubic_values(mu, 0.1)
        dp, dm = alt_distances(L, U, M, w, 1.0), alt_distances(L, U, M, w, 0.0)
        assert np.allclose(dp["WHD"] + dm["WHD"], 1.0)
        for key in dp:
            ssi = dm[key] / (dp[key] + dm[key])
            assert (ssi >= 0).all() and (ssi <= 1).all()


def test_case_study_regression():
    P = load_problem(ROOT / "data" / "config_pakistan2022.json")
    res = evaluate(P)
    R = P.alternatives
    order = lambda s: [R[i] for i in np.argsort(res[s]["rank"]["WHD"])]
    assert order("T1") == ["Sindh", "Punjab", "KP", "Balochistan", "AJ&K", "GB", "ICT"]
    assert order("T2") == ["Sindh", "Punjab", "KP", "Balochistan", "GB", "AJ&K", "ICT"]
    assert order("T3") == ["Sindh", "Balochistan", "Punjab", "KP", "AJ&K", "GB", "ICT"]
    i = R.index("Punjab")
    assert abs(res["T1"]["ssi"]["WHD"][i] - 0.3472) < 5e-5
    assert abs(res["T1"]["d_plus"]["WED"][i] - 0.6591) < 5e-5
    assert abs(res["T3"]["ssi"]["WHD"][R.index("Balochistan")] - 0.5078) < 5e-5
    assert np.allclose(P.X.sum(axis=0), [1545, 12860, 12735, 375, 1943978, 943909, 33046329])


def test_critical_tolerance_closed_form():
    w = np.array([0.625, 0.375])
    hi, lo = np.array([0.2806, 0.4581]), np.array([0.4505, 0.0438])
    s_hi, s_lo = (hi * w).sum(), (lo * w).sum()
    assert abs(critical_tolerance(hi, lo, w) - (s_hi - s_lo) / (s_hi + s_lo)) < 1e-6


def test_benchmarks_basic():
    mu = np.array([[1.0, 1.0], [0.5, 0.2], [0.0, 0.0]]); w = np.array([0.5, 0.5])
    assert list(saw(mu, w)[1]) == [1, 2, 3]
    assert list(topsis(mu, w)[1]) == [1, 2, 3]
    assert list(vikor(mu, w)[1]) == [1, 2, 3]
    assert abs(entropy_weights(np.array([[1, 5], [1, 0], [1, 0.0]])).sum() - 1) < 1e-12
    assert abs(roc_weights_from_scores(np.array([0.5, 0.3, 0.2])).sum() - 1) < 1e-12
    assert list(rank_desc(np.array([0.2, 0.9, 0.2]))) == [2, 1, 2]
