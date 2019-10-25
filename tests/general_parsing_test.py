from datetime import time as Time

import bs4

from cagrex.cagr import _table_to_classlist, _parse_time, Class, ScheduleTime, Weekday


def test_time_from_str():
    """Tests if a class's schedules are correctly extracted from default CAGR
    time strings."""
    expected_times = {
        "3.1330-3 / CTC-CTC108": ScheduleTime(
            weekday=Weekday.TUESDAY,
            time=Time(13, 30),
            duration=3,
            room="CTC-CTC108",
        ),
        "4.0820-2 / CTC-CTC107": ScheduleTime(
            weekday=Weekday.WEDNESDAY,
            time=Time(8, 20),
            duration=2,
            room="CTC-CTC107",
        ),
    }

    assert all(_parse_time(text) == expected for text, expected in expected_times.items())


def test_class_from_table():
    """Tests if classes are correctly extracted from <table> tags."""
    with open('tests/assets/class_table.html') as f:
        table_html = f.read()

    table = bs4.BeautifulSoup(table_html, "html.parser")

    expected_classes = [
        Class(
            class_id="04208A",
            offered_vacancies=24,
            available_vacancies=3,
            orders_without_vacancy=0,
            special_students=0,
            teachers=["Ricardo Pereira e Silva"],
            schedule=[
                ScheduleTime(
                    weekday=Weekday.TUESDAY,
                    time=Time(13, 30),
                    duration=3,
                    room="CTC-CTC108",
                ),
                ScheduleTime(
                    weekday=Weekday.WEDNESDAY,
                    time=Time(8, 20),
                    duration=2,
                    room="CTC-CTC107",
                ),
            ],
        ),
        Class(
            class_id="04208B",
            offered_vacancies=22,
            available_vacancies=0,
            orders_without_vacancy=0,
            special_students=0,
            teachers=["Patricia Vilain"],
            schedule=[
                ScheduleTime(
                    weekday=Weekday.TUESDAY,
                    time=Time(13, 30),
                    duration=3,
                    room="AUX-ALOCAR",
                ),
                ScheduleTime(
                    weekday=Weekday.WEDNESDAY,
                    time=Time(8, 20),
                    duration=2,
                    room="AUX-ALOCAR",
                ),
            ],
        ),
    ]

    assert _table_to_classlist(table) == expected_classes
