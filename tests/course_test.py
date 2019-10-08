"""Tests for subject data extraction."""
import pytest

from datetime import time as Time

# from cagrex.cagr import Class, ScheduleTime, Weekday


# def test_subject_retrieval():
#     SUBJECT_ID, SEMESTER = "INE5417", "20172"
#     cagr = CAGR()
#     subject = cagr.subject(SUBJECT_ID, SEMESTER)
#
#     assert subject["id"] == SUBJECT_ID
#     assert subject["nome"] == "Engenharia de Software I"
#     assert subject["horas_aula"] == 90
#     assert subject["ementa"].startswith("Análise de requisitos:")
#     assert all(class_ in subject["turmas"] for class_ in ["04208A", "04208B"])
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
