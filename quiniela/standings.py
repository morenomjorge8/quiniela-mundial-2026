"""
Calcula la tabla general acumulada de la temporada regular (J1–J6).

Ya no hay grupos ni head-to-head: la temporada regular es una sola liga por
puntos acumulados de quiniela. Los 6 primeros clasifican a playoffs.

Orden de desempate:
  1. Puntos totales acumulados
  2. Bonus acumulado (rojas + penales acertados)
  3. Mejor jornada individual
  4. Segunda mejor jornada individual
  5. Tercera mejor jornada individual
"""
from quiniela.models import Participante, ResultadoJornada

CLASIFICAN = 6  # los 6 primeros pasan a playoffs


def clave_desempate(stats: dict) -> tuple:
    """Clave de orden: puntos totales → bonus acumulado → mejor jornada →
    segunda mejor jornada → tercera mejor jornada → nombre.

    El nombre (alfabético) es el último criterio: con todos en cero (antes de
    arrancar el torneo) la tabla queda ordenada alfabéticamente.
    """
    return (
        -stats['puntos_total'],
        -stats['bonus'],
        -stats['mejor_jornada'],
        -stats.get('segunda_mejor_jornada', 0),
        -stats.get('tercera_mejor_jornada', 0),
        stats['nombre'].lower(),
    )


def calcular_tabla_general(
    participantes: list[Participante],
    historial_resultados: list[ResultadoJornada],
) -> list[dict]:
    """
    Devuelve lista de dicts ordenada por desempate, formato:
    {'nombre', 'puntos_total', 'aciertos', 'bonus', 'mejor_jornada', 'jornadas'}
    """
    stats: dict[str, dict] = {
        p.nombre: {
            'nombre': p.nombre,
            'puntos_total': 0,
            'aciertos': 0,
            'bonus': 0,
            'mejor_jornada': 0,
            'segunda_mejor_jornada': 0,
            'tercera_mejor_jornada': 0,
            'jornadas': 0,
            '_totales': [],
        }
        for p in participantes
    }

    for r in historial_resultados:
        s = stats.get(r.participante)
        if s is None:
            # Participante en el historial pero no en la lista actual — ignorar.
            continue
        s['puntos_total'] += r.total
        s['aciertos'] += r.puntos_partidos
        s['bonus'] += r.bonus_rojas + r.bonus_penales
        s['jornadas'] += 1
        s['_totales'].append(r.total)

    for s in stats.values():
        totales = sorted(s.pop('_totales'), reverse=True)
        s['mejor_jornada'] = totales[0] if totales else 0
        s['segunda_mejor_jornada'] = totales[1] if len(totales) > 1 else 0
        s['tercera_mejor_jornada'] = totales[2] if len(totales) > 2 else 0

    return sorted(stats.values(), key=clave_desempate)


def imprimir_tabla(tabla: list[dict], clasifican: int = CLASIFICAN) -> None:
    print(f"\n{'#':>2} {'Nombre':<22} {'J':>3} {'Acie':>5} {'Bon':>4} {'Mej':>4} {'Mej2':>5} {'Mej3':>5} {'Pts':>5}")
    print("-" * 62)
    for i, s in enumerate(tabla, 1):
        corte = "  ◄ corte playoffs" if i == clasifican else ""
        print(
            f"{i:>2} {s['nombre']:<22} {s['jornadas']:>3} "
            f"{s['aciertos']:>5} {s['bonus']:>4} {s['mejor_jornada']:>4} "
            f"{s.get('segunda_mejor_jornada', 0):>5} {s.get('tercera_mejor_jornada', 0):>5} "
            f"{s['puntos_total']:>5}{corte}"
        )


if __name__ == '__main__':
    from data.loader import cargar_participantes

    participantes = cargar_participantes()
    print("Tabla vacía (sin jornadas jugadas):")
    imprimir_tabla(calcular_tabla_general(participantes, []))
