"""Tests for jobs/materialize.py contracts."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from jobs import materialize as materialize_job


def test_parse_end_date_supports_z_suffix():
    parsed = materialize_job._parse_end_date("2026-05-24T12:00:00Z")
    assert parsed == datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


def test_main_calls_materialize_incremental_with_end_date(monkeypatch):
    mock_service = MagicMock()
    mock_service.materialize_incremental.return_value = True
    mock_service_class = MagicMock(return_value=mock_service)

    monkeypatch.setattr(materialize_job, "FeastService", mock_service_class)
    monkeypatch.setattr(
        materialize_job.sys,
        "argv",
        ["materialize.py", "--end-date", "2026-05-24T12:00:00Z"],
    )

    exit_code = materialize_job.main()

    assert exit_code == 0
    call_args = mock_service.materialize_incremental.call_args
    passed_end_date = call_args.kwargs.get("end_date")
    assert passed_end_date == datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


def test_main_returns_1_on_invalid_end_date(monkeypatch):
    mock_service = MagicMock()
    mock_service_class = MagicMock(return_value=mock_service)

    monkeypatch.setattr(materialize_job, "FeastService", mock_service_class)
    monkeypatch.setattr(
        materialize_job.sys,
        "argv",
        ["materialize.py", "--end-date", "invalid-end-date"],
    )

    exit_code = materialize_job.main()

    assert exit_code == 1
    mock_service.materialize_incremental.assert_not_called()
