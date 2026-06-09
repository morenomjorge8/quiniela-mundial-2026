# Quiniela Mundial 2026

Quiniela del Mundial 2026: **11 participantes**, temporada regular de 6 jornadas como
**tabla general acumulada** por puntos, y los **6 mejores clasifican a playoffs**
(bracket por implementar en la segunda etapa).

## Para operadores

👉 **Lee [OPERATING_GUIDE.md](OPERATING_GUIDE.md)** para el flujo jornada por jornada.

## Quick start

```powershell
py -m pip install -r requirements.txt

# Verificar que todo funciona
py -m pytest tests/ -v

# Probar el flujo completo con datos inventados
py reports/generar_reporte.py 1 sim
```

## Estructura

```
quiniela/      # Lógica core: modelos, scorer, standings (tabla general)
data/          # Loaders (calendario Excel, CSV de respuestas, JSON de historial/resultados)
evaluator/     # Pipeline orquestador + reporte por consola
reports/       # Generador del HTML que se comparte en WhatsApp
forms/         # Google Apps Script: un form por jornada (J1-J6) para los 11
tests/         # pytest suite + script de simulación manual
Caricaturas/   # Avatares de los participantes (embebidos en el HTML)
```

## Reglas (temporada regular J1–J6)

- **1 pt** por resultado correcto (1/X/2) en cada partido del Mundial.
- **+2 pts** si adivinas el total exacto de tarjetas **rojas** de la jornada.
- **+2 pts** si adivinas el total exacto de **penales de falta** (no tandas).
- La **tabla general** suma todos los puntos de J1–J6. Desempate:
  puntos totales → bonus acumulado → mejor jornada individual.
- Los **6 primeros** clasifican a playoffs.
