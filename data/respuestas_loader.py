"""
Carga predicciones de los participantes desde el CSV exportado del Google Sheet
de respuestas creado por `forms/crear_forms.js`.

Formato esperado del CSV (pestaña JN del spreadsheet "Respuestas Quiniela 2026"):
  - Columna "Marca temporal" (timestamp de Google Forms)
  - Columna "Tu nombre" — nombre del participante
  - Columnas "#N  Local  vs  Visitante" — una por cada partido de la jornada
    Las respuestas vienen como "México  (1)", "Empate  (X)", "Sudáfrica  (2)"
  - Columna "Total de tarjetas ROJAS en la jornada" — entero
  - Columna "Total de PENALES de falta en la jornada (no incluye tandas)" — entero

Si una persona respondió varias veces se queda con la última respuesta
(la fila más reciente del CSV).
"""
import csv
import re
from quiniela.models import Prediccion, BonusPrediccion, Resultado


# Variantes de nombre (como las escriben en el form, en minúsculas y sin espacios
# sobrantes) → nombre canónico de `data/loader.py::PARTICIPANTES`.
# Sirve para que respuestas con mayúsculas/acentos/apellidos distintos mapeen a
# la misma persona. Extender aquí si alguien escribe su nombre diferente.
ALIAS = {
    'george': 'George',
    'pedro': 'Pedro',
    'jime': 'Jime',
    'jimena': 'Jime',
    'sof orozco': 'Sof Orozco',
    'sofia orozco': 'Sof Orozco',
    'sofía orozco': 'Sof Orozco',
    'lucia': 'Lucía',
    'lucía': 'Lucía',
    'sof': 'Sof',
    'dani': 'Dani',
    'row': 'Row',
    'rowland': 'Row',
    'pablo': 'Pablo',
    'pau': 'Pau',
    'paula': 'Pau',
    'toninho': 'Toninho',
    'toninho pernanbucano': 'Toninho',
    'llanos': 'Llanos',
    'pedro llanos': 'Llanos',
    'vicente': 'Vicente',
    'vicente roquení': 'Vicente',
    'vicente roqueni': 'Vicente',
    'roqueni': 'Vicente',
}


def normalizar_nombre(nombre: str) -> str:
    """Mapea el nombre escrito en el form a su forma canónica vía ALIAS.

    Si no hay alias, devuelve el nombre tal cual (stripeado) — así no se pierde
    silenciosamente una respuesta de alguien que escribió un nombre nuevo.
    """
    limpio = (nombre or '').strip()
    return ALIAS.get(limpio.lower(), limpio)


_RESULTADO_RE = re.compile(r'\(([1X2])\)\s*$')


def _parsear_resultado(valor: str) -> Resultado:
    """Extrae '1', 'X' o '2' del texto '... (1)' / '... (X)' / '... (2)'."""
    if not valor:
        raise ValueError("Respuesta vacía de partido")
    m = _RESULTADO_RE.search(valor.strip())
    if not m:
        raise ValueError(f"No se pudo parsear resultado de: {valor!r}")
    return Resultado(m.group(1))


def _parsear_entero(valor: str, campo: str) -> int:
    """Parsea un entero tolerando espacios y validando que no sea negativo."""
    if valor is None or str(valor).strip() == '':
        raise ValueError(f"Campo '{campo}' vacío")
    txt = str(valor).strip()
    try:
        n = int(txt)
    except ValueError:
        raise ValueError(f"Campo '{campo}' no es entero: {txt!r}")
    if n < 0:
        raise ValueError(f"Campo '{campo}' negativo: {n}")
    return n


def _columna_partido(header: str) -> int | None:
    """Devuelve el número de partido si la columna es de tipo '#N ...', sino None."""
    m = re.match(r'\s*#\s*(\d+)\b', header)
    return int(m.group(1)) if m else None


def cargar_respuestas(
    jornada: int,
    csv_path: str,
) -> tuple[list[Prediccion], list[BonusPrediccion]]:
    """
    Lee el CSV y devuelve (predicciones, bonus_predicciones).
    Una entrada por participante (la más reciente si hubo múltiples respuestas).
    """
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        filas = list(reader)
        headers = reader.fieldnames or []

    # Detectar columnas: nombre, partidos por número, rojas, penales
    col_nombre = next(
        (h for h in headers if h and h.strip().lower().startswith('tu nombre')),
        None,
    )
    if col_nombre is None:
        raise ValueError("CSV no tiene columna 'Tu nombre'")

    cols_partido: dict[int, str] = {}
    for h in headers:
        if not h:
            continue
        num = _columna_partido(h)
        if num is not None:
            cols_partido[num] = h

    col_rojas = next(
        (h for h in headers if h and 'roja' in h.lower()),
        None,
    )
    col_penales = next(
        (h for h in headers if h and 'penal' in h.lower()),
        None,
    )
    if col_rojas is None or col_penales is None:
        raise ValueError("CSV no tiene columnas de bonus (rojas/penales)")

    # Quedarnos con la última respuesta de cada participante (orden de aparición en CSV).
    # El nombre se normaliza vía ALIAS para que variantes mapeen a la misma persona.
    por_participante: dict[str, dict] = {}
    for fila in filas:
        nombre = normalizar_nombre(fila.get(col_nombre))
        if not nombre:
            continue
        por_participante[nombre] = fila

    predicciones: list[Prediccion] = []
    bonus: list[BonusPrediccion] = []
    for nombre, fila in por_participante.items():
        for num_partido, col in cols_partido.items():
            predicciones.append(Prediccion(
                participante=nombre,
                partido_numero=num_partido,
                prediccion=_parsear_resultado(fila.get(col, '')),
            ))
        bonus.append(BonusPrediccion(
            participante=nombre,
            jornada=jornada,
            total_rojas=_parsear_entero(fila.get(col_rojas), 'rojas'),
            total_penales=_parsear_entero(fila.get(col_penales), 'penales'),
        ))

    return predicciones, bonus
