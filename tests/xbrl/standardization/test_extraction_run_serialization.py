"""Tests that ExtractionRun.to_dict() stays in sync with its dataclass fields.

The to_dict() method and the dataclass field set can drift over time as new
fields are added. This test is the lock that prevents that drift: any field
added to the dataclass must either appear in to_dict() output or be listed
explicitly in TRANSIENT_FIELDS (for fields that are intentionally not
persisted, like validation_tolerance which is used only in __post_init__).

See Consensus 024 for the incident that motivated this test.
"""
from dataclasses import fields

import pytest

from edgar.xbrl.standardization.ledger.schema import ExtractionRun

pytestmark = pytest.mark.fast


# Fields that are present on the dataclass but intentionally NOT persisted
# via to_dict(). Adding a field here is a deliberate decision; the test will
# fail until the field is either included in to_dict() or listed here.
TRANSIENT_FIELDS = frozenset({
    "validation_tolerance",  # Transient: used only in __post_init__, not persisted.
                             # See ExtractionRun dataclass field comment.
})


def _make_minimal_run() -> ExtractionRun:
    """Construct a fully deterministic ExtractionRun for structural tests."""
    return ExtractionRun(
        ticker="AAPL",
        metric="Revenue",
        fiscal_period="2024-FY",
        form_type="10-K",
        archetype="A",
        run_id="test-run-id-0000",
        run_timestamp="2024-01-01T00:00:00",
    )


def test_to_dict_includes_every_dataclass_field_except_transient():
    """to_dict() must serialize every dataclass field that is not in TRANSIENT_FIELDS.

    This is the anti-drift lock. If this test fails, either:
    1. A new dataclass field was added without updating to_dict() — add it there.
    2. The field is intentionally transient — add it to TRANSIENT_FIELDS with a comment.
    """
    run = _make_minimal_run()
    serialized = run.to_dict()

    dataclass_field_names = {f.name for f in fields(ExtractionRun)}
    expected_serialized = dataclass_field_names - TRANSIENT_FIELDS

    missing = expected_serialized - set(serialized.keys())
    assert not missing, (
        f"to_dict() is missing these dataclass fields: {sorted(missing)}. "
        f"Either add them to to_dict() or add them to TRANSIENT_FIELDS with a reason."
    )


def test_to_dict_has_no_unexpected_fields():
    """to_dict() must NOT return keys that are not on the dataclass.

    Catches typos and hand-written keys that don't correspond to real fields.
    """
    run = _make_minimal_run()
    serialized = run.to_dict()

    dataclass_field_names = {f.name for f in fields(ExtractionRun)}
    unexpected = set(serialized.keys()) - dataclass_field_names
    assert not unexpected, (
        f"to_dict() contains keys that are not dataclass fields: {sorted(unexpected)}. "
        f"Either remove them or add the corresponding fields to the dataclass."
    )


def test_to_dict_preserves_provenance_field_values():
    """to_dict() must preserve the actual values of provenance fields, not drop them.

    Ground-truth assertion: construct a run with specific provenance values and
    verify they round-trip through to_dict() unchanged. This catches the
    specific drift pattern we saw in Consensus 024 where 10 fields were silently
    dropped.
    """
    run = ExtractionRun(
        ticker="AAPL",
        metric="Revenue",
        fiscal_period="2024-FY",
        form_type="10-K",
        archetype="A",
        concept="us-gaap:Revenues",
        accession_number="0000320193-24-000123",
        statement_role="http://fasb.org/us-gaap/role/statement/StatementOfIncome",
        period_type="duration",
        period_start="2023-09-30",
        period_end="2024-09-28",
        unit="USD",
        decimals=-6,
        reference_source="yfinance",
        publish_confidence="high",
    )

    serialized = run.to_dict()

    assert serialized["concept"] == "us-gaap:Revenues"
    assert serialized["accession_number"] == "0000320193-24-000123"
    assert serialized["statement_role"] == "http://fasb.org/us-gaap/role/statement/StatementOfIncome"
    assert serialized["period_type"] == "duration"
    assert serialized["period_start"] == "2023-09-30"
    assert serialized["period_end"] == "2024-09-28"
    assert serialized["unit"] == "USD"
    assert serialized["decimals"] == -6
    assert serialized["reference_source"] == "yfinance"
    assert serialized["publish_confidence"] == "high"
