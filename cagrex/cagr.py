import mechanicalsoup
import requests
from bs4 import BeautifulSoup


CAGR_URL = 'https://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/'


class InvalidCredentials(Exception):
    pass


class NotLoggedIn(Exception):
    pass


def _parse_time(time):
    time, room = time.split(' / ')
    weekday, time = time.split('.')
    time, duration = time.split('-')

    return {'dia_da_semana': int(weekday) - 1,
            'horario': time,
            'duracao': int(duration),
            'sala': room}


def _parse_class(row):
    cells = [c.get_text('\n', strip=True) for c in row.find_all('td')]
    return {
        'id_disciplina': cells[3],
        'nome': cells[5],
        'horas_aula': int(cells[6]),
        'id_turma': cells[4],
        'vagas_ofertadas': int(cells[7]),
        'vagas_disponiveis': int(cells[10].replace('LOTADA', '0')),
        'pedidos_sem_vaga': int(cells[11] or '0'),
        'professores': cells[-1].splitlines(),
        'horarios': [_parse_time(time) for time in cells[-2].splitlines()],
    }


def _course_from_classes(classes):
    classes = list(classes)
    first = classes[0]
    course_id = first['id_disciplina'].upper()

    response = requests.get(
        CAGR_URL + f'ementaDisciplina.xhtml?codigoDisciplina={course_id}'
    )
    syllabus = BeautifulSoup(response.text, 'html.parser').find('td')
    syllabus = syllabus.get_text('\n', strip=True)

    course = {
        'id': course_id,
        'nome': first['nome'],
        'ementa': syllabus,
        'horas_aula': first['horas_aula'],
        'turmas': []
    }

    for c in classes:
        del c['nome']
        del c['id_disciplina']
        del c['horas_aula']
        c['id'] = c.pop('id_turma')
        course['turmas'].append(c)

    return course


class CAGR:
    def __init__(self):
        self._browser = mechanicalsoup.StatefulBrowser()
        self._logged_in = False

    def login(self, username, password):
        self._browser.open('https://sistemas.ufsc.br/login',
                           params={'service': 'http://forum.cagr.ufsc.br/'})

        self._browser.select_form('#fm1')
        self._browser['username'] = username
        self._browser['password'] = password

        response = self._browser.submit_selected()
        if response.ok:
            self._logged_in = True
        else:
            raise InvalidCredentials()

    def student(self, student_id):
        if not self._logged_in:
            raise NotLoggedIn()

        url = 'http://forum.cagr.ufsc.br/mostrarPerfil.jsf'
        params = {'usuarioTipo': 'Aluno', 'usuarioId': student_id}
        self._browser.open(url, params=params)

        page = self._browser.get_current_page()

        columns = (page.find_all('td', class_=f'coluna{i+1}_listar_salas')
                   for i in range(4))

        rows = zip(*columns)
        courses = [
            {'nome': course_name.get_text(strip=True),
             'id': course_id.get_text(strip=True),
             'turma': class_id.get_text(strip=True),
             'semestre': semester.get_text(strip=True)}
            for course_name, course_id, class_id, semester in rows
        ]

        program = page.find('span', class_='texto_negrito_pequeno2')
        program = program.get_text(strip=True).split(':')[-1].strip()

        return {
            'id': student_id,
            'nome': page.find('strong').get_text(strip=True),
            'curso': program.title(),
            'disciplinas': [c for c in courses
                            if '[MONITOR]' not in c['nome']
                            and c['nome'] != '-' and c['id'] != '-']
        }

    def course(self, course_id, semester):
        session = requests.Session()

        response = session.get(CAGR_URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        submit_id = soup.find(value='Buscar')['id']

        form_data = {
            'AJAXREQUEST': '_viewRoot',
            'formBusca': 'formBusca',
            'javax.faces.ViewState': 'j_id1',
            submit_id: submit_id,
            'formBusca:selectSemestre': semester,
            'formBusca:codigoDisciplina': course_id,
        }

        response = session.post(CAGR_URL, data=form_data)
        soup = BeautifulSoup(response.text, 'html.parser')

        course = _course_from_classes(
            _parse_class(row)
            for row in soup.find_all('tr', class_='rich-table-row')
        )

        course.update(semestre=int(semester))
        return course

    def semesters(self):
        html = requests.get(CAGR_URL).text
        soup = BeautifulSoup(html, 'html.parser')

        select = soup.find('select', id='formBusca:selectSemestre')
        return [option['value'] for option in select.find_all('option')]
