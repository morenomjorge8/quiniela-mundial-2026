from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Resultado(str, Enum):
    LOCAL = "1"
    EMPATE = "X"
    VISITANTE = "2"


@dataclass
class Participante:
    nombre: str


@dataclass
class PartidoMundial:
    numero: int
    jornada: int
    local: str
    visitante: str
    resultado: Optional[Resultado] = None
    fecha: Optional[str] = None  # texto libre, ej. "Jue 11 jun · 18:00"


@dataclass
class Prediccion:
    participante: str
    partido_numero: int
    prediccion: Resultado


@dataclass
class BonusPrediccion:
    participante: str
    jornada: int
    total_rojas: int
    total_penales: int


@dataclass
class PrediccionPlayoff:
    """Predicción de un partido de playoff (marcador al minuto 90 + primer gol)."""
    participante: str
    partido_numero: int
    goles_local: int
    goles_visitante: int
    primer_gol: str  # 'L' (local) o 'V' (visitante) — qué equipo mete el primer gol


@dataclass
class ResultadoPlayoff:
    """Resultado real de un partido de playoff (al minuto 90, sin prórroga/penales)."""
    partido_numero: int
    goles_local: int
    goles_visitante: int
    primer_gol: Optional[str] = None  # 'L', 'V', o None si terminó 0-0


@dataclass
class ResultadoJornada:
    participante: str
    jornada: int
    puntos_partidos: int
    bonus_rojas: int = 0
    bonus_penales: int = 0

    @property
    def total(self) -> int:
        return self.puntos_partidos + self.bonus_rojas + self.bonus_penales
