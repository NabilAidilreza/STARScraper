"""Tests for the weekly-format extractor (zWORKINPROGRESS, not yet integrated).

Covers the pure parsing helpers against hand-written entries and full-file
integration tests against the two real weekly HTML samples.
"""

import os

import pytest

from scripts.ntu_weekly_format_extract import (
    REMARK,
    STANDARD_DAYS,
    create_weekly_timetable_list,
    expand_weeks,
    parse_entry,
    parse_weekly_file,
    to_standard_rows,
)

WEEKLY_NAB = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "zWORKINPROGRESS", "WEEKLY_NAB.html"))
TEST_HTML = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "zWORKINPROGRESS", "test.html"))


# --------------------------------------------------------------------------
# expand_weeks
# --------------------------------------------------------------------------

def test_expand_weeks_full_range():
    assert expand_weeks("1-13") == list(range(1, 14))


def test_expand_weeks_list_and_ranges():
    assert expand_weeks("1,2,4-13") == [1, 2] + list(range(4, 14))


def test_expand_weeks_single_values():
    assert expand_weeks("6,12") == [6, 12]


def test_expand_weeks_missing_means_all():
    assert expand_weeks("") == list(range(1, 14))
    assert expand_weeks(None) == list(range(1, 14))


def test_expand_weeks_deduplicates_and_sorts():
    assert expand_weeks("13,1,5-7,6") == [1, 5, 6, 7, 13]


def test_expand_weeks_invalid_tokens_are_ignored():
    assert expand_weeks("1,abc,3") == [1, 3]


# --------------------------------------------------------------------------
# parse_entry
# --------------------------------------------------------------------------

def test_parse_entry_full_with_weeks():
    e = parse_entry("IE2107 LEC/STU EELE LKC-LT 0930to1050- Wk1,2,4-13", "MON", "0930 to 1000")
    assert e["course"] == "IE2107"
    assert e["class_type"] == "LEC/STU"
    assert e["venue"] == "EELE LKC-LT"
    assert e["time"] == "0930to1050"
    assert e["weeks_spec"] == "1,2,4-13"
    assert e["weeks"] == [1, 2] + list(range(4, 14))
    assert e["day"] == "MON"
    assert e["slot"] == "0930 to 1000"
    assert e["slot_start"] == "0930"
    assert e["slot_end"] == "1000"


def test_parse_entry_no_week_suffix_means_all_weeks():
    e = parse_entry("IE2110 TUT EE05 TR+69 0930to1050", "TUE", "0930 to 1000")
    assert e["weeks_spec"] == "1-13"
    assert e["weeks"] == list(range(1, 14))


def test_parse_entry_single_week():
    e = parse_entry("IE2107 LEC/STU EELE ONLINE 0930to1050- Wk3", "MON", "0930 to 1000")
    assert e["weeks_spec"] == "3"
    assert e["weeks"] == [3]


def test_parse_entry_venue_with_spaces():
    e = parse_entry("CC0007 TUT T053 COLLAB 1 1230to1420", "WED", "1230 to 1300")
    assert e["venue"] == "T053 COLLAB 1"
    assert e["time"] == "1230to1420"


def test_parse_entry_venue_with_underscore_and_dash():
    e = parse_entry("IE4727 LEC/STU F32 S2-B3A_06 1330to1520- Wk1-11", "MON", "1330 to 1400")
    assert e["venue"] == "F32 S2-B3A_06"
    assert e["weeks"] == list(range(1, 12))


@pytest.mark.parametrize("entry", ["", "   ", "garbage", "ONLYTWO TOKENS", "MH1000 LEC 0930to1030 Wk999"])
def test_parse_entry_invalid_returns_none(entry):
    assert parse_entry(entry, "MON", "0930 to 1000") is None


def test_parse_entry_handles_nbsp():
    e = parse_entry("\xa0IE2107 TUT EE10 TR+91 0930to1050- Wk1,2,4-13", "THU", "0930 to 1000")
    assert e["course"] == "IE2107"


# --------------------------------------------------------------------------
# Integration against real files
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def weekly_nab():
    if not os.path.exists(WEEKLY_NAB):
        pytest.skip("missing real fixture: WEEKLY_NAB.html")
    return parse_weekly_file(WEEKLY_NAB)


@pytest.fixture(scope="module")
def test_html():
    if not os.path.exists(TEST_HTML):
        pytest.skip("missing real fixture: test.html")
    return parse_weekly_file(TEST_HTML)


def test_weekly_nab_semester(weekly_nab):
    assert weekly_nab["semester"] == "Academic Year 2026,Semester 1"


def test_weekly_nab_courses(weekly_nab):
    assert set(weekly_nab["courses"]) == {"IE4758", "IE4727", "LG5002"}
    assert weekly_nab["courses"]["IE4758"]["exam"] == "26-Nov-2026 0900to1100 hrs"
    assert weekly_nab["courses"]["IE4727"]["exam"] == "Not Applicable"


def test_weekly_nab_entries(weekly_nab):
    # 4 unique entries; the IE4727 Wk12,13 duplicate from the rowspan grid is deduped
    assert len(weekly_nab["entries"]) == 4
    keys = {(e["day"], e["course"], e["time"]) for e in weekly_nab["entries"]}
    assert keys == {
        ("Mon", "IE4727", "1330to1520"),
        ("Mon", "IE4727", "1330to1620"),
        ("Mon", "LG5002", "1630to1950"),
        ("Tue", "IE4758", "1330to1620"),
    }


def test_weekly_nab_no_duplicate_weeks12_13(weekly_nab):
    # the same IE4727 Wk12,13 class is rendered twice in the raw grid
    dupes = [e for e in weekly_nab["entries"] if e["course"] == "IE4727" and e["weeks_spec"] == "12,13"]
    assert len(dupes) == 1


def test_test_html_semester_and_courses(test_html):
    assert test_html["semester"] == "Academic Year 2024,Semester 2"
    assert len(test_html["courses"]) == 9
    assert set(test_html["courses"]) == {"EE2102", "EE2005", "IE2107", "IE2110", "IE2108", "CC0007", "E2005L", "E2110L", "EE2073"}


def test_test_html_entries(test_html):
    assert len(test_html["entries"]) == 19
    # every entry must map to a course in the list table
    for e in test_html["entries"]:
        assert e["course"] in test_html["courses"]
    # all entries use a standard title-case day
    for e in test_html["entries"]:
        assert e["day"] in STANDARD_DAYS


def test_test_html_known_entries(test_html):
    by_key = {(e["day"], e["course"], e["class_type"], e["time"]): e for e in test_html["entries"]}
    # venue with spaces (cell is in the THU column once rowspans are resolved)
    cc = by_key[("Thu", "CC0007", "TUT", "1230to1420")]
    assert cc["venue"] == "T053 COLLAB 1"
    assert cc["weeks"] == list(range(1, 14))
    # week-split class: MON IE2107 LEC/STU appears for both Wk1,2,4-13 and Wk3
    lec_entries = [e for e in test_html["entries"] if e["day"] == "Mon" and e["course"] == "IE2107" and e["class_type"] == "LEC/STU"]
    assert sorted(e["weeks_spec"] for e in lec_entries) == ["1,2,4-13", "3"]


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_weekly_file("no_such_file.html")


# --------------------------------------------------------------------------
# Standard-row bridge
# --------------------------------------------------------------------------

def test_to_standard_rows_bridge(weekly_nab):
    rows = to_standard_rows(weekly_nab)
    assert len(rows) == 4
    for row in rows:
        assert len(row) == 16
    by_course = {row[0]: row for row in rows}
    # IE4758 merges grid info with course-list info (title, index, exam)
    ie4758 = by_course["IE4758"]
    assert ie4758[1] == "Information Security"      # COURSE_TITLE
    assert ie4758[6] == "32558"                      # INDEX_NUMBER
    assert ie4758[7] == "Registered"                 # STATUS
    assert ie4758[9] == "LEC/STU"                    # CLASS_TYPE
    assert ie4758[11] == "Tue"                       # DAY
    assert ie4758[12] == "1330to1620"                # TIME
    assert ie4758[13] == "EELE LT23"                 # VENUE
    assert ie4758[14] == "Teaching Wk1-13"           # REMARK
    assert ie4758[15] == "26-Nov-2026 0900to1100 hrs"  # EXAM


def test_to_standard_rows_remark_carries_week_spec(test_html):
    rows = to_standard_rows(test_html)
    remarks = {row[14] for row in rows}
    assert "Teaching Wk1-13" in remarks
    assert "Teaching Wk1,2,4-13" in remarks
    assert "Teaching Wk3" in remarks


# --------------------------------------------------------------------------
# create_weekly_timetable_list (standard-shaped output)
# --------------------------------------------------------------------------

def test_create_weekly_timetable_list_shape(weekly_nab):
    data = create_weekly_timetable_list(WEEKLY_NAB)
    # header group + one group per teaching week (1-13)
    assert len(data) == 14
    assert len(data[0]) == 16
    for week in range(1, 14):
        for row in data[week]:
            assert len(row) == 16
            assert row[REMARK] == f"Teaching Wk{week}"
            assert row[11] in STANDARD_DAYS


def test_create_weekly_timetable_list_expansion(weekly_nab):
    data = create_weekly_timetable_list(WEEKLY_NAB)
    # IE4727 runs Wk1-11 with one end time and Wk12-13 with another
    wk1 = [(r[0], r[12], r[14]) for r in data[1]]
    assert ("IE4727", "1330to1520", "Teaching Wk1") in wk1
    assert ("IE4758", "1330to1620", "Teaching Wk1") in wk1
    wk12 = [(r[0], r[12]) for r in data[12]]
    assert ("IE4727", "1330to1620") in wk12  # week-split class now has the other time
    assert ("LG5002", "1630to1950") in wk12
    # all 13 groups exist even for weeks with no classes (week index 1:1 mapping)
    assert len(data[13]) >= 1


def test_create_weekly_timetable_list_empty_week_group_present(weekly_nab):
    data = create_weekly_timetable_list(WEEKLY_NAB)
    # LG5002 starts Wk2; a week with no LG5002 but others is still a real group
    assert isinstance(data[1], list)
    assert isinstance(data[13], list)
