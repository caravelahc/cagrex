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

>>> cagr = CAGR('id.ufsc', 'password')

>>> pprint(c.student(16100719))
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

>>> pprint(cagr.course('INE5417', '20172'))
{'id': 'INE5417',
 'nome': 'Engenharia de Software I',
 'ementa': 'Análise de requisitos: requisitos funcionais e requisitos '
           'não-funcionais; técnicas para levantamento e representação de '
           'requisitos, incluindo casos de uso. Modelagem OO: classe, '
           'atributo, associação, agregação e herança. Projeto OO: técnicas '
           'para projeto; padrões de projeto, componentes e frameworks; '
           'projeto de arquitetura; mapeamento objeto-relacional. Linguagem de '
           'especificação orientada a objetos. Métodos de análise e projeto '
           'orientados a objetos. Desenvolvimento de um software OO.',
 'semestre': 20172,
 'horas_aula': 90,
 'turmas': [{'id': '04208A',
             'professores': ['Ricardo Pereira e Silva'],
             'vagas_ofertadas': 24,
             'vagas_disponiveis': 2,
             'pedidos_sem_vaga': 0,
             'horarios': [{'dia_da_semana': 2,
                           'duracao': 3,
                           'horario': '1330',
                           'sala': 'CTC-CTC108'},
                          {'dia_da_semana': 3,
                           'duracao': 2,
                           'horario': '0820',
                           'sala': 'CTC-CTC107'}]},
            {'id': '04208B',
             'professores': ['Patricia Vilain'],
             'vagas_ofertadas': 22},
             'vagas_disponiveis': 0,
             'pedidos_sem_vaga': 0,
             'horarios': [{'dia_da_semana': 2,
                           'duracao': 3,
                           'horario': '1330',
                           'sala': 'AUX-ALOCAR'},
                          {'dia_da_semana': 3,
                           'duracao': 2,
                           'horario': '0820',
                           'sala': 'AUX-ALOCAR'}]}]
```
