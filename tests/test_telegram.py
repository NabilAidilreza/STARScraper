from scripts.ntu_telegrambot_functions import (
    compile_mods,
    create_timetable_list,
    get_today,
    get_weekly,
)


def _build_mods(fixture_path):
    data = create_timetable_list(fixture_path)
    return compile_mods(data, "15/01/2024")


def test_compile_mods_structure(compare_fixtures):
    mods = _build_mods(compare_fixtures[0])
    assert mods
    for code, info in mods.items():
        assert code
        assert "Course_Info" in info
        assert "Timeline" in info


def test_compile_mods_dates_use_slashes(compare_fixtures):
    mods = _build_mods(compare_fixtures[0])
    sample_date = None
    for info in mods.values():
        for days in info["Timeline"].values():
            for slots in days.values():
                for value in slots.values():
                    sample_date = value[2]
                    break
            if sample_date:
                break
        if sample_date:
            break
    assert sample_date is not None
    assert "/" in sample_date  # matches the bot's %d/%m/%Y query format


def test_get_today_includes_all_slots_same_day():
    ldict = {
        "MH1000": {
            "Timeline": {
                "Wk3": {
                    "Mon": {
                        "0830to0920": ["LEC", "LT20", "15/01/2024"],
                        "0930to1020": ["TUT", "TR+24", "15/01/2024"],
                    }
                }
            }
        }
    }
    result = get_today(ldict, "15/01/2024")
    assert result.count("MH1000") == 2


def test_get_today_no_classes():
    assert get_today({}, "15/01/2024") == "No classes today on 15/01/2024"


def test_get_weekly_includes_multiple_friday_items():
    ldict = {
        "MH1000": {
            "Timeline": {
                "Wk3": {
                    "Fri": {
                        "0830to0920": ["LEC", "LT20", "01/02/2024"],
                        "0930to1020": ["TUT", "TR+24", "01/02/2024"],
                    }
                }
            }
        }
    }
    result = get_weekly(ldict, 3)
    assert result.count("MH1000") == 2
    assert "Fri" in result


def test_get_weekly_empty_week_returns_message():
    ldict = {"MH1000": {"Timeline": {}}}
    assert "No classes in Wk3" in get_weekly(ldict, 3)


def test_get_weekly_zero_week_returns_error():
    assert "Error" in get_weekly({}, 0)


def test_get_weekly_real_data_does_not_crash(compare_fixtures):
    mods = _build_mods(compare_fixtures[0])
    result = get_weekly(mods, 2)
    assert isinstance(result, str)
    assert result.startswith("Wk2")
