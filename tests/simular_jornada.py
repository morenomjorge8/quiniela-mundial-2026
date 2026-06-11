"""
Datos simulados de la Jornada 1 con predicciones ficticias de los 11 participantes.

Sirve para dos cosas:
  1. Como fuente de fixtures para los tests (tests/conftest.py importa de aquí).
  2. Como script ejecutable (`py tests/simular_jornada.py`) que corre el pipeline
     completo y muestra el reporte por consola — útil para validar a mano que todo funciona.

Resultados reales inventados para la prueba (J1):
  #1  México vs Sudáfrica         → 1 (México)
  #2  Corea vs Chequia            → X (Empate)
  #3  Canadá vs Bosnia            → 1 (Canadá)
  #4  USA vs Paraguay             → 1 (USA)
  #5  Qatar vs Suiza              → 2 (Suiza)
  #6  Brasil vs Marruecos         → 1 (Brasil)
  #7  Haití vs Escocia            → 2 (Escocia)
  #8  Australia vs Turquía        → X (Empate)
  #9  Alemania vs Curazao         → 1 (Alemania)
  #10 Países Bajos vs Japón       → 1 (Países Bajos)
  #11 Costa de Marfil vs Ecuador  → 2 (Ecuador)
  #12 Suecia vs Túnez             → X (Empate)

Total rojas reales : 3
Total penales reales: 1
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from quiniela.models import Resultado, Prediccion, BonusPrediccion


# ── Resultados reales de la Jornada 1 ──────────────────────────
RESULTADOS_REALES_J1: dict[int, Resultado] = {
    1:  Resultado.LOCAL,
    2:  Resultado.EMPATE,
    3:  Resultado.LOCAL,
    4:  Resultado.LOCAL,
    5:  Resultado.VISITANTE,
    6:  Resultado.LOCAL,
    7:  Resultado.VISITANTE,
    8:  Resultado.EMPATE,
    9:  Resultado.LOCAL,
    10: Resultado.LOCAL,
    11: Resultado.VISITANTE,
    12: Resultado.EMPATE,
}
ROJAS_REALES_J1 = 3
PENALES_REALES_J1 = 1

# ── Predicciones de cada participante (J1) ─────────────────────
# Formato: [pred_p1, p2, p3, ..., p12, rojas, penales]
_R = Resultado

RESPUESTAS_J1: dict[str, list] = {
    'George':     [_R.LOCAL, _R.LOCAL,  _R.LOCAL, _R.LOCAL, _R.VISITANTE, _R.LOCAL, _R.VISITANTE, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.LOCAL,     _R.EMPATE, 3, 2],
    'Pedro':      [_R.LOCAL, _R.EMPATE, _R.LOCAL, _R.EMPATE,_R.VISITANTE, _R.LOCAL, _R.VISITANTE, _R.VISITANTE,_R.LOCAL,_R.LOCAL,_R.LOCAL,     _R.EMPATE, 2, 1],
    'Jime':       [_R.LOCAL, _R.LOCAL,  _R.LOCAL, _R.LOCAL, _R.LOCAL,     _R.LOCAL, _R.LOCAL,     _R.LOCAL,  _R.LOCAL, _R.LOCAL, _R.LOCAL,     _R.LOCAL,  3, 1],
    'Sof Orozco': [_R.LOCAL, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.VISITANTE, _R.LOCAL, _R.LOCAL,     _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.LOCAL,     _R.EMPATE, 3, 1],
    'Lucía':      [_R.EMPATE,_R.EMPATE, _R.LOCAL, _R.LOCAL, _R.LOCAL,     _R.EMPATE,_R.VISITANTE, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.VISITANTE, _R.LOCAL,  3, 1],
    'Sof':        [_R.LOCAL, _R.LOCAL,  _R.LOCAL, _R.VISITANTE,_R.VISITANTE,_R.LOCAL,_R.VISITANTE,_R.LOCAL,  _R.LOCAL, _R.LOCAL, _R.EMPATE,    _R.EMPATE, 2, 3],
    'Dani':       [_R.LOCAL, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.VISITANTE, _R.LOCAL, _R.VISITANTE, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.VISITANTE, _R.EMPATE, 3, 1],
    'Row':        [_R.LOCAL, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.LOCAL,     _R.LOCAL, _R.LOCAL,     _R.EMPATE, _R.EMPATE,_R.LOCAL, _R.EMPATE,    _R.EMPATE, 1, 1],
    'Pablo':      [_R.LOCAL, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.VISITANTE, _R.LOCAL, _R.VISITANTE, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.VISITANTE, _R.LOCAL,  2, 1],
    'Pau':        [_R.LOCAL, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.VISITANTE, _R.LOCAL, _R.VISITANTE, _R.EMPATE, _R.LOCAL, _R.LOCAL, _R.LOCAL,     _R.EMPATE, 3, 1],
    'Toninho':    [_R.VISITANTE,_R.EMPATE,_R.VISITANTE,_R.EMPATE,_R.VISITANTE,_R.EMPATE,_R.VISITANTE,_R.EMPATE,_R.EMPATE,_R.EMPATE,_R.VISITANTE,_R.EMPATE,3,1],
    'Llanos':     [_R.EMPATE,_R.VISITANTE,_R.LOCAL,_R.LOCAL,_R.VISITANTE,_R.VISITANTE,_R.LOCAL,_R.LOCAL,_R.LOCAL,_R.EMPATE,_R.VISITANTE,_R.LOCAL,4,0],
    'Vicente':    [_R.LOCAL,_R.EMPATE,_R.LOCAL,_R.LOCAL,_R.VISITANTE,_R.LOCAL,_R.VISITANTE,_R.EMPATE,_R.LOCAL,_R.LOCAL,_R.LOCAL,_R.EMPATE,3,1],
}


def _construir_predicciones(jornada: int, respuestas: dict, partidos_jornada):
    """Convierte el dict `RESPUESTAS_J1` (u otro similar) en listas de Predicciones y bonus."""
    predicciones = []
    bonus = []
    for nombre, vals in respuestas.items():
        n_partidos = len(partidos_jornada)
        preds_partidos = vals[:n_partidos]
        rojas = vals[n_partidos]
        penales = vals[n_partidos + 1]
        for i, partido in enumerate(partidos_jornada):
            predicciones.append(Prediccion(
                participante=nombre,
                partido_numero=partido.numero,
                prediccion=preds_partidos[i],
            ))
        bonus.append(BonusPrediccion(
            participante=nombre,
            jornada=jornada,
            total_rojas=rojas,
            total_penales=penales,
        ))
    return predicciones, bonus


def datos_simulados_jornada(jornada: int) -> dict:
    """
    Devuelve los datos simulados de una jornada para inyectar al pipeline.

    Hoy sólo está implementada J1. Para añadir otras jornadas, agregar arriba
    sus diccionarios RESULTADOS/RESPUESTAS y extender este match.

    Devuelve dict con: 'resultados_reales', 'total_rojas', 'total_penales',
    'predicciones', 'bonus_preds'.
    """
    from data.loader import cargar_calendario

    if jornada != 1:
        raise NotImplementedError(f"Sin datos simulados para jornada {jornada}; sólo J1.")

    partidos_j = [p for p in cargar_calendario() if p.jornada == jornada]
    predicciones, bonus = _construir_predicciones(jornada, RESPUESTAS_J1, partidos_j)

    return {
        'resultados_reales': RESULTADOS_REALES_J1,
        'total_rojas': ROJAS_REALES_J1,
        'total_penales': PENALES_REALES_J1,
        'predicciones': predicciones,
        'bonus_preds': bonus,
    }


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

    from evaluator.pipeline import correr_jornada
    from evaluator.console_report import imprimir_reporte

    sim = datos_simulados_jornada(1)
    resultado = correr_jornada(
        jornada=1,
        persistir_historial=False,
        predicciones_override=(sim['predicciones'], sim['bonus_preds']),
        resultados_override=(sim['resultados_reales'], sim['total_rojas'], sim['total_penales']),
        historial_override=[],
    )
    imprimir_reporte(
        jornada=1,
        resultados_j=resultado['resultados_j'],
        tabla=resultado['tabla'],
        total_rojas_real=sim['total_rojas'],
        total_penales_real=sim['total_penales'],
    )
