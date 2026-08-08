"""Integration tests: both timetable formats (standard planner + weekly grid)
must be auto-detected and work through every existing main function."""

import os
import shutil

import pytest
from icalendar import Calendar

from scripts.ntu_check_exam_schedules import check_exam_schedules
from scripts.ntu_compare_timetables import compare_grp_timetables
from scripts.ntu_extract_timetable import create_timetable_list
from scripts.ntu_ics_generator import generate_exam_ics_file, generate_ics_file
from scripts.ntu_telegrambot_functions import compile_mods

WEEKLY_NAB = os.path.abspath("zWORKINPROGRESS/WEEKLY_NAB.html")
TEST_HTML = os.path.abspath("zWORKINPROGRESS/test.html")
SAMPLE = os.path.abspath("samples/STARS_SAMPLE.html")
START_DATE = "15/01/2024"


@pytest.fixture(scope="module")
def weekly_files_present():
    if not (os.path.exists(WEEKLY_NAB) and os.path.exists(TEST_HTML)):
        pytest.skip("weekly fixtures missing")


def _event_count(ics_path):
    with open(ics_path, "rb") as f:
        cal = Calendar.from_ical(f.read())
    return len([c for c in cal.walk() if c.name == "VEVENT"])


# --------------------------------------------------------------------------
# Auto-detection
# --------------------------------------------------------------------------

def test_create_timetable_list_detects_standard(weekly_files_present):
    data = create_timetable_list(SAMPLE)
    assert len(data) == 14  # header + 13 teaching weeks
    assert data[1][0][14] == "Teaching Wk1"
    assert data[1][0][11] == "Mon"


def test_create_timetable_list_detects_weekly_nab(weekly_files_present):
    data = create_timetable_list(WEEKLY_NAB)
    assert len(data) == 14
    codes = {row[0] for week in data[1:] for row in week}
    assert codes == {"IE4727", "IE4758", "LG5002"}


def test_create_timetable_list_detects_weekly_test(weekly_files_present):
    data = create_timetable_list(TEST_HTML)
    assert len(data) == 14
    codes = {row[0] for week in data[1:] for row in week}
    assert len(codes) == 9


# --------------------------------------------------------------------------
# generate_ics_file (class timetable) - both formats
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path,expected_events", [
    (SAMPLE, 159),                # standard planner sample
    (WEEKLY_NAB, 38),             # weekly grid, AY2026S1
    ("STARS_TEST.html", 136),    # weekly grid, AY2024S2 (renamed: no underscore otherwise)
])
def test_generate_ics_file_both_formats(path, expected_events, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    if path == "STARS_TEST.html":
        # ics generator validates the file name convention STARS_<name>.html
        shutil.copy(TEST_HTML, os.path.join(tmp_path, path))
        path = os.path.abspath(path)
    name = generate_ics_file(path, START_DATE)
    assert name is not None
    assert _event_count(os.path.join("calendars", name)) == expected_events


def test_ics_events_carry_exam_and_venue_info(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    name = generate_ics_file(WEEKLY_NAB, START_DATE)
    with open(os.path.join("calendars", name), "rb") as f:
        cal = Calendar.from_ical(f.read())
    events = [c for c in cal.walk() if c.name == "VEVENT"]
    # venue from the weekly grid cell
    assert any(e.get("location") == "F32 S2-B3A_06" for e in events)
    # exam from the weekly course-list table is embedded in the description
    descs = "".join(str(e.get("description", "")) for e in events)
    assert "26-Nov-2026 0900to1100 hrs" in descs


# --------------------------------------------------------------------------
# generate_exam_ics_file - both formats
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path,expected_exams", [
    (SAMPLE, 3),                  # standard planner sample
    (WEEKLY_NAB, 1),              # only IE4758 has a real exam slot
    ("STARS_TEST.html", 5),      # 5 courses have exam slots
])
def test_generate_exam_ics_file_both_formats(path, expected_exams, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    if path == "STARS_TEST.html":
        shutil.copy(TEST_HTML, os.path.join(tmp_path, path))
        path = os.path.abspath(path)
    name = generate_exam_ics_file(path)
    assert name is not None
    assert _event_count(os.path.join("calendars", name)) == expected_exams


def test_exam_ics_uses_weekly_exam_dates(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    name = generate_exam_ics_file(WEEKLY_NAB)
    with open(os.path.join("calendars", name), "rb") as f:
        cal = Calendar.from_ical(f.read())
    events = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(events) == 1
    event = events[0]
    assert "IE4758" in str(event.get("summary"))
    assert event.decoded("dtstart").strftime("%d-%b-%Y %H:%M") == "26-Nov-2026 09:00"
    assert event.decoded("dtend").strftime("%d-%b-%Y %H:%M") == "26-Nov-2026 11:00"


# --------------------------------------------------------------------------
# check_exam_schedules - both formats
# --------------------------------------------------------------------------

def test_check_exam_schedules_weekly(weekly_files_present, capsys):
    check_exam_schedules([WEEKLY_NAB, TEST_HTML], START_DATE)
    out, _ = capsys.readouterr()
    assert "Exam Schedule" in out
    assert "26-Nov-2026" in out       # WEEKLY_NAB exam
    assert "02-May-2025" in out       # test.html exam


def test_check_exam_schedules_standard(weekly_files_present, capsys):
    check_exam_schedules([SAMPLE], START_DATE)
    out, _ = capsys.readouterr()
    assert "Exam Schedule" in out
    assert "MH1810" in out
    assert "27-Nov-2023" in out


# --------------------------------------------------------------------------
# compare_grp_timetables - mixed formats in one run
# --------------------------------------------------------------------------

def test_compare_mixed_formats(weekly_files_present, tmp_path, monkeypatch):
    # one standard file + two weekly files compared together
    monkeypatch.chdir(tmp_path)
    file_name = compare_grp_timetables([SAMPLE, WEEKLY_NAB, TEST_HTML], 2, START_DATE)
    assert file_name is not None
    assert os.path.exists(os.path.join(tmp_path, file_name))


def test_compare_weekly_only(weekly_files_present, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    file_name = compare_grp_timetables([WEEKLY_NAB, TEST_HTML], 2, START_DATE)
    assert file_name is not None
    assert os.path.exists(os.path.join(tmp_path, file_name))


def test_compare_standard_only(weekly_files_present, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    std_copies = []
    for name in ("STARS_AAA.html", "STARS_BBB.html", "STARS_CCC.html"):
        dest = os.path.join(tmp_path, name)
        shutil.copy(SAMPLE, dest)
        std_copies.append(dest)
    file_name = compare_grp_timetables(std_copies, 2, START_DATE)
    assert file_name is not None
    assert os.path.exists(os.path.join(tmp_path, file_name))


# --------------------------------------------------------------------------
# Bot pipeline (compile_mods) - both formats
# --------------------------------------------------------------------------

def test_compile_mods_weekly_nab(weekly_files_present):
    data = create_timetable_list(WEEKLY_NAB)
    mods = compile_mods(data, START_DATE)
    assert set(mods) == {"IE4727", "IE4758", "LG5002"}
    # exam + title carried over from the weekly course-list table
    assert mods["IE4758"]["Course_Info"]["Finals"] == "26-Nov-2026 0900to1100 hrs"
    assert mods["IE4758"]["Course_Info"]["Name"] == "Information Security"
    # timeline dates use the %d/%m/%Y format the bot queries with
    sample_date = None
    for days in mods["IE4727"]["Timeline"].values():
        for slots in days.values():
            for value in slots.values():
                sample_date = value[2]
                break
            if sample_date:
                break
        if sample_date:
            break
    assert "/" in sample_date


def test_compile_mods_standard(weekly_files_present):
    data = create_timetable_list(SAMPLE)
    mods = compile_mods(data, START_DATE)
    assert mods  # non-empty, standard path unchanged
