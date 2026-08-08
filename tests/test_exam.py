from scripts.ntu_check_exam_schedules import check_exam_schedules, split_date_time


def test_split_date_time():
    assert split_date_time("04-Dec-2025 0900to1100 hrs ") == ("04-Dec-2025", "0900to1100")
    assert split_date_time("04-Dec-2025 0900to1100") == ("04-Dec-2025", "0900to1100")


def test_split_date_time_no_time_does_not_crash():
    assert split_date_time("") == ("", "")
    assert split_date_time("To Be Announced") == ("To Be Announced", "")


def test_check_exam_schedules_no_crash(compare_fixtures, capsys):
    check_exam_schedules(list(compare_fixtures), "15/01/2024")
    out, _ = capsys.readouterr()
    assert "Exam Schedule" in out
