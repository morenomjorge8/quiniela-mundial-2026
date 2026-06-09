"""Impresión por consola del resultado de una jornada."""
from quiniela.standings import imprimir_tabla


def imprimir_reporte(
    jornada: int,
    resultados_j: list,
    tabla: list,
    total_rojas_real: int,
    total_penales_real: int,
) -> None:
    sep = "=" * 62

    print(f"\n{sep}")
    print(f"  REPORTE JORNADA {jornada}")
    print(sep)
    print(f"  Rojas reales: {total_rojas_real}  |  Penales reales: {total_penales_real}")
    print(sep)

    print(f"\n{'PARTICIPANTE':<22} {'Partidos':>8} {'Rojas':>6} {'Penales':>7} {'TOTAL':>6}")
    print("-" * 52)
    for r in sorted(resultados_j, key=lambda x: -x.total):
        print(
            f"{r.participante:<22} {r.puntos_partidos:>8} {r.bonus_rojas:>6} "
            f"{r.bonus_penales:>7} {r.total:>6}"
        )

    print(f"\nTABLA GENERAL ACUMULADA")
    imprimir_tabla(tabla)
    print()
