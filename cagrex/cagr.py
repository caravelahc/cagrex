import mechanicalsoup
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from collections import Counter
from bs4 import BeautifulSoup


CAGR_URL = "http://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/"


class InvalidCredentials(Exception):
    pass


class NotLoggedIn(Exception):
    pass


def _parse_time(time):
    time, room = time.split(" / ")
    weekday, time = time.split(".")
    time, duration = time.split("-")

    return {
        "dia_da_semana": int(weekday) - 1,
        "horario": time,
        "duracao": int(duration),
        "sala": room,
    }


def _parse_class(row):
    cells = [c.get_text("\n", strip=True) for c in row.find_all("td")]
    return {
        "id_disciplina": cells[3],
        "nome": cells[5],
        "horas_aula": int(cells[6]),
        "id_turma": cells[4],
        "vagas_ofertadas": int(cells[7]),
        "vagas_disponiveis": int(cells[10].replace("LOTADA", "0")),
        "pedidos_sem_vaga": int(cells[11] or "0"),
        "professores": cells[-1].splitlines(),
        "horarios": [_parse_time(time) for time in cells[-2].splitlines()],
    }


def _course_from_classes(classes):
    classes = list(classes)
    first = classes[0]
    course_id = first["id_disciplina"].upper()

    response = requests.get(
        CAGR_URL + f"ementaDisciplina.xhtml?codigoDisciplina={course_id}"
    )
    syllabus = BeautifulSoup(response.text, "html.parser").find("td")
    syllabus = syllabus.get_text("\n", strip=True)

    course = {
        "id": course_id,
        "nome": first["nome"],
        "ementa": syllabus,
        "horas_aula": first["horas_aula"],
        "turmas": {},
    }

    for c in classes:
        del c["nome"]
        del c["id_disciplina"]
        del c["horas_aula"]
        class_id = c.pop("id_turma")
        course["turmas"][class_id] = c

    return course


def _get_semester_from_id(student_id):
    student_id = str(student_id)
    return student_id[0:2] + "." + student_id[2]


class CAGR:
    def __init__(self):
        self._browser = mechanicalsoup.StatefulBrowser()
        self._logged_in = False

    def _students_from_forum(self, program_id):
        url = "http://forum.cagr.ufsc.br/listarMembros.jsf"
        params = {"salaId": "100000" + program_id}
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
        courses = [
            {
                "nome": course_name.get_text(strip=True),
                "id": course_id.get_text(strip=True),
                "turma": class_id.get_text(strip=True),
                "semestre": semester.get_text(strip=True),
            }
            for course_name, course_id, class_id, semester in rows
        ]

        program = page.find("span", class_="texto_negrito_pequeno2")
        program = program.get_text(strip=True).split(":")[-1].strip()

        return {
            "id": student_id,
            "nome": page.find("strong").get_text(strip=True),
            "curso": program.title(),
            "disciplinas": [
                c
                for c in courses
                if "[MONITOR]" not in c["nome"] and c["nome"] != "-" and c["id"] != "-"
            ],
        }

    def course(self, course_id, semester):
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
            "formBusca:codigoDisciplina": course_id,
        }

        response = session.post(CAGR_URL, data=form_data)
        soup = BeautifulSoup(response.text, "html.parser")

        course = _course_from_classes(
            _parse_class(row) for row in soup.find_all("tr", class_="rich-table-row")
        )

        course.update(semestre=int(semester))
        return course

    def courses(self, course_ids, semester):
        with ThreadPoolExecutor() as executor:
            func = partial(self.course, semester=semester)
            return executor.map(func, course_ids)

    def semesters(self):
        html = requests.get(CAGR_URL).text
        soup = BeautifulSoup(html, "html.parser")

        select = soup.find("select", id="formBusca:selectSemestre")
        return [option["value"] for option in select.find_all("option")]

    def students_per_semester(self, program_id):
        if not self._logged_in:
            raise NotLoggedIn()

        students = self._students_from_forum(program_id)
        page = self._browser.get_current_page()

        counter = Counter()
        for student in students:
            semester = student.find("span", class_="texto_pequeno3").get_text()
            semester = _get_semester_from_id(semester)
            counter[semester] += 1

        program_name = page.find("td", class_="coluna5_listar_membros").get_text()

        return {"curso": program_name, "alunos_por_semestre": counter.most_common()}

    def students_from_course(self, program_id):
        url = "http://forum.cagr.ufsc.br/listarMembros.jsf"
        params = {"salaId": "100000" + program_id}
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

    def total_students(self, program_id):
        if not self._logged_in:
            raise NotLoggedIn()

        students = self._students_from_forum(program_id)
        page = self._browser.get_current_page()

        program_name = page.find("td", class_="coluna5_listar_membros").get_text()

        return {"curso": program_name, "estudantes": len(students)}

    def suspended_students(self, program_id):
        if not self._logged_in:
            raise NotLoggedIn()

        students = self._students_from_forum(program_id)
        total_students = len(students)
        page = self._browser.get_current_page()

        program_name = page.find("td", class_="coluna5_listar_membros").get_text()

        pool = ThreadPoolExecutor()
        futures = []
        for student in students:
            futures.append(pool.submit(self._is_student_suspended, student))

        suspended = 0
        for f in as_completed(futures):
            if f.result():
                suspended += 1

        return {
            "curso": program_name,
            "estudantes": total_students,
            "alunos_trancados": suspended,
            "porcentagem": (suspended / len(students)) * 100.0,
        }
