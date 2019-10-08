from datetime import time as Time

import bs4
import pytest

from cagrex.cagr import _parse_class, _parse_time, Class, ScheduleTime, Weekday


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


def test_class_from_row_html():
    """Tests if classes are correctly extracted from <tr> tags."""
    with open('tests/assets/class_row.html') as f:
        row_html = f.read()

    row = bs4.BeautifulSoup(row_html, "html.parser")

    expected_class = Class(
        subject_id="INE5417",
        name="Engenharia de Software I",
        instruction_hours=90,
        class_id="04208A",
        semester="20172",
        offered_vacancies=24,
        available_vacancies=3,
        orders_without_vacancies=0,
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
    )

    assert _parse_class(row) == expected_class
