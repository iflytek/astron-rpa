from datetime import datetime, timedelta, timezone

import pytest

from app.models.point import PointExpirationPolicy, calculate_expiration_date


def test_calculate_expiration_date_rejects_naive_reference_date():
    reference_date = datetime(2026, 8, 14, 12)

    with pytest.raises(ValueError, match="reference_date must be timezone-aware"):
        calculate_expiration_date(
            "manual_add",
            policy=PointExpirationPolicy.THIRTY_DAYS,
            reference_date=reference_date,
        )


def test_calculate_expiration_date_accepts_timezone_aware_reference_date():
    reference_date = datetime(2026, 8, 14, 12, tzinfo=timezone(timedelta(hours=8)))

    result = calculate_expiration_date(
        "manual_add",
        policy=PointExpirationPolicy.THIRTY_DAYS,
        reference_date=reference_date,
        target_timezone=timezone.utc,
    )

    assert result == datetime(2026, 9, 13, 4, tzinfo=timezone.utc)
