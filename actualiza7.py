"""
Regenera los 5 HTML head-to-head de la J7 de playoffs.

Lee EN VIVO:
  - "Respuestas Quiniela 2026 Playoffs.xlsx"  (predicciones de cada quien)
  - data/resultados_playoffs.json             (resultados reales, conforme se juegan)

y reescribe los archivos reports/output/h2h_j7_*.html (predicciones + resultado
real + puntos por partido). Para PDF: abre cada uno y Ctrl+P → "Guardar como PDF".

Uso:
    py actualiza7.py             # regenera los 5 cruces y abre el primero
    py actualiza7.py --no-open   # regenera sin abrir el navegador
    py actualiza7.py --publicar  # regenera + git add/commit/push (sube a la web)
"""
import datetime
import os
import subprocess
import sys
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def _publicar():
    """git add -A + commit (si hay cambios) + push."""
    print("== publicando en GitHub ==")
    subprocess.run(['git', 'add', '-A'], cwd=ROOT, check=True)
    hay_cambios = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=ROOT).returncode != 0
    if hay_cambios:
        fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        subprocess.run(['git', 'commit', '-m', f'playoffs J7: actualiza cruces ({fecha})'],
                       cwd=ROOT, check=True)
    else:
        print("  (sin cambios nuevos para commitear)")
    subprocess.run(['git', 'push'], cwd=ROOT, check=True)
    print("  ✅ publicado. Link: https://morenomjorge8.github.io/quiniela-mundial-2026/cruces_j7.html"
          f"?v={datetime.datetime.now().strftime('%m%d%H%M')}")


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

    from reports.h2h_playoff import generar, generar_web, JORNADAS, sincronizar_resultados_json
    from reports.generar_reporte import construir_index

    sincronizar_resultados_json()  # vuelca resultados del Excel → data/resultados_playoffs.json
    print("== resultados del Excel volcados a data/resultados_playoffs.json ==")

    primera = None
    for j in JORNADAS:
        rutas = generar(jornada=j)             # PDFs en reports/output/
        landing, _info = generar_web(jornada=j)  # versión web en docs/ + cruces_j{n}.html
        completos = sum(1 for *_x, ok in rutas if ok)
        print(f"== J{j}: {completos}/{len(rutas)} cruces con ambos rivales ==")
        for ruta, a, b, llave, ok in rutas:
            estado = '✅' if ok else '⏳ falta alguien'
            print(f"   [{llave:9}] {a} vs {b:12} -> {os.path.basename(ruta)}  {estado}")
        primera = primera or (rutas[0][0] if rutas else None)

    construir_index()  # index + playoffs.html (avanza el bracket con la J7)
    print("   PDFs: reports/output/  ·  Web: docs/ (cruces_j7.html, cruces_j8.html)")

    if '--publicar' in sys.argv:
        _publicar()
    else:
        print("   (para subir a la web: 'git push'  o  'py actualiza7.py --publicar')")

    abrir = '--no-open' not in sys.argv and '--publicar' not in sys.argv
    if abrir and primera:
        webbrowser.open(f'file:///{primera.replace(os.sep, "/")}')


if __name__ == '__main__':
    main()
