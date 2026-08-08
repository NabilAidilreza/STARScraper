from scripts.ntu_extract_timetable import (
    COURSE_CODE,
    DAY,
    REMARK,
    STATUS,
    TIME,
    create_timetable_list,
    expand_weeks,
    process_html_to_data,
)


def test_expand_weeks():
    assert expand_weeks("Teaching Wk1-13") == list(range(1, 14))
    assert expand_weeks("Teaching Wk2-13") == list(range(2, 14))
    assert expand_weeks("Teaching Wk12,13") == [12, 13]
    assert expand_weeks("Teaching Wk1-7") == list(range(1, 8))
    assert expand_weeks("Teaching Wk9") == [9]
    assert expand_weeks("Teaching Wk1-9,11-13") == list(range(1, 10)) + [11, 12, 13]


def test_process_html_to_data_structure():
    table = process_html_to_data("samples/STARS_SAMPLE.html")
    assert table, "No rows extracted"
    for row in table:
        assert len(row) >= 15, f"Row too short: {len(row)}"


def test_create_timetable_list_shape():
    data = create_timetable_list("samples/STARS_SAMPLE.html")
    # header group + 13 teaching week groups
    assert len(data) == 14
    for item in data[0]:
        # header row cells are non-empty
        assert all(item)


def test_week_groups_are_consistent():
    data = create_timetable_list("samples/STARS_SAMPLE.html")
    for week_number in range(1, 14):
        group = data[week_number]
        assert group, f"Wk{week_number} group is empty"
        for item in group:
            assert item[REMARK] == f"Teaching Wk{week_number}"
            assert item[STATUS] != ""


def test_course_rows_have_expected_fields():
    data = create_timetable_list("samples/STARS_SAMPLE.html")
    # Spot check a registered course appears with a code, day and time
    seen = set()
    for week_number in range(1, 14):
        for item in data[week_number]:
            if item[STATUS] == "Registered":
                seen.add((item[COURSE_CODE], item[DAY], item[TIME]))
    assert seen, "No registered courses found"
    for code, day, time_ in seen:
        assert code
        assert day in {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat"}
        assert len(time_) >= 9


def test_no_phantom_week_entries():
    data = create_timetable_list("samples/STARS_SAMPLE.html")
    for week_number in range(1, 14):
        for item in data[week_number]:
            wk = int(item[REMARK].replace("Teaching Wk", ""))
            assert 1 <= wk <= 13
