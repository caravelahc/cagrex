"""Tests for course data extraction."""
import pytest

from datetime import time as Time

from cagrex.cagr import _course_from_classes, Class, ScheduleTime, Weekday


def test_course_from_classes():
    classes = [
        Class(
            subject_id="XXX0000",
            name="Test Course",
            instruction_hours=30,
            class_id="04208",
            semester="20172",
            offered_vacancies=10,
            available_vacancies=3,
            orders_without_vacancies=0,
            teachers=["Awesome Teacher"],
            schedule=[
                ScheduleTime(
                    weekday=Weekday.MONDAY,
                    time=Time(13, 30),
                    duration=2,
                    room="AUX-ALOCAR",
                ),
            ],
        ),
    ]

    course = _course_from_classes(classes)

    print(course)


# def test_course_retrieval():
#     COURSE_ID, SEMESTER = "INE5417", "20172"
#     cagr = CAGR()
#     course = cagr.course(COURSE_ID, SEMESTER)
#
#     assert course["id"] == COURSE_ID
#     assert course["nome"] == "Engenharia de Software I"
#     assert course["horas_aula"] == 90
#     assert course["ementa"].startswith("Análise de requisitos:")
#     assert all(class_ in course["turmas"] for class_ in ["04208A", "04208B"])
#
#
# def test_student_not_logged_in():
#     cagr = CAGR()
#     with pytest.raises(NotLoggedIn):
#         cagr.student("16100719")
#
#
# def test_student_logged_in():
#     cagr = CAGR()
#
#     student = cagr.student("16100719")
#
#     assert student["nome"] == "Cauê Baasch de Souza"
#     assert student["curso"] == "Ciências da Computação"
