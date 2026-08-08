import os

from scripts.ntu_compare_timetables import (
    check_file,
    compare_grp_timetables,
    validate_date,
    validate_week_number,
)


def test_validate_date_rejects_bad_month():
    assert validate_date("31/13/2025") != ""


def test_validate_date_accepts_valid():
    assert validate_date("15/01/2025") == ""


def test_validate_date_rejects_garbage():
    assert validate_date("not-a-date") != ""


def test_validate_week_number():
    assert validate_week_number(1) == ""
    assert validate_week_number(13) == ""
    assert validate_week_number(14) != ""
    assert validate_week_number(0) != ""
    assert validate_week_number("abc") != ""


def test_check_file_success():
    assert check_file("samples/STARS_SAMPLE.html") == ""


def test_check_file_missing():
    assert check_file("does_not_exist.html") == "File not found."


def test_compare_week13_does_not_crash(compare_fixtures, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = compare_grp_timetables(compare_fixtures, 13, "13/01/2025")
    assert result is not None
    assert os.path.exists(result)


def test_compare_week2_generates_file(compare_fixtures, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = compare_grp_timetables(compare_fixtures, 2, "13/01/2025")
    assert result is not None
    assert os.path.exists(result)


def test_compare_week1_generates_file(compare_fixtures, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = compare_grp_timetables(compare_fixtures, 1, "13/01/2025")
    assert result is not None
    assert os.path.exists(result)


def test_compare_invalid_week_returns_none(compare_fixtures, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert compare_grp_timetables(compare_fixtures, 14, "13/01/2025") is None
