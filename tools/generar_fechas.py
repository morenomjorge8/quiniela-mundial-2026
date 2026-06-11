"""
Genera data/fechas_partidos.json a partir de Mundial_2026_completo.xlsx.

El Excel "completo" trae la fecha de cada partido, pero numera distinto al
calendario que usan los forms (MAIN DATA). Por eso emparejamos por
ENFRENTAMIENTO (par de equipos), no por número, y escribimos la fecha contra
el número de partido del MAIN DATA.

Uso:
    py tools/generar_fechas.py
"""
import json
import os
import sys
import unicodedata

import openpyxl

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from data.loader import cargar_calendario, FECHAS_PATH

EXCEL_COMPLETO = os.path.join(os.path.dirname(__file__), '..', 'Mundial_2026_completo.xlsx')

# Variantes de nombre de equipo (ya normalizadas: sin acentos, MAYÚSCULAS) → canónico.
ALIAS_EQUIPO = {
    'ARABIA SAUDI': 'ARABIA', 'ARABIA SAUDITA': 'ARABIA',
    'BOSNIA Y HER': 'BOSNIA', 'BOSNIA Y HERZEGOVINA': 'BOSNIA', 'BOSNIA': 'BOSNIA',
    'COREA': 'COREA', 'COREA DEL SUR': 'COREA',
    'R. CONGO': 'CONGO', 'RD CONGO': 'CONGO', 'R CONGO': 'CONGO',
    'USA': 'USA', 'ESTADOS UNIDOS': 'USA',
    'USBEKISTAN': 'UZBEKISTAN', 'UZBEKISTAN': 'UZBEKISTAN',
}


_DIAS = {
    'LUN': 'Lunes', 'MAR': 'Martes', 'MIE': 'Miércoles',
    'JUE': 'Jueves', 'VIE': 'Viernes', 'SAB': 'Sábado', 'DOM': 'Domingo',
}
_MESES = {
    'ENE': 'enero', 'FEB': 'febrero', 'MAR': 'marzo', 'ABR': 'abril',
    'MAY': 'mayo', 'JUN': 'junio', 'JUL': 'julio', 'AGO': 'agosto',
    'SEP': 'septiembre', 'OCT': 'octubre', 'NOV': 'noviembre', 'DIC': 'diciembre',
}


def _norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().upper().strip()
    return ' '.join(s.split())


def _formatear_fecha(fecha):
    """'Jue 11 jun' → 'Jueves 11 de junio' (día de la semana + día + mes)."""
    partes = str(fecha).split()
    if len(partes) == 3:
        dia, num, mes = partes
        dia = _DIAS.get(_norm(dia)[:3], dia)
        mes = _MESES.get(_norm(mes)[:3], mes)
        return f'{dia} {num} de {mes}'
    return str(fecha).strip()


def _canon(equipo):
    n = _norm(equipo)
    return ALIAS_EQUIPO.get(n, n)


def _clave(a, b):
    """Clave de enfrentamiento independiente del orden local/visitante."""
    return frozenset({_canon(a), _canon(b)})


def fechas_desde_excel():
    """{frozenset(par de equipos): fecha} para las jornadas de grupos."""
    wb = openpyxl.load_workbook(EXCEL_COMPLETO, data_only=True)
    ws = wb['Mundial 2026']
    fechas = {}
    for row in ws.iter_rows(min_row=3, values_only=True):
        num, fecha, etapa, partido = row[0], row[1], row[2], row[3]
        if not (etapa and str(etapa).startswith('Jornada')):
            continue
        if not partido or ' vs ' not in str(partido):
            continue
        a, b = str(partido).split(' vs ', 1)
        fechas[_clave(a, b)] = _formatear_fecha(fecha)
    return fechas


def main():
    fechas_excel = fechas_desde_excel()
    partidos = cargar_calendario()

    salida = {}
    faltantes = []
    for p in partidos:
        fecha = fechas_excel.get(_clave(p.local, p.visitante), '')
        if not fecha:
            faltantes.append(f'#{p.numero} {p.local} vs {p.visitante}')
        salida[str(p.numero)] = {
            'partido': f'{p.local} vs {p.visitante}',
            'fecha': fecha,
        }

    # Orden numérico estable
    ordenado = {str(n): salida[str(n)] for n in sorted(int(k) for k in salida)}
    with open(FECHAS_PATH, 'w', encoding='utf-8') as f:
        json.dump(ordenado, f, ensure_ascii=False, indent=2)

    print(f'Escrito {FECHAS_PATH}')
    print(f'Partidos: {len(salida)} | con fecha: {len(salida) - len(faltantes)} | sin fecha: {len(faltantes)}')
    if faltantes:
        print('SIN FECHA (revisar ALIAS_EQUIPO):')
        for x in faltantes:
            print('  ', x)


if __name__ == '__main__':
    main()
