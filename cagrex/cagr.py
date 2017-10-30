import mechanicalsoup
import requests
from bs4 import BeautifulSoup


def parse_time(time):
        time, room = time.split(' / ')
        weekday, time = time.split('.')
        time, length = time.split('-')

        return {'weekday': int(weekday) - 1,
                'time': time,
                'duration': length,
                'room': room}


class CAGR:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def student(self, student_id):
        student_id = int(student_id)

        browser = mechanicalsoup.StatefulBrowser()

        url = 'https://sistemas.ufsc.br/login'
        params = {'service': 'http://forum.cagr.ufsc.br/'}
        browser.open(url, params=params)

        browser.select_form('#fm1')
        browser['username'] = self.username
        browser['password'] = self.password
        browser.submit_selected()

        url = 'http://forum.cagr.ufsc.br/mostrarPerfil.jsf'
        params = {'usuarioTipo': 'Aluno', 'usuarioId': student_id}
        browser.open(url, params=params)

        page = browser.get_current_page()

        columns = (page.find_all('td', class_=f'coluna{i+1}_listar_salas')
                   for i in range(4))

        rows = zip(*columns)

        program = page.find('span', class_='texto_negrito_pequeno2')
        program = program.get_text(strip=True).split(':')[-1].strip()

        student = {
            'name': page.find('strong').get_text(strip=True),
            'program': program.title()
        }

        courses = (
            {'course_name': course_name.get_text(strip=True),
             'course_id': course_id.get_text(strip=True),
             'class_id': class_id.get_text(strip=True),
             'semester': semester.get_text(strip=True)}
            for course_name, course_id, class_id, semester in rows
        )

        student['courses'] = [c for c in courses
                           if '[MONITOR]' not in c['course_name']
                           and c['course_name'] != '-'
                           and c['course_id'] != '-']

        return student

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
            'course_id': course_id.upper(),
            'name': first_row[5],
            'syllabus': syllabus,
            'class_hours': first_row[6],
        }

        course['classes'] = []
        for row in soup.find_all('tr', class_='rich-table-row'):
            row = row.find_all('td')

            c = {
                'class_id': row[4].text,
                'total_slots': int(row[7].text),
                'available_slots': int(row[10].text.replace('LOTADA', '0')),
                'requests_awaiting': int(row[11].text or '0'),
                'professors': row[-1].get_text('\n', strip=True).splitlines(),
                'times': [
                    parse_time(time)
                    for time in row[-2].get_text('\n', strip=True).splitlines()
                ],
            }

            course['classes'].append(c)

        return course
