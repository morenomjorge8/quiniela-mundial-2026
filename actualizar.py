"""
Actualiza y publica la web de la quiniela en UN SOLO COMANDO.

Uso:
    py actualizar.py 1     # J1: lee resultados del Excel, re-evalua, regenera y publica
    py actualizar.py       # solo regenera la portada (p.ej. tras editar data/entregas.json) y publica

Qué hace `py actualizar.py N`:
  1. Exporta las predicciones y los resultados reales de la jornada N desde
     "Respuestas Quiniela 2026.xlsx".
  2. Re-evalúa la jornada (idempotente) y regenera docs/ (tabla + detalle + portada).
  3. git add + commit + push  (sube también commits pendientes).

Requisitos: estar en la carpeta del proyecto y tener el Excel de respuestas ahí.
"""
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def _run(cmd, **kw):
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT, **kw)


def _paso_python(script, *args):
    """Corre un tool del proyecto; avisa si falla pero no detiene todo."""
    r = _run([sys.executable, os.path.join('tools', script), *args])
    if r.returncode != 0:
        print(f"  (aviso: '{script} {' '.join(args)}' no terminó bien; continúo)")


def main():
    jornada = None
    if len(sys.argv) > 1:
        try:
            jornada = int(sys.argv[1])
        except ValueError:
            sys.exit("Uso: py actualizar.py [numero_de_jornada]")

    from reports.generar_reporte import generar, construir_index

    if jornada is not None:
        print(f"== Jornada {jornada}: leyendo Excel ==")
        _paso_python('exportar_respuestas.py', str(jornada))   # predicciones -> CSV
        _paso_python('exportar_resultados.py', str(jornada))   # resultados reales -> JSON
        print("== Evaluando y regenerando la web ==")
        generar(jornada)                                       # scorea + docs/ (detalle + portada)
        msg = f"J{jornada}: actualiza resultados y tabla"
    else:
        print("== Regenerando la portada ==")
        construir_index()
        msg = "web: actualiza portada"

    print("== Publicando en GitHub ==")
    _run(['git', 'add', '-A'], check=True)
    hay_cambios = _run(['git', 'diff', '--cached', '--quiet']).returncode != 0
    if hay_cambios:
        fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        _run(['git', 'commit', '-m', f"{msg} ({fecha})"], check=True)
    else:
        print("  (sin cambios nuevos; reviso si hay commits pendientes por subir)")
    _run(['git', 'push'], check=True)

    print("\n✅ Listo. Refresca la página con Ctrl+F5 (o agrega ?v=algo a la URL).")


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    main()
