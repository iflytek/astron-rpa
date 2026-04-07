import math

import pytest

from app.services.speech_pricing import (
    calculate_audio_points,
    calculate_text_points,
)


def test_calculate_audio_points_rounds_up():
    assert calculate_audio_points(61, seconds_per_unit=30, points_per_unit=7) == 21


def test_calculate_audio_points_has_minimum_unit():
    assert calculate_audio_points(1, seconds_per_unit=60, points_per_unit=9) == 9


def test_calculate_audio_points_rejects_invalid_duration():
    with pytest.raises(ValueError):
        calculate_audio_points(0, seconds_per_unit=60, points_per_unit=9)


def test_calculate_text_points_rounds_up():
    assert calculate_text_points("abcdefghijk", chars_per_unit=5, points_per_unit=4) == 12


def test_calculate_text_points_ignores_blank_text():
    with pytest.raises(ValueError):
        calculate_text_points("   ", chars_per_unit=50, points_per_unit=3)
