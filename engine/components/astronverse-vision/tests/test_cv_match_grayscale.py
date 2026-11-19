"""Exercise real template matching without starting desktop/action components."""

import importlib.util
import logging
import sys
import types
from pathlib import Path

import cv2
import numpy as np
import pytest


@pytest.fixture
def matcher(monkeypatch):
    logger_module = types.ModuleType("astronverse.actionlib.logger")
    logger_module.logger = logging.getLogger(__name__)
    monkeypatch.setitem(sys.modules, "astronverse.actionlib.logger", logger_module)
    source = Path(__file__).parents[1] / "src/astronverse/vision/cv_match.py"
    spec = importlib.util.spec_from_file_location("cv_match_under_test", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.AnchorMatch()


@pytest.mark.parametrize("grayscale", [False, True], ids=["colored", "grayscale"])
@pytest.mark.parametrize("with_anchor", [False, True], ids=["direct", "anchor"])
def test_aligned_targets_keep_their_score_and_location(matcher, monkeypatch, grayscale, with_anchor):
    # Nonconstant patches avoid TM_CCOEFF_NORMED's degenerate constant-template case.
    template = np.zeros((40, 60, 3), dtype=np.uint8)
    template[:, :20] = (220, 0, 0)
    template[:, 20:40] = (0, 200, 0)
    template[:, 40:] = (0, 0, 220)
    template[18:22] = 255
    anchor = np.rot90(template, 2).copy()
    if grayscale:
        template = cv2.cvtColor(cv2.cvtColor(template, cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2RGB)
        anchor = cv2.cvtColor(cv2.cvtColor(anchor, cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2RGB)
    screen = np.full((200, 320, 3), 240, dtype=np.uint8)
    screen[80:120, 120:180] = template
    if with_anchor:
        screen[20:60, 20:80] = anchor

    real_match = cv2.matchTemplate
    scores = []

    def record_match(image, target, method):
        result = real_match(image, target, method)
        scores.append(float(cv2.minMaxLoc(result)[1]))
        return result

    monkeypatch.setattr(cv2, "matchTemplate", record_match)
    _, box = matcher.process_image(
        screen,
        template,
        anchor=anchor if with_anchor else None,
        center_coords_aim="120,80",
        center_coords_anchor="20,20" if with_anchor else "",
        ratio="1,1",
        match_similarity=0.95,
        line_width_match=1,
    )
    assert box == (120, 80, 60, 40)
    assert scores
    assert all(score >= 0.99 for score in scores)
