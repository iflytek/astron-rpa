import math


def calculate_audio_points(duration_seconds: float, seconds_per_unit: int, points_per_unit: int) -> int:
    if duration_seconds <= 0:
        raise ValueError("Audio duration must be greater than zero.")
    if seconds_per_unit <= 0 or points_per_unit <= 0:
        raise ValueError("Pricing configuration must be greater than zero.")

    billable_units = math.ceil(duration_seconds / seconds_per_unit)
    return billable_units * points_per_unit


def calculate_text_points(text: str, chars_per_unit: int, points_per_unit: int) -> int:
    normalized = (text or "").strip()
    if not normalized:
        raise ValueError("Text must not be empty.")
    if chars_per_unit <= 0 or points_per_unit <= 0:
        raise ValueError("Pricing configuration must be greater than zero.")

    billable_units = math.ceil(len(normalized) / chars_per_unit)
    return billable_units * points_per_unit
