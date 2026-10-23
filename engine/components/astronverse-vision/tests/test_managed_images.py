from types import SimpleNamespace

import pytest
from astronverse.vision import core
from PIL import Image


@pytest.mark.parametrize("managed", [False, True])
def test_managed_matching_does_not_write_desktop_debug_images(monkeypatch, tmp_path, managed):
    monkeypatch.chdir(tmp_path)
    if managed:
        monkeypatch.setenv("ASTRON_RPA_MANAGED_DESKTOP", "1")
    else:
        monkeypatch.delenv("ASTRON_RPA_MANAGED_DESKTOP", raising=False)
    screen = Image.new("RGB", (80, 60), "white")
    monkeypatch.setattr(core.pyautogui, "screenshot", lambda **_: screen)
    monkeypatch.setattr(core.CvCore, "base64_to_image", lambda _: screen)
    monkeypatch.setattr(
        core, "AnchorMatch", lambda: SimpleNamespace(process_image=lambda image, *_args, **_kw: (image, [1, 2, 3, 4]))
    )
    pick = {
        "elementData": {
            "img": {"self": "sample", "parent": ""},
            "pos": {"self_x": 0, "self_y": 0},
            "sr": {"screen_w": 80, "screen_h": 60},
        }
    }
    assert core.CvCore.match_imgs(pick) == [1, 2, 3, 4]
    assert (tmp_path / "desktop.png").exists() is not managed
    assert (tmp_path / "desktop_filepath_match.png").exists() is not managed
