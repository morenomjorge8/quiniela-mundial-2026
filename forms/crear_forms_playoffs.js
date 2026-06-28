// ================================================================
// QUINIELA MUNDIAL 2026 — Creador de Google Forms de PLAYOFFS
//
// A diferencia de la fase regular (1/X/2 + bonos), en playoffs cada partido
// pide MARCADOR EXACTO (goles de cada equipo) y QUIÉN METE EL PRIMER GOL.
//
// Puntuación (al minuto 90, sin prórroga ni penales):
//   Marcador exacto ............ 3 pts
//   Solo resultado (1/X/2) ..... 2 pts
//   Acertar el primer gol ...... +1 pt   (si el partido es 0-0, ese punto no lo gana nadie)
//   Máximo 4 pts por partido.
// Bonos de la ronda (igual que la fase regular):
//   Total de tarjetas rojas exacto ... +2 pts
//   Total de penales de falta exacto . +2 pts
//
// INSTRUCCIONES:
//   1. Ve a https://script.google.com  → "Nuevo proyecto"
//   2. Pega TODO este archivo
//   3. EDITA el array RONDAS con los cruces reales del Mundial de cada ronda
//      (los equipos se conocen cuando termina la fase de grupos)
//   4. Ejecuta la función crearTodo  → acepta permisos
//   5. Copia las URLs y pégalas donde corresponda
// ================================================================

const CONFIG = {
  nombreCarpeta: 'Mundial2026-GAS SL',                 // misma carpeta que la fase regular
  nombreHoja:    'Respuestas Quiniela 2026 Playoffs',  // spreadsheet de respuestas de playoffs
};

// IMPORTANTE: deben coincidir EXACTAMENTE con data/loader.py::PARTICIPANTES.
const PARTICIPANTES = [
  'George', 'Pedro', 'Jime', 'Sof Orozco', 'Lucía', 'Sof', 'Dani',
  'Row', 'Pablo', 'Pau', 'Toninho', 'Llanos', 'Vicente',
];

// ── Rondas de playoffs ──────────────────────────────────────────────────
// Una ronda = una jornada de playoff (todos los vivos predicen estos partidos).
// Los #num siguen después del 72 (la fase de grupos fue #1–#72), así que en
// numeración FIFA los dieciseisavos son #73–#88. La quiniela usa SOLO los
// primeros 8 (#73–#80) para la primera ronda de playoffs (J7).
//
// J7 ya está lista con sus 8 partidos. Cuando termine la fase de grupos, solo
// EDITA local/visitante de cada uno con los equipos reales (deja los num igual).
// Las rondas siguientes (octavos, cuartos, …) se definen después: están abajo
// comentadas como plantilla.
const RONDAS = [
  {
    clave: 'J7', titulo: 'Playoffs J7 — Dieciseisavos (primeros 8)', fechas: 'por definir',
    partidos: [
      { num: 73, local: 'Equipo A', visitante: 'Equipo B' },
      { num: 74, local: 'Equipo C', visitante: 'Equipo D' },
      { num: 75, local: 'Equipo E', visitante: 'Equipo F' },
      { num: 76, local: 'Equipo G', visitante: 'Equipo H' },
      { num: 77, local: 'Equipo I', visitante: 'Equipo J' },
      { num: 78, local: 'Equipo K', visitante: 'Equipo L' },
      { num: 79, local: 'Equipo M', visitante: 'Equipo N' },
      { num: 80, local: 'Equipo O', visitante: 'Equipo P' },
    ],
  },

  // ── Rondas siguientes (por definir según avance el bracket) ──────────────
  // Descomenta y edita cuando se conozcan los cruces:
  //
  // { clave: 'J8', titulo: 'Playoffs J8 — Octavos', fechas: 'por definir',
  //   partidos: [
  //     { num: 89, local: 'Equipo A', visitante: 'Equipo B' },
  //     // … octavos
  //   ],
  // },
  // { clave: 'J9', titulo: 'Playoffs J9 — Cuartos', fechas: 'por definir',
  //   partidos: [ { num: 97, local: 'Equipo A', visitante: 'Equipo B' } ],
  // },
];

// ================================================================
// FUNCIÓN PRINCIPAL — ejecuta esta
// ================================================================
function crearTodo() {
  const carpeta = obtenerOCrearCarpeta(CONFIG.nombreCarpeta);
  const ss = crearHojaRespuestas(carpeta);

  const urls = [];
  RONDAS.forEach(function(ronda) {
    const url = crearFormRonda(ronda, carpeta, ss);
    urls.push(ronda.clave + ': ' + url);
    Logger.log(ronda.clave + ' creada: ' + url);
  });

  Logger.log('\n=== LINKS DE LOS FORMULARIOS DE PLAYOFFS ===');
  urls.forEach(function(u) { Logger.log(u); });
  Logger.log('\nHoja de respuestas: ' + ss.getUrl());
  Logger.log('Listo! Revisa la carpeta: ' + CONFIG.nombreCarpeta);
}

// ================================================================
// CREA UN FORMULARIO PARA UNA RONDA DE PLAYOFF
// ================================================================
function crearFormRonda(ronda, carpeta, ss) {
  const titulo = 'Quiniela Playoffs ' + ronda.clave + ' — Mundial 2026 (' + ronda.fechas + ')';
  const form = FormApp.create(titulo);

  form.setDescription(
    'Predicciones de playoffs. Marcador al minuto 90 (SIN prorroga ni penales).\n\n' +
    'Puntuacion por partido:\n' +
    '  Marcador exacto = 3 puntos\n' +
    '  Solo resultado (gana uno / empate) = 2 puntos\n' +
    '  Acertar que equipo mete el PRIMER gol = +1 punto\n' +
    '  (Si el partido es 0-0, el punto del primer gol no lo gana nadie.)'
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(true);
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage('Predicciones de playoffs guardadas (' + ronda.clave + '). Suerte!');

  // --- Nombre del participante ---
  form.addListItem()
    .setTitle('Tu nombre')
    .setChoiceValues(PARTICIPANTES)
    .setRequired(true);

  // Validacion: numero entero >= 0 para los goles
  var valGoles = FormApp.createTextValidation()
    .setHelpText('Escribe un numero entero (0, 1, 2, ...)')
    .requireNumberGreaterThanOrEqualTo(0)
    .build();

  // --- Un bloque por partido: goles local, goles visitante, primer gol ---
  ronda.partidos.forEach(function(p) {
    form.addSectionHeaderItem()
      .setTitle('#' + p.num + '  ' + p.local + '  vs  ' + p.visitante)
      .setHelpText('Marcador al minuto 90 (sin prorroga/penales).');

    form.addTextItem()
      .setTitle('#' + p.num + '  Goles de ' + p.local)
      .setValidation(valGoles)
      .setRequired(true);

    form.addTextItem()
      .setTitle('#' + p.num + '  Goles de ' + p.visitante)
      .setValidation(valGoles)
      .setRequired(true);

    var pg = form.addMultipleChoiceItem();
    pg.setTitle('#' + p.num + '  Primer gol: quien anota primero?');
    pg.setChoices([
      pg.createChoice(p.local),
      pg.createChoice(p.visitante),
    ]);
    pg.setRequired(true);
  });

  // --- Bonos de la ronda (rojas y penales, +2 c/u) ---
  form.addSectionHeaderItem()
    .setTitle('Bonos de la ronda (+2 puntos cada uno)')
    .setHelpText('Predice el total para TODA la ronda (suma de los ' +
                 ronda.partidos.length + ' partidos). Las tandas de penales NO cuentan.');

  form.addTextItem()
    .setTitle('Total de tarjetas ROJAS en la ronda')
    .setValidation(valGoles)
    .setRequired(true);

  form.addTextItem()
    .setTitle('Total de PENALES de falta en la ronda (no incluye tandas)')
    .setValidation(valGoles)
    .setRequired(true);

  // --- Vincular al spreadsheet ---
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  SpreadsheetApp.flush();
  var hojas = ss.getSheets();
  hojas[hojas.length - 1].setName(ronda.clave);

  DriveApp.getFileById(form.getId()).moveTo(carpeta);
  return form.getPublishedUrl();
}

// ================================================================
// HELPERS
// ================================================================
function crearHojaRespuestas(carpeta) {
  var ss = SpreadsheetApp.create(CONFIG.nombreHoja);
  var hojasIniciales = ss.getSheets();
  if (hojasIniciales.length === 1) {
    hojasIniciales[0].setName('Inicio');
    hojasIniciales[0].getRange('A1').setValue('Respuestas Playoffs Quiniela Mundial 2026');
    hojasIniciales[0].getRange('A2').setValue('Las respuestas de cada ronda apareceran en las pestanas J7, J8, ...');
  }
  DriveApp.getFileById(ss.getId()).moveTo(carpeta);
  return ss;
}

function obtenerOCrearCarpeta(nombre) {
  var resultados = DriveApp.getFoldersByName(nombre);
  if (resultados.hasNext()) {
    Logger.log('Carpeta existente encontrada: ' + nombre);
    return resultados.next();
  }
  Logger.log('Creando carpeta: ' + nombre);
  return DriveApp.createFolder(nombre);
}
