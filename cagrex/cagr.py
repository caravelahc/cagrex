import mechanicalsoup
import requests
from bs4 import BeautifulSoup


def parse_time(time):
        time, room = time.split(' / ')
        weekday, time = time.split('.')
        time, duration = time.split('-')

        return {'dia_da_semana': int(weekday) - 1,
                'horario': time,
                'duracao': int(duration),
                'sala': room}


class CAGR:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth()

    def auth(self):
        self.browser = mechanicalsoup.StatefulBrowser()

        url = 'https://sistemas.ufsc.br/login'
        params = {'service': 'http://forum.cagr.ufsc.br/'}
        self.browser.open(url, params=params)

        self.browser.select_form('#fm1')
        self.browser['username'] = self.username
        self.browser['password'] = self.password
        self.browser.submit_selected()

    def student(self, student_id):
        student_id = int(student_id)

        url = 'http://forum.cagr.ufsc.br/mostrarPerfil.jsf'
        params = {'usuarioTipo': 'Aluno', 'usuarioId': student_id}
        self.browser.open(url, params=params)

        page = self.browser.get_current_page()

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
        base_url = ('https://cagr.sistemas.ufsc.br/'
                    'modules/comunidade/cadastroTurmas/')
        cookies = requests.get(base_url).cookies

        form_data = {
            'AJAXREQUEST': '_viewRoot',
            'formBusca': 'formBusca',
            'javax.faces.ViewState': 'j_id1',
            'formBusca:j_id122': 'formBusca:j_id122',
            'formBusca:selectSemestre': semester,
            'formBusca:codigoDisciplina': course_id,
        }

        response = requests.post(base_url, data=form_data, cookies=cookies)
        soup = BeautifulSoup(response.text)

        first_row = soup.find('tr', class_='rich-table-firstrow')
        first_row = [cell.get_text('\n', strip=True)
                     for cell in first_row.find_all('td')]

        response = requests.get(
            base_url + f'ementaDisciplina.xhtml?codigoDisciplina={course_id}'
        )
        syllabus = BeautifulSoup(response.text).find('td')
        syllabus = syllabus.get_text('\n', strip=True)

        course = {
            'id': course_id.upper(),
            'nome': first_row[5],
            'ementa': syllabus,
            'horas_aula': int(first_row[6]),
        }

        course['turmas'] = []
        for row in soup.find_all('tr', class_='rich-table-row'):
            row = row.find_all('td')

            c = {
                'id': row[4].text,
                'vagas_ofertadas': int(row[7].text),
                'vagas_disponiveis': int(row[10].text.replace('LOTADA', '0')),
                'pedidos_sem_vaga': int(row[11].text or '0'),
                'professores': row[-1].get_text('\n', strip=True).splitlines(),
                'horarios': [
                    parse_time(time)
                    for time in row[-2].get_text('\n', strip=True).splitlines()
                ],
            }

            course['turmas'].append(c)

        return course

    def semesters(self):
        url = ('https://cagr.sistemas.ufsc.br/'
               'modules/comunidade/cadastroTurmas/')

        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        select = soup.find('select', id='formBusca:selectSemestre')
        return [option['value'] for option in select.find_all('option')]
