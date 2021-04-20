CAGR Explorer (CAGRex)
======================

Installation
------------
```bash
pip install cagrex
```

Usage
-----
```python
>>> from cagrex import CAGR
>>> from pprint import pprint

>>> cagr = CAGR()

>>> pprint(cagr.course('INE5417', '20172'))
{'ementa': 'Análise de requisitos: requisitos funcionais e requisitos '
           'não-funcionais; técnicas para levantamento e representação de '
           'requisitos, incluindo casos de uso. Modelagem OO: classe, '
           'atributo, associação, agregação e herança. Projeto OO: técnicas '
           'para projeto; padrões de projeto, componentes e frameworks; '
           'projeto de arquitetura; mapeamento objeto-relacional. Linguagem de '
           'especificação orientada a objetos. Métodos de análise e projeto '
           'orientados a objetos. Desenvolvimento de um software OO.',
 'horas_aula': 90,
 'id': 'INE5417',
 'nome': 'Engenharia de Software I',
 'semestre': 20181,
 'turmas': {'04208A': {'horarios': [{'dia_da_semana': 2,
                                     'duracao': 3,
                                     'horario': '1330',
                                     'sala': 'CTC-CTC108'},
                                    {'dia_da_semana': 3,
                                     'duracao': 2,
                                     'horario': '0820',
                                     'sala': 'CTC-CTC107'}],
                       'pedidos_sem_vaga': 0,
                       'professores': ['Ricardo Pereira e Silva'],
                       'vagas_disponiveis': 10,
                       'vagas_ofertadas': 25},
            '04208B': {'horarios': [{'dia_da_semana': 2,
                                     'duracao': 3,
                                     'horario': '1330',
                                     'sala': 'AUX-ALOCAR'},
                                    {'dia_da_semana': 3,
                                     'duracao': 2,
                                     'horario': '0820',
                                     'sala': 'AUX-ALOCAR'}],
                       'pedidos_sem_vaga': 0,
                       'professores': ['Patricia Vilain'],
                       'vagas_disponiveis': 9,
                       'vagas_ofertadas': 25}}}

>>> cagr.login('id.ufsc', 'password')
>>> pprint(cagr.student(16100719))
{'id': 16100719,
 'nome': 'Cauê Baasch de Souza',
 'curso': 'Ciências Da Computação',
 'disciplinas': [{'id': 'INE5413',
                  'nome': 'Grafos',
                  'semestre': '20172',
                  'turma': '04208'},
                 {'id': 'INE5414',
                  'nome': 'Redes de Computadores I',
                  'semestre': '20172',
                  'turma': '04208'},
                 {'id': 'INE5415',
                  'nome': 'Teoria da Computação',
                  'semestre': '20172',
                  'turma': '04208'},
                 {'id': 'INE5416',
                  'nome': 'Paradigmas de Programação',
                  'semestre': '20172',
                  'turma': '04208'},
                 {'id': 'INE5417',
                  'nome': 'Engenharia de Software I',
                  'semestre': '20172',
                  'turma': '04208B'}]}

>>> pprint(cagr.students_per_semester(cagr.program_id()))
{'alunos_por_semestre': [('19.2', 54),
                         ('20.1', 52),
                         ('20.2', 52),
                         ('19.1', 50),
                         ('18.2', 40),
                         ('17.2', 37),
                         ('18.1', 37),
                         ('17.1', 31),
                         ('16.2', 27),
                         ('16.1', 26),
                         ('15.2', 18),
                         ('15.1', 14),
                         ('14.2', 14),
                         ('13.2', 11),
                         ('14.1', 6),
                         ('13.1', 6),
                         ('12.2', 5),
                         ('12.1', 5),
                         ('11.1', 2),
                         ('10.2', 1),
                         ('11.2', 1)],
'curso': 'CIÊNCIAS DA COMPUTAÇÃO'}

>>> pprint(cagr.students_from_course(cagr.program_id()))
[{'id': 16100719, 'name': 'Cauê Baasch de Souza'},
 ...
 {'id': 12345678, 'name': 'John Doe'}]

>>> pprint(cagr.total_students(cagr.program_id()))
{'curso': 'CIÊNCIAS DA COMPUTAÇÃO', 'estudantes': 497}

>>> pprint(cagr.suspended_students(cagr.program_id()))
{'curso': 'CIÊNCIAS DA COMPUTAÇÃO',
 'estudantes': 497,
 'alunos_trancados': 35,
 'porcentagem': 7.042253521126761}

```

Running tests
-------------
Run tests without network access with:
```bash
$ poetry run pytest
```

To enable network access:
```bash
$ NETWORK_TESTS=1 poetry run pytest
```

To enable tests that required authentication, you must
provide a `tests/credentials.json` file.
```
file: tests/credentials.json

{
    "username": "",
    "password": ""
}
```
