"""
Resumen / premios de una jornada (para compartir en WhatsApp / PDF).

Incluye:
  - Podio Top 1/2/3 (maneja empates: varios por escalón).
  - "Mejor de la jornada": acertó X de N partidos.
  - 🎯 Francotirador: acertó un partido que nadie más.
  - 📈 Comeback: quien más subió en la tabla (desde la J2).
  - 💀 Peores de la jornada: "No le aciertan ni en las fáciles".

Usa <img> a archivos (output/caric/), igual que la hoja de predicciones, para
que el PDF se vea bien en iOS.

Uso:
    py reports/resumen_jornada.py 1        # lee CSV + resultados_reales.json reales
    py reports/resumen_jornada.py 1 sim    # datos simulados (prueba)
"""
import os
import sys
import webbrowser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from evaluator.pipeline import correr_jornada
from quiniela.standings import calcular_tabla_general
from reports.predicciones_jornada import _preparar_srcs, OUTPUT_DIR
from reports.generar_reporte import JORNADA_META

_CSS = """
  :root{
    --bg:#0b1020; --card:#141c2e; --card2:#1a2440; --border:rgba(255,255,255,.08);
    --cyan:#00d4ff; --verde:#2ed573; --rojo:#ff4757; --dorado:#ffd700;
    --txt:#e6ecf7; --txt2:#8d99af; --gris:#5a6a80;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:-apple-system,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--txt);}
  .hdr{background:linear-gradient(108deg,#00d8ec 0%,#1248c8 38%,#7218a8 66%,#3a0068 100%);padding:22px 24px;color:#fff;}
  .hdr-eyebrow{font-size:.66rem;font-weight:700;letter-spacing:3px;opacity:.85;text-transform:uppercase;}
  .hdr-title{font-size:1.9rem;font-weight:900;letter-spacing:-.5px;line-height:1.05;margin-top:4px;}
  .hdr-sub{font-size:.84rem;opacity:.85;margin-top:5px;}
  .wrap{max-width:720px;margin:0 auto;padding:18px 14px 28px;}
  .card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:14px;
        page-break-inside:avoid;break-inside:avoid;}
  .card-title{font-size:.72rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:var(--cyan);
              margin-bottom:14px;display:flex;align-items:center;gap:8px;}

  /* ── Podio ── */
  .podio{display:flex;align-items:flex-end;justify-content:center;gap:10px;margin-top:6px;}
  .step{flex:1 1 0;max-width:200px;text-align:center;}
  .step-avs{display:flex;justify-content:center;flex-wrap:wrap;gap:5px;margin-bottom:8px;}
  .podio-av{border-radius:50%;object-fit:cover;object-position:center;border:3px solid var(--border);background:#26314d;}
  .podio-ph{display:flex;align-items:center;justify-content:center;color:var(--cyan);font-weight:800;}
  .step-1 .podio-av{width:70px;height:70px;border-color:var(--dorado);}
  .step-2 .podio-av{width:56px;height:56px;border-color:#c0c0c0;}
  .step-3 .podio-av{width:56px;height:56px;border-color:#cd7f32;}
  .step-nm{font-weight:800;font-size:.82rem;line-height:1.25;margin-bottom:2px;}
  .step-pts{font-weight:900;font-size:.9rem;color:var(--dorado);margin-bottom:6px;}
  .bar{border-radius:12px 12px 0 0;display:flex;align-items:flex-start;justify-content:center;
       font-size:2rem;font-weight:900;color:rgba(0,0,0,.55);padding-top:8px;}
  .bar-1{background:linear-gradient(180deg,#ffe25a,#e3a900);height:104px;}
  .bar-2{background:linear-gradient(180deg,#dfe3e8,#9aa0a8);height:78px;}
  .bar-3{background:linear-gradient(180deg,#e0975a,#a5612a);height:58px;}

  /* ── Premios ── */
  .premio{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid var(--border);
          border-radius:12px;margin-bottom:10px;background:var(--bg);}
  .premio:last-child{margin-bottom:0;}
  .premio-ic{font-size:1.7rem;flex-shrink:0;width:34px;text-align:center;}
  .premio-av{width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid rgba(0,212,255,.5);flex-shrink:0;background:#26314d;}
  .premio-av.ph{display:flex;align-items:center;justify-content:center;color:var(--cyan);font-weight:800;font-size:.7rem;}
  .premio-body{flex:1;min-width:0;}
  .premio-tit{font-size:.7rem;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:var(--cyan);}
  .premio-txt{font-size:.9rem;font-weight:700;color:var(--txt);margin-top:2px;}
  .premio-txt b{color:var(--dorado);}
  .premio.malo{border-color:rgba(255,71,87,.4);}
  .premio.malo .premio-tit{color:var(--rojo);}
  .foot{text-align:center;color:var(--gris);font-size:.72rem;padding:10px;}

  @media print{ @page{size:A4;margin:0;} *{-webkit-print-color-adjust:exact;print-color-adjust:exact;} }
"""


def _avatar(nombre, srcs, cls):
    src = srcs.get(nombre)
    if src:
        return f'<img class="{cls}" src="{src}" alt="">'
    ini = ''.join(w[0] for w in nombre.split()[:2]).upper()
    return f'<div class="{cls} ph">{ini}</div>'


def _grupos_por_total(resultados_j):
    """{total: [nombres]} y lista de totales descendente."""
    por_total = {}
    for r in resultados_j:
        por_total.setdefault(r.total, []).append(r.participante)
    for t in por_total:
        por_total[t].sort(key=str.lower)
    return por_total, sorted(por_total, reverse=True)


def _francotiradores(predicciones, resultados_reales, partidos_por_num):
    """[(nombre, partido)] de quienes acertaron un partido que nadie más acertó."""
    preds = {}
    for pr in predicciones:
        preds.setdefault(pr.partido_numero, {})[pr.participante] = pr.prediccion
    out = []
    for num, real in resultados_reales.items():
        correctos = [n for n, p in preds.get(num, {}).items() if p == real]
        if len(correctos) == 1:
            out.append((correctos[0], partidos_por_num.get(num)))
    return out


def _comeback(participantes, historial_previo, tabla_despues, jornada):
    """(nombres, lugares_subidos) del que más subió; None si no hay jornada previa."""
    hist_sin = [r for r in historial_previo if r.jornada != jornada]
    if not {r.jornada for r in hist_sin}:
        return None
    tabla_antes = calcular_tabla_general(participantes, hist_sin)
    pos_antes = {s['nombre']: i for i, s in enumerate(tabla_antes, 1)}
    pos_desp = {s['nombre']: i for i, s in enumerate(tabla_despues, 1)}
    subidas = {n: pos_antes.get(n, 0) - pos_desp[n] for n in pos_desp}
    mejor = max(subidas.values(), default=0)
    if mejor <= 0:
        return None
    nombres = sorted([n for n, v in subidas.items() if v == mejor], key=str.lower)
    return nombres, mejor


def _podio_html(por_total, totales, srcs):
    def step(idx, clase, medalla):
        if idx >= len(totales):
            return ''
        total = totales[idx]
        nombres = por_total[total]
        avs = ''.join(_avatar(n, srcs, 'podio-av') for n in nombres)
        noms = '<br>'.join(nombres)
        return f"""
      <div class="step step-{clase}">
        <div class="step-avs">{avs}</div>
        <div class="step-nm">{noms}</div>
        <div class="step-pts">{total} pts</div>
        <div class="bar bar-{clase}">{medalla}</div>
      </div>"""
    # Orden visual: 2º, 1º, 3º
    return f"""
  <div class="podio">
    {step(1, '2', '2')}
    {step(0, '1', '1')}
    {step(2, '3', '3')}
  </div>"""


def _premio(ic, titulo, texto, nombre=None, srcs=None, malo=False):
    av = _avatar(nombre, srcs, 'premio-av') if (nombre and srcs is not None) else f'<div class="premio-ic">{ic}</div>'
    return f"""
  <div class="premio{' malo' if malo else ''}">
    {av}
    <div class="premio-body">
      <div class="premio-tit">{ic} {titulo}</div>
      <div class="premio-txt">{texto}</div>
    </div>
  </div>"""


def construir_html(jornada, estado, srcs):
    resultados_j = estado['resultados_j']
    predicciones = estado['predicciones']
    resultados_reales = estado['resultados_reales']
    partidos = estado['partidos_jornada']
    tabla_despues = estado['tabla']
    historial_previo = estado['historial_previo']

    partidos_por_num = {p.numero: p for p in partidos}
    n_jugados = len(resultados_reales)
    n_total = len(partidos)
    por_jugador = {r.participante: r for r in resultados_j}

    por_total, totales = _grupos_por_total(resultados_j)

    # ── Mejor de la jornada (líder) ──
    mejores = por_total[totales[0]] if totales else []
    def linea_mejor(n):
        r = por_jugador[n]
        extra = ''
        bonus = r.bonus_rojas + r.bonus_penales
        if bonus:
            extra = f' + {bonus} de bonus'
        return f'<b>{n}</b> — acertó <b>{r.puntos_partidos} de {n_jugados}</b> partidos{extra}'
    mejor_txt = '<br>'.join(linea_mejor(n) for n in mejores)

    # ── Francotirador ──
    snipers = _francotiradores(predicciones, resultados_reales, partidos_por_num)
    if snipers:
        partes = []
        for nombre, partido in snipers:
            vs = f'{partido.local} vs {partido.visitante}' if partido else 'un partido'
            partes.append(f'<b>{nombre}</b> fue el único que le atinó a {vs}')
        franco_txt = '<br>'.join(partes)
    else:
        franco_txt = 'Esta jornada nadie tuvo un acierto solitario.'

    # ── Comeback ──
    cb = _comeback(estado['participantes'], historial_previo, tabla_despues, jornada)

    # ── Peores ──
    peores = por_total[totales[-1]] if totales else []
    peor_pts = totales[-1] if totales else 0
    peor_txt = f'<b>{", ".join(peores)}</b> — apenas <b>{peor_pts} pts</b> esta jornada 💀'

    premios = _premio('🔥', 'Mejor de la jornada', mejor_txt)
    premios += _premio('🎯', 'Francotirador', franco_txt)
    if cb:
        nombres, lugares = cb
        cb_txt = f'<b>{", ".join(nombres)}</b> subió <b>{lugares}</b> lugar{"es" if lugares != 1 else ""} en la tabla 📈'
        premios += _premio('📈', 'Comeback de la jornada', cb_txt)
    premios += _premio('💀', 'No le aciertan ni en las fáciles', peor_txt, malo=True)

    fechas = JORNADA_META.get(jornada, {}).get('fechas', '')
    parcial = f' · parcial ({n_jugados}/{n_total} partidos)' if n_jugados < n_total else ''

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resumen J{jornada} — Mundial 2026</title><style>{_CSS}</style></head>
<body>
<header class="hdr">
  <div class="hdr-eyebrow">⚽ Quiniela Mundial 2026</div>
  <div class="hdr-title">Resumen · Jornada {jornada}</div>
  <div class="hdr-sub">{fechas}{parcial}</div>
</header>
<div class="wrap">
  <div class="card">
    <div class="card-title">🏆 Podio de la jornada</div>
    {_podio_html(por_total, totales, srcs)}
  </div>
  <div class="card">
    <div class="card-title">Premios</div>
    {premios}
  </div>
</div>
<div class="foot">Quiniela Mundial 2026 — Resumen Jornada {jornada}</div>
</body></html>"""


def generar(jornada, sim=False):
    if sim:
        from tests.simular_jornada import datos_simulados_jornada
        s = datos_simulados_jornada(jornada)
        estado = correr_jornada(
            jornada, persistir_historial=False,
            predicciones_override=(s['predicciones'], s['bonus_preds']),
            resultados_override=(s['resultados_reales'], s['total_rojas'], s['total_penales']),
            historial_override=[],
        )
    else:
        estado = correr_jornada(jornada, persistir_historial=False)

    nombres = {r.participante for r in estado['resultados_j']}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    srcs = _preparar_srcs(nombres, OUTPUT_DIR)

    html = construir_html(jornada, estado, srcs)
    ruta = os.path.join(OUTPUT_DIR, f'resumen_jornada_{jornada}.html')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    return ruta


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

    jornada = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    usar_sim = len(sys.argv) > 2 and sys.argv[2] == 'sim'
    ruta = generar(jornada, sim=usar_sim)
    print(f'Resumen generado: {ruta}')
    print('Para PDF: ábrelo y Ctrl+P → "Guardar como PDF" (activa Gráficos de fondo).')
    webbrowser.open(f'file:///{ruta.replace(os.sep, "/")}')
