"""Tests for the FIFO baseline — must match the verified reference values."""

import pytest

from app.core.fifo import run_baseline, fifo_permutation


def test_fifo_permutation_is_a_permutation(problem):
    perm = fifo_permutation(problem.groups)
    assert sorted(perm) == sorted(g["index"] for g in problem.groups)


def test_fifo_baseline_matches_verified_values(problem):
    """Locks in the published baseline: f1=7.2138, f2=12.6377, f3=17540."""
    _, (f1, f2, f3) = run_baseline(problem)
    assert f1 == pytest.approx(7.213761579913789, rel=1e-6)
    assert f2 == pytest.approx(12.637687366167023, rel=1e-6)
    assert f3 == pytest.approx(17540.0, rel=1e-9)


def test_fifo_is_deterministic(problem):
    _, fit_a = run_baseline(problem)
    _, fit_b = run_baseline(problem)
    assert fit_a == fit_b
