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
// Numeración FIFA continuando tras #72 (fase de grupos):
//   J7 = primeros 8 dieciseisavos (#73–#80)   ·   J8 = segundos 8 dieciseisavos (#81–#88)
//   J9 = octavos / Round of 16 (#89–#96) → ronda FINAL del bracket.
//
// IMPORTANTE: crearTodo crea un form por CADA ronda que esté en RONDAS. J7 y J8 YA
// fueron creadas, así que abajo dejo activa SOLO la J9 (para no duplicarlas).
const RONDAS = [
  // J7 (dieciseisavos #73–#80) y J8 (dieciseisavos #81–#88) — YA CREADAS, no recrear.
  {
    clave: 'J9', titulo: 'Playoffs J9 — Octavos (FINAL del bracket)', fechas: '4 – 7 jul',
    partidos: [
      { num: 89, local: 'Canadá',    visitante: 'Marruecos',      fecha: 'Sáb 4 jul · 11:00 AM' },
      { num: 90, local: 'Paraguay',  visitante: 'Francia',        fecha: 'Sáb 4 jul · 3:00 PM' },
      { num: 91, local: 'Brasil',    visitante: 'Noruega',        fecha: 'Dom 5 jul · 2:00 PM' },
      { num: 92, local: 'México',    visitante: 'Inglaterra',     fecha: 'Dom 5 jul · 6:00 PM' },
      { num: 93, local: 'Portugal',  visitante: 'España',         fecha: 'Lun 6 jul · 1:00 PM' },
      { num: 94, local: 'Estados Unidos', visitante: 'Bélgica',   fecha: 'Lun 6 jul · 6:00 PM' },
      { num: 95, local: 'Argentina', visitante: 'Egipto',         fecha: 'Mar 7 jul · 10:00 AM' },
      { num: 96, local: 'Suiza',     visitante: 'Colombia/Ghana', fecha: 'Mar 7 jul · 2:00 PM' },
    ],
  },
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
      .setHelpText((p.fecha ? p.fecha + '  ·  ' : '') + 'Marcador al minuto 90 (sin prorroga/penales).');

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
