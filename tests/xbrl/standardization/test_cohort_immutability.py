"""Tests that expansion cohorts are frozen tuples, not mutable lists.

The autonomous system's safety guarantees (Sub-project A determinism gate,
Sub-project B chokepoint baseline check) depend on evaluation cohorts being
stable reference points. A test that mutates EXPANSION_COHORT_50 via
.append() or .clear() can silently corrupt every downstream run.

DETERMINISM_TEST_COHORT is already a tuple by Sub-project A convention.
This test extends that discipline to the EXPANSION_COHORT_50/100/500 chain.

See Consensus 024 Phase 1 Finding 4 for the incident that motivated this.
"""
import pytest

from edgar.xbrl.standardization.tools.auto_eval import (
    DETERMINISM_TEST_COHORT,
    EXPANSION_COHORT_50,
    EXPANSION_COHORT_100,
    EXPANSION_COHORT_500,
)

pytestmark = pytest.mark.fast


def test_determinism_test_cohort_is_frozen():
    """Precondition: DETERMINISM_TEST_COHORT was already a tuple (Sub-project A).

    If this fails, something has regressed Sub-project A's safety work and
    this test file's assumptions no longer hold.
    """
    assert isinstance(DETERMINISM_TEST_COHORT, tuple), (
        "DETERMINISM_TEST_COHORT must be a tuple (Sub-project A precedent). "
        f"Got {type(DETERMINISM_TEST_COHORT).__name__}."
    )


def test_expansion_cohort_50_is_frozen():
    """EXPANSION_COHORT_50 must be a tuple to prevent accidental mutation."""
    assert isinstance(EXPANSION_COHORT_50, tuple), (
        "EXPANSION_COHORT_50 must be a tuple, not a list, to prevent accidental "
        "mutation by tests or overnight loops. "
        f"Got {type(EXPANSION_COHORT_50).__name__}. "
        "See Consensus 024 Phase 1 Finding 4."
    )


def test_expansion_cohort_100_is_frozen():
    """EXPANSION_COHORT_100 must be a tuple (cohort chain must stay uniform)."""
    assert isinstance(EXPANSION_COHORT_100, tuple), (
        "EXPANSION_COHORT_100 must be a tuple. "
        f"Got {type(EXPANSION_COHORT_100).__name__}."
    )


def test_expansion_cohort_500_is_frozen():
    """EXPANSION_COHORT_500 must be a tuple (cohort chain must stay uniform)."""
    assert isinstance(EXPANSION_COHORT_500, tuple), (
        "EXPANSION_COHORT_500 must be a tuple. "
        f"Got {type(EXPANSION_COHORT_500).__name__}."
    )


def test_expansion_cohort_chain_contains_expected_companies():
    """Regression guard: the type change must not alter cohort membership.

    Cohort membership is load-bearing for reproducibility across runs
    (determinism CI gate, golden master comparison, baseline snapshots).
    Catch any accidental drop/add during the tuple conversion.
    """
    # EXPANSION_COHORT_50 should have exactly 50 tickers
    assert len(EXPANSION_COHORT_50) == 50, (
        f"EXPANSION_COHORT_50 must have 50 tickers; got {len(EXPANSION_COHORT_50)}"
    )

    # EXPANSION_COHORT_100 should have exactly 100
    assert len(EXPANSION_COHORT_100) == 100, (
        f"EXPANSION_COHORT_100 must have 100 tickers; got {len(EXPANSION_COHORT_100)}"
    )

    # EXPANSION_COHORT_500 should have exactly 500
    assert len(EXPANSION_COHORT_500) == 500, (
        f"EXPANSION_COHORT_500 must have 500 tickers; got {len(EXPANSION_COHORT_500)}"
    )

    # EXPANSION_COHORT_100 must start with the 50-cohort (tuple concatenation order)
    assert EXPANSION_COHORT_100[:50] == EXPANSION_COHORT_50, (
        "EXPANSION_COHORT_100 must begin with EXPANSION_COHORT_50 in order. "
        "If the tuple conversion changed concatenation semantics, this catches it."
    )

    # EXPANSION_COHORT_500 must start with the 100-cohort
    assert EXPANSION_COHORT_500[:100] == EXPANSION_COHORT_100, (
        "EXPANSION_COHORT_500 must begin with EXPANSION_COHORT_100 in order."
    )

    # Spot-check a few well-known tickers that must be present
    for ticker in ["AAPL", "JPM", "XOM", "WMT", "JNJ"]:
        assert ticker in EXPANSION_COHORT_50, f"{ticker} missing from EXPANSION_COHORT_50"
        assert ticker in EXPANSION_COHORT_100, f"{ticker} missing from EXPANSION_COHORT_100"
        assert ticker in EXPANSION_COHORT_500, f"{ticker} missing from EXPANSION_COHORT_500"
