from datetime import timedelta

from scripts.ntu_extract_timetable import (
    NUM_TEACHING_WEEKS,
    generate_timeline,
    parse_start_date,
    teaching_week_start,
)

START = "13/01/2025"


def test_teaching_week_start_weeks_1_to_7():
    startday = parse_start_date(START)
    for wk in range(1, 8):
        assert teaching_week_start(wk, START) == startday + timedelta(weeks=wk - 1)


def test_teaching_week_start_weeks_8_to_13_skip_recess():
    startday = parse_start_date(START)
    # Recess is after teaching week 7, so week 8 starts two weeks after week 7
    assert teaching_week_start(8, START) == startday + timedelta(weeks=8)
    assert teaching_week_start(13, START) == startday + timedelta(weeks=13)


def test_recess_gap_is_exactly_one_week():
    gap = teaching_week_start(8, START) - teaching_week_start(7, START)
    assert gap == timedelta(weeks=2)


def test_teaching_week_start_known_dates():
    assert teaching_week_start(1, START).strftime("%d/%m/%Y") == "13/01/2025"
    assert teaching_week_start(7, START).strftime("%d/%m/%Y") == "24/02/2025"
    assert teaching_week_start(8, START).strftime("%d/%m/%Y") == "10/03/2025"
    assert teaching_week_start(13, START).strftime("%d/%m/%Y") == "14/04/2025"


def test_generate_timeline_shape():
    tl = generate_timeline(START)
    assert len(tl) == NUM_TEACHING_WEEKS
    assert len(tl[0]) == 6  # Monday to Saturday


def test_generate_timeline_mon_start():
    tl = generate_timeline(START)
    assert tl[0][0] == "13/01/2025"
    assert tl[6][0] == "24/02/2025"   # teaching week 7
    assert tl[7][0] == "10/03/2025"   # teaching week 8 (recess skipped)
    assert tl[12][0] == "14/04/2025"  # teaching week 13


def test_generate_timeline_second_semester():
    tl = generate_timeline("11/08/2025")
    assert tl[0][0] == "11/08/2025"
    assert tl[12][0] == "10/11/2025"
