"""Tests del loader de CSV de respuestas de Google Forms."""
import os

import pytest

from data.respuestas_loader import cargar_respuestas, normalizar_nombre
from quiniela.models import Resultado


FIXTURE_CSV = os.path.join(os.path.dirname(__file__), 'fixtures', 'respuestas_j1_sample.csv')


def test_cargar_respuestas_parsea_3_participantes():
    preds, bonus = cargar_respuestas(jornada=1, csv_path=FIXTURE_CSV)
    nombres = {b.participante for b in bonus}
    assert nombres == {'Daniela Reyes', 'Pablo Quintero', 'George'}


def test_cargar_respuestas_genera_12_predicciones_por_persona():
    preds, _ = cargar_respuestas(jornada=1, csv_path=FIXTURE_CSV)
    daniela = [p for p in preds if p.participante == 'Daniela Reyes']
    assert len(daniela) == 12
    numeros = {p.partido_numero for p in daniela}
    assert numeros == set(range(1, 13))


def test_cargar_respuestas_parsea_resultados_1_x_2():
    preds, _ = cargar_respuestas(jornada=1, csv_path=FIXTURE_CSV)
    daniela = {p.partido_numero: p.prediccion for p in preds if p.participante == 'Daniela Reyes'}
    assert daniela[1] == Resultado.LOCAL
    assert daniela[2] == Resultado.EMPATE
    assert daniela[5] == Resultado.VISITANTE


def test_cargar_respuestas_parsea_bonus():
    _, bonus = cargar_respuestas(jornada=1, csv_path=FIXTURE_CSV)
    daniela = next(b for b in bonus if b.participante == 'Daniela Reyes')
    assert daniela.total_rojas == 3
    assert daniela.total_penales == 1
    assert daniela.jornada == 1


def test_cargar_respuestas_falla_si_falta_columna(tmp_path):
    csv = tmp_path / 'bad.csv'
    csv.write_text('Marca temporal,#1 A vs B\n2026-01-01,Local  (1)\n', encoding='utf-8')
    with pytest.raises(ValueError, match='Tu nombre'):
        cargar_respuestas(jornada=1, csv_path=str(csv))


def test_normalizar_nombre_mapea_variantes():
    assert normalizar_nombre('sof orozco') == 'Sof Orozco'
    assert normalizar_nombre('SOFÍA OROZCO') == 'Sof Orozco'
    assert normalizar_nombre('Toninho Pernanbucano') == 'Toninho'
    # Sin alias: se respeta el texto stripeado tal cual
    assert normalizar_nombre('  Nuevo Jugador ') == 'Nuevo Jugador'


def test_cargar_respuestas_normaliza_nombre(tmp_path):
    csv = tmp_path / 'r.csv'
    csv.write_text(
        'Marca temporal,Tu nombre,#1 A vs B,Total de tarjetas ROJAS,Total de PENALES\n'
        '2026-01-01,sof orozco,Local  (1),2,1\n',
        encoding='utf-8',
    )
    _, bonus = cargar_respuestas(jornada=1, csv_path=str(csv))
    assert {b.participante for b in bonus} == {'Sof Orozco'}
