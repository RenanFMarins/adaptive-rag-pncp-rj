from scripts.audit_billion_contracts import _classify


def test_classifies_global_far_above_initial_first() -> None:
    assert _classify(1_000, 10, 1_000, 1_000) == "GLOBAL_GT_10X_INITIAL"


def test_classifies_global_far_above_parent() -> None:
    assert _classify(1_000, 1_000, 10, 50) == "GLOBAL_GT_10X_PARENT"


def test_internal_consistency_does_not_mean_external_confirmation() -> None:
    assert _classify(1_000, 1_000, 900, 1_000) == "INTERNALLY_CONSISTENT"
