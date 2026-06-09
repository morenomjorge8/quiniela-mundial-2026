"""
Lógica de puntuación de la Quiniela.

Reglas:
- Resultado correcto (1/X/2): 1 punto por partido
- Bonus jornada: +2 pts si adivinas el total de tarjetas rojas
- Bonus jornada: +2 pts si adivinas el total de penales (de falta, no tanda)

El total de la jornada (puntos_partidos + bonus) alimenta la tabla general
acumulada en `quiniela/standings.py`.
"""
from quiniela.models import (
    Resultado, Prediccion, PartidoMundial,
    BonusPrediccion, ResultadoJornada,
)

PUNTOS_ACIERTO = 1
BONUS_ROJAS = 2
BONUS_PENALES = 2


def calcular_puntos_partidos(
    predicciones: list[Prediccion],
    partidos: list[PartidoMundial],
) -> dict[str, int]:
    """Devuelve {participante: puntos_acumulados} para un conjunto de partidos."""
    resultado_real: dict[int, Resultado] = {
        p.numero: p.resultado for p in partidos if p.resultado is not None
    }
    puntos: dict[str, int] = {}
    for pred in predicciones:
        real = resultado_real.get(pred.partido_numero)
        if real is None:
            continue
        acumulado = puntos.get(pred.participante, 0)
        puntos[pred.participante] = acumulado + (PUNTOS_ACIERTO if pred.prediccion == real else 0)
    return puntos


def calcular_bonus_jornada(
    bonus_preds: list[BonusPrediccion],
    total_rojas_real: int,
    total_penales_real: int,
) -> dict[str, tuple[int, int]]:
    """Devuelve {participante: (bonus_rojas, bonus_penales)}."""
    resultado: dict[str, tuple[int, int]] = {}
    for bp in bonus_preds:
        br = BONUS_ROJAS if bp.total_rojas == total_rojas_real else 0
        bpen = BONUS_PENALES if bp.total_penales == total_penales_real else 0
        resultado[bp.participante] = (br, bpen)
    return resultado


def calcular_resultado_jornada(
    jornada: int,
    predicciones: list[Prediccion],
    partidos: list[PartidoMundial],
    bonus_preds: list[BonusPrediccion],
    total_rojas_real: int,
    total_penales_real: int,
    todos_los_participantes: list[str],
) -> list[ResultadoJornada]:
    """Devuelve ResultadoJornada para cada participante en la jornada."""
    puntos_p = calcular_puntos_partidos(predicciones, partidos)
    bonus = calcular_bonus_jornada(bonus_preds, total_rojas_real, total_penales_real)

    resultados = []
    for nombre in todos_los_participantes:
        br, bpen = bonus.get(nombre, (0, 0))
        resultados.append(ResultadoJornada(
            participante=nombre,
            jornada=jornada,
            puntos_partidos=puntos_p.get(nombre, 0),
            bonus_rojas=br,
            bonus_penales=bpen,
        ))
    return resultados
