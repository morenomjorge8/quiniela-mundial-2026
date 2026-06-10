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
  @media (max-width: 480px) {
    .hdr { min-height: 160px; }
    .hdr-j { font-size: 2rem; }
    .hdr-pl { display: none; }
    /* En celular mostramos las últimas 5 caricaturas (las más grandes/al frente) */
    .hdr-pl:nth-last-child(-n+5) { display: block; margin-left: -52px; }
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
    body { background: #fff; color: #111; }
    .btn-form { display: none !important; }
    .hdr { background: #0d1b3e !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .card { background: #fff; border: 1px solid #ccc; page-break-inside: avoid; }
    .tbl thead tr { background: #0d1b3e !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .gcard-hdr { background: #0d1b3e !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .tbl td, .tbl th { color: #111; }
    .tbl th { color: #fff; }
    .gcard-row { background: #fff; }
    .match-item { background: #f5f5f5; border-left-color: #0d1b3e; }
    .h2h-score { background: #f5f5f5; }
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
    padding: 12px 4px; text-decoration: none;
    border-bottom: 1px solid var(--border);
  }
  .jor-link:last-child { border-bottom: none; }
  .jor-n      { font-weight: 800; color: var(--txt); font-size: 0.9rem; min-width: 92px; }
  .jor-fechas { flex: 1; color: var(--txt2); font-size: 0.78rem; }
  .jor-go     { font-size: 0.74rem; font-weight: 800; letter-spacing: 0.5px; }
  .jor-link.jugada   .jor-go { color: var(--cyan); }
  .jor-link.jugada:hover { background: var(--card2); border-radius: 8px; }
  .jor-link.pendiente .jor-n,
  .jor-link.pendiente .jor-fechas { opacity: 0.55; }
  .jor-link.pendiente .jor-go { color: var(--gris); }

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
}


def _cargar_imagenes() -> dict:
    """Devuelve {nombre_canónico: data-url} para las caricaturas existentes."""
    imgs = {}
    for nombre, fname in _CARICATURA_FILE.items():
        fpath = os.path.join(CARICATURAS_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'rb') as fh:
            b64 = base64.b64encode(fh.read()).decode('ascii')
        ext  = fname.rsplit('.', 1)[-1].lower()
        mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else f'image/{ext}'
        imgs[nombre] = f'data:{mime};base64,{b64}'
    return imgs


def _imagen_para(nombre: str, imagenes: dict):
    """Devuelve la data-url de la caricatura del participante, o None."""
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

_MAX_HDR_PLAYERS = 11   # máximo de caricaturas visibles en el header (los 11 participantes)


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
        items += f"""
        <div class="match-item">
          <div class="match-num">Partido #{p.numero}</div>
          <div class="match-teams">{p.local} <span class="match-sep">vs</span> {p.visitante}</div>
          {resultado_txt}
        </div>"""
    return f"""
<div class="card">
  <div class="card-title">Partidos del Mundial</div>
  <div class="match-grid">{items}
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
    for i, s in enumerate(tabla, 1):
        clases = []
        if i in top_cls:
            clases.append(top_cls[i])
        if i <= clasifican:
            clases.append('qual')
        if i == clasifican:
            clases.append('cut')
        row_cls = ' '.join(clases)
        pj = pts_jornada.get(s['nombre'], 0)
        filas += f"""
        <tr class="{row_cls}">
          <td class="rank">{i}</td>
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
    for i, s in enumerate(tabla, 1):
        clases = []
        if i in top_cls:
            clases.append(top_cls[i])
        if i <= clasifican:
            clases.append('qual')
        if i == clasifican:
            clases.append('cut')
        filas += f"""
        <tr class="{' '.join(clases)}">
          <td class="rank">{i}</td>
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


def _section_jornadas(disponibles):
    """Lista J1–J6 con link a su detalle si ya se jugó."""
    items = ''
    for n in sorted(JORNADA_META):
        meta = JORNADA_META[n]
        if n in disponibles:
            items += f"""
      <a class="jor-link jugada" href="jornada_{n}.html">
        <span class="jor-n">Jornada {n}</span>
        <span class="jor-fechas">{meta['fechas']}</span>
        <span class="jor-go">Ver resultados →</span>
      </a>"""
        else:
            items += f"""
      <div class="jor-link pendiente">
        <span class="jor-n">Jornada {n}</span>
        <span class="jor-fechas">{meta['fechas']}</span>
        <span class="jor-go">Pendiente</span>
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
    <div class="info-item"><span class="info-ic">🔢</span><div><b>Desempate en la tabla:</b> puntos totales → bonus acertados → tu mejor jornada.</div></div>
    <div class="info-item"><span class="info-ic">💰</span><div><b>Apuesta:</b> 15 USD por persona.</div></div>
  </div>
</div>"""


def _section_participantes(participantes, imagenes):
    cards = ''
    for p in sorted(participantes, key=lambda x: x.nombre.lower()):
        url = _imagen_para(p.nombre, imagenes)
        if url:
            av = f'<img class="part-av" src="{url}" alt="{p.nombre}">'
        else:
            iniciales = ''.join(w[0] for w in p.nombre.split()[:2]).upper()
            av = f'<div class="part-av part-ph">{iniciales}</div>'
        cards += f"""
      <div class="part-card">
        {av}
        <span class="part-name">{p.nombre}</span>
      </div>"""
    return f"""
<div class="card">
  <div class="card-title">Participantes ({len(participantes)})</div>
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
    parts  = _section_participantes(d['participantes'], imgs)
    tabla  = _section_tabla_general(d['tabla'])
    jorns  = _section_jornadas(d['disponibles'])
    foot   = _footer()
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quiniela Mundial 2026</title>
  <style>{_CSS}{_CSS_SITIO}</style>
</head>
<body>
{head}
<div class="wrap">
  {cta}
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
    jornada = _section_jornada(d['resultados_j'], imgs)
    tabla   = _section_tabla(d['tabla'], d['resultados_j'])
    foot    = _footer()

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quiniela J{d['jornada']} — Mundial 2026</title>
  <style>{_CSS}</style>
</head>
<body>
{head}
<div class="wrap">
  {btn}
  {part}
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


def construir_index() -> str:
    """
    Reconstruye docs/index.html (portada): tabla general acumulada del historial
    real persistido + navegación a las jornadas ya jugadas + CTA de la próxima.

    Es independiente de cualquier simulación: siempre lee el historial real.
    """
    from data.loader import cargar_participantes
    from data.historial_io import cargar_historial_resultados
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
    # Próxima jornada abierta = la primera que aún no se juega.
    proxima = next((n for n in sorted(JORNADA_META) if n not in jugadas), None)

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
        'proxima_jornada':  proxima,
        'proxima_form_url': JORNADA_META.get(proxima, {}).get('form_url', '') if proxima else '',
        'imagenes':         _cargar_imagenes(),
    }
    html = _build_index_html(datos)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta = os.path.join(OUTPUT_DIR, 'index.html')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    # .nojekyll evita que GitHub Pages procese el sitio con Jekyll.
    open(os.path.join(OUTPUT_DIR, '.nojekyll'), 'w').close()
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
