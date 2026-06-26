"""
Llaves de playoffs de la quiniela (después de la J6).

Dos llaves, sembradas con la tabla general final (13 participantes):

  🏆 CAMPEONES (lugares 1–6) — por los premios 1°/2°/3°
     Cuartos:  3 vs 6, 4 vs 5     (bye: 1, 2)
     Semis:    1 vs G(4v5), 2 vs G(3v6)
     Final:    G(SF1) vs G(SF2)   → 1° y 2°
     3er lugar: P(SF1) vs P(SF2)
     Avanza el que GANA el cruce (más puntos de playoff esa jornada).

  💩 SÓTANO (lugares 7–13) — "toilet bowl" invertido, para NO ser el peor
     Repechaje: 12 vs 13           (bye: 7, 8)
     Cuartos:   9 vs P(rep), 10 vs 11
     Semis:     7 vs P(10v11), 8 vs P(9vRep)
     Final:     P(SF1) vs P(SF2)   → el que PIERDE es "el peor"
     Aquí avanza el que PIERDE el cruce (cae hacia el fondo); el que gana se salva.

Cada cruce (H2H) lo gana quien hace más puntos de playoff esa jornada; empate →
mejor sembrado (lugar más alto en la tabla final).
"""
from quiniela.standings import calcular_tabla_general


# ── Siembra ──────────────────────────────────────────────────────────────

def sembrar(tabla: list[dict]) -> list[str]:
    """Devuelve los nombres por seed: índice 0 = lugar 1, … índice 12 = lugar 13."""
    return [s['nombre'] for s in tabla]


def clasificacion(seeds: list[str]) -> dict[str, list[str]]:
    """{'campeones': [1..6], 'sotano': [7..13]} con los nombres."""
    return {'campeones': seeds[:6], 'sotano': seeds[6:13]}


def bracket_display(seeds: list[str]) -> dict:
    """Estructura de ambas llaves para mostrar (siembra actual).

    Cada ronda: (nombre, [(slot_a, slot_b), ...]) donde un slot es el nombre de
    un participante (si está sembrado) o un texto placeholder (rondas futuras).
    """
    s = seeds
    return {
        'campeones': [
            ('Cuartos',     [(s[2], s[5]), (s[3], s[4])]),
            ('Semifinales', [(s[0], 'Ganador 4°v5°'), (s[1], 'Ganador 3°v6°')]),
            ('Final',       [('Ganador Semifinal A', 'Ganador Semifinal B')]),
            ('3er lugar',   [('Perdedor Semifinal A', 'Perdedor Semifinal B')]),
        ],
        'sotano': [
            ('Repechaje',   [(s[11], s[12])]),
            ('Cuartos',     [(s[8], 'Pierde repechaje'), (s[9], s[10])]),
            ('Semifinales', [(s[6], 'Pierde 10°v11°'), (s[7], 'Pierde 9°vRepe')]),
            ('Final',       [('Pierde Semifinal A', 'Pierde Semifinal B')]),
        ],
    }


# ── H2H ──────────────────────────────────────────────────────────────────

def _h2h(a, b, puntos: dict[str, int], seeds: list[str]):
    """Devuelve (ganador, perdedor) del cruce por puntos; empate → mejor sembrado."""
    if a is None or b is None:
        return (a or b), None
    pa, pb = puntos.get(a, 0), puntos.get(b, 0)
    if pa != pb:
        return (a, b) if pa > pb else (b, a)
    # empate → mejor sembrado (menor índice en seeds)
    g = a if seeds.index(a) < seeds.index(b) else b
    return g, (b if g == a else a)


# ── Definición de cruces por ronda ───────────────────────────────────────
# Cada cruce: (id, jugador_a, jugador_b). Los ids permiten referir ganadores/perdedores.

def _campeones_cuartos(s):
    return [('C-CF1', s[2], s[5]), ('C-CF2', s[3], s[4])]            # 3v6, 4v5

def _campeones_semis(s, gan):
    return [('C-SF1', s[0], gan['C-CF2']), ('C-SF2', s[1], gan['C-CF1'])]

def _campeones_final(gan, perd):
    return [('C-FINAL', gan['C-SF1'], gan['C-SF2']),
            ('C-3ER',   perd['C-SF1'], perd['C-SF2'])]

def _sotano_repechaje(s):
    return [('S-REP', s[11], s[12])]                                 # 12v13

def _sotano_cuartos(s, perd):
    rep = perd['S-REP']                                              # cae el que pierde el repechaje
    return [('S-CF1', s[8], rep), ('S-CF2', s[9], s[10])]            # 9 vs P(rep), 10v11

def _sotano_semis(s, perd):
    return [('S-SF1', s[6], perd['S-CF2']), ('S-SF2', s[7], perd['S-CF1'])]

def _sotano_final(perd):
    return [('S-FINAL', perd['S-SF1'], perd['S-SF2'])]


# Qué ronda se juega en cada jornada de playoff
PLAN = {
    7:  ('campeones_cuartos', 'sotano_repechaje'),
    8:  ('campeones_semis',   'sotano_cuartos'),
    9:  ('campeones_final',   'sotano_semis'),
    10: ('sotano_final',),
}


def correr_playoffs(seeds: list[str], puntos_por_jornada: dict[int, dict[str, int]]) -> dict:
    """
    Resuelve ambas llaves dado el puntaje de playoff por jornada.

    `puntos_por_jornada`: {7: {nombre: pts}, 8: {...}, 9: {...}, 10: {...}}.
    Devuelve dict con cruces resueltos y los resultados clave.
    """
    gan: dict[str, str] = {}
    perd: dict[str, str] = {}
    cruces: dict[str, tuple] = {}

    def resolver(lista, jornada):
        pts = puntos_por_jornada.get(jornada, {})
        for cid, a, b in lista:
            g, p = _h2h(a, b, pts, seeds)
            gan[cid], perd[cid] = g, p
            cruces[cid] = (a, b, g, p)

    resolver(_campeones_cuartos(seeds), 7)
    resolver(_sotano_repechaje(seeds), 7)
    resolver(_campeones_semis(seeds, gan), 8)
    resolver(_sotano_cuartos(seeds, perd), 8)
    resolver(_campeones_final(gan, perd), 9)
    resolver(_sotano_semis(seeds, perd), 9)
    resolver(_sotano_final(perd), 10)

    return {
        'cruces': cruces,
        'campeon':    gan.get('C-FINAL'),
        'subcampeon': perd.get('C-FINAL'),
        'tercero':    gan.get('C-3ER'),
        'peor':       perd.get('S-FINAL'),   # pierde la final del sótano
        'salvado':    gan.get('S-FINAL'),    # penúltimo (se salva en la final)
    }


if __name__ == '__main__':
    from data.loader import cargar_participantes
    from data.historial_io import cargar_historial_resultados
    tabla = calcular_tabla_general(cargar_participantes(), cargar_historial_resultados())
    seeds = sembrar(tabla)
    clas = clasificacion(seeds)
    print('🏆 Campeones (1-6):', clas['campeones'])
    print('💩 Sótano   (7-13):', clas['sotano'])
