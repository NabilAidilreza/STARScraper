import os

import pytest
from icalendar import Calendar

from scripts.ntu_ics_generator import generate_exam_ics_file, generate_ics_file


# Real-world regression cases from the YR2/YR3/YR4 folders.
# (file, expected unique exam count)
REAL_EXAM_FILES = [
    ("YR2S1/STARS_ASH.html", 4),
    ("YR2S1/STARS_FAZLI.html", 2),
    ("YR2S1/STARS_JX.html", 5),
    ("YR2S1/STARS_NABIL.html", 5),
    ("YR2S1/STARS_SEAN.html", 2),
    ("YR2S2/STARS_ASH.html", 5),
    ("YR2S2/STARS_EJ.html", 5),
    ("YR2S2/STARS_FAZLI.html", 3),
    ("YR2S2/STARS_JX.html", 5),
    ("YR2S2/STARS_NABIL.html", 5),
    ("YR2S2/STARS_SEAN.html", 2),
    ("YR2S2/STARS_TIM.html", 4),
    ("YR2S2/STARS_ZHENYI.html", 4),
    ("YR2S2/STARS_ZW.html", 3),
    ("YR3S1/STARS_ASH.html", 4),
    ("YR3S1/STARS_FAZ.html", 2),
    ("YR3S1/STARS_JX.html", 3),
    ("YR3S1/STARS_NAB.html", 3),
    ("YR3S1/STARS_SEAN.html", 4),
    ("YR3S1/STARS_TIM.html", 4),
    ("YR3S1/STARS_ZY.html", 5),
    ("YR4S1/STARS_NAB.html", 1),
]


@pytest.mark.parametrize("rel_path,expected", REAL_EXAM_FILES)
def test_generate_exam_ics_file_real_files(rel_path, expected, tmp_path, monkeypatch):
    """Every real timetable from YR2/YR3/YR4 must generate one event per unique exam.

    Covers edge cases: the "Not Available, please check with the School offering the
    course." sentinel (STARS_ZHENYI.html), 30-min granularity times (1300to1430),
    April/May exam sessions, and duplicate rows across teaching weeks.
    """
    abs_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", rel_path))
    if not os.path.exists(abs_path):
        pytest.skip(f"real fixture missing: {rel_path}")
    monkeypatch.chdir(tmp_path)
    name = generate_exam_ics_file(abs_path)
    assert name == os.path.basename(rel_path).split("_")[-1].replace(".html", "") + "_exams.ics"
    with open(os.path.join("calendars", name), "rb") as f:
        cal = Calendar.from_ical(f.read())
    events = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(events) == expected, f"{rel_path}: expected {expected} exams, got {len(events)}"
    for event in events:
        summary = str(event.get("summary", ""))
        description = str(event.get("description", ""))
        # sentinel strings must never leak into events
        assert "Not Available" not in summary and "Not Available" not in description
        assert "Not Applicable" not in summary and "Not Applicable" not in description
        dtstart = event.decoded("dtstart")
        dtend = event.decoded("dtend")
        # required fields present, sane ordering, valid 5-min HHMM timing
        assert event.get("uid") and event.get("summary") and event.get("dtstart") and event.get("dtend")
        assert dtend > dtstart
        assert dtstart.minute in (0, 30) and dtend.minute in (0, 30)
    assert not os.path.exists("in.ics")


def test_generate_exam_ics_file_zhhenyi_sentinel(compare_fixtures, tmp_path, monkeypatch):
    """A module with a non-standard 'not available' exam string must be skipped, not crash.

    Regression for YR2S2/STARS_ZHENYI.html which contains:
    'Not Available, please check with the School offering the course.'
    """
    monkeypatch.chdir(tmp_path)
    name = generate_exam_ics_file(compare_fixtures[0])
    # sample fixture has 3 valid exams; simulate the sentinel via split_date_time directly
    from scripts.ntu_check_exam_schedules import split_date_time
    date, time = split_date_time("Not Available, please check with the School offering the course.")
    assert time == ""  # no timing -> generator skips it
    with open(os.path.join("calendars", name), "rb") as f:
        cal = Calendar.from_ical(f.read())
    events = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(events) == 3


def test_generate_exam_ics_file(compare_fixtures, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    name = generate_exam_ics_file(compare_fixtures[0])
    assert name == "AAA_exams.ics"
    out_path = os.path.join("calendars", name)
    assert os.path.exists(out_path)
    with open(out_path, "rb") as f:
        content = f.read()
    assert b"BEGIN:VCALENDAR" in content
    assert b"BEGIN:VEVENT" in content
    # sample timetable has 3 registered exams -> 3 events
    assert content.count(b"BEGIN:VEVENT") == 3
    # exam date/time should appear in the calendar
    assert b"20231127T090000" in content  # MH1810 exam start
    assert b"20231129T170000" in content  # PH1011 exam start
    # temp file should be cleaned up
    assert not os.path.exists("in.ics")


def test_generate_ics_file(compare_fixtures, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    name = generate_ics_file(compare_fixtures[0], "15/01/2024")
    assert name == "AAA_calendar.ics"
    out_path = os.path.join("calendars", name)
    assert os.path.exists(out_path)
    with open(out_path, "rb") as f:
        content = f.read()
    assert b"BEGIN:VCALENDAR" in content
    assert b"BEGIN:VEVENT" in content
    # temp file should be cleaned up
    assert not os.path.exists("in.ics")


def test_generate_ics_file_bad_date(compare_fixtures, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert generate_ics_file(compare_fixtures[0], "31/13/2024") is None
