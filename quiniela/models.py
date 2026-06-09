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
class ResultadoJornada:
    participante: str
    jornada: int
    puntos_partidos: int
    bonus_rojas: int = 0
    bonus_penales: int = 0

    @property
    def total(self) -> int:
        return self.puntos_partidos + self.bonus_rojas + self.bonus_penales
