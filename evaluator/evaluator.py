"""
Pipeline de evaluación de una jornada (temporada regular).

Flujo:
  1. Aplicar resultados reales del Mundial a los partidos de la jornada
  2. Calcular puntos de cada participante (aciertos + bonus)
  3. Acumular al historial y recalcular la tabla general
"""
from quiniela.models import (
    Resultado, Prediccion, BonusPrediccion, PartidoMundial,
)
from quiniela.scorer import calcular_resultado_jornada
from quiniela.standings import calcular_tabla_general


def evaluar_jornada(
    jornada: int,
    participantes: list,
    partidos_jornada: list[PartidoMundial],
    resultados_reales: dict[int, Resultado],
    predicciones: list[Prediccion],
    bonus_preds: list[BonusPrediccion],
    total_rojas_real: int,
    total_penales_real: int,
    historial_previo: list = None,
) -> dict:
    """
    Evalúa una jornada completa. No imprime nada — sólo calcula.

    Devuelve dict con:
      'resultados_j'     : list[ResultadoJornada] de cada participante
      'tabla'            : list[dict] tabla general acumulada
      'historial_total'  : list[ResultadoJornada] (previo + actual) para persistir
    """
    for p in partidos_jornada:
        p.resultado = resultados_reales.get(p.numero)

    nombres = [p.nombre for p in participantes]

    resultados_j = calcular_resultado_jornada(
        jornada=jornada,
        predicciones=predicciones,
        partidos=partidos_jornada,
        bonus_preds=bonus_preds,
        total_rojas_real=total_rojas_real,
        total_penales_real=total_penales_real,
        todos_los_participantes=nombres,
    )

    # Reemplaza (no suma) los resultados previos de ESTA jornada, para que
    # re-correrla en vivo —según van terminando los partidos— sea idempotente.
    historial_total = [
        r for r in (historial_previo or []) if r.jornada != jornada
    ] + resultados_j
    tabla = calcular_tabla_general(participantes, historial_total)

    return {
        'resultados_j': resultados_j,
        'tabla': tabla,
        'historial_total': historial_total,
    }
