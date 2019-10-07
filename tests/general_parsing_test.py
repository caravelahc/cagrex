import pytest

import bs4

from cagrex.cagr import _parse_class, _parse_time


def test_time_from_str():
    """Tests if a class's schedules are correctly extracted from default CAGR
    time strings."""
    expected_times = {
        "3.1330-3 / CTC-CTC108": {
            "dia_da_semana": 2,
            "horario": "1330",
            "duracao": 3,
            "sala": "CTC-CTC108",
        },
        "4.0820-2 / CTC-CTC107": {
            "dia_da_semana": 3,
            "horario": "0820",
            "duracao": 2,
            "sala": "CTC-CTC107",
        },
    }

    assert all(_parse_time(text) == expected for text, expected in expected_times.items())


def test_class_from_row_html():
    """Tests if classes are correctly extracted from <tr> tags."""
    with open('tests/assets/class_row.html') as f:
        row_html = f.read()

    row = bs4.BeautifulSoup(row_html, "html.parser")

    expected_class = {
        "id_disciplina": "INE5417",
        "nome": "Engenharia de Software I",
        "horas_aula": 90,
        "id_turma": "04208A",
        "vagas_ofertadas": 24,
        "vagas_disponiveis": 3,
        "pedidos_sem_vaga": 0,
        "professores": ["Ricardo Pereira e Silva"],
        "horarios": [
            {
                "dia_da_semana": 2,
                "horario": "1330",
                "duracao": 3,
                "sala": "CTC-CTC108",
            },
            {
                "dia_da_semana": 3,
                "horario": "0820",
                "duracao": 2,
                "sala": "CTC-CTC107",
            },
        ],
    }

    assert _parse_class(row) == expected_class
