"""Tests for subject data extraction."""
from os import environ

import pytest

from cagrex.cagr import CAGR, NotLoggedIn, StudentClass
from tests.util import load_credentials

network_needed = pytest.mark.skipif(
    environ.get("NETWORK_TESTS") != "1",
    reason="NETWORK_TESTS variable required since test requires network access.",
)

CREDENTIALS = load_credentials()

requires_auth = pytest.mark.skipif(CREDENTIALS is None, reason="Credentials file missing.")


@network_needed
def test_subject_retrieval():
    subject_id = "INE5417"
    semester = "20172"

    cagr = CAGR()
    subject = cagr.subject(subject_id, semester)

    assert subject.subject_id == subject_id
    assert subject.name == "Engenharia de Software I"
    assert subject.instruction_hours == 90
    assert subject.syllabus.startswith("Análise de requisitos:")

    expected_class_ids = ["04208A", "04208B"]
    assert all([class_.class_id in expected_class_ids for class_ in subject.classes])


@network_needed
def test_student_not_logged_in():
    cagr = CAGR()
    with pytest.raises(NotLoggedIn):
        cagr.student("16100719")
