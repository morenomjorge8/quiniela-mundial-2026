# Quiniela Mundial 2026 — Guía Operativa

Este documento explica **cómo operar la quiniela jornada por jornada** durante el Mundial. Está pensado para que cualquier organizador (o yo mismo dentro de tres meses) pueda reanudar el flujo sin preguntar nada.

---

## 1. Resumen del sistema

- **11 participantes** (registro cerrado). Sin grupos ni head-to-head en la temporada regular.
- **Temporada regular J1–J6**: es una **tabla general acumulada** por puntos de quiniela.
  Cada persona predice los 12 partidos de la jornada; los puntos se suman jornada a jornada.
- Al terminar J6, los **6 primeros de la tabla clasifican a playoffs**.
- **Playoffs (segunda etapa, aún no implementada)**: 6 clasificados; seeds 1–2 con bye,
  cuartos (3v6, 4v5), semis y final; el avance se define por **puntos acumulados totales**.
  Se construirá cuando se conozcan los cruces de eliminatoria del Mundial.

### Reglas de puntuación
- **1 pt** por resultado correcto (1/X/2) en cada partido del Mundial.
- **+2 pts** si adivinas el total exacto de **tarjetas rojas** en la jornada.
- **+2 pts** si adivinas el total exacto de **penales de falta** (NO incluye tandas).
- **Criterio de desempate en la tabla general**:
  puntos totales → bonus acumulado (rojas+penales) → mejor jornada individual.

---

## 2. Setup inicial (una sola vez, antes del Mundial)

### 2.1 Instalar dependencias
```powershell
py -m pip install -r requirements.txt
```

### 2.2 Participantes y calendario
- **Participantes**: la lista canónica de las 11 personas vive en
  [`data/loader.py`](data/loader.py) → constante `PARTICIPANTES` (registro cerrado,
  ya no se lee del Excel). Si alguien escribe su nombre distinto en un form, agrega la
  variante al dict `ALIAS` de [`data/respuestas_loader.py`](data/respuestas_loader.py).
- **Calendario**: el archivo `MAIN DATA Quinieal MUNDIAL 2026.xlsx` en la raíz sigue
  aportando los 72 partidos de fase de grupos (hoja **Calendario de partidos**).

### 2.3 Crear los Google Forms
[`forms/crear_forms.js`](forms/crear_forms.js) crea **un form por jornada (J1–J6) para los
11**: un desplegable "Tu nombre" con la lista canónica, los 12 partidos de la jornada
(1/X/2) y los dos bonos (rojas, penales). La lista `PARTICIPANTES` del script debe
coincidir exactamente con [`data/loader.py::PARTICIPANTES`](data/loader.py).

1. Abre [script.google.com](https://script.google.com) → "Nuevo proyecto".
2. Pega el contenido completo de [`forms/crear_forms.js`](forms/crear_forms.js).
3. Ejecuta `crearTodo` → acepta permisos de Drive/Forms.
4. En la carpeta `Mundial2026-GAS SL` aparecen los 6 forms y el spreadsheet
   `Respuestas Quiniela 2026` con pestañas `J1`…`J6`.
5. Copia la URL pública de cada form en
   [`reports/generar_reporte.py`](reports/generar_reporte.py) → `JORNADA_META`.

> El "Tu nombre" es un desplegable cerrado: cada quien elige su nombre canónico, así que
> normalmente no hace falta tocar el `ALIAS` de `respuestas_loader.py`.

### 2.4 Verificar que todo funciona
```powershell
py -m pytest tests/ -v
py tests/simular_jornada.py
```
La primera debe mostrar **23 tests verdes**. La segunda imprime el reporte
completo de la J1 con predicciones inventadas (11 participantes) — útil para confirmar
a mano que el cálculo de puntos y la tabla general lucen sensatos.

---

## 3. Ciclo semanal por jornada (J1–J6)

Para cada jornada `N`, este es el flujo que se repite:

### 3.1 ANTES de la jornada (lunes de esa semana)
- Compartir el link del form de la jornada N en el grupo de WhatsApp.
- Mensaje sugerido:
  > 📝 **Jornada N — Mundial 2026**
  > Llena tus predicciones antes del [martes XX a las 16:00 CDMX]
  > 👉 [URL del form]
- Día antes del deadline: recordar a los que aún no respondan.

### 3.2 DURANTE la jornada (mientras se juegan los partidos)
- Apuntar mentalmente o en papel: total de rojas y total de penales de falta
  (no tandas) acumulados de la jornada.

### 3.3 DESPUÉS de la jornada (al día siguiente del último partido)

**Paso 1 — Bajar las respuestas:**
1. Abre el spreadsheet `Respuestas Quiniela 2026` en Drive.
2. Selecciona la pestaña `J{N}`.
3. Archivo → Descargar → Valores separados por comas (.csv).
4. Mueve el archivo a `data/respuestas/jornada_N.csv` (créa la carpeta si no existe).

**Paso 2 — Llenar los resultados oficiales:**
Edita `data/resultados_reales.json` y completa la jornada `N`:
```json
"1": {
  "resultados": {
    "1": "1",
    "2": "X",
    "3": "1",
    ...
    "12": "X"
  },
  "total_rojas": 3,
  "total_penales": 1
}
```
- Clave = número del partido (`1`–`12` para J1, `13`–`24` para J2, etc.).
- Valor = `"1"` (gana local), `"X"` (empate), `"2"` (gana visitante).

**Paso 3 — Generar el reporte:**
```powershell
py reports/generar_reporte.py N
```
Lo que hace:
1. Lee la lista de participantes (constante) y el calendario del Excel.
2. Lee respuestas del CSV (normalizando nombres vía `ALIAS`).
3. Lee resultados reales del JSON.
4. Calcula los puntos de cada participante en la jornada y recalcula la tabla general.
5. **Persiste** el historial acumulado en `data/historial_resultados.json`.
6. Escribe `reports/output/jornada_N.html` y lo abre en el navegador.

**Paso 4 — Compartir al grupo:**
- Toma screenshot del HTML (o usa Ctrl+P → guardar como PDF).
- Compártelo en el WhatsApp.
- (Opcional) Suelta el link del form de la próxima jornada y vuelve al paso 3.1.

---

## 4. Fase de playoffs (segunda etapa)

Aún no implementada. Diseño acordado para cuando termine J6 y se conozcan los cruces de
eliminatoria del Mundial:

- Clasifican los **6 primeros** de la tabla general (seeds 1–6 por su posición tras J6).
- **Seeds 1 y 2**: bye directo a semifinales.
- **Cuartos**: seed 3 vs 6, seed 4 vs 5.
- **Semis**: ganador(3v6) vs seed 2, ganador(4v5) vs seed 1.
- **Final**: los dos ganadores de semis.
- **Avance**: en cada ronda avanza quien tenga **más puntos acumulados totales** de toda
  la quiniela (el bracket solo siembra; las jornadas de playoff siguen sumando puntos).

Pendiente al construirla: cargar los partidos de eliminatoria en el calendario y crear
un form por ronda con los partidos correspondientes.

---

## 5. Cómo se calcula todo (referencia rápida del código)

| Pregunta | Dónde mirar |
|---|---|
| ¿Cómo se calculan los puntos de una jornada? | [`quiniela/scorer.py::calcular_resultado_jornada`](quiniela/scorer.py) |
| ¿Cómo se construye y ordena la tabla general (desempate)? | [`quiniela/standings.py::calcular_tabla_general` / `clave_desempate`](quiniela/standings.py) |
| ¿Cuántos clasifican a playoffs? | [`quiniela/standings.py::CLASIFICAN`](quiniela/standings.py) (= 6) |
| ¿Dónde está la lista canónica de participantes? | [`data/loader.py::PARTICIPANTES`](data/loader.py) |
| ¿Cómo se normalizan variantes de nombre? | [`data/respuestas_loader.py::ALIAS` / `normalizar_nombre`](data/respuestas_loader.py) |
| ¿Cómo se lee el CSV de Google Forms? | [`data/respuestas_loader.py::cargar_respuestas`](data/respuestas_loader.py) |
| ¿Dónde se persiste el historial entre jornadas? | [`data/historial_io.py`](data/historial_io.py) → `data/historial_resultados.json` |
| ¿Cómo se orquesta el flujo de una jornada? | [`evaluator/pipeline.py::correr_jornada`](evaluator/pipeline.py) |
| ¿Cómo se construye el HTML? | [`reports/generar_reporte.py::generar`](reports/generar_reporte.py) |

---

## 6. Persistencia del estado

| Archivo | Qué contiene | Quién lo escribe |
|---|---|---|
| `data/respuestas/jornada_N.csv` | Predicciones crudas de Google Forms | Tú, manual |
| `data/resultados_reales.json` | Resultados oficiales del Mundial | Tú, manual |
| `data/historial_resultados.json` | Puntos por jornada acumulados (1 por participante/jornada) | El script, automático |
| `reports/output/jornada_N.html` | Reporte final que compartes | El script, automático |

> Si quieres "recalcular desde cero" (p. ej. corregiste un resultado real), borra
> `data/historial_resultados.json` y vuelve a correr cada jornada en orden:
> `py reports/generar_reporte.py 1`, luego `2`, etc.

---

## 7. Verificación rápida (smoke test)

Después de cualquier cambio al código:

```powershell
py -m pytest tests/ -v
```
Debe mostrar **23 tests verdes**.

Para probar el ciclo completo sin tocar datos reales:
```powershell
py reports/generar_reporte.py 1 sim
```
Genera el HTML de la J1 con predicciones inventadas y lo abre en el navegador.
**No persiste historial** ni toca `data/resultados_reales.json`.

---

## 8. Troubleshooting

| Error | Causa probable | Cómo arreglar |
|---|---|---|
| Una persona no aparece en la tabla | El nombre del CSV no matchea ningún canónico ni `ALIAS` | Agregar la variante (en minúsculas) al dict `ALIAS` de `data/respuestas_loader.py` |
| HTML sin caricaturas | Falta carpeta `Caricaturas/` o nombres mal | Cada archivo debe llamarse `PAIS_NOMBRE_VF.png` (o sufijo similar) |
| Tabla da todos 0 después de correr jornada | `data/resultados_reales.json` está vacío para esa jornada | Llenar el campo `resultados` con todos los partidos |
| `data/historial_resultados.json` no existe | Primera corrida; se crea automáticamente al terminar J1 | No es un error |
| Test `test_persistencia_de_historial` falla | Cambio reciente en `data/historial_io.py` | Verificar que `_resolver_ruta` lee el atributo del módulo en runtime |

---

## 9. Cómo añadir mejoras al sistema

- **Nuevas reglas de puntuación**: editar las constantes en [`quiniela/scorer.py`](quiniela/scorer.py) (`PUNTOS_ACIERTO`, `BONUS_ROJAS`, `BONUS_PENALES`).
- **Cambiar cuántos clasifican**: editar `CLASIFICAN` en [`quiniela/standings.py`](quiniela/standings.py).
- **Nuevas vistas en el reporte**: añadir una función `_section_X` en [`reports/generar_reporte.py`](reports/generar_reporte.py) y llamarla desde `_build_html`.
- **Notificaciones automáticas a WhatsApp**: fuera de alcance (Meta no expone API gratis para grupos), pero sí se puede generar un mensaje pre-formateado para copy/paste.
- **Soporte para playoffs (etapa 2)**: nuevo módulo con el bracket de 6 seeds (byes 1–2,
  cuartos 3v6/4v5, semis, final; avance por acumulado total) y carga de los partidos de
  eliminatoria; extender `correr_jornada` para jornadas ≥ 7.

Al hacer cualquier cambio, correr `py -m pytest tests/` antes de operar la jornada real.

---

## 10. Sitio web (GitHub Pages)

La web pública vive en `docs/` y la sirve GitHub Pages desde la rama `main`, carpeta `/docs`.

### ⚡ Atajo: actualizar y publicar con un solo comando
```powershell
py actualizar.py 1     # J1: lee resultados del Excel, re-evalúa, regenera y publica (commit+push)
py actualizar.py       # solo regenera la portada (tras editar data/entregas.json) y publica
```
`actualizar.py` hace todo el flujo de abajo de una. Solo necesitas tener actualizado el
Excel ("Respuesta" para resultados) o `data/entregas.json` (quién envió el form) antes de correrlo.
El resto de esta sección explica los pasos manuales que ese script automatiza.

- **Portada** `docs/index.html`: tabla general acumulada + navegación de jornadas + botón
  para llenar el form de la próxima jornada. Se reconstruye sola al correr una jornada real
  (`py reports/generar_reporte.py N`), o a mano con:
  ```powershell
  py reports/generar_reporte.py sitio
  ```
- **Detalle por jornada** `docs/jornada_N.html`: lo genera `generar_reporte.py N`.
- **Quién ya envió el form**: edita `data/entregas.json` (`{ "1": ["George", ...] }`)
  agregando nombres conforme la gente llena el form, y corre `py reports/generar_reporte.py sitio`.
  En la sección Participantes se marcan en verde con el badge "✓ Jornada N" y un contador.

### Publicar / actualizar la web
Después de generar (al cerrar cada jornada):
```powershell
git add docs/
git commit -m "Jornada N: actualiza tabla y resultados"
git push
```
GitHub Pages republica en ~1 min. URL: `https://morenomjorge8.github.io/quiniela-mundial-2026/`

> ⚠️ Privacidad: el `.gitignore` excluye `*.xlsx` (tienen teléfonos) y `Caricaturas/PENDING/`
> (fotos reales). La web solo muestra apodos, puntos y caricaturas. No quites esas reglas.
