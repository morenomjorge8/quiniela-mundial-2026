"""Tests del scoring de playoffs (marcador exacto / resultado / primer gol)."""
from quiniela.models import PrediccionPlayoff, ResultadoPlayoff, BonusPrediccion
from quiniela.playoff_scorer import puntos_partido, puntos_ronda


def _pred(gl, gv, pg, nombre='Ana', num=1):
    return PrediccionPlayoff(participante=nombre, partido_numero=num,
                             goles_local=gl, goles_visitante=gv, primer_gol=pg)


def _real(gl, gv, pg=None, num=1):
    return ResultadoPlayoff(partido_numero=num, goles_local=gl, goles_visitante=gv, primer_gol=pg)


def test_marcador_exacto_da_3():
    # exacto pero primer gol equivocado → 3
    assert puntos_partido(_pred(2, 1, 'V'), _real(2, 1, 'L')) == 3


def test_marcador_exacto_con_primer_gol_da_4():
    assert puntos_partido(_pred(2, 1, 'L'), _real(2, 1, 'L')) == 4


def test_solo_resultado_da_2():
    # acierta gana local (1) pero no el marcador
    assert puntos_partido(_pred(3, 0, 'V'), _real(2, 1, 'L')) == 2


def test_resultado_mas_primer_gol_da_3():
    assert puntos_partido(_pred(3, 0, 'L'), _real(2, 1, 'L')) == 3


def test_resultado_equivocado_da_0_aunque_primer_gol_mal():
    # predijo gana local, fue gana visitante; primer gol tambien mal
    assert puntos_partido(_pred(2, 1, 'L'), _real(0, 2, 'V')) == 0


def test_primer_gol_solo_sin_resultado():
    # resultado mal (predijo local, fue visitante) pero acierta primer gol
    assert puntos_partido(_pred(2, 1, 'L'), _real(0, 1, 'L')) == 1


def test_cerodos_nadie_gana_primer_gol():
    # 0-0 real: primer_gol None → el +1 no aplica aunque el exacto sí
    assert puntos_partido(_pred(0, 0, 'L'), _real(0, 0, None)) == 3  # exacto 0-0
    assert puntos_partido(_pred(1, 1, 'V'), _real(0, 0, None)) == 2  # empate, no exacto


def test_empate_exacto():
    assert puntos_partido(_pred(1, 1, 'L'), _real(1, 1, 'L')) == 4


def test_puntos_ronda_suma_por_participante():
    preds = [
        _pred(2, 1, 'L', 'Ana', 1),   # exacto + primer gol = 4
        _pred(1, 0, 'L', 'Ana', 2),   # resultado (1) sin exacto +? real 2-0 L primer L → 2+1=3
        _pred(0, 0, 'L', 'Beto', 1),  # real 2-1: resultado mal (X vs 1)=0, pero primer gol L=L → +1
    ]
    reales = {
        1: _real(2, 1, 'L', 1),
        2: _real(2, 0, 'L', 2),
    }
    pts = puntos_ronda(preds, reales, ['Ana', 'Beto', 'Cyn'])
    assert pts['Ana'] == 4 + 3
    assert pts['Beto'] == 1   # solo el +1 del primer gol
    assert pts['Cyn'] == 0    # sin predicciones


def test_puntos_ronda_con_bonus_rojas_y_penales():
    preds = [_pred(2, 1, 'L', 'Ana', 1)]   # exacto + primer gol = 4
    reales = {1: _real(2, 1, 'L', 1)}
    bonus = [BonusPrediccion('Ana', 7, total_rojas=3, total_penales=1),
             BonusPrediccion('Beto', 7, total_rojas=2, total_penales=2)]
    pts = puntos_ronda(preds, reales, ['Ana', 'Beto'], bonus,
                       total_rojas_real=3, total_penales_real=2)
    # Ana: 4 (partido) + 2 (rojas 3=3) + 0 (penales 1≠2) = 6
    assert pts['Ana'] == 6
    # Beto: 0 (partido) + 0 (rojas 2≠3) + 2 (penales 2=2) = 2
    assert pts['Beto'] == 2


def test_puntos_ronda_bonus_pendiente_si_totales_none():
    bonus = [BonusPrediccion('Ana', 7, total_rojas=0, total_penales=0)]
    pts = puntos_ronda([], {}, ['Ana'], bonus,
                       total_rojas_real=None, total_penales_real=None)
    assert pts['Ana'] == 0  # sin totales reales, el bonus queda pendiente
