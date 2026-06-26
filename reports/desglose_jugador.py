"""
Desglose de puntos de uno o varios jugadores (para auditar cómo llegan a su total).

Para cada jugador, muestra jornada por jornada todas sus predicciones, el
resultado real de cada partido, si acertó (+1), y los bonos de rojas/penales,
con el subtotal de cada jornada y el total.

Uso:
    py reports/desglose_jugador.py George Row Jime
    py reports/desglose_jugador.py            # default: George, Row, Jime
"""
import os
import sys
import webbrowser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.loader import cargar_calendario
from data.respuestas_loader import cargar_respuestas
from evaluator.pipeline import cargar_resultados_reales, ruta_respuestas_csv
from quiniela.models import Resultado

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
JORNADAS = range(1, 7)

_CSS = """
  :root{--bg:#0b1020;--card:#141c2e;--bg2:#0f1523;--border:rgba(255,255,255,.08);
    --cyan:#00d4ff;--verde:#2ed573;--rojo:#ff4757;--dorado:#ffd700;--txt:#e6ecf7;--txt2:#8d99af;--gris:#5a6a80;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:-apple-system,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--txt);}
  .hdr{background:linear-gradient(108deg,#00d8ec 0%,#1248c8 38%,#7218a8 66%,#3a0068 100%);padding:20px 22px;color:#fff;}
  .hdr-title{font-size:1.7rem;font-weight:900;}
  .hdr-sub{font-size:.82rem;opacity:.85;margin-top:4px;}
  .wrap{max-width:760px;margin:0 auto;padding:16px 14px 28px;}
  .jug{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px;margin-bottom:16px;
       page-break-inside:avoid;}
  .jug-h{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:6px;
         padding-bottom:10px;border-bottom:1px solid var(--border);}
  .jug-nm{font-size:1.3rem;font-weight:900;color:var(--cyan);}
  .jug-tot{font-size:1.1rem;font-weight:900;color:var(--dorado);}
  .jor{margin-top:12px;}
  .jor-h{font-size:.7rem;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--cyan);
         display:flex;justify-content:space-between;margin-bottom:6px;}
  .jor-sub{color:var(--dorado);}
  table{width:100%;border-collapse:collapse;font-size:.78rem;}
  td,th{padding:4px 6px;border-bottom:1px solid var(--border);text-align:left;}
  th{color:var(--txt2);font-size:.64rem;text-transform:uppercase;letter-spacing:.5px;font-weight:700;}
  .num{color:var(--gris);font-weight:700;width:26px;}
  .pred{color:var(--txt2);}
  .real{font-weight:700;}
  .pts{text-align:center;width:34px;font-weight:800;}
  tr.ok td{background:rgba(46,213,115,.07);}
  tr.ok .real{color:var(--verde);}
  .pts.win{color:var(--verde);} .pts.zero{color:var(--gris);} .pts.na{color:var(--gris);}
  .bonus{margin-top:6px;font-size:.76rem;color:var(--txt2);}
  .bonus b{color:var(--txt);}
  .bonus .ok{color:var(--verde);font-weight:800;} .bonus .no{color:var(--gris);}
  .foot{text-align:center;color:var(--gris);font-size:.72rem;padding:10px;}
  @media print{@page{size:A4;margin:0;}*{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
"""


def _etiqueta(res, partido):
    if res is None:
        return '—'
    if res == Resultado.LOCAL:
        return partido.local
    if res == Resultado.VISITANTE:
        return partido.visitante
    return 'Empate'


def _cargar_datos():
    """Pre-carga, por jornada: partidos, predicciones, bonos y resultados reales."""
    calendario = cargar_calendario()
    datos = {}
    for j in JORNADAS:
        partidos = [p for p in calendario if p.jornada == j]
        csv_path = ruta_respuestas_csv(j)
        if os.path.exists(csv_path):
            preds, bonus = cargar_respuestas(j, csv_path)
        else:
            preds, bonus = [], []
        resultados, rojas, penales = cargar_resultados_reales(j)
        datos[j] = {
            'partidos': partidos,
            'preds': preds,
            'bonus': bonus,
            'resultados': resultados,
            'rojas': rojas,
            'penales': penales,
        }
    return datos


def _seccion_jugador(nombre, datos):
    total = 0
    jornadas_html = ''
    for j in JORNADAS:
        d = datos[j]
        pred_map = {p.partido_numero: p.prediccion for p in d['preds'] if p.participante == nombre}
        if not pred_map:
            continue  # no participó esa jornada
        bonus = next((b for b in d['bonus'] if b.participante == nombre), None)

        sub = 0
        filas = ''
        for p in d['partidos']:
            pred = pred_map.get(p.numero)
            real = d['resultados'].get(p.numero)
            if real is not None and pred == real:
                pts, cls, rowcls = 1, 'win', 'ok'
            elif real is not None:
                pts, cls, rowcls = 0, 'zero', ''
            else:
                pts, cls, rowcls = '—', 'na', ''
            if isinstance(pts, int):
                sub += pts
            filas += (f'<tr class="{rowcls}"><td class="num">#{p.numero}</td>'
                      f'<td>{p.local} vs {p.visitante}</td>'
                      f'<td class="pred">{_etiqueta(pred, p)}</td>'
                      f'<td class="real">{_etiqueta(real, p)}</td>'
                      f'<td class="pts {cls}">{pts}</td></tr>')

        # bonos
        bonus_html = ''
        if bonus is not None:
            def _b(label, pred_v, real_v, pts):
                if real_v is None:
                    estado = '<span class="no">pendiente</span>'
                elif pred_v == real_v:
                    estado = f'<span class="ok">✓ +{pts}</span>'
                    return f'{label}: <b>{pred_v}</b> (real {real_v}) {estado}', pts
                else:
                    estado = f'<span class="no">✗ (real {real_v})</span>'
                return f'{label}: <b>{pred_v}</b> {estado}', 0
            txt_r, p_r = _b('🟥 Rojas', bonus.total_rojas, d['rojas'], 2)
            txt_p, p_p = _b('🎯 Penales', bonus.total_penales, d['penales'], 2)
            sub += p_r + p_p
            bonus_html = f'<div class="bonus">{txt_r} &nbsp;·&nbsp; {txt_p}</div>'

        total += sub
        jornadas_html += f"""
    <div class="jor">
      <div class="jor-h"><span>Jornada {j}</span><span class="jor-sub">+{sub} pts</span></div>
      <table>
        <thead><tr><th></th><th>Partido</th><th>Predijo</th><th>Real</th><th>Pts</th></tr></thead>
        <tbody>{filas}</tbody>
      </table>
      {bonus_html}
    </div>"""

    return f"""
  <div class="jug">
    <div class="jug-h"><span class="jug-nm">{nombre}</span><span class="jug-tot">{total} pts</span></div>
    {jornadas_html}
  </div>"""


def generar(nombres):
    datos = _cargar_datos()
    secciones = ''.join(_seccion_jugador(n, datos) for n in nombres)
    html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Desglose — Quiniela Mundial 2026</title><style>{_CSS}</style></head>
<body>
<header class="hdr">
  <div class="hdr-title">Desglose de puntos</div>
  <div class="hdr-sub">{', '.join(nombres)} · predicciones y resultados, jornada por jornada</div>
</header>
<div class="wrap">{secciones}</div>
<div class="foot">Quiniela Mundial 2026 — desglose</div>
</body></html>"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta = os.path.join(OUTPUT_DIR, 'desglose.html')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    return ruta


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    nombres = sys.argv[1:] or ['George', 'Row', 'Jime']
    ruta = generar(nombres)
    print(f'Desglose generado: {ruta}')
    print('Para PDF: ábrelo y Ctrl+P → "Guardar como PDF" (activa Gráficos de fondo).')
    webbrowser.open(f'file:///{ruta.replace(os.sep, "/")}')
