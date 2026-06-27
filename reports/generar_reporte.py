"""
Genera el reporte HTML de una jornada de la Quiniela Mundial 2026.

Uso:
    py reports/generar_reporte.py 1          # Jornada 1, lee CSV real de data/respuestas/
    py reports/generar_reporte.py 1 sim      # Jornada 1, con datos simulados de prueba
"""
import os
import sys
import base64
import webbrowser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from quiniela.standings import CLASIFICAN

# La web pública vive en docs/ (fuente de GitHub Pages). Cada jornada escribe
# docs/jornada_N.html y reconstruye docs/index.html (la tabla general).
OUTPUT_DIR      = os.path.join(os.path.dirname(__file__), '..', 'docs')
CARICATURAS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Caricaturas')
# Quién ya envió el form de cada jornada: { "1": ["George", ...] }. Solo nombres
# (sin predicciones); se edita a mano conforme la gente va llenando el form.
ENTREGAS_PATH   = os.path.join(os.path.dirname(__file__), '..', 'data', 'entregas.json')


def _cargar_entregas() -> dict:
    """Devuelve {jornada(str): [nombres]} de quienes ya enviaron el form."""
    import json
    if not os.path.exists(ENTREGAS_PATH):
        return {}
    with open(ENTREGAS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

JORNADA_META = {
    1: {'fechas': '11–14 junio 2026', 'form_url': 'https://docs.google.com/forms/d/e/1FAIpQLSc4-RPizFfBoJ4J-VWumdoV114d7gU2kHBbpkfmDx7HkJ5Gwg/viewform?usp=sharing&ouid=113079264479944386424'},
    2: {'fechas': '15–17 junio 2026', 'form_url': 'https://docs.google.com/forms/d/e/1FAIpQLSePQocWnOgDwsJQQinjgUSYfcK3FXN2o7OJWvsRvF9DiQpIQA/viewform?usp=sharing&ouid=113079264479944386424'},
    3: {'fechas': '18–20 junio 2026', 'form_url': 'https://docs.google.com/forms/d/e/1FAIpQLSer5AFh3taxa6J1enjoTtOLXfWfRYanmaxZ6lJC2nS6USTCwQ/viewform?usp=sharing&ouid=113079264479944386424'},
    4: {'fechas': '21–23 junio 2026', 'form_url': 'https://forms.gle/j3cEonQaeGVVKF6EA'},
    5: {'fechas': '24–25 junio 2026', 'form_url': 'https://forms.gle/37MXCzUSGZZwVLATA'},
    6: {'fechas': '26–27 junio 2026', 'form_url': 'https://forms.gle/dETboF8q9oymCJiq9'},
}

# ─────────────────────────────────────────────
# CSS embebido — tema oscuro estilo esports
# ─────────────────────────────────────────────
_CSS = """
  :root {
    --bg:       #080b14;
    --bg2:      #0f1523;
    --card:     #141c2e;
    --card2:    #1a2440;
    --border:   rgba(255,255,255,0.07);
    --cyan:     #00d4ff;
    --cyan2:    #0096cc;
    --dorado:   #ffd700;
    --rojo:     #ff4757;
    --verde:    #2ed573;
    --gris:     #5a6a80;
    --txt:      #d8e0ee;
    --txt2:     #8892a4;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, "Segoe UI", Arial, sans-serif;
    background: var(--bg);
    color: var(--txt);
    line-height: 1.5;
  }

  /* ── Header estilo FPL ── */
  .hdr {
    background: linear-gradient(108deg, #00d8ec 0%, #1248c8 38%, #7218a8 66%, #3a0068 100%);
    padding: 0;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: stretch;
    min-height: 200px;
  }
  .hdr::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 30% 50%, rgba(255,255,255,0.08) 0%, transparent 60%);
    pointer-events: none;
  }
  .hdr-content {
    flex: 1 1 auto;
    padding: 28px 12px 26px 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
    position: relative; z-index: 2;
  }
  .hdr-eyebrow {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 3px;
    color: rgba(255,255,255,0.78); text-transform: uppercase; margin-bottom: 6px;
  }
  .hdr-title {
    font-size: 1.45rem; font-weight: 800; color: #fff; letter-spacing: -0.5px;
  }
  .hdr-j {
    font-size: 2.5rem; font-weight: 900; color: #fff;
    letter-spacing: -1px; line-height: 1.05; margin: 4px 0 3px;
    text-shadow: 0 2px 14px rgba(0,0,0,0.2);
  }
  .hdr-dates { font-size: 0.83rem; color: rgba(255,255,255,0.68); }
  .badge-open {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.45);
    color: #fff;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px;
    padding: 4px 12px; border-radius: 20px; margin-top: 12px;
    text-transform: uppercase;
  }
  .badge-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #fff; box-shadow: 0 0 6px rgba(255,255,255,0.8);
    animation: pulse 1.8s ease-in-out infinite;
  }
  @keyframes pulse {
    0%,100% { opacity: 1; } 50% { opacity: 0.4; }
  }
  /* Grupo de jugadores (derecha) */
  .hdr-players {
    flex-shrink: 0;
    display: flex;
    align-items: flex-end;
    position: relative; z-index: 1;
    padding-right: 0;
  }
  .hdr-pl {
    object-fit: contain;
    object-position: bottom center;
    filter: drop-shadow(-4px 0 8px rgba(0,0,0,0.35));
    position: relative;
    flex-shrink: 0;
  }
  @media (max-width: 600px) {
    /* En celular apilamos: texto arriba, caricaturas en su banda abajo
       (así nunca se encima el subtítulo con los jugadores). */
    .hdr { flex-direction: column; min-height: auto; }
    .hdr-content { padding: 24px 20px 8px; }
    .hdr-j { font-size: 2.1rem; }
    .hdr-dates { font-size: 0.88rem; }
    .hdr-players {
      width: 100%;
      justify-content: center;
      align-items: flex-end;
      overflow: hidden;
      padding-top: 4px;
    }
    /* Mostramos solo el Top 5 de la tabla (las del frente) para que quepan */
    .hdr-pl { display: none; }
    .hdr-pl:nth-last-child(-n+5) { display: block; }
    .hdr-pl:nth-last-child(5) { margin-left: 0 !important; }
  }

  /* ── Layout ── */
  .wrap { max-width: 680px; margin: 0 auto; padding: 16px 14px 8px; }

  /* ── Deadline del form ── */
  .btn-deadline {
    text-align: center;
    font-size: 0.74rem;
    color: var(--txt2);
    line-height: 1.6;
    margin: -8px 0 14px;
    padding: 0 4px;
  }
  .btn-deadline strong { color: var(--cyan); font-weight: 700; }
  .btn-deadline .tz-list {
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 2px 10px; margin-top: 3px;
  }
  .btn-deadline .tz-item { white-space: nowrap; }

  /* ── Cards ── */
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 18px 14px;
    margin-bottom: 14px;
  }
  .card-title {
    font-size: 0.72rem; font-weight: 800;
    color: var(--cyan); text-transform: uppercase; letter-spacing: 2px;
    padding-bottom: 12px; margin-bottom: 14px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 8px;
  }
  .card-title::before {
    content: '';
    display: inline-block; width: 3px; height: 14px;
    background: var(--cyan); border-radius: 2px; flex-shrink: 0;
  }

  /* ── Botón Form ── */
  .btn-form {
    display: flex; align-items: center; justify-content: center; gap: 10px;
    background: linear-gradient(135deg, var(--cyan2) 0%, var(--cyan) 100%);
    color: #000;
    text-decoration: none;
    padding: 15px 20px;
    border-radius: 10px;
    font-size: 0.95rem; font-weight: 800; letter-spacing: 0.5px;
    box-shadow: 0 4px 20px rgba(0,212,255,0.3);
    margin-bottom: 14px;
    transition: opacity 0.2s;
  }
  .btn-form:hover { opacity: 0.88; }

  /* ── Partidos ── */
  .match-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .match-item {
    padding: 10px 12px;
    background: var(--bg2);
    border-radius: 8px;
    border: 1px solid var(--border);
    border-left: 3px solid var(--cyan2);
  }
  .match-num   { font-size: 0.66rem; font-weight: 700; color: var(--gris); text-transform: uppercase; letter-spacing: 0.5px; }
  .match-teams { font-size: 0.83rem; font-weight: 600; color: var(--txt); margin-top: 3px; }
  .match-sep   { color: var(--gris); font-weight: 400; }
  .match-result { font-size: 0.72rem; font-weight: 700; color: var(--verde); margin-top: 3px; }
  .match-fecha  { font-size: 0.68rem; font-weight: 700; color: var(--cyan); margin-top: 4px; }

  /* ── Rojas y penales de la jornada ── */
  .bonosj-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .bonosj { background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 11px; }
  .bonosj-h { font-size: 0.82rem; font-weight: 800; color: var(--txt); margin-bottom: 8px;
              padding-bottom: 7px; border-bottom: 1px solid var(--border); }
  .bonosj-h b { color: var(--dorado); font-size: 0.95rem; }
  .bonosj-row { display: flex; align-items: flex-start; gap: 8px; padding: 6px 0;
                font-size: 0.8rem; border-bottom: 1px solid var(--border); }
  .bonosj-row:last-child { border-bottom: none; }
  .bv { flex-shrink: 0; min-width: 24px; text-align: center; font-weight: 900;
        color: var(--gris); background: var(--bg); border: 1px solid var(--border);
        border-radius: 6px; padding: 1px 5px; }
  .bn { flex: 1; color: var(--txt2); line-height: 1.4; }
  .bonosj-row.acerto .bv { color: #001018; background: var(--verde); border-color: var(--verde); }
  .bonosj-row.acerto .bn { color: var(--verde); font-weight: 700; }
  .bonosj-ok { color: var(--verde); font-weight: 800; font-size: 0.68rem; flex-shrink: 0; }
  @media (max-width: 480px) { .bonosj-grid { grid-template-columns: 1fr; } }

  /* ── H2H ── */
  .h2h-item {
    display: flex; align-items: center;
    padding: 10px 0; gap: 8px;
    border-bottom: 1px solid var(--border);
    font-size: 0.87rem;
  }
  .h2h-item:last-child { border-bottom: none; }
  .h2h-p   { flex: 1; font-weight: 600; color: var(--txt); }
  .h2h-p.left  { text-align: left; }
  .h2h-p.right { text-align: right; }
  .h2h-mid { text-align: center; flex-shrink: 0; min-width: 64px; }
  .h2h-vs  { color: var(--gris); font-size: 0.75rem; font-weight: 700; letter-spacing: 1px; }
  .h2h-score {
    font-weight: 800; font-size: 1rem;
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 6px; padding: 2px 10px; display: inline-block;
  }
  .win  { color: var(--verde); }
  .lose { color: var(--gris); }
  .draw { color: var(--cyan); }

  /* ── Standings ── */
  .tbl { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  .tbl thead tr { background: var(--bg2); }
  .tbl th {
    padding: 9px 5px; font-weight: 700; text-align: center;
    color: var(--cyan); font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 1px; border-bottom: 1px solid var(--border);
  }
  .tbl th.left { text-align: left; padding-left: 10px; }
  .tbl td {
    padding: 8px 5px; text-align: center;
    border-bottom: 1px solid var(--border); color: var(--txt);
  }
  .tbl td.left { text-align: left; padding-left: 10px; font-weight: 600; }
  .tbl tbody tr:hover td { background: var(--card2); }
  .tbl .rank { color: var(--gris); font-weight: 700; font-size: 0.8rem; }
  .tbl .pts  { font-weight: 900; color: var(--dorado); font-size: 0.95rem; }
  .tbl .dif.pos { color: var(--verde); font-weight: 700; }
  .tbl .dif.neg { color: var(--rojo);  font-weight: 700; }
  .gbadge {
    display: inline-block;
    background: rgba(0,212,255,0.12);
    border: 1px solid rgba(0,212,255,0.3);
    color: var(--cyan);
    font-size: 0.62rem; font-weight: 800;
    padding: 1px 5px; border-radius: 4px;
    vertical-align: middle; margin-left: 5px;
  }
  .top3-1 td:first-child { color: #ffd700; }
  .top3-2 td:first-child { color: #c0c0c0; }
  .top3-3 td:first-child { color: #cd7f32; }

  /* Zona de clasificación a playoffs (Top 6) */
  .tbl tr.qual td { background: rgba(46,213,115,0.06); }
  .tbl tr.cut td  { border-bottom: 2px solid var(--verde); }
  .cut-legend {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.68rem; color: var(--verde); font-weight: 700;
    margin-top: 10px; text-transform: uppercase; letter-spacing: 1px;
  }
  .cut-legend::before {
    content: ''; display: inline-block; width: 18px; height: 2px;
    background: var(--verde);
  }

  /* ── Puntos de la jornada ── */
  .j-row {
    display: flex; align-items: center;
    padding: 9px 0; gap: 8px;
    border-bottom: 1px solid var(--border);
    font-size: 0.87rem;
  }
  .j-row:last-child { border-bottom: none; }
  .j-name  { flex: 1; font-weight: 600; color: var(--txt); }
  .j-bonus { font-size: 0.66rem; font-weight: 700; color: var(--cyan); }
  .j-pts {
    font-weight: 900; font-size: 1rem; color: var(--dorado);
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 6px; padding: 2px 12px; min-width: 38px; text-align: center;
  }

  /* ── Grupos ── */
  .grupos-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
  }
  .gcard { border-radius: 10px; overflow: hidden; border: 1px solid var(--border); position: relative; }
  .gcard-bg {
    position: absolute; right: -8px; bottom: -8px;
    height: 90px; width: auto;
    object-fit: contain; object-position: bottom right;
    opacity: 0.18; filter: brightness(0.75) saturate(0.7);
    pointer-events: none; z-index: 0;
  }
  .gcard-hdr, .gcard-row { position: relative; z-index: 1; }
  .gcard-hdr {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    color: var(--dorado);
    font-size: 0.72rem; font-weight: 800;
    padding: 8px 10px; letter-spacing: 2px;
    text-align: center; text-transform: uppercase;
  }
  .gcard-row {
    display: flex; align-items: center;
    padding: 7px 10px;
    border-bottom: 1px solid var(--border);
    font-size: 0.79rem; background: var(--card);
  }
  .gcard-row:last-child { border-bottom: none; }
  .gcard-pos { color: var(--gris); font-size: 0.68rem; font-weight: 700; margin-right: 7px; min-width: 14px; }
  .gcard-pts { margin-left: auto; font-weight: 800; font-size: 0.75rem; color: var(--dorado); }

  /* ── Footer ── */
  .footer {
    text-align: center; padding: 20px;
    color: var(--gris); font-size: 0.73rem;
    border-top: 1px solid var(--border);
  }


  /* ── Avatars ── */
  .avatar, .avatar-ph {
    width: 32px; height: 32px; border-radius: 50%;
    flex-shrink: 0; margin-right: 7px;
    object-fit: cover; border: 2px solid rgba(0,212,255,0.5);
  }
  .avatar-ph {
    background: var(--card2);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.62rem; font-weight: 800; color: var(--cyan);
    border: 1px solid rgba(0,212,255,0.25);
  }
  .h2h-av, .h2h-av-ph {
    width: 38px; height: 38px; border-radius: 50%;
    flex-shrink: 0;
    object-fit: cover; border: 2px solid rgba(0,212,255,0.5);
  }
  .h2h-av-ph {
    background: var(--card2);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 800; color: var(--cyan);
    border: 1px solid rgba(0,212,255,0.25);
  }

  /* ── Print ── */
  @media print {
    /* Mantener el tema azul/oscuro en el PDF (no cambiar a blanco). */
    @page { margin: 0; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .btn-form { display: none !important; }
    .card { page-break-inside: avoid; break-inside: avoid; }
  }

  /* ── Responsive ── */
  @media (max-width: 420px) {
    .match-grid  { grid-template-columns: 1fr; }
    .grupos-grid { grid-template-columns: 1fr 1fr; }
    .hdr-j { font-size: 2rem; }
  }
"""

# CSS extra solo para la landing del sitio (navegación de jornadas)
_CSS_SITIO = """
  .jor-link {
    display: flex; align-items: center; gap: 10px;
    padding: 11px 8px; border-bottom: 1px solid var(--border);
  }
  .jor-link:last-child { border-bottom: none; }
  .jor-n      { font-weight: 800; color: var(--txt); font-size: 0.9rem; min-width: 84px; }
  .jor-fechas { flex: 1; color: var(--txt2); font-size: 0.76rem; min-width: 0; }
  .jor-actions{ display: flex; align-items: center; gap: 8px; flex-shrink: 0; flex-wrap: wrap; justify-content: flex-end; }
  .jor-go     { font-size: 0.74rem; font-weight: 800; letter-spacing: 0.4px; color: var(--cyan); text-decoration: none; }
  .jor-go.pend{ color: var(--gris); }
  .jor-form {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.72rem; font-weight: 800; letter-spacing: 0.3px;
    color: #001018; text-decoration: none;
    background: linear-gradient(135deg, var(--cyan2) 0%, var(--cyan) 100%);
    padding: 6px 11px; border-radius: 18px;
    box-shadow: 0 2px 10px rgba(0,212,255,0.25);
  }
  .jor-badge {
    font-size: 0.6rem; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;
    color: var(--verde); background: rgba(46,213,115,0.14);
    border: 1px solid rgba(46,213,115,0.45); border-radius: 20px; padding: 2px 8px;
  }
  .jor-link.abierta {
    background: rgba(0,212,255,0.06);
    border-left: 3px solid var(--cyan); border-radius: 8px;
  }

  /* Bloques informativos (cómo funciona / reglas) */
  .info-item {
    display: flex; gap: 11px; align-items: flex-start;
    padding: 10px 0; border-bottom: 1px solid var(--border);
    font-size: 0.86rem; color: var(--txt); line-height: 1.45;
  }
  .info-item:last-child { border-bottom: none; }
  .info-ic { font-size: 1.15rem; flex-shrink: 0; line-height: 1.3; }
  .info-item b { color: var(--cyan); font-weight: 700; }
  .intro { color: var(--txt2); font-size: 0.88rem; line-height: 1.55; margin: -4px 0 4px; }

  /* Grid de participantes */
  .part-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
  }
  .part-card {
    display: flex; flex-direction: column; align-items: center; gap: 8px;
    padding: 14px 6px; background: var(--bg2);
    border: 1px solid var(--border); border-radius: 10px;
  }
  .part-av {
    width: 62px; height: 62px; border-radius: 50%;
    object-fit: cover; border: 2px solid rgba(0,212,255,0.5);
  }
  .part-ph {
    display: flex; align-items: center; justify-content: center;
    background: var(--card2); color: var(--cyan); font-weight: 800; font-size: 1rem;
  }
  .part-name { font-size: 0.8rem; font-weight: 700; color: var(--txt); text-align: center; }
  .part-sub {
    font-size: 0.74rem; color: var(--verde); font-weight: 700;
    margin: -4px 0 12px;
  }

  /* ── Playoffs (bracket) ── */
  .po-btn {
    display: flex; align-items: center; justify-content: center; gap: 8px;
    background: linear-gradient(135deg, #7218a8 0%, #c026d3 100%);
    color: #fff; text-decoration: none; font-weight: 800; letter-spacing: 0.5px;
    padding: 13px 18px; border-radius: 10px; margin-bottom: 14px;
    box-shadow: 0 4px 18px rgba(192,38,211,0.3);
  }
  .po-sub { color: var(--txt2); font-size: 0.84rem; margin: -4px 0 12px; line-height: 1.5; }
  /* Bracket: rondas en columnas, scroll horizontal en pantallas chicas */
  .po-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 8px; }
  .po-rounds { display: flex; gap: 12px; align-items: stretch; }
  .po-ronda { flex: 1 1 0; min-width: 150px; display: flex; flex-direction: column; }
  .po-ronda-h {
    font-size: 0.64rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase;
    color: var(--cyan); margin-bottom: 10px; text-align: center;
  }
  .po-ronda-body { display: flex; flex-direction: column; justify-content: space-around; flex: 1; gap: 10px; }
  .po-cruce { background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 6px 10px; }
  .po-3er { margin-top: 12px; }
  .po-slot { display: flex; align-items: center; gap: 8px; padding: 6px 2px; }
  .po-slot + .po-slot { border-top: 1px dashed var(--border); }
  .po-seed { font-size: 0.68rem; font-weight: 800; color: var(--gris); min-width: 24px; }
  .po-slot .avatar, .po-slot .avatar-ph { width: 26px; height: 26px; margin-right: 0; }
  .po-name { font-size: 0.82rem; font-weight: 700; color: var(--txt); }
  .po-slot.po-tbd { padding-left: 6px; }
  .po-slot.po-tbd .po-name { color: var(--txt2); font-weight: 600; font-style: italic; font-size: 0.76rem; }
  .po-prize { color: var(--dorado); font-weight: 800; }
  /* Marca de "ya envió el form" */
  .part-card.entregado {
    border-color: rgba(46,213,115,0.55);
    background: linear-gradient(180deg, rgba(46,213,115,0.12), rgba(46,213,115,0.04));
    box-shadow: 0 0 0 1px rgba(46,213,115,0.25) inset;
  }
  .part-card.entregado .part-av { border-color: var(--verde); }
  .part-badge {
    font-size: 0.58rem; font-weight: 800; letter-spacing: 0.3px;
    color: var(--verde); background: rgba(46,213,115,0.14);
    border: 1px solid rgba(46,213,115,0.4);
    border-radius: 20px; padding: 2px 8px; white-space: nowrap;
  }
  .part-badge.pend {
    color: var(--gris); background: var(--bg2);
    border-color: var(--border);
  }
  @media (max-width: 420px) { .part-grid { grid-template-columns: repeat(2, 1fr); } }
"""


# ─────────────────────────────────────────────
# Caricaturas
# ─────────────────────────────────────────────

# Caricatura de cada participante: nombre canónico → archivo en Caricaturas/.
# Mapa explícito (los nombres de archivo no siguen una convención uniforme).
# Actualiza aquí si agregas o cambias caricaturas.
_CARICATURA_FILE = {
    'George':     '11_MX_GEORGE_VF_B.png',
    'Pedro':      '10_PEDRO_MX.png',
    'Jime':       '03_MX_JIMENA_VF.png',
    'Sof Orozco': '06_MX_SOF_OROZCO_VF.png',
    'Lucía':      '04_LU_MX.png',
    'Sof':        '09_sof_mx2.png',
    'Dani':       '07_DANI_MX.png',
    'Row':        '02_CR_ROWLAND_VS.png',
    'Pablo':      '08_pablo_co.png',
    'Pau':        '01_paula_Ar.png',
    'Toninho':    '05_CL_TOÑO_VF_B.png',
    'Llanos':     '12_mx_llanos_vf.png',
    'Vicente':    '13_vicente_-removebg-preview.png',
}


def _cargar_imagenes() -> dict:
    """Copia las caricaturas a docs/img/ y devuelve {nombre_canónico: ruta_relativa}.

    Se referencian como <img src="img/..."> (no base64): las páginas pesan unos KB
    en vez de ~14 MB, y el navegador cachea las imágenes entre páginas.
    """
    import shutil
    import urllib.parse
    img_dir = os.path.join(OUTPUT_DIR, 'img')
    os.makedirs(img_dir, exist_ok=True)
    imgs = {}
    for nombre, fname in _CARICATURA_FILE.items():
        fpath = os.path.join(CARICATURAS_DIR, fname)
        if not os.path.exists(fpath):
            continue
        shutil.copy(fpath, os.path.join(img_dir, fname))
        imgs[nombre] = f'img/{urllib.parse.quote(fname)}'
    return imgs


def _imagen_para(nombre: str, imagenes: dict):
    """Devuelve la ruta de la caricatura del participante, o None."""
    return imagenes.get(nombre)


def _get_avatar(nombre: str, imagenes: dict, css_cls: str = 'avatar') -> str:
    data_url = _imagen_para(nombre, imagenes)
    if data_url:
        return f'<img class="{css_cls}" src="{data_url}" alt="{nombre}">'
    initials = ''.join(w[0] for w in nombre.split()[:2]).upper()
    ph_cls = 'avatar-ph' if css_cls == 'avatar' else 'h2h-av-ph'
    return f'<div class="{ph_cls}">{initials}</div>'


# ─────────────────────────────────────────────
# Constructores de secciones
# ─────────────────────────────────────────────

_MAX_HDR_PLAYERS = 13   # máximo de caricaturas visibles en el header (todos los participantes)


def _orden_urls_header(orden_nombres, imagenes):
    """URLs de caricaturas en el orden de la tabla, con el #1 al frente.

    El header crece de atrás (pequeño/tenue) hacia el frente (grande/opaco):
    el último de la lista es el más prominente. Por eso invertimos, para que el
    líder de la tabla (orden_nombres[0]) quede al frente.
    """
    if orden_nombres is None:
        urls = list(imagenes.values())
    else:
        urls = [imagenes[n] for n in orden_nombres if n in imagenes]
    urls = urls[:_MAX_HDR_PLAYERS]
    return list(reversed(urls))


def _header_players_html(urls):
    """Construye el grupo de caricaturas estilo FPL a partir de una lista de URLs."""
    n      = len(urls)
    solape = -44 if n <= 7 else -58   # más caricaturas → más solape para que quepan
    players = ''
    for i, url in enumerate(urls):
        h  = int(130 + i * (70 / max(n - 1, 1)))   # 130 px → 200 px
        op = round(0.48 + i * (0.52 / max(n - 1, 1)), 2)   # 0.48 → 1.0
        ml = f'{solape}px' if i > 0 else '0'
        players += (f'<img class="hdr-pl" '
                    f'style="height:{h}px;opacity:{op};z-index:{i + 1};margin-left:{ml};" '
                    f'src="{url}" alt="">')
    return f'<div class="hdr-players">{players}</div>' if players else ''


def _header(jornada, fechas, form_url, imagenes, orden_nombres=None):
    badge = ''
    if form_url:
        badge = '<span class="badge-open"><span class="badge-dot"></span>PREDICCIONES ABIERTAS</span>'

    # Grupo de caricaturas estilo FPL, ordenado por la tabla (líder al frente)
    players_div = _header_players_html(_orden_urls_header(orden_nombres, imagenes))

    return f"""
<header class="hdr">
  <div class="hdr-content">
    <div class="hdr-eyebrow">⚽ Mundial 2026</div>
    <div class="hdr-title">QUINIELA OFICIAL</div>
    <div class="hdr-j">JORNADA {jornada}</div>
    <div class="hdr-dates">{fechas}</div>
    {badge}
  </div>
  {players_div}
</header>"""


def _btn_form(form_url):
    if not form_url:
        return ''
    return """
<a class="btn-form" href="{url}" target="_blank">
  <span>📝</span> LLENAR MIS PREDICCIONES
</a>
<div class="btn-deadline">
  Llenar predicciones antes del <strong>martes 9 de junio a las 16:00 hrs</strong>
  <div class="tz-list">
    <span class="tz-item">CDMX &#127474;&#127485; 16:00 hrs</span>
    <span class="tz-item">San Jos&#233; &#127464;&#127479; 16:00 hrs</span>
    <span class="tz-item">Bogot&#225; &#127464;&#127476; 17:00 hrs</span>
    <span class="tz-item">Santiago &#127464;&#127473; 19:00 hrs</span>
    <span class="tz-item">Buenos Aires &#127462;&#127479; 20:00 hrs</span>
  </div>
</div>""".format(url=form_url)


def _section_partidos(partidos):
    items = ''
    for p in partidos:
        resultado_txt = ''
        if p.resultado:
            mapa = {'1': p.local, 'X': 'Empate', '2': p.visitante}
            resultado_txt = f'<div class="match-num" style="color:#2a9d5c">✓ {mapa.get(p.resultado.value, "")}</div>'
        fecha_txt = f'<div class="match-fecha">📅 {p.fecha}</div>' if p.fecha else ''
        items += f"""
        <div class="match-item">
          <div class="match-num">Partido #{p.numero}</div>
          <div class="match-teams">{p.local} <span class="match-sep">vs</span> {p.visitante}</div>
          {fecha_txt}
          {resultado_txt}
        </div>"""
    return f"""
<div class="card">
  <div class="card-title">Partidos del Mundial</div>
  <div class="match-grid">{items}
  </div>
</div>"""


def _bonosj_bloque(titulo, ic, preds_por_valor, real):
    filas = ''
    for val in sorted(preds_por_valor, reverse=True):
        nombres = ', '.join(sorted(preds_por_valor[val], key=str.lower))
        acerto = (real is not None and val == real)
        ok = '<span class="bonosj-ok">✓ +2</span>' if acerto else ''
        filas += (f'<div class="bonosj-row{" acerto" if acerto else ""}">'
                  f'<span class="bv">{val}</span><span class="bn">{nombres}</span>{ok}</div>')
    real_txt = real if real is not None else '—'
    return f"""
    <div class="bonosj">
      <div class="bonosj-h">{ic} {titulo} · Real: <b>{real_txt}</b></div>
      {filas}
    </div>"""


def _section_bonos_jornada(bonus_preds, rojas_real, penales_real):
    """Predicciones de rojas/penales de cada persona, resaltando el resultado real."""
    if not bonus_preds:
        return ''
    rojas, penales = {}, {}
    for b in bonus_preds:
        rojas.setdefault(b.total_rojas, []).append(b.participante)
        penales.setdefault(b.total_penales, []).append(b.participante)
    return f"""
<div class="card">
  <div class="card-title">Rojas y penales de la jornada</div>
  <div class="bonosj-grid">
    {_bonosj_bloque('Tarjetas rojas', '🟥', rojas, rojas_real)}
    {_bonosj_bloque('Penales de falta', '🎯', penales, penales_real)}
  </div>
</div>"""


def _section_jornada(resultados_j, imagenes):
    """Ranking de los puntos de ESTA jornada (no acumulado)."""
    items = ''
    for r in sorted(resultados_j, key=lambda x: -x.total):
        av = _get_avatar(r.participante, imagenes, 'avatar')
        bonus = r.bonus_rojas + r.bonus_penales
        bonus_txt = f'<span class="j-bonus">+{bonus} bonus</span>' if bonus else ''
        items += f"""
      <div class="j-row">
        {av}
        <span class="j-name">{r.participante}</span>
        {bonus_txt}
        <span class="j-pts">{r.total}</span>
      </div>"""
    return f"""
<div class="card">
  <div class="card-title">Puntos de la jornada</div>
  {items}
</div>"""


def _section_tabla(tabla, resultados_j, clasifican=CLASIFICAN):
    """Tabla general acumulada con la zona de clasificación (Top N) marcada."""
    pts_jornada = {r.participante: r.total for r in resultados_j}
    top_cls = {1: 'top3-1', 2: 'top3-2', 3: 'top3-3'}

    filas = ''
    prev_pts = None
    rank = 0
    for pos, s in enumerate(tabla, 1):
        # Lugar compartido en empates; el corte de playoffs sigue la posición.
        if s['puntos_total'] != prev_pts:
            rank = pos
            prev_pts = s['puntos_total']
        clases = []
        if rank in top_cls:
            clases.append(top_cls[rank])
        if pos <= clasifican:
            clases.append('qual')
        if pos == clasifican:
            clases.append('cut')
        row_cls = ' '.join(clases)
        pj = pts_jornada.get(s['nombre'], 0)
        filas += f"""
        <tr class="{row_cls}">
          <td class="rank">{rank}</td>
          <td class="left">{s['nombre']}</td>
          <td>{pj}</td>
          <td>{s['bonus']}</td>
          <td class="pts">{s['puntos_total']}</td>
        </tr>"""

    return f"""
<div class="card">
  <div class="card-title">Tabla General</div>
  <table class="tbl">
    <thead>
      <tr>
        <th>#</th><th class="left">Participante</th>
        <th>Jor</th><th>Bon</th><th>Pts</th>
      </tr>
    </thead>
    <tbody>{filas}
    </tbody>
  </table>
  <div class="cut-legend">Top {clasifican} clasifican a playoffs</div>
</div>"""


def _footer():
    return '<div class="footer">QUINIELA MUNDIAL 2026 &nbsp;&nbsp;|&nbsp;&nbsp; Hecho con amor ⚽</div>'


# ─────────────────────────────────────────────
# Landing del sitio (docs/index.html)
# ─────────────────────────────────────────────

def _site_header(subtitulo, imagenes, orden_nombres=None):
    # Caricaturas ordenadas por la tabla general (líder al frente)
    players_div = _header_players_html(_orden_urls_header(orden_nombres, imagenes))

    return f"""
<header class="hdr">
  <div class="hdr-content">
    <div class="hdr-eyebrow">⚽ Mundial 2026</div>
    <div class="hdr-title">QUINIELA OFICIAL</div>
    <div class="hdr-j">TABLA GENERAL</div>
    <div class="hdr-dates">{subtitulo}</div>
  </div>
  {players_div}
</header>"""


def _cta_form(jornada, form_url):
    if not form_url:
        return ''
    return f"""
<a class="btn-form" href="{form_url}" target="_blank">
  <span>📝</span> LLENAR PREDICCIONES — JORNADA {jornada}
</a>"""


def _section_tabla_general(tabla, clasifican=CLASIFICAN):
    """Tabla acumulada de toda la temporada (sin columna de jornada puntual)."""
    top_cls = {1: 'top3-1', 2: 'top3-2', 3: 'top3-3'}
    filas = ''
    prev_pts = None
    rank = 0
    for pos, s in enumerate(tabla, 1):
        # Lugar compartido para empates (mismos puntos = mismo #). El corte de
        # playoffs sigue la posición física (solo 6 lugares; el desempate decide).
        if s['puntos_total'] != prev_pts:
            rank = pos
            prev_pts = s['puntos_total']
        clases = []
        if rank in top_cls:
            clases.append(top_cls[rank])
        if pos <= clasifican:
            clases.append('qual')
        if pos == clasifican:
            clases.append('cut')
        filas += f"""
        <tr class="{' '.join(clases)}">
          <td class="rank">{rank}</td>
          <td class="left">{s['nombre']}</td>
          <td>{s['jornadas']}</td>
          <td>{s['bonus']}</td>
          <td class="pts">{s['puntos_total']}</td>
        </tr>"""
    return f"""
<div class="card">
  <div class="card-title">Tabla General — Temporada Regular</div>
  <table class="tbl">
    <thead>
      <tr>
        <th>#</th><th class="left">Participante</th>
        <th>J</th><th>Bon</th><th>Pts</th>
      </tr>
    </thead>
    <tbody>{filas}
    </tbody>
  </table>
  <div class="cut-legend">Top {clasifican} clasifican a playoffs</div>
</div>"""


def _section_jornadas(disponibles, jornada_actual=None):
    """Lista J1–J6: link al form de predicciones de cada una y, si ya se jugó,
    link a sus resultados. La jornada abierta se marca con un badge."""
    items = ''
    for n in sorted(JORNADA_META):
        meta = JORNADA_META[n]
        form_url = meta.get('form_url', '')
        es_actual = (n == jornada_actual)

        acciones = ''
        if es_actual:
            acciones += '<span class="jor-badge">● Abierta</span>'
        if n in disponibles:
            acciones += f'<a class="jor-go" href="jornada_{n}.html">Ver resultados →</a>'
        elif form_url:
            acciones += f'<a class="jor-form" href="{form_url}" target="_blank">📝 Predicciones →</a>'
        else:
            acciones += '<span class="jor-go pend">Pendiente</span>'

        items += f"""
      <div class="jor-link{' abierta' if es_actual else ''}">
        <span class="jor-n">Jornada {n}</span>
        <span class="jor-fechas">{meta['fechas']}</span>
        <span class="jor-actions">{acciones}</span>
      </div>"""
    return f"""
<div class="card">
  <div class="card-title">Jornadas</div>
  {items}
</div>"""


def _section_intro():
    return """
<div class="card">
  <div class="card-title">La Quiniela</div>
  <p class="intro">
    Compite con tus pronósticos del Mundial 2026. Cada jornada predices los
    resultados de los partidos y sumas puntos. Las primeras 6 jornadas son la
    temporada regular: arman una tabla general y los mejores pelean el título
    en los playoffs. ⚽🏆
  </p>
</div>"""


def _section_como_funciona():
    return """
<div class="card">
  <div class="card-title">Cómo funciona</div>
  <div class="info-ico-list">
    <div class="info-item"><span class="info-ic">📅</span><div><b>Temporada regular (Jornadas 1–6):</b> cada jornada pronosticas los 12 partidos del Mundial. Tus aciertos se acumulan en la <b>tabla general</b>.</div></div>
    <div class="info-item"><span class="info-ic">🎟️</span><div><b>Clasificación:</b> al terminar la Jornada 6, los <b>6 primeros</b> de la tabla general avanzan a los Playoffs.</div></div>
    <div class="info-item"><span class="info-ic">🏆</span><div><b>Playoffs:</b> los lugares <b>1 y 2</b> descansan (bye) y esperan en semifinales. En cuartos juegan <b>3 vs 6</b> y <b>4 vs 5</b>. Luego semifinales y la gran final.</div></div>
    <div class="info-item"><span class="info-ic">⚖️</span><div>En los playoffs avanza quien tenga <b>más puntos acumulados</b> de toda la quiniela.</div></div>
  </div>
</div>"""


def _section_reglas():
    return """
<div class="card">
  <div class="card-title">Reglas y puntuación</div>
  <div class="info-ico-list">
    <div class="info-item"><span class="info-ic">✅</span><div><b>+1 punto</b> por cada resultado correcto: gana local <b>(1)</b> · empate <b>(X)</b> · gana visitante <b>(2)</b>.</div></div>
    <div class="info-item"><span class="info-ic">🟥</span><div><b>+2 puntos</b> si aciertas el <b>total de tarjetas rojas</b> de la jornada.</div></div>
    <div class="info-item"><span class="info-ic">🎯</span><div><b>+2 puntos</b> si aciertas el <b>total de penales de falta</b> (las tandas no cuentan).</div></div>
    <div class="info-item"><span class="info-ic">🔢</span><div><b>Desempate en la tabla:</b> puntos totales → bonus acertados → tu mejor jornada → 2ª mejor → 3ª mejor → nombre.</div></div>
    <div class="info-item"><span class="info-ic">💰</span><div><b>Apuesta:</b> 15 USD por persona.</div></div>
  </div>
</div>"""


def _section_participantes(participantes, imagenes, entregados=None, jornada=None):
    entregados = entregados or set()
    cards = ''
    for p in sorted(participantes, key=lambda x: x.nombre.lower()):
        url = _imagen_para(p.nombre, imagenes)
        if url:
            av = f'<img class="part-av" src="{url}" alt="{p.nombre}">'
        else:
            iniciales = ''.join(w[0] for w in p.nombre.split()[:2]).upper()
            av = f'<div class="part-av part-ph">{iniciales}</div>'
        if p.nombre in entregados:
            extra = ' entregado'
            badge = f'<span class="part-badge">✓ Jornada {jornada}</span>'
        else:
            extra = ''
            badge = '<span class="part-badge pend">Pendiente</span>' if jornada else ''
        cards += f"""
      <div class="part-card{extra}">
        {av}
        <span class="part-name">{p.nombre}</span>
        {badge}
      </div>"""

    sub = ''
    if jornada:
        sub = (f'<div class="part-sub">{len(entregados)}/{len(participantes)} '
               f'ya enviaron la Jornada {jornada}</div>')
    return f"""
<div class="card">
  <div class="card-title">Participantes ({len(participantes)})</div>
  {sub}
  <div class="part-grid">{cards}
  </div>
</div>"""


def _build_index_html(d: dict) -> str:
    imgs   = d['imagenes']
    head   = _site_header(d['subtitulo'], imgs, [s['nombre'] for s in d['tabla']])
    cta    = _cta_form(d['proxima_jornada'], d['proxima_form_url'])
    intro  = _section_intro()
    como   = _section_como_funciona()
    reglas = _section_reglas()
    parts  = _section_participantes(d['participantes'], imgs,
                                    d['entregados'], d['proxima_jornada'])
    tabla  = _section_tabla_general(d['tabla'])
    jorns  = _section_jornadas(d['disponibles'], d['proxima_jornada'])
    foot   = _footer()
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
  <title>Quiniela Mundial 2026</title>
  <style>{_CSS}{_CSS_SITIO}</style>
</head>
<body>
{head}
<div class="wrap">
  {cta}
  <a class="po-btn" href="playoffs.html">🏆 Ver Playoffs (proyección) 💩</a>
  {intro}
  {como}
  {reglas}
  {parts}
  {tabla}
  {jorns}
</div>
{foot}
</body>
</html>"""


# ─────────────────────────────────────────────
# Constructor HTML principal
# ─────────────────────────────────────────────

def _build_html(d: dict) -> str:
    imgs    = d.get('imagenes', {})
    head    = _header(d['jornada'], d['fechas'], d['form_url'], imgs,
                      [s['nombre'] for s in d['tabla']])
    btn     = _btn_form(d['form_url'])
    part    = _section_partidos(d['partidos'])
    bonos   = _section_bonos_jornada(d['bonus_preds'], d['rojas_real'], d['penales_real'])
    jornada = _section_jornada(d['resultados_j'], imgs)
    tabla   = _section_tabla(d['tabla'], d['resultados_j'])
    foot    = _footer()

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
  <title>Quiniela J{d['jornada']} — Mundial 2026</title>
  <style>{_CSS}</style>
</head>
<body>
{head}
<div class="wrap">
  {btn}
  {part}
  {bonos}
  {jornada}
  {tabla}
</div>
{foot}
</body>
</html>"""


# ─────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────

def generar(
    jornada_num: int,
    predicciones_override=None,
    resultados_override=None,
) -> str:
    """
    Genera el HTML de una jornada.

    - Sin override: lee CSV de `data/respuestas/jornada_N.csv` y resultados de
      `data/resultados_reales.json`, y persiste el historial acumulado.
    - Con override: usa datos programáticos (modo simulación) y NO persiste.
    """
    from evaluator.pipeline import correr_jornada

    estado = correr_jornada(
        jornada=jornada_num,
        persistir_historial=predicciones_override is None,
        predicciones_override=predicciones_override,
        resultados_override=resultados_override,
        historial_override=[] if predicciones_override is not None else None,
    )

    # Marcar partidos con sus resultados (correr_jornada ya los aplicó en memoria)
    partidos_j = estado['partidos_jornada']

    meta = JORNADA_META[jornada_num]
    datos = {
        'jornada':       jornada_num,
        'fechas':        meta['fechas'],
        'form_url':      meta['form_url'],
        'partidos':      partidos_j,
        'resultados_j':  estado['resultados_j'],
        'tabla':         estado['tabla'],
        'bonus_preds':   estado['bonus_preds'],
        'rojas_real':    estado['total_rojas_real'],
        'penales_real':  estado['total_penales_real'],
        'imagenes':      _cargar_imagenes(),
    }

    html = _build_html(datos)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta = os.path.join(OUTPUT_DIR, f'jornada_{jornada_num}.html')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)

    # En flujo real (sin override) reconstruimos la portada con la tabla acumulada.
    if predicciones_override is None:
        construir_index()

    return ruta


def _po_slot(slot, seeds, imagenes):
    """Un casillero del bracket: participante sembrado (con seed+avatar) o placeholder."""
    if slot in seeds:
        seed = seeds.index(slot) + 1
        av = _get_avatar(slot, imagenes, 'avatar')
        return f'<div class="po-slot"><span class="po-seed">{seed}°</span>{av}<span class="po-name">{slot}</span></div>'
    return f'<div class="po-slot po-tbd"><span class="po-name">{slot}</span></div>'


def _po_ronda(nombre, cruces, seeds, imagenes):
    cards = ''
    for a, b in cruces:
        cards += (f'<div class="po-cruce">{_po_slot(a, seeds, imagenes)}'
                  f'{_po_slot(b, seeds, imagenes)}</div>')
    return (f'<div class="po-ronda"><div class="po-ronda-h">{nombre}</div>'
            f'<div class="po-ronda-body">{cards}</div></div>')


def _po_bracket(titulo, sub, rondas, seeds, imagenes, extra=''):
    cols = ''.join(_po_ronda(n, c, seeds, imagenes) for n, c in rondas)
    return f"""
<div class="card">
  <div class="card-title">{titulo}</div>
  <p class="po-sub">{sub}</p>
  <div class="po-scroll"><div class="po-rounds">{cols}</div></div>
  {extra}
</div>"""


def _po_cruce_suelto(label, a, b, seeds, imagenes):
    """Un cruce aparte (ej. el juego por el 3er lugar)."""
    return (f'<div class="po-3er"><div class="po-ronda-h">{label}</div>'
            f'<div class="po-cruce">{_po_slot(a, seeds, imagenes)}'
            f'{_po_slot(b, seeds, imagenes)}</div></div>')


def _section_reglas_playoff():
    return """
<div class="card">
  <div class="card-title">Cómo funcionan los Playoffs</div>
  <div class="info-ico-list">
    <div class="info-item"><span class="info-ic">🏆</span><div><b>Llave de Campeones</b> (lugares 1–6): pelean por <b>1° $115</b>, <b>2° $60</b>, <b>3° $20</b>.</div></div>
    <div class="info-item"><span class="info-ic">💩</span><div><b>Llave del Sótano</b> (lugares 7–13): el objetivo es <b>NO quedar último</b>. El que pierde la final del sótano es "el peor".</div></div>
    <div class="info-item"><span class="info-ic">⚔️</span><div>Son <b>enfrentamientos directos</b>: en cada ronda avanza quien hace más puntos esa jornada (empate → mejor sembrado).</div></div>
  </div>
</div>
<div class="card">
  <div class="card-title">Puntos en Playoffs (al minuto 90)</div>
  <div class="info-ico-list">
    <div class="info-item"><span class="info-ic">🎯</span><div><b>+3</b> si atinas el <b>marcador exacto</b> (ej. 2–1).</div></div>
    <div class="info-item"><span class="info-ic">✅</span><div><b>+2</b> si atinas solo el resultado (gana uno / empate) — sin el marcador.</div></div>
    <div class="info-item"><span class="info-ic">⚽</span><div><b>+1</b> si aciertas <b>qué equipo mete el primer gol</b> (si es 0–0, nadie lo gana).</div></div>
    <div class="info-item"><span class="info-ic">📏</span><div>Marcador al <b>minuto 90</b> (sin prórroga ni penales). Máximo <b>4 pts</b> por partido.</div></div>
    <div class="info-item"><span class="info-ic">🟥</span><div><b>+2</b> si aciertas el total de <b>tarjetas rojas</b> de la jornada.</div></div>
    <div class="info-item"><span class="info-ic">🎯</span><div><b>+2</b> si aciertas el total de <b>penales de falta</b> de la jornada.</div></div>
  </div>
</div>"""


def _build_playoffs_html(seeds, disp, imagenes):
    head = _site_header('Playoffs · proyección', imagenes, seeds)
    reglas = _section_reglas_playoff()
    a3, b3 = disp['campeones_3er']
    tercer = _po_cruce_suelto('🥉 Juego por el 3er lugar ($20)', a3, b3, seeds, imagenes)
    campeones = _po_bracket(
        '🏆 Llave de Campeones (1°–6°)',
        'Por los premios. Bye para 1° y 2°. <span class="po-prize">1° $115 · 2° $60 · 3° $20</span>',
        disp['campeones'], seeds, imagenes, extra=tercer,
    )
    sotano = _po_bracket(
        '💩 Toilet Playoffs (7°–13°)',
        '¿Quién es el peor de la quiniela? Bye para el 13°. El que pierde la '
        '<b>Poop Final</b> es <b>el peor</b> 😈',
        disp['sotano'], seeds, imagenes,
    )
    nota = ('<div class="card"><p class="po-sub">⚠️ Es una <b>proyección con la tabla de '
            'ahorita</b>. La siembra real se fija al terminar la Jornada 6.</p></div>')
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
  <title>Playoffs — Quiniela Mundial 2026</title>
  <style>{_CSS}{_CSS_SITIO}</style>
</head>
<body>
{head}
<div class="wrap">
  <a class="btn-form" href="index.html">← Volver a la tabla</a>
  {nota}
  {reglas}
  {campeones}
  {sotano}
</div>
{_footer()}
</body>
</html>"""


def construir_playoffs() -> str | None:
    """Genera docs/playoffs.html con las dos llaves sembradas con la tabla actual."""
    from data.loader import cargar_participantes
    from data.historial_io import cargar_historial_resultados
    from quiniela.standings import calcular_tabla_general
    from quiniela.playoffs import sembrar, bracket_display

    tabla = calcular_tabla_general(cargar_participantes(), cargar_historial_resultados())
    seeds = sembrar(tabla)
    if len(seeds) < 13:
        return None

    html = _build_playoffs_html(seeds, bracket_display(seeds), _cargar_imagenes())
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta = os.path.join(OUTPUT_DIR, 'playoffs.html')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    return ruta


def construir_index() -> str:
    """
    Reconstruye docs/index.html (portada): tabla general acumulada del historial
    real persistido + navegación a las jornadas ya jugadas + CTA de la próxima.

    Es independiente de cualquier simulación: siempre lee el historial real.
    """
    from data.loader import cargar_participantes
    from data.historial_io import cargar_historial_resultados
    from data.respuestas_loader import normalizar_nombre
    from quiniela.standings import calcular_tabla_general

    participantes = cargar_participantes()
    historial = cargar_historial_resultados()
    tabla = calcular_tabla_general(participantes, historial)

    jugadas = {r.jornada for r in historial}
    # La portada enlaza una jornada si su detalle ya fue generado en docs/.
    disponibles = {
        n for n in JORNADA_META
        if os.path.exists(os.path.join(OUTPUT_DIR, f'jornada_{n}.html'))
    } | jugadas

    # Jornada "actual" para la sección de entregados y el CTA del form: la última
    # con entregas registradas (la que se está recolectando/jugando). Así, aunque
    # una jornada ya empezó a contar puntos, la portada no salta a la siguiente.
    entregas = _cargar_entregas()
    if entregas:
        jornada_form = max(int(k) for k in entregas)
    else:
        jornada_form = next((n for n in sorted(JORNADA_META) if n not in jugadas), None)

    entregados = {
        normalizar_nombre(n) for n in entregas.get(str(jornada_form), [])
    } if jornada_form else set()

    # El CTA "Llenar predicciones" solo si esa jornada aún no empieza a jugarse.
    cta_abierto = jornada_form is not None and jornada_form not in jugadas
    form_url = JORNADA_META.get(jornada_form, {}).get('form_url', '') if cta_abierto else ''

    n_jugadas = len(jugadas)
    if n_jugadas == 0:
        subtitulo = 'Temporada por comenzar · J1–J6'
    else:
        subtitulo = f'Temporada regular · {n_jugadas}/6 jornadas jugadas'

    datos = {
        'subtitulo':        subtitulo,
        'participantes':    participantes,
        'tabla':            tabla,
        'disponibles':      disponibles,
        'entregados':       entregados,
        'proxima_jornada':  jornada_form,
        'proxima_form_url': form_url,
        'imagenes':         _cargar_imagenes(),
    }
    html = _build_index_html(datos)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta = os.path.join(OUTPUT_DIR, 'index.html')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    # .nojekyll evita que GitHub Pages procese el sitio con Jekyll.
    open(os.path.join(OUTPUT_DIR, '.nojekyll'), 'w').close()
    # Página de playoffs (proyección con la tabla actual).
    construir_playoffs()
    return ruta


if __name__ == '__main__':
    # `py reports/generar_reporte.py sitio` → solo reconstruye la portada (index.html)
    # con el historial real. Útil antes de la J1 para publicar la tabla en ceros.
    if len(sys.argv) > 1 and sys.argv[1] == 'sitio':
        ruta = construir_index()
        print(f'Portada generada: {ruta}')
        webbrowser.open(f'file:///{ruta.replace(os.sep, "/")}')
        sys.exit(0)

    jornada = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    usar_sim = len(sys.argv) > 2 and sys.argv[2] == 'sim'

    preds_override = None
    resultados_override = None
    if usar_sim:
        from tests.simular_jornada import datos_simulados_jornada
        sim = datos_simulados_jornada(jornada)
        preds_override = (sim['predicciones'], sim['bonus_preds'])
        resultados_override = (
            sim['resultados_reales'],
            sim['total_rojas'],
            sim['total_penales'],
        )

    ruta = generar(
        jornada,
        predicciones_override=preds_override,
        resultados_override=resultados_override,
    )
    print(f'Reporte generado: {ruta}')
    webbrowser.open(f'file:///{ruta.replace(os.sep, "/")}')
