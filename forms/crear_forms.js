// ================================================================
// QUINIELA MUNDIAL 2026 — Creador de Google Forms
//
// Instrucciones:
//   1. Ve a https://script.google.com
//   2. Crea un proyecto nuevo ("Nuevo proyecto")
//   3. Borra el código que viene por defecto
//   4. Pega TODO este archivo
//   5. Haz clic en "Ejecutar" → función: crearTodo
//   6. Acepta los permisos que pida Google
//   7. Los 6 formularios aparecerán en la carpeta indicada
// ================================================================

const CONFIG = {
  nombreCarpeta: 'Mundial2026-GAS SL',       // <-- cambia si quieres otro nombre
  nombreHoja:    'Respuestas Quiniela 2026',  // spreadsheet donde llegan todas las respuestas
};

// IMPORTANTE: estos nombres deben coincidir EXACTAMENTE con
// data/loader.py::PARTICIPANTES para que el match de respuestas funcione.
// El "Tu nombre" del form es un desplegable cerrado con esta lista, así que
// cada persona elige su nombre canónico (no hay texto libre que normalizar).
const PARTICIPANTES = [
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
];

const JORNADAS = [
  {
    numero: 1,
    fechas: '11–14 jun 2026',
    partidos: [
      { num: 1,  local: 'México',           visitante: 'Sudáfrica'            },
      { num: 2,  local: 'Corea del Sur',    visitante: 'Chequia'              },
      { num: 3,  local: 'Canadá',           visitante: 'Bosnia y Herzegovina' },
      { num: 4,  local: 'USA',              visitante: 'Paraguay'             },
      { num: 5,  local: 'Qatar',            visitante: 'Suiza'                },
      { num: 6,  local: 'Brasil',           visitante: 'Marruecos'            },
      { num: 7,  local: 'Haití',            visitante: 'Escocia'              },
      { num: 8,  local: 'Australia',        visitante: 'Turquía'              },
      { num: 9,  local: 'Alemania',         visitante: 'Curazao'              },
      { num: 10, local: 'Países Bajos',     visitante: 'Japón'                },
      { num: 11, local: 'Costa de Marfil',  visitante: 'Ecuador'              },
      { num: 12, local: 'Suecia',           visitante: 'Túnez'                },
    ],
  },
  {
    numero: 2,
    fechas: '15–17 jun 2026',
    partidos: [
      { num: 13, local: 'España',           visitante: 'Cabo Verde'           },
      { num: 14, local: 'Bélgica',          visitante: 'Egipto'               },
      { num: 15, local: 'Arabia Saudí',     visitante: 'Uruguay'              },
      { num: 16, local: 'Irán',             visitante: 'Nueva Zelanda'        },
      { num: 17, local: 'Francia',          visitante: 'Senegal'              },
      { num: 18, local: 'Irak',             visitante: 'Noruega'              },
      { num: 19, local: 'Argentina',        visitante: 'Argelia'              },
      { num: 20, local: 'Austria',          visitante: 'Jordania'             },
      { num: 21, local: 'Portugal',         visitante: 'R. Congo'             },
      { num: 22, local: 'Inglaterra',       visitante: 'Croacia'              },
      { num: 23, local: 'Ghana',            visitante: 'Panamá'               },
      { num: 24, local: 'Uzbekistán',       visitante: 'Colombia'             },
    ],
  },
  {
    numero: 3,
    fechas: '18–20 jun 2026',
    partidos: [
      { num: 25, local: 'Chequia',          visitante: 'Sudáfrica'            },
      { num: 26, local: 'Suiza',            visitante: 'Bosnia y Herzegovina' },
      { num: 27, local: 'Canadá',           visitante: 'Qatar'                },
      { num: 28, local: 'México',           visitante: 'Corea del Sur'        },
      { num: 29, local: 'USA',              visitante: 'Australia'            },
      { num: 30, local: 'Escocia',          visitante: 'Marruecos'            },
      { num: 31, local: 'Brasil',           visitante: 'Haití'                },
      { num: 32, local: 'Turquía',          visitante: 'Paraguay'             },
      { num: 33, local: 'Países Bajos',     visitante: 'Suecia'               },
      { num: 34, local: 'Alemania',         visitante: 'Costa de Marfil'      },
      { num: 35, local: 'Ecuador',          visitante: 'Curazao'              },
      { num: 36, local: 'Túnez',            visitante: 'Japón'                },
    ],
  },
  {
    numero: 4,
    fechas: '21–23 jun 2026',
    partidos: [
      { num: 37, local: 'España',           visitante: 'Arabia Saudí'         },
      { num: 38, local: 'Bélgica',          visitante: 'Irán'                 },
      { num: 39, local: 'Uruguay',          visitante: 'Cabo Verde'           },
      { num: 40, local: 'Nueva Zelanda',    visitante: 'Egipto'               },
      { num: 41, local: 'Argentina',        visitante: 'Austria'              },
      { num: 42, local: 'Francia',          visitante: 'Irak'                 },
      { num: 43, local: 'Noruega',          visitante: 'Senegal'              },
      { num: 44, local: 'Jordania',         visitante: 'Argelia'              },
      { num: 45, local: 'Portugal',         visitante: 'Uzbekistán'           },
      { num: 46, local: 'Inglaterra',       visitante: 'Ghana'                },
      { num: 47, local: 'Panamá',           visitante: 'Croacia'              },
      { num: 48, local: 'Colombia',         visitante: 'R. Congo'             },
    ],
  },
  {
    numero: 5,
    fechas: '24–25 jun 2026',
    partidos: [
      { num: 49, local: 'Suiza',            visitante: 'Canadá'               },
      { num: 50, local: 'Bosnia y Herz.',   visitante: 'Qatar'                },
      { num: 51, local: 'Escocia',          visitante: 'Brasil'               },
      { num: 52, local: 'Marruecos',        visitante: 'Haití'                },
      { num: 53, local: 'Chequia',          visitante: 'México'               },
      { num: 54, local: 'Sudáfrica',        visitante: 'Corea del Sur'        },
      { num: 55, local: 'Curazao',          visitante: 'Costa de Marfil'      },
      { num: 56, local: 'Ecuador',          visitante: 'Alemania'             },
      { num: 57, local: 'Japón',            visitante: 'Suecia'               },
      { num: 58, local: 'Túnez',            visitante: 'Países Bajos'         },
      { num: 59, local: 'Turquía',          visitante: 'USA'                  },
      { num: 60, local: 'Paraguay',         visitante: 'Australia'            },
    ],
  },
  {
    numero: 6,
    fechas: '26–27 jun 2026',
    partidos: [
      { num: 61, local: 'Noruega',          visitante: 'Francia'              },
      { num: 62, local: 'Senegal',          visitante: 'Irak'                 },
      { num: 63, local: 'Cabo Verde',       visitante: 'Arabia Saudí'         },
      { num: 64, local: 'Uruguay',          visitante: 'España'               },
      { num: 65, local: 'Egipto',           visitante: 'Irán'                 },
      { num: 66, local: 'Nueva Zelanda',    visitante: 'Bélgica'              },
      { num: 67, local: 'Panamá',           visitante: 'Inglaterra'           },
      { num: 68, local: 'Croacia',          visitante: 'Ghana'                },
      { num: 69, local: 'Colombia',         visitante: 'Portugal'             },
      { num: 70, local: 'R. Congo',         visitante: 'Uzbekistán'           },
      { num: 71, local: 'Argelia',          visitante: 'Austria'              },
      { num: 72, local: 'Jordania',         visitante: 'Argentina'            },
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
  JORNADAS.forEach(function(jornada) {
    const url = crearFormJornada(jornada, carpeta, ss);
    urls.push('J' + jornada.numero + ': ' + url);
    Logger.log('Jornada ' + jornada.numero + ' creada: ' + url);
  });

  Logger.log('\n=== LINKS DE LOS FORMULARIOS ===');
  urls.forEach(function(u) { Logger.log(u); });
  Logger.log('\nHoja de respuestas: ' + ss.getUrl());
  Logger.log('Todo listo! Revisa la carpeta: ' + CONFIG.nombreCarpeta);
}

// ================================================================
// CREA UN FORMULARIO PARA UNA JORNADA
// ================================================================
function crearFormJornada(jornada, carpeta, ss) {
  const titulo = 'Quiniela J' + jornada.numero + ' — Mundial 2026 (' + jornada.fechas + ')';
  const form = FormApp.create(titulo);

  form.setDescription(
    'Registra tus predicciones antes de que arranque la jornada.\n\n' +
    'Puntuacion:\n' +
    '  Resultado correcto (1/X/2) = 1 punto por partido\n' +
    '  Total de rojas exacto = +2 puntos\n' +
    '  Total de penales exacto = +2 puntos'
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(true);
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage(
    'Predicciones guardadas para la Jornada ' + jornada.numero + '. Buena suerte!'
  );

  // --- Pregunta: nombre del participante ---
  form.addListItem()
    .setTitle('Tu nombre')
    .setChoiceValues(PARTICIPANTES)
    .setRequired(true);

  // --- Sección: partidos ---
  form.addSectionHeaderItem()
    .setTitle('Predicciones — Jornada ' + jornada.numero)
    .setHelpText(
      'Selecciona el resultado que esperas para cada partido.\n' +
      '"1" = gana el equipo de la izquierda | "X" = empate | "2" = gana el de la derecha'
    );

  jornada.partidos.forEach(function(partido) {
    var item = form.addMultipleChoiceItem();
    item.setTitle('#' + partido.num + '  ' + partido.local + '  vs  ' + partido.visitante);
    item.setChoices([
      item.createChoice(partido.local + '  (1)'),
      item.createChoice('Empate  (X)'),
      item.createChoice(partido.visitante + '  (2)'),
    ]);
    item.setRequired(true);
  });

  // --- Sección: bonos ---
  form.addSectionHeaderItem()
    .setTitle('Bonos de jornada (+2 puntos cada uno)')
    .setHelpText(
      'Predice el total para TODA la jornada (suma de los ' + jornada.partidos.length + ' partidos).\n' +
      'Las tandas de penales NO cuentan como penales de falta.'
    );

  form.addTextItem()
    .setTitle('Total de tarjetas ROJAS en la jornada')
    .setHelpText('Escribe un numero entero, ejemplo: 2')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Total de PENALES de falta en la jornada (no incluye tandas)')
    .setHelpText('Escribe un numero entero, ejemplo: 1')
    .setRequired(true);

  // --- Vincular al spreadsheet de respuestas ---
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // Renombrar la hoja que se acaba de crear
  SpreadsheetApp.flush();
  var hojas = ss.getSheets();
  var ultimaHoja = hojas[hojas.length - 1];
  ultimaHoja.setName('J' + jornada.numero);

  // Mover el formulario a la carpeta
  var formFile = DriveApp.getFileById(form.getId());
  formFile.moveTo(carpeta);

  return form.getPublishedUrl();
}

// ================================================================
// HELPERS
// ================================================================
function crearHojaRespuestas(carpeta) {
  var ss = SpreadsheetApp.create(CONFIG.nombreHoja);
  // Borrar la hoja vacía por defecto (Sheet1)
  var hojasIniciales = ss.getSheets();
  if (hojasIniciales.length === 1) {
    hojasIniciales[0].setName('Inicio');
    hojasIniciales[0].getRange('A1').setValue('Respuestas Quiniela Mundial 2026');
    hojasIniciales[0].getRange('A2').setValue('Las respuestas de cada jornada apareceran en las pestanas J1, J2, ... J6');
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
