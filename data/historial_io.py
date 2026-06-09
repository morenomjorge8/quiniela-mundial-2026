"""Persistencia del historial de resultados por jornada en JSON.

Guarda un `ResultadoJornada` por participante y jornada. La tabla general se
recalcula a partir de este historial acumulado.
"""
import json
import os
from quiniela.models import ResultadoJornada

HISTORIAL_PATH = os.path.join(os.path.dirname(__file__), 'historial_resultados.json')


def _resolver_ruta(ruta: str | None) -> str:
    """Si ruta es None, devuelve el HISTORIAL_PATH actual del módulo (respeta monkeypatch)."""
    if ruta is not None:
        return ruta
    # Lee del módulo en runtime para que tests con monkeypatch funcionen
    import data.historial_io as _self
    return _self.HISTORIAL_PATH


def cargar_historial_resultados(ruta: str | None = None) -> list[ResultadoJornada]:
    """Carga el historial acumulado de resultados. Lista vacía si no existe el archivo."""
    ruta = _resolver_ruta(ruta)
    if not os.path.exists(ruta):
        return []
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [
        ResultadoJornada(
            jornada=r['jornada'],
            participante=r['participante'],
            puntos_partidos=r['puntos_partidos'],
            bonus_rojas=r.get('bonus_rojas', 0),
            bonus_penales=r.get('bonus_penales', 0),
        )
        for r in data
    ]


def guardar_historial_resultados(
    historial: list[ResultadoJornada], ruta: str | None = None
) -> None:
    """Sobreescribe el archivo con el historial completo acumulado."""
    ruta = _resolver_ruta(ruta)
    data = [
        {
            'jornada': r.jornada,
            'participante': r.participante,
            'puntos_partidos': r.puntos_partidos,
            'bonus_rojas': r.bonus_rojas,
            'bonus_penales': r.bonus_penales,
        }
        for r in historial
    ]
    os.makedirs(os.path.dirname(ruta) or '.', exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
