"""
Puntuación de PLAYOFFS (distinta a la fase regular).

Por cada partido (marcador al minuto 90, sin prórroga ni penales):
  - 3 pts si aciertas el marcador EXACTO (ej. 2-1)
  - 2 pts si aciertas solo el resultado (1/X/2) pero no el marcador
  - +1 pt si aciertas qué equipo mete el PRIMER gol (si el partido es 0-0,
    ese punto no lo gana nadie)
  - Máximo 4 pts por partido.

Bonos de la ronda (igual que la fase regular):
  - +2 pts si aciertas el total de tarjetas ROJAS de la jornada
  - +2 pts si aciertas el total de PENALES de falta de la jornada

En cada ronda de playoff, el puntaje de la jornada de cada participante es la
suma de sus partidos + bonos; el cruce H2H lo gana quien tenga más puntos esa jornada.
"""
from quiniela.models import Resultado, PrediccionPlayoff, ResultadoPlayoff

PTS_EXACTO = 3
PTS_RESULTADO = 2
PTS_PRIMER_GOL = 1
BONUS_ROJAS = 2
BONUS_PENALES = 2


def _signo(goles_local: int, goles_visitante: int) -> Resultado:
    if goles_local > goles_visitante:
        return Resultado.LOCAL
    if goles_local == goles_visitante:
        return Resultado.EMPATE
    return Resultado.VISITANTE


def puntos_partido(pred: PrediccionPlayoff, real: ResultadoPlayoff) -> int:
    """Puntos de un participante en un partido de playoff."""
    if pred.goles_local == real.goles_local and pred.goles_visitante == real.goles_visitante:
        pts = PTS_EXACTO
    elif _signo(pred.goles_local, pred.goles_visitante) == _signo(real.goles_local, real.goles_visitante):
        pts = PTS_RESULTADO
    else:
        pts = 0

    # +1 por el primer gol (None = el partido fue 0-0, nadie lo gana)
    if real.primer_gol is not None and pred.primer_gol == real.primer_gol:
        pts += PTS_PRIMER_GOL
    return pts


def puntos_ronda(
    predicciones: list[PrediccionPlayoff],
    resultados: dict[int, ResultadoPlayoff],
    participantes: list[str],
    bonus_preds: list = None,
    total_rojas_real: int | None = None,
    total_penales_real: int | None = None,
) -> dict[str, int]:
    """Devuelve {participante: puntos} para una ronda de playoff (partidos + bonos).

    `bonus_preds`: lista de objetos con .participante/.total_rojas/.total_penales
    (BonusPrediccion). Si los totales reales son None, ese bonus queda pendiente
    (nadie lo recibe). Solo cuenta partidos que ya tienen resultado.
    """
    puntos: dict[str, int] = {p: 0 for p in participantes}
    for pred in predicciones:
        real = resultados.get(pred.partido_numero)
        if real is None or pred.participante not in puntos:
            continue
        puntos[pred.participante] += puntos_partido(pred, real)

    for bp in (bonus_preds or []):
        if bp.participante not in puntos:
            continue
        if total_rojas_real is not None and bp.total_rojas == total_rojas_real:
            puntos[bp.participante] += BONUS_ROJAS
        if total_penales_real is not None and bp.total_penales == total_penales_real:
            puntos[bp.participante] += BONUS_PENALES
    return puntos
