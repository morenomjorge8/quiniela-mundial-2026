"""Fixtures compartidos para los tests."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from quiniela.models import (
    Participante, PartidoMundial, Resultado,
    Prediccion, BonusPrediccion,
)


@pytest.fixture
def participantes_mock() -> list[Participante]:
    """Los participantes canónicos, sin tocar Excel."""
    nombres = [
        'George', 'Pedro', 'Jime', 'Sof Orozco', 'Lucía', 'Sof',
        'Dani', 'Row', 'Pablo', 'Pau', 'Toninho', 'Llanos', 'Vicente',
    ]
    return [Participante(nombre=n) for n in nombres]


@pytest.fixture
def partidos_j1() -> list[PartidoMundial]:
    """12 partidos hipotéticos para la jornada 1 (numerados 1-12)."""
    return [
        PartidoMundial(numero=i, jornada=1, local=f'Local{i}', visitante=f'Visitante{i}')
        for i in range(1, 13)
    ]


@pytest.fixture
def predicciones_todos_local(participantes_mock, partidos_j1) -> list[Prediccion]:
    """Cada participante predice LOCAL en cada partido."""
    return [
        Prediccion(
            participante=p.nombre,
            partido_numero=pa.numero,
            prediccion=Resultado.LOCAL,
        )
        for p in participantes_mock
        for pa in partidos_j1
    ]


@pytest.fixture
def bonus_todos_iguales(participantes_mock) -> list[BonusPrediccion]:
    """Todos predicen 3 rojas y 1 penal."""
    return [
        BonusPrediccion(
            participante=p.nombre,
            jornada=1,
            total_rojas=3,
            total_penales=1,
        )
        for p in participantes_mock
    ]


@pytest.fixture
def resultados_todos_local() -> dict[int, Resultado]:
    """Resultado real LOCAL en los 12 partidos."""
    return {i: Resultado.LOCAL for i in range(1, 13)}


@pytest.fixture
def sim_j1_completa():
    """Bundle de datos simulados de J1 (predicciones + resultados reales)."""
    from tests.simular_jornada import datos_simulados_jornada
    return datos_simulados_jornada(1)
