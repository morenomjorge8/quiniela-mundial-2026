"""Tests de las llaves de playoffs (siembra, avance H2H, campeón y peor)."""
from quiniela.playoffs import sembrar, clasificacion, correr_playoffs, _h2h

SEEDS = [f'S{i}' for i in range(1, 14)]  # S1 = lugar 1 (mejor) … S13 = lugar 13 (peor)


def test_sembrar_y_clasificacion():
    tabla = [{'nombre': n} for n in SEEDS]
    seeds = sembrar(tabla)
    clas = clasificacion(seeds)
    assert clas['campeones'] == SEEDS[:6]
    assert clas['sotano'] == SEEDS[6:13]
    assert len(clas['campeones']) == 6 and len(clas['sotano']) == 7


def test_h2h_gana_mas_puntos_y_empate_por_seed():
    assert _h2h('S3', 'S6', {'S3': 8, 'S6': 5}, SEEDS) == ('S3', 'S6')
    assert _h2h('S3', 'S6', {'S3': 5, 'S6': 8}, SEEDS) == ('S6', 'S3')
    # empate → mejor sembrado (S3 está antes que S6)
    assert _h2h('S3', 'S6', {'S3': 5, 'S6': 5}, SEEDS) == ('S3', 'S6')
    # bye (uno None)
    assert _h2h('S1', None, {}, SEEDS) == ('S1', None)


def test_playoff_completo():
    pts = {
        7:  {'S3': 10, 'S6': 5, 'S4': 10, 'S5': 5, 'S12': 10, 'S13': 5},
        8:  {'S1': 10, 'S4': 5, 'S2': 10, 'S3': 5,
             'S9': 10, 'S13': 5, 'S10': 10, 'S11': 5},
        9:  {'S1': 10, 'S2': 5, 'S4': 10, 'S3': 5,
             'S7': 10, 'S11': 5, 'S8': 10, 'S13': 5},
        10: {'S11': 10, 'S13': 5},
    }
    r = correr_playoffs(SEEDS, pts)

    # Campeones: S1 le gana a S2 en la final; tercero S4
    assert r['campeon'] == 'S1'
    assert r['subcampeon'] == 'S2'
    assert r['tercero'] == 'S4'

    # Sótano: el peor seed S13 va perdiendo todo y cae hasta el fondo
    assert r['peor'] == 'S13'
    assert r['salvado'] == 'S11'  # pierde la final del sótano por puntos → se salva


def test_byes_campeones_entran_en_semis():
    # S1 y S2 (bye) no aparecen en cuartos; sí en semis
    pts = {7: {'S3': 9, 'S6': 1, 'S4': 9, 'S5': 1, 'S12': 9, 'S13': 1}}
    r = correr_playoffs(SEEDS, pts)
    cuartos_ids = [c for c in r['cruces'] if c.startswith('C-CF')]
    jugadores_cuartos = {p for cid in cuartos_ids for p in r['cruces'][cid][:2]}
    assert 'S1' not in jugadores_cuartos and 'S2' not in jugadores_cuartos
    # S1 entra en C-SF1
    assert 'S1' in r['cruces']['C-SF1'][:2]
