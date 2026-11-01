from __future__ import annotations

from scripts.audit_anomalous_entity_years import _expected_year


def test_expected_ata_year_prefers_control_identifier() -> None:
    assert _expected_year(
        "ata",
        "13828365000150-1-000010/2024-000001",
        "2024-06-18",
        "2024-06-18T13:26:34",
    ) == 2024


def test_expected_contract_year_uses_signature_then_publication() -> None:
    assert _expected_year(
        "contrato", "id", "2023-07-04", "2023-07-07T10:41:57"
    ) == 2023
    assert _expected_year(
        "contrato", "id", None, "2024-10-18T14:30:57"
    ) == 2024


def test_expected_year_refuses_unusable_values() -> None:
    assert _expected_year("contrato", "id", None, None) is None
