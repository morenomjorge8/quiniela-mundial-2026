"""
Regenera los 5 HTML head-to-head de la J7 de playoffs.

Lee EN VIVO:
  - "Respuestas Quiniela 2026 Playoffs.xlsx"  (predicciones de cada quien)
  - data/resultados_playoffs.json             (resultados reales, conforme se juegan)

y reescribe los archivos reports/output/h2h_j7_*.html (predicciones + resultado
real + puntos por partido). Para PDF: abre cada uno y Ctrl+P → "Guardar como PDF".

Uso:
    py actualiza7.py            # regenera los 5 cruces y abre el primero
    py actualiza7.py --no-open  # regenera sin abrir el navegador
"""
import os
import sys
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

    from reports.h2h_playoff import generar, generar_web

    rutas = generar()                 # PDFs en reports/output/
    landing, _info = generar_web()    # versión web en docs/ + cruces_j7.html
    print(f"== {len(rutas)} cruces H2H de la J7 regenerados ==")
    completos = 0
    for ruta, a, b, llave, ok in rutas:
        completos += 1 if ok else 0
        estado = '✅ completo' if ok else '⏳ falta alguien'
        print(f"   [{llave:9}] {a} vs {b:12} -> {os.path.basename(ruta)}  {estado}")
    print(f"\n{completos}/{len(rutas)} con ambos rivales.")
    print(f"   PDFs:    reports/output/  (Ctrl+P → Guardar como PDF)")
    print(f"   Web:     docs/  (landing: {os.path.basename(landing)}) — publica con git push")

    if '--no-open' not in sys.argv and rutas:
        webbrowser.open(f'file:///{rutas[0][0].replace(os.sep, "/")}')


if __name__ == '__main__':
    main()
