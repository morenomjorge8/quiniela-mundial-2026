"""
Smoke test end-to-end: pipeline completo de la J1 con datos simulados,
desde cargar el calendario hasta generar el HTML.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

N_PARTICIPANTES = 11


@pytest.fixture
def historial_aislado(tmp_path, monkeypatch):
    """Aísla el historial_resultados.json para que los tests no toquen el archivo real."""
    from data import historial_io
    fake_path = str(tmp_path / 'historial_resultados.json')
    monkeypatch.setattr(historial_io, 'HISTORIAL_PATH', fake_path)
    return fake_path


def test_correr_jornada_j1_con_datos_simulados(sim_j1_completa, historial_aislado):
    """El pipeline corre sin errores y produce resultados + tabla coherentes."""
    from evaluator.pipeline import correr_jornada

    sim = sim_j1_completa
    resultado = correr_jornada(
        jornada=1,
        persistir_historial=False,
        predicciones_override=(sim['predicciones'], sim['bonus_preds']),
        resultados_override=(sim['resultados_reales'], sim['total_rojas'], sim['total_penales']),
        historial_override=[],
    )

    assert len(resultado['resultados_j']) == N_PARTICIPANTES
    assert len(resultado['tabla']) == N_PARTICIPANTES

    # La tabla está ordenada de mayor a menor puntaje total
    puntos = [s['puntos_total'] for s in resultado['tabla']]
    assert puntos == sorted(puntos, reverse=True)

    # El total de la tabla coincide con la suma de los puntos de la jornada
    total_tabla = sum(s['puntos_total'] for s in resultado['tabla'])
    total_jornada = sum(r.total for r in resultado['resultados_j'])
    assert total_tabla == total_jornada


def test_persistencia_de_historial(sim_j1_completa, historial_aislado):
    """Después de correr una jornada, el historial se puede leer del JSON."""
    from evaluator.pipeline import correr_jornada
    from data.historial_io import cargar_historial_resultados

    sim = sim_j1_completa
    correr_jornada(
        jornada=1,
        persistir_historial=True,
        predicciones_override=(sim['predicciones'], sim['bonus_preds']),
        resultados_override=(sim['resultados_reales'], sim['total_rojas'], sim['total_penales']),
        historial_override=[],
    )
    cargado = cargar_historial_resultados(historial_aislado)
    assert len(cargado) == N_PARTICIPANTES  # un ResultadoJornada por participante
    assert all(r.jornada == 1 for r in cargado)


def test_generar_html_j1_simulada(tmp_path, sim_j1_completa, historial_aislado, monkeypatch):
    """El archivo HTML se genera y contiene las secciones esperadas."""
    from reports import generar_reporte
    monkeypatch.setattr(generar_reporte, 'OUTPUT_DIR', str(tmp_path))

    sim = sim_j1_completa
    ruta = generar_reporte.generar(
        jornada_num=1,
        predicciones_override=(sim['predicciones'], sim['bonus_preds']),
        resultados_override=(sim['resultados_reales'], sim['total_rojas'], sim['total_penales']),
    )

    assert os.path.exists(ruta)
    contenido = open(ruta, 'r', encoding='utf-8').read()
    assert 'JORNADA 1' in contenido
    assert 'George' in contenido
    assert 'Partido #1' in contenido
    assert 'Puntos de la jornada' in contenido
    assert 'Tabla General' in contenido
    assert 'clasifican a playoffs' in contenido
    # No deben quedar restos de la estructura vieja
    assert 'Enfrentamientos Quiniela' not in contenido
    assert 'GRUPO' not in contenido
