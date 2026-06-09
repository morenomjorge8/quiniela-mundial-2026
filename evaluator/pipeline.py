"""
Pipeline de alto nivel para preparar el estado de una jornada.

Centraliza el setup que antes estaba duplicado entre `tests/simular_jornada.py`
y `reports/generar_reporte.py`. Carga participantes, calendario, respuestas
y resultados reales — luego invoca el evaluator.
"""
import json
import os

from data.loader import cargar_participantes, cargar_calendario
from data.historial_io import cargar_historial_resultados, guardar_historial_resultados
from data.respuestas_loader import cargar_respuestas
from quiniela.models import Resultado, Prediccion, BonusPrediccion
from evaluator.evaluator import evaluar_jornada

RESULTADOS_REALES_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'resultados_reales.json'
)
RESPUESTAS_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'respuestas'
)


def cargar_resultados_reales(
    jornada: int,
    ruta: str = RESULTADOS_REALES_PATH,
) -> tuple[dict[int, Resultado], int, int]:
    """Devuelve (mapa partido→Resultado, total_rojas, total_penales) para la jornada."""
    if not os.path.exists(ruta):
        return {}, 0, 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entrada = data.get(str(jornada), {})
    resultados_raw = entrada.get('resultados', {}) or {}
    resultados = {
        int(num): Resultado(valor)
        for num, valor in resultados_raw.items()
    }
    return (
        resultados,
        int(entrada.get('total_rojas', 0)),
        int(entrada.get('total_penales', 0)),
    )


def cargar_estado_jornada(
    jornada: int,
    respuestas_csv: str | None = None,
    resultados_reales_path: str = RESULTADOS_REALES_PATH,
    predicciones_override: tuple[list[Prediccion], list[BonusPrediccion]] | None = None,
    resultados_override: tuple[dict[int, Resultado], int, int] | None = None,
    historial_override: list | None = None,
) -> dict:
    """
    Carga todo lo necesario para evaluar/reportar una jornada.

    Overrides (para tests/simulaciones):
      - `predicciones_override`: usar en lugar de leer el CSV.
      - `resultados_override`: (mapa partido→Resultado, total_rojas, total_penales).
      - `historial_override`: usar en lugar de leer historial_resultados.json.

    Devuelve dict con:
      'participantes', 'partidos_jornada',
      'predicciones', 'bonus_preds',
      'resultados_reales', 'total_rojas_real', 'total_penales_real',
      'historial_previo'
    """
    participantes = cargar_participantes()
    partidos_all = cargar_calendario()
    partidos_j = [p for p in partidos_all if p.jornada == jornada]

    if predicciones_override is not None:
        predicciones, bonus_preds = predicciones_override
    elif respuestas_csv and os.path.exists(respuestas_csv):
        predicciones, bonus_preds = cargar_respuestas(jornada, respuestas_csv)
    else:
        predicciones, bonus_preds = [], []

    if resultados_override is not None:
        resultados_reales, total_rojas, total_penales = resultados_override
    else:
        resultados_reales, total_rojas, total_penales = cargar_resultados_reales(
            jornada, resultados_reales_path
        )

    historial_previo = (
        historial_override if historial_override is not None
        else cargar_historial_resultados()
    )

    return {
        'participantes': participantes,
        'partidos_jornada': partidos_j,
        'predicciones': predicciones,
        'bonus_preds': bonus_preds,
        'resultados_reales': resultados_reales,
        'total_rojas_real': total_rojas,
        'total_penales_real': total_penales,
        'historial_previo': historial_previo,
    }


def ruta_respuestas_csv(jornada: int) -> str:
    """Path canónico para el CSV de respuestas de una jornada."""
    return os.path.join(RESPUESTAS_DIR, f'jornada_{jornada}.csv')


def correr_jornada(
    jornada: int,
    persistir_historial: bool = True,
    predicciones_override: tuple[list[Prediccion], list[BonusPrediccion]] | None = None,
    resultados_override: tuple[dict[int, Resultado], int, int] | None = None,
    historial_override: list | None = None,
) -> dict:
    """
    Flujo completo de una jornada: cargar estado, evaluar, opcionalmente persistir.

    Devuelve el dict de `evaluar_jornada` enriquecido con el estado cargado.
    """
    estado = cargar_estado_jornada(
        jornada=jornada,
        respuestas_csv=ruta_respuestas_csv(jornada),
        predicciones_override=predicciones_override,
        resultados_override=resultados_override,
        historial_override=historial_override,
    )

    resultado = evaluar_jornada(
        jornada=jornada,
        participantes=estado['participantes'],
        partidos_jornada=estado['partidos_jornada'],
        resultados_reales=estado['resultados_reales'],
        predicciones=estado['predicciones'],
        bonus_preds=estado['bonus_preds'],
        total_rojas_real=estado['total_rojas_real'],
        total_penales_real=estado['total_penales_real'],
        historial_previo=estado['historial_previo'],
    )

    if persistir_historial:
        guardar_historial_resultados(resultado['historial_total'])

    return {**estado, **resultado}
