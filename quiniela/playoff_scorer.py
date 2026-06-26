"""
Puntuación de PLAYOFFS (distinta a la fase regular).

Por cada partido (marcador al minuto 90, sin prórroga ni penales):
  - 3 pts si aciertas el marcador EXACTO (ej. 2-1)
  - 2 pts si aciertas solo el resultado (1/X/2) pero no el marcador
  - +1 pt si aciertas qué equipo mete el PRIMER gol (si el partido es 0-0,
    ese punto no lo gana nadie)
  - Máximo 4 pts por partido.

En cada ronda de playoff, el puntaje de la jornada de cada participante es la
suma de sus partidos; el cruce H2H lo gana quien tenga más puntos esa jornada.
"""
from quiniela.models import Resultado, PrediccionPlayoff, ResultadoPlayoff

PTS_EXACTO = 3
PTS_RESULTADO = 2
PTS_PRIMER_GOL = 1


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
) -> dict[str, int]:
    """Devuelve {participante: puntos} para una ronda de playoff.

    Solo cuenta partidos que ya tienen resultado. Todos los participantes dados
    aparecen (con 0 si no tienen predicciones evaluables).
    """
    puntos: dict[str, int] = {p: 0 for p in participantes}
    for pred in predicciones:
        real = resultados.get(pred.partido_numero)
        if real is None or pred.participante not in puntos:
            continue
        puntos[pred.participante] += puntos_partido(pred, real)
    return puntos
