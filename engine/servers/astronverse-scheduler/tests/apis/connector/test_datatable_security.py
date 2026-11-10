from pathlib import Path
from types import SimpleNamespace

import pytest
from astronverse.scheduler.apis.connector.datatable import get_project_dir
from astronverse.scheduler.core.datatable.excel_service import ExcelService


def test_project_id_cannot_escape_venv_directory(tmp_path):
    svc = SimpleNamespace(config=SimpleNamespace(venv_base_dir=str(tmp_path / "venvs")))
    with pytest.raises(ValueError):
        get_project_dir(svc, "../outside")


def test_excel_filename_cannot_escape_project_directory(tmp_path):
    service = ExcelService(str(tmp_path / "project"))
    with pytest.raises(ValueError):
        service.get_file_path("../outside")
    with pytest.raises(ValueError):
        service.get_file_path("nested\\outside")
    with pytest.raises(ValueError):
        service.get_file_path("data.xlsx:secret")


def test_excel_filename_stays_inside_project_directory(tmp_path):
    service = ExcelService(str(tmp_path / "project"))
    assert Path(service.get_file_path("data_table")).parent == (tmp_path / "project").resolve()
