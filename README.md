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
{'curso': 'CIÊNCIAS DA COMPUTAÇÃO',
'alunos_por_semestre': [('18.2', 50),
                        ('17.2', 48),
                        ('18.1', 44),
                        ('17.1', 44),
                        ('16.2', 39),
                        ('16.1', 35),
                        ('15.2', 34),
                        ('13.2', 32),
                        ('15.1', 30),
                        ('14.2', 25),
                        ('12.1', 20),
                        ('13.1', 18),
                        ('12.2', 14),
                        ('11.2', 12),
                        ('14.1', 11),
                        ('11.1', 6),
                        ('10.2', 4),
                        ('09.2', 1),
                        ('09.1', 1),
                        ('10.1', 1),
                        ('08.2', 1)]}

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
$ pytest
```

To enable network access:
```bash
$ NETWORK_TESTS=1 pytest
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

And run:
```bash
$ NETWORK_TESTS=1 pytest
```
