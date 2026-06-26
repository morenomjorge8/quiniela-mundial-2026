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
        # J7 — cuartos campeones (3v6, 4v5) y cuartos sótano (7v12, 8v11, 9v10)
        7:  {'S3': 10, 'S6': 5, 'S4': 10, 'S5': 5,
             'S7': 10, 'S12': 5, 'S8': 10, 'S11': 5, 'S9': 10, 'S10': 5},
        # J8 — semis campeones y semis sótano (13 vs P(7v12)=S12; P(8v11)=S11 vs P(9v10)=S10)
        8:  {'S1': 10, 'S4': 5, 'S2': 10, 'S3': 5,
             'S13': 5, 'S12': 10, 'S11': 10, 'S10': 5},
        # J9 — final+3er campeones y final sótano (P(SF1)=S13 vs P(SF2)=S10)
        9:  {'S1': 10, 'S2': 5, 'S4': 10, 'S3': 5,
             'S13': 5, 'S10': 10},
    }
    r = correr_playoffs(SEEDS, pts)

    # Campeones: S1 le gana a S2 en la final; tercero S4
    assert r['campeon'] == 'S1'
    assert r['subcampeon'] == 'S2'
    assert r['tercero'] == 'S4'

    # Sótano: S13 (peor seed) va perdiendo todo y cae hasta el fondo
    assert r['peor'] == 'S13'
    assert r['salvado'] == 'S10'  # le gana a S13 la final → se salva (12°)


def test_sotano_bye_13_entra_en_semis():
    # 13° no aparece en cuartos del sótano; sí en semis
    pts = {7: {'S7': 9, 'S12': 1, 'S8': 9, 'S11': 1, 'S9': 9, 'S10': 1}}
    r = correr_playoffs(SEEDS, pts)
    cuartos_ids = [c for c in r['cruces'] if c.startswith('S-CF')]
    jugadores = {p for cid in cuartos_ids for p in r['cruces'][cid][:2]}
    assert 'S13' not in jugadores
    assert 'S13' in r['cruces']['S-SF1'][:2]


def test_byes_campeones_entran_en_semis():
    # S1 y S2 (bye) no aparecen en cuartos; sí en semis
    pts = {7: {'S3': 9, 'S6': 1, 'S4': 9, 'S5': 1, 'S12': 9, 'S13': 1}}
    r = correr_playoffs(SEEDS, pts)
    cuartos_ids = [c for c in r['cruces'] if c.startswith('C-CF')]
    jugadores_cuartos = {p for cid in cuartos_ids for p in r['cruces'][cid][:2]}
    assert 'S1' not in jugadores_cuartos and 'S2' not in jugadores_cuartos
    # S1 entra en C-SF1
    assert 'S1' in r['cruces']['C-SF1'][:2]
