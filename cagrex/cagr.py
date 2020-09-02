from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date as Date, time as Time
from enum import auto, IntEnum
from functools import partial
from typing import Iterable, List, Optional

from bs4 import BeautifulSoup
import bs4
import mechanicalsoup
import requests


CAGR_URL = "http://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/"


class InvalidCredentials(Exception):
    pass


class NotLoggedIn(Exception):
    pass


@dataclass
class Subject:
    subject_id: str
    name: str
    syllabus: str
    instruction_hours: int
    classes: Optional[List[str]] = None


@dataclass
class Class:
    class_id: str
    offered_vacancies: int
    available_vacancies: int
    orders_without_vacancy: int
    special_students: int
    teachers: List[str]
    schedule: List[ScheduleTime]


class Weekday(IntEnum):
    SUNDAY = auto()
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()


@dataclass
class ScheduleTime:
    weekday: Weekday
    time: Time
    duration: int
    room: str


@dataclass
class Student:
    student_id: str
    name: str


def forum_program_id(program_id: int) -> str:
    return f"100000{program_id}"


def _parse_time(time: str) -> ScheduleTime:
    time, room = time.split(" / ")
    weekday, time = time.split(".")
    time, duration = time.split("-")
    hour, minute = time[:2], time[2:]

    return ScheduleTime(
        weekday=Weekday(int(weekday)),
        time=Time(int(hour), int(minute)),
        duration=int(duration),
        room=room,
    )


def _get_program_name(page):
        return page.find_all("span", class_="texto_pequeno3")[3].get_text()


def _make_class(data: Dict[str, str]) -> Class:
    return Class(
        class_id=data["turma"],
        offered_vacancies=int(data["vagas ofertadas"]),
        available_vacancies=int(data["saldo vagas"].replace("LOTADA", "0")),
        orders_without_vacancy=int(data["pedidos sem vaga"] or "0"),
        special_students=int(data["alunos especiais"]),
        teachers=data["professor"].splitlines(),
        schedule=[_parse_time(time) for time in data["horários"].splitlines()]
    )
    cells = [c.get_text("\n", strip=True) for c in row.find_all("td")]


def _table_to_dicts(table: bs4.Tag) -> List[Dict[str, str]]:
    headers = [
        th.get_text(" ", strip=True).lower()
        for th in table.find_all("th", class_="rich-table-subheadercell")
    ]
    rows = [
        [c.get_text("\n", strip=True) for c in row.find_all("td")]
        for row in table.find_all("tr", class_="rich-table-row")
    ]
    dicts = [
        {header: value for header, value in zip(headers, row)}
        for row in rows
    ]

    return dicts


def _table_to_classlist(table: bs4.Tag) -> List[Class]:
    return [_make_class(_dict) for _dict in _table_to_dicts(table)]


def _load_name_and_syllabus(subject_id: str) -> Tuple[str, str]:
    response = requests.get(
        CAGR_URL + f"ementaDisciplina.xhtml?codigoDisciplina={subject_id}"
    )
    page_content = BeautifulSoup(response.text, "html.parser")
    name = page_content.find("span").get_text("\n", strip=True).split(" - ")[1]
    syllabus = page_content.find("td").get_text("\n", strip=True)

    return name, syllabus


def _get_semester_from_id(student_id):
    student_id = str(student_id)
    return student_id[0:2] + "." + student_id[2]


class CAGR:
    def __init__(self):
        self._browser = mechanicalsoup.StatefulBrowser()
        self._logged_in = False

    def _memberlist_html_from_forum(self, room_id):
        url = "http://forum.cagr.ufsc.br/listarMembros.jsf"
        params = {"salaId": forum_program_id(room_id)}
        self._browser.open(url, params=params)
        page = self._browser.get_current_page()

        students = page.find_all("tr", class_="cor1_celula_forum")
        students.extend(page.find_all("tr", class_="cor2_celula_forum"))
        return students

    def _is_student_suspended(self, student):
        profile_url = "http://forum.cagr.ufsc.br/mostrarPerfil.jsf"
        semester = student.find("span", class_="texto_pequeno3").get_text()
        params = {"usuarioId": semester, "usuarioTipo": "Aluno"}
        self._browser.open(profile_url, params=params)
        page = self._browser.get_current_page()

        status_text = page.find_all("span", class_="texto_pequeno1")[1]
        return "trancado" in str(status_text)

    def login(self, username, password):
        self._browser.open(
            "https://sistemas.ufsc.br/login",
            params={"service": "http://forum.cagr.ufsc.br/"},
        )

        self._browser.select_form("#fm1")
        self._browser["username"] = username
        self._browser["password"] = password

        response = self._browser.submit_selected()
        if response.ok:
            self._logged_in = True
        else:
            raise InvalidCredentials()

    def program_id(self):
        if not self._logged_in:
            raise NotLoggedIn()

        url = "https://cagr.sistemas.ufsc.br/modules/aluno/historicoEscolar/"
        self._browser.open(url)
        page = self._browser.get_current_page()

        program_id = page.find_all("td", class_="aluno_info_col2")
        return str(program_id[4].get_text()[0:3])

    def student(self, student_id):
        if not self._logged_in:
            raise NotLoggedIn()

        url = "http://forum.cagr.ufsc.br/mostrarPerfil.jsf"
        params = {"usuarioTipo": "Aluno", "usuarioId": student_id}
        self._browser.open(url, params=params)

        page = self._browser.get_current_page()

        columns = (
            page.find_all("td", class_=f"coluna{i+1}_listar_salas") for i in range(4)
        )

        rows = zip(*columns)
        subjects = [
            Subject(
                subject_id=subject_id.get_text(strip=True),
                class_id=class_id.get_text(strip=True),
                name=subject_name.get_text(strip=True),
                semester=semester.get_text(strip=True),
            )
            for subject_name, subject_id, class_id, semester in rows
        ]

        program = page.find("span", class_="texto_negrito_pequeno2")
        program = program.get_text(strip=True).split(":")[-1].strip()

        return {
            "id": student_id,
            "nome": page.find("strong").get_text(strip=True),
            "curso": program.title(),
            "disciplinas": [
                c
                for c in subjects
                if "[MONITOR]" not in c.name and c.name != "-" and c.subject_id != "-"
            ],
        }

    def subject(self, subject_id: str, semester: str):
        session = requests.Session()
        response = session.get(CAGR_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        submit_id = soup.find(value="Buscar")["id"]

        form_data = {
            "AJAXREQUEST": "_viewRoot",
            "formBusca": "formBusca",
            "javax.faces.ViewState": "j_id1",
            submit_id: submit_id,
            "formBusca:selectSemestre": semester,
            "formBusca:codigoDisciplina": subject_id,
        }

        response = session.post(CAGR_URL, data=form_data)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        name, syllabus = _load_name_and_syllabus(subject_id)

        data = _table_to_dicts(table)

        subject = Subject(
            subject_id=subject_id,
            name=name,
            syllabus=syllabus,
            instruction_hours=int(data[0]["horas aula"]),
            classes=[_make_class(_dict) for _dict in _table_to_dicts(table)],
        )

        return subject

    def subjects(self, subject_ids, semester):
        with ThreadPoolExecutor() as executor:
            func = partial(self.subject, semester=semester)
            return executor.map(func, subject_ids)

    def semesters(self):
        html = requests.get(CAGR_URL).text
        soup = BeautifulSoup(html, "html.parser")

        select = soup.find("select", id="formBusca:selectSemestre")
        return [option["value"] for option in select.find_all("option")]

    def students_per_semester(self, program_id):
        if not self._logged_in:
            raise NotLoggedIn()

        students = self._memberlist_html_from_forum(forum_program_id(program_id))
        page = self._browser.get_current_page()

        counter = Counter()
        for student in students:
            semester = student.find("span", class_="texto_pequeno3").get_text()
            semester = _get_semester_from_id(semester)
            counter[semester] += 1
        program_name = _get_program_name(page)

        return {"curso": program_name, "alunos_por_semestre": counter.most_common()}

    def students_from_subject(self, program_id):
        url = "http://forum.cagr.ufsc.br/listarMembros.jsf"
        params = {"salaId": forum_program_id(program_id)}
        self._browser.open(url, params=params)
        page = self._browser.get_current_page()

        students = page.find_all("tr", class_="cor1_celula_forum")
        students.extend(page.find_all("tr", class_="cor2_celula_forum"))

        return [
            {
                "id": int(
                    student.find("td", class_="coluna2_listar_membros").get_text()
                ),
                "nome": student.find("td", class_="coluna4_listar_membros").get_text(),
            }
            for student in students
        ]

    def students_from_class(
        self,
        subject_id: str,
        class_id: str,
        semester: str,
    ) -> List[Student]:
        url = "http://forum.cagr.ufsc.br/formularioBusca.jsf"
        self._browser.open(url)
        form = self._browser.select_form("form#buscaSala")

        params = {
            "buscaSala:salaCodigo": subject_id,
            "buscaSala:salaTurma": class_id,
            "buscaSala:salaSemestre": semester,
            "buscaSala:j_id_jsp_632900747_29": "disciplinas",
        }

        for param, value in params.items():
            self._browser[param] = value

        soup = BeautifulSoup(self._browser.submit_selected().text, "html.parser")
        td = soup.find("td", attrs={"class": "coluna1_listar_salas"})
        _, room_id = td.find("a")["href"].split("salaId=")

        memberlist_html = self._memberlist_html_from_forum(room_id)
        students = []
        for row in memberlist_html:
            student_type = row.find("td", class_="coluna3_listar_membros").get_text()
            if student_type != "Aluno":
                continue

            student_id = row.find("td", class_="coluna2_listar_membros").get_text()
            student_name = row.find("td", class_="coluna4_listar_membros").get_text()
            students.append(Student(student_id, student_name))

        return students

    def total_students(self, program_id):
        if not self._logged_in:
            raise NotLoggedIn()

        students = self._memberlist_html_from_forum(program_id)
        page = self._browser.get_current_page()
        program_name = _get_program_name(page)

        return {"curso": program_name, "estudantes": len(students)}

    def suspended_students(self, program_id):
        if not self._logged_in:
            raise NotLoggedIn()

        students = self._memberlist_html_from_forum(program_id)
        total_students = len(students)
        page = self._browser.get_current_page()
        program_name = _get_program_name(page)

        pool = ThreadPoolExecutor()
        futures = []
        for student in students:
            futures.append(pool.submit(self._is_student_suspended, student))

        suspended = 0
        students_processed = 0
        for f in as_completed(futures):
            if f.result():
                suspended += 1
            students_processed += 1
            print(f"Progress: {students_processed}/{total_students} students ({suspended} suspended)", end="\r")

        return {
            "curso": program_name,
            "estudantes": total_students,
            "alunos_trancados": suspended,
            "porcentagem": (suspended / len(students)) * 100.0,
        }
