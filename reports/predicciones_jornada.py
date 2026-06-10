"""
Hoja visual de predicciones de una jornada (para compartir en WhatsApp / PDF).

Para cada partido muestra tres columnas — gana local (1), empate (X), gana
visitante (2) — y en cada una las caricaturas de quienes eligieron esa opción.

Uso:
    py reports/predicciones_jornada.py 1        # lee data/respuestas/jornada_1.csv
    py reports/predicciones_jornada.py 1 sim    # datos simulados (prueba)

Genera reports/output/predicciones_jornada_N.html y lo abre en el navegador.
Para el PDF: en el navegador Ctrl+P → "Guardar como PDF" (activa
"Gráficos de fondo"). O con Edge headless (ver README de uso al final).
"""
import os
import re
import sys
import webbrowser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.loader import cargar_calendario
from data.respuestas_loader import cargar_respuestas
from quiniela.models import Resultado
from reports.generar_reporte import _cargar_imagenes, _imagen_para, JORNADA_META

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

_CSS = """
  :root{
    --bg:#0b1020; --card:#141c2e; --card2:#1a2440; --border:rgba(255,255,255,.08);
    --cyan:#00d4ff; --verde:#2ed573; --rojo:#ff4757; --dorado:#ffd700;
    --txt:#e6ecf7; --txt2:#8d99af; --gris:#5a6a80;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:-apple-system,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--txt);}
  .hdr{
    background:linear-gradient(108deg,#00d8ec 0%,#1248c8 38%,#7218a8 66%,#3a0068 100%);
    padding:22px 24px;color:#fff;
  }
  .hdr-eyebrow{font-size:.66rem;font-weight:700;letter-spacing:3px;opacity:.85;text-transform:uppercase;}
  .hdr-title{font-size:1.9rem;font-weight:900;letter-spacing:-.5px;line-height:1.05;margin-top:4px;}
  .hdr-sub{font-size:.84rem;opacity:.8;margin-top:5px;}
  .wrap{max-width:780px;margin:0 auto;padding:16px 14px 28px;}

  .match{
    background:var(--card);border:1px solid var(--border);border-radius:12px;
    padding:12px 12px 14px;margin-bottom:12px;page-break-inside:avoid;break-inside:avoid;
  }
  .match-head{font-size:.95rem;font-weight:800;color:var(--txt);margin-bottom:10px;display:flex;align-items:center;gap:8px;}
  .mnum{font-size:.66rem;font-weight:800;color:#001018;background:var(--cyan);border-radius:6px;padding:2px 7px;}
  .match-head i{color:var(--gris);font-style:normal;font-weight:600;font-size:.82rem;}

  .cols{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;}
  .col{background:var(--bg);border:1px solid var(--border);border-radius:9px;padding:8px;min-height:64px;}
  .col-h{font-size:.66rem;font-weight:800;text-transform:uppercase;letter-spacing:.5px;
         padding-bottom:7px;margin-bottom:7px;border-bottom:1px solid var(--border);text-align:center;}
  .col-h b{font-size:.78rem;}
  .col-1 .col-h{color:var(--verde);} .col-1{border-left:3px solid var(--verde);}
  .col-x .col-h{color:var(--cyan);}  .col-x{border-left:3px solid var(--cyan);}
  .col-2 .col-h{color:var(--dorado);}.col-2{border-left:3px solid var(--dorado);}

  .chips{display:flex;flex-wrap:wrap;gap:6px;}
  .chip{display:flex;align-items:center;gap:5px;background:var(--card2);
        border:1px solid var(--border);border-radius:20px;padding:2px 9px 2px 2px;}
  .chip-av{width:24px;height:24px;border-radius:50%;border:1.5px solid rgba(0,212,255,.5);
           background-size:cover;background-position:center top;flex-shrink:0;}
  .chip-ph{display:flex;align-items:center;justify-content:center;background:#26314d;
           color:var(--cyan);font-size:.55rem;font-weight:800;}
  .chip-name{font-size:.72rem;font-weight:700;color:var(--txt);white-space:nowrap;}
  .empty{color:var(--gris);font-size:.8rem;text-align:center;padding:6px 0;}

  .foot{text-align:center;color:var(--gris);font-size:.72rem;padding:10px;}

  @media print{
    @page{size:A4;margin:10mm;}
    body{background:#fff;}
    .hdr{-webkit-print-color-adjust:exact;print-color-adjust:exact;}
    .match{background:#fff;border:1px solid #ccc;}
    .col{background:#f6f8fb;}
    .chip{background:#eef2f8;}
    .chip-name,.match-head{color:#111;}
    *{-webkit-print-color-adjust:exact;print-color-adjust:exact;}
  }
"""


def _slug(nombre):
    return re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')


def _chip(nombre, imagenes):
    """Chip de un participante. Usa clase .av-<slug> (la imagen se embebe una
    sola vez en el <style>) o iniciales si no tiene caricatura."""
    if _imagen_para(nombre, imagenes):
        av = f'<span class="chip-av av-{_slug(nombre)}"></span>'
    else:
        ini = ''.join(w[0] for w in nombre.split()[:2]).upper()
        av = f'<div class="chip-av chip-ph">{ini}</div>'
    return f'<div class="chip">{av}<span class="chip-name">{nombre}</span></div>'


def _estilos_avatares(predicciones, imagenes):
    """Una regla CSS por persona (imagen embebida 1 sola vez)."""
    nombres = {p.participante for p in predicciones}
    reglas = ''
    for nombre in sorted(nombres):
        url = _imagen_para(nombre, imagenes)
        if url:
            reglas += f'.av-{_slug(nombre)}{{background-image:url({url});}}'
    return reglas


def _columna(titulo, clase, nombres, imagenes):
    if nombres:
        ordenados = sorted(nombres, key=str.lower)
        chips = '<div class="chips">' + ''.join(_chip(n, imagenes) for n in ordenados) + '</div>'
    else:
        chips = '<div class="empty">—</div>'
    return f'<div class="col {clase}"><div class="col-h">{titulo}</div>{chips}</div>'


def _agrupar(predicciones):
    """{num_partido: {Resultado: [nombres en orden]}}."""
    por_partido = {}
    for p in predicciones:
        d = por_partido.setdefault(p.partido_numero, {r: [] for r in Resultado})
        if p.participante not in d[p.prediccion]:
            d[p.prediccion].append(p.participante)
    return por_partido


def construir_html(jornada, partidos, predicciones, imagenes):
    por_partido = _agrupar(predicciones)
    n_participantes = len({p.participante for p in predicciones})

    bloques = ''
    for partido in partidos:
        grupos = por_partido.get(partido.numero, {r: [] for r in Resultado})
        cols = (
            _columna(f'Gana {partido.local} <b>(1)</b>', 'col-1', grupos[Resultado.LOCAL], imagenes)
            + _columna('Empate <b>(X)</b>', 'col-x', grupos[Resultado.EMPATE], imagenes)
            + _columna(f'Gana {partido.visitante} <b>(2)</b>', 'col-2', grupos[Resultado.VISITANTE], imagenes)
        )
        bloques += f"""
    <div class="match">
      <div class="match-head"><span class="mnum">#{partido.numero}</span>
        {partido.local} <i>vs</i> {partido.visitante}</div>
      <div class="cols">{cols}</div>
    </div>"""

    fechas = JORNADA_META.get(jornada, {}).get('fechas', '')
    estilos_av = _estilos_avatares(predicciones, imagenes)
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Predicciones J{jornada} — Mundial 2026</title><style>{_CSS}{estilos_av}</style></head>
<body>
<header class="hdr">
  <div class="hdr-eyebrow">⚽ Quiniela Mundial 2026</div>
  <div class="hdr-title">Predicciones · Jornada {jornada}</div>
  <div class="hdr-sub">Quién eligió qué · {n_participantes} participantes{(' · ' + fechas) if fechas else ''}</div>
</header>
<div class="wrap">{bloques}
</div>
<div class="foot">Quiniela Mundial 2026 — Jornada {jornada}</div>
</body></html>"""


def generar(jornada, predicciones_override=None):
    partidos = [p for p in cargar_calendario() if p.jornada == jornada]
    if not partidos:
        raise SystemExit(f"No hay partidos para la jornada {jornada} en el calendario.")

    if predicciones_override is not None:
        predicciones = predicciones_override
    else:
        csv_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'respuestas', f'jornada_{jornada}.csv'
        )
        if not os.path.exists(csv_path):
            raise SystemExit(
                f"No encuentro {csv_path}.\n"
                f"Exporta las respuestas del form de la J{jornada} a CSV y guárdalas ahí "
                f"(o corre con 'sim' para una prueba)."
            )
        predicciones, _ = cargar_respuestas(jornada, csv_path)

    imagenes = _cargar_imagenes()
    html = construir_html(jornada, partidos, predicciones, imagenes)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta = os.path.join(OUTPUT_DIR, f'predicciones_jornada_{jornada}.html')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    return ruta


if __name__ == '__main__':
    jornada = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    usar_sim = len(sys.argv) > 2 and sys.argv[2] == 'sim'

    override = None
    if usar_sim:
        from tests.simular_jornada import datos_simulados_jornada
        sim = datos_simulados_jornada(jornada)
        override = sim['predicciones']

    ruta = generar(jornada, predicciones_override=override)
    print(f'Hoja de predicciones generada: {ruta}')
    print('Para PDF: ábrela y Ctrl+P → "Guardar como PDF" (activa Gráficos de fondo).')
    webbrowser.open(f'file:///{ruta.replace(os.sep, "/")}')
