"""Tests for subject data extraction."""
from datetime import time as Time
from os import environ

import pytest

from cagrex.cagr import CAGR, Class, ScheduleTime, NotLoggedIn, Weekday


network_needed = pytest.mark.skipif(
    environ.get("NETWORK_TESTS") != "1",
    reason="NETWORK_TESTS variable required since test requires network access."
)

requires_auth = pytest.mark.skip(
    reason="No authentication method implemented for tests yet."
)


@network_needed
def test_subject_retrieval():
    SUBJECT_ID, SEMESTER = "INE5417", "20172"
    cagr = CAGR()
    subject = cagr.subject(SUBJECT_ID, SEMESTER)

    assert subject.subject_id == SUBJECT_ID
    assert subject.name == "Engenharia de Software I"
    assert subject.instruction_hours == 90
    assert subject.syllabus.startswith("Análise de requisitos:")

    expected_class_ids = ["04208A", "04208B"]
    assert all([
        class_.class_id in expected_class_ids
        for class_ in subject.classes
    ])


@network_needed
def test_student_not_logged_in():
    cagr = CAGR()
    with pytest.raises(NotLoggedIn):
        cagr.student("16100719")


@network_needed
@requires_auth
def test_student_logged_in():
    cagr = CAGR()

    student = cagr.student("16100719")

    assert student["nome"] == "Cauê Baasch de Souza"
    assert student["curso"] == "Ciências da Computação"
