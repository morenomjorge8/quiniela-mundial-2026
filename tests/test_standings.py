"""Tests del módulo quiniela.standings (tabla general acumulada)."""
from quiniela.models import Participante, ResultadoJornada
from quiniela.standings import calcular_tabla_general, clave_desempate


def _mk(nombre, pts=0, bonus=0, mejor=0):
    return {
        'nombre': nombre,
        'puntos_total': pts,
        'aciertos': 0,
        'bonus': bonus,
        'mejor_jornada': mejor,
        'jornadas': 0,
    }


def test_clave_desempate_prioriza_puntos_totales():
    a = _mk('A', pts=10, bonus=8)
    b = _mk('B', pts=12, bonus=0)
    assert clave_desempate(b) < clave_desempate(a)


def test_clave_desempate_segundo_criterio_es_bonus():
    a = _mk('A', pts=10, bonus=6)
    b = _mk('B', pts=10, bonus=2)
    assert clave_desempate(a) < clave_desempate(b)


def test_clave_desempate_tercero_es_mejor_jornada():
    a = _mk('A', pts=10, bonus=4, mejor=9)
    b = _mk('B', pts=10, bonus=4, mejor=6)
    assert clave_desempate(a) < clave_desempate(b)


def test_calcular_tabla_acumula_puntos_y_bonus():
    parts = [Participante('Ana'), Participante('Bea'), Participante('Cyn')]
    historial = [
        ResultadoJornada(participante='Ana', jornada=1, puntos_partidos=8, bonus_rojas=2, bonus_penales=0),
        ResultadoJornada(participante='Ana', jornada=2, puntos_partidos=5, bonus_rojas=0, bonus_penales=2),
        ResultadoJornada(participante='Bea', jornada=1, puntos_partidos=3, bonus_rojas=0, bonus_penales=0),
        ResultadoJornada(participante='Cyn', jornada=1, puntos_partidos=6, bonus_rojas=2, bonus_penales=2),
    ]
    tabla = calcular_tabla_general(parts, historial)
    by_name = {s['nombre']: s for s in tabla}

    # Ana: (8+2) + (5+2) = 17, bonus acumulado 4, mejor jornada 10, 2 jornadas
    assert by_name['Ana']['puntos_total'] == 17
    assert by_name['Ana']['bonus'] == 4
    assert by_name['Ana']['mejor_jornada'] == 10
    assert by_name['Ana']['jornadas'] == 2
    assert by_name['Ana']['aciertos'] == 13

    # Orden esperado: Ana (17) > Cyn (10) > Bea (3)
    assert [s['nombre'] for s in tabla] == ['Ana', 'Cyn', 'Bea']


def test_tabla_incluye_a_todos_aunque_no_tengan_resultados(participantes_mock):
    tabla = calcular_tabla_general(participantes_mock, [])
    assert len(tabla) == len(participantes_mock)
    assert all(s['puntos_total'] == 0 for s in tabla)


def test_desempate_por_bonus_en_tabla_real():
    parts = [Participante('A'), Participante('B')]
    historial = [
        ResultadoJornada(participante='A', jornada=1, puntos_partidos=6, bonus_rojas=2, bonus_penales=2),
        ResultadoJornada(participante='B', jornada=1, puntos_partidos=10, bonus_rojas=0, bonus_penales=0),
    ]
    tabla = calcular_tabla_general(parts, historial)
    # Mismos puntos totales (10) → desempata el de más bonus (A)
    assert [s['nombre'] for s in tabla] == ['A', 'B']
