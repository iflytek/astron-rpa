import csv

import openpyxl
import pytest
from astronverse.datatable.openpyxl import OpenpyxlWrapper


def test_csv_export_contains_csv_bytes_and_preserves_values(tmp_path):
    table = OpenpyxlWrapper(str(tmp_path / "source.xlsx"))
    values = [["中文", 'comma,quote"', "line\nbreak"], [0, False, None]]
    for row in values:
        table.sheet.append(row)
    target = tmp_path / "result.csv"
    table.export_to_file(str(target))
    assert not target.read_bytes().startswith(b"PK")
    with target.open(encoding="utf-8-sig", newline="") as stream:
        assert list(csv.reader(stream)) == [values[0], ["0", "False", ""]]
    table.close()


def test_xlsx_export_remains_readable_and_xls_is_not_mislabeled(tmp_path):
    table = OpenpyxlWrapper(str(tmp_path / "source.xlsx"))
    table.sheet.append([0, False, "中文"])
    target = tmp_path / "result.xlsx"
    table.export_to_file(str(target))
    book = openpyxl.load_workbook(target)
    assert list(book.active.values) == [(0, False, "中文")]
    book.close()
    with pytest.raises(ValueError, match=".xls"):
        table.export_to_file(str(tmp_path / "result.xls"))
    assert not (tmp_path / "result.xls").exists()
    table.close()
