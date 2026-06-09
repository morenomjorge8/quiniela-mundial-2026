"""Tests del módulo quiniela.scorer."""
import pytest

from quiniela.models import (
    Resultado, Prediccion, PartidoMundial, BonusPrediccion,
    ResultadoJornada,
)
from quiniela.scorer import (
    calcular_puntos_partidos, calcular_bonus_jornada,
    calcular_resultado_jornada,
    PUNTOS_ACIERTO, BONUS_ROJAS, BONUS_PENALES,
)


def test_puntos_partidos_todos_aciertan():
    partidos = [PartidoMundial(numero=1, jornada=1, local='A', visitante='B', resultado=Resultado.LOCAL)]
    preds = [
        Prediccion(participante='Ana', partido_numero=1, prediccion=Resultado.LOCAL),
        Prediccion(participante='Bea', partido_numero=1, prediccion=Resultado.LOCAL),
    ]
    pts = calcular_puntos_partidos(preds, partidos)
    assert pts == {'Ana': PUNTOS_ACIERTO, 'Bea': PUNTOS_ACIERTO}


def test_puntos_partidos_nadie_acierta():
    partidos = [PartidoMundial(numero=1, jornada=1, local='A', visitante='B', resultado=Resultado.LOCAL)]
    preds = [Prediccion(participante='Ana', partido_numero=1, prediccion=Resultado.VISITANTE)]
    assert calcular_puntos_partidos(preds, partidos) == {'Ana': 0}


def test_puntos_partidos_sin_resultado_se_ignora():
    """Predicciones para partidos sin resultado no suman ni restan."""
    partidos = [PartidoMundial(numero=1, jornada=1, local='A', visitante='B', resultado=None)]
    preds = [Prediccion(participante='Ana', partido_numero=1, prediccion=Resultado.LOCAL)]
    assert calcular_puntos_partidos(preds, partidos) == {}


def test_bonus_rojas_exacto():
    bonus_preds = [BonusPrediccion(participante='Ana', jornada=1, total_rojas=3, total_penales=2)]
    resultado = calcular_bonus_jornada(bonus_preds, total_rojas_real=3, total_penales_real=0)
    assert resultado == {'Ana': (BONUS_ROJAS, 0)}


def test_bonus_penales_exacto():
    bonus_preds = [BonusPrediccion(participante='Ana', jornada=1, total_rojas=0, total_penales=2)]
    resultado = calcular_bonus_jornada(bonus_preds, total_rojas_real=5, total_penales_real=2)
    assert resultado == {'Ana': (0, BONUS_PENALES)}


def test_resultado_jornada_incluye_todos_los_participantes():
    """Aun un participante sin predicciones debe aparecer con 0."""
    partidos = [PartidoMundial(numero=1, jornada=1, local='A', visitante='B', resultado=Resultado.LOCAL)]
    preds = [Prediccion(participante='Ana', partido_numero=1, prediccion=Resultado.LOCAL)]
    resultados = calcular_resultado_jornada(
        jornada=1,
        predicciones=preds,
        partidos=partidos,
        bonus_preds=[],
        total_rojas_real=0,
        total_penales_real=0,
        todos_los_participantes=['Ana', 'Bea'],
    )
    nombres = {r.participante for r in resultados}
    assert nombres == {'Ana', 'Bea'}
    by_name = {r.participante: r for r in resultados}
    assert by_name['Ana'].total == PUNTOS_ACIERTO
    assert by_name['Bea'].total == 0


def test_resultado_jornada_suma_bonus_al_total():
    partidos = [PartidoMundial(numero=1, jornada=1, local='A', visitante='B', resultado=Resultado.LOCAL)]
    preds = [Prediccion(participante='Ana', partido_numero=1, prediccion=Resultado.LOCAL)]
    bonus = [BonusPrediccion(participante='Ana', jornada=1, total_rojas=3, total_penales=1)]
    resultados = calcular_resultado_jornada(
        jornada=1,
        predicciones=preds,
        partidos=partidos,
        bonus_preds=bonus,
        total_rojas_real=3,
        total_penales_real=1,
        todos_los_participantes=['Ana'],
    )
    ana = resultados[0]
    # 1 acierto + 2 (rojas) + 2 (penales) = 5
    assert ana.puntos_partidos == PUNTOS_ACIERTO
    assert ana.bonus_rojas == BONUS_ROJAS
    assert ana.bonus_penales == BONUS_PENALES
    assert ana.total == PUNTOS_ACIERTO + BONUS_ROJAS + BONUS_PENALES
