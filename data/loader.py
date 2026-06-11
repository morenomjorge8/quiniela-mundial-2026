"""
Carga participantes y calendario.

El registro cerró con 11 personas: la lista canónica vive aquí como constante
(no se lee de Excel). El calendario de partidos del Mundial sí se carga del
Excel principal.
"""
import json
import os
import openpyxl
from quiniela.models import Participante, PartidoMundial

EXCEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'MAIN DATA Quinieal MUNDIAL 2026.xlsx')
FECHAS_PATH = os.path.join(os.path.dirname(__file__), 'fechas_partidos.json')

# Lista canónica de participantes (registro cerrado, 11 personas).
# El nombre es la clave de match con las respuestas del form; la normalización
# de variantes vive en `data/respuestas_loader.py::ALIAS`.
PARTICIPANTES = [
    'George',
    'Pedro',
    'Jime',
    'Sof Orozco',
    'Lucía',
    'Sof',
    'Dani',
    'Row',
    'Pablo',
    'Pau',
    'Toninho',
    'Llanos',
    'Vicente',
]


def cargar_participantes() -> list[Participante]:
    return [Participante(nombre=n) for n in PARTICIPANTES]


def cargar_fechas(ruta: str = FECHAS_PATH) -> dict[int, str]:
    """Devuelve {numero_partido: fecha_texto} desde fechas_partidos.json.

    Acepta valores vacíos (se ignoran). Si el archivo no existe, dict vacío.
    """
    if not os.path.exists(ruta):
        return {}
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    fechas = {}
    for num, valor in data.items():
        if isinstance(valor, dict):       # tolera {"fecha": "..."}
            valor = valor.get('fecha', '')
        if valor:
            fechas[int(num)] = str(valor)
    return fechas


def cargar_calendario(ruta: str = EXCEL_PATH) -> list[PartidoMundial]:
    """Carga los 72 partidos de la fase de grupos (J1–J6)."""
    wb = openpyxl.load_workbook(ruta, data_only=True)
    ws = wb['Calendario de partidos']
    rows = list(ws.iter_rows(values_only=True))
    fechas = cargar_fechas()

    # Filas con datos de partidos (índice 0-based): 4, 7, 10, ..., 37  → 12 filas por jornada
    data_row_indices = [4 + 3 * i for i in range(12)]

    partidos = []
    for jornada in range(1, 7):
        col_start = (jornada - 1) * 4  # cada jornada ocupa 4 columnas
        for row_i in data_row_indices:
            row = rows[row_i]
            num = row[col_start]
            local = row[col_start + 1]
            visitante = row[col_start + 3]
            if num is not None and local is not None and visitante is not None:
                n = int(num)
                partidos.append(PartidoMundial(
                    numero=n,
                    jornada=jornada,
                    local=str(local).strip(),
                    visitante=str(visitante).strip(),
                    fecha=fechas.get(n),
                ))

    return sorted(partidos, key=lambda p: p.numero)


if __name__ == '__main__':
    participantes = cargar_participantes()
    print(f"=== PARTICIPANTES ({len(participantes)}) ===")
    for p in participantes:
        print(f"  - {p.nombre}")

    partidos = cargar_calendario()
    print(f"\n=== CALENDARIO ({len(partidos)} partidos) ===")
    for p in partidos:
        print(f"  J{p.jornada} #{p.numero:2d}: {p.local} vs {p.visitante}")
