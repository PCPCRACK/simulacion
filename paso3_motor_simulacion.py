"""
PASO 3: Motor de simulación completo
--------------------------------------
Construido sobre los pasos 1 y 2 ya terminados (Edificio, distancia,
tiempo_de_viaje, calcular_puntos_equipo_por_segundo, probabilidad_de_ganar,
resolver_combate).

Todo está completo EXCEPTO la función `decidir_accion_agente_tonto()`,
que queda como TODO para completar con guía paso a paso, tal como el
resto del proyecto.
"""
import json
import os
from datetime import datetime
import math
import random

_PLANTILLA_HTML_REPLAY = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Elixir Scramble -- Replay de partida</title>
<style>
  :root {
    --bg: #0d1117;
    --panel: #151b23;
    --line: #263140;
    --team-a: #3987e5;
    --team-a-dim: #1f3a52;
    --team-b: #e66767;
    --team-b-dim: #522020;
    --free: #4a5568;
    --text: #d7dee6;
    --text-dim: #7c8a99;
    --accent: #c98500;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 12px 40px;
  }
  h1 { font-size: 1.1rem; font-weight: 600; letter-spacing: 0.03em; margin: 0 0 4px; }
  .subt { color: var(--text-dim); font-size: 0.8rem; margin-bottom: 16px; }
  .marcador {
    display: flex; gap: 24px; align-items: center;
    background: var(--panel); border: 1px solid var(--line);
    border-radius: 10px; padding: 10px 22px; margin-bottom: 14px;
    font-variant-numeric: tabular-nums;
  }
  .equipo { display: flex; align-items: center; gap: 8px; font-size: 1.05rem; font-weight: 600; }
  .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  .dot.a { background: var(--team-a); }
  .dot.b { background: var(--team-b); }
  .tiempo { color: var(--accent); font-weight: 600; min-width: 90px; text-align: center; }
  canvas { background: #0a0e14; border: 1px solid var(--line); border-radius: 10px; }
  .controles { display: flex; align-items: center; gap: 12px; margin-top: 14px; width: 100%; max-width: 720px; }
  button {
    background: var(--panel); border: 1px solid var(--line); color: var(--text);
    border-radius: 8px; padding: 8px 14px; cursor: pointer; font-size: 0.85rem;
  }
  button:hover { border-color: var(--accent); color: var(--accent); }
  input[type=range] { flex: 1; accent-color: var(--accent); }
  select {
    background: var(--panel); color: var(--text); border: 1px solid var(--line);
    border-radius: 8px; padding: 6px 8px; font-size: 0.8rem;
  }
  .leyenda {
    display: flex; gap: 18px; margin-top: 14px; font-size: 0.75rem;
    color: var(--text-dim); flex-wrap: wrap; justify-content: center; max-width: 720px;
  }
  .leyenda span { display: flex; align-items: center; gap: 5px; }
  .sq { width: 10px; height: 10px; border-radius: 2px; display: inline-block; flex-shrink: 0; }

  .tooltip {
    position: fixed; pointer-events: none; display: none; z-index: 20;
    background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
    padding: 8px 10px; font-size: 0.75rem; color: var(--text);
    max-width: 230px; line-height: 1.45; box-shadow: 0 6px 20px rgba(0,0,0,0.45);
  }
  .tooltip b { color: var(--accent); }
  .tooltip .fila { display: flex; justify-content: space-between; gap: 12px; }
  .tooltip .efecto { margin-top: 4px; color: var(--text-dim); }

  .resumen {
    width: 100%; max-width: 720px; margin-top: 18px; background: var(--panel);
    border: 1px solid var(--line); border-radius: 10px; padding: 14px 18px 18px;
    font-size: 0.8rem;
  }
  .resumen h2 {
    font-size: 0.78rem; margin: 0 0 12px; color: var(--text-dim); font-weight: 600;
    letter-spacing: 0.04em; text-transform: uppercase;
  }
  .resumen-equipos { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
  @media (max-width: 620px) { .resumen-equipos { grid-template-columns: 1fr; } }
  .resumen-equipo { border-left: 2px solid var(--line); padding-left: 12px; }
  .resumen-equipo.a { border-left-color: var(--team-a); }
  .resumen-equipo.b { border-left-color: var(--team-b); }
  .resumen-equipo h3 {
    font-size: 0.82rem; margin: 0 0 10px; display: flex; align-items: center; gap: 7px;
  }
  .barra-fuente { margin-bottom: 7px; }
  .barra-fuente .etq {
    display: flex; justify-content: space-between; font-size: 0.7rem;
    color: var(--text-dim); margin-bottom: 2px;
  }
  .barra-fuente .pista { background: rgba(255,255,255,0.07); border-radius: 4px; height: 6px; overflow: hidden; }
  .barra-fuente .relleno { height: 100%; border-radius: 4px; }
  .genoma-pesos { display: flex; gap: 5px; flex-wrap: wrap; margin: 10px 0; }
  .genoma-pesos span {
    background: rgba(255,255,255,0.06); border-radius: 5px; padding: 2px 6px;
    font-size: 0.66rem; color: var(--text-dim);
  }
  .top-jugadores { font-size: 0.72rem; color: var(--text-dim); margin-top: 6px; }
  .top-jugadores .fila { display: flex; justify-content: space-between; padding: 2px 0; }
  .top-jugadores .fila b { color: var(--text); font-weight: 500; }
</style>
</head>
<body>

<div id="tooltip" class="tooltip"></div>

<h1>ELIXIR SCRAMBLE -- REPLAY DE PARTIDA</h1>
<div class="subt">Time-lapse de la simulacion -- pasa el mouse sobre un edificio, jugador o escuadron para ver sus detalles</div>

<div class="marcador">
  <div class="equipo"><span class="dot a"></span><span id="pa">0</span></div>
  <div class="tiempo" id="reloj">00:00</div>
  <div class="equipo"><span id="pb">0</span><span class="dot b"></span></div>
</div>

<canvas id="mapa" width="700" height="700"></canvas>

<div class="controles">
  <button id="btnPlay">Reproducir</button>
  <input type="range" id="slider" min="0" max="0" value="0" step="1">
  <select id="velocidad">
    <option value="1">1x</option>
    <option value="3" selected>3x</option>
    <option value="8">8x</option>
    <option value="30">30x</option>
  </select>
</div>

<div class="leyenda">
  <span><i class="sq" style="background:var(--team-a)"></i> Equipo A</span>
  <span><i class="sq" style="background:var(--team-b)"></i> Equipo B</span>
  <span><i class="sq" style="background:var(--free);border-radius:50%"></i> Edificio libre</span>
  <span><i class="sq" style="border:1px dashed var(--free);background:transparent;border-radius:50%"></i> Edificio aun no disponible</span>
  <span><i class="sq" style="border:1.4px solid var(--text-dim);background:transparent;border-radius:50%"></i> Escuadron defendiendo</span>
  <span><i class="sq" style="border:1.4px dashed var(--accent);background:transparent;border-radius:50%"></i> Escuadron esperando rally</span>
  <span><i class="sq" style="background:var(--text-dim);opacity:0.45;border-radius:50%"></i> Escuadron regresando a base</span>
  <span>Tamano del punto = soldados del escuadron</span>
</div>

<div class="resumen">
  <h2>Resumen final de la partida</h2>
  <div id="resumenBody"></div>
</div>

<script>
const replay = REPLAY_DATA_PLACEHOLDER;
const resumen = RESUMEN_DATA_PLACEHOLDER;

const canvas = document.getElementById('mapa');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const MAPA_MAX = 1000;
const CAPACIDAD_MAX_ESTIMADA = 4300; // techo aproximado de soldados de UN escuadron, para escalar su tamano

const NOMBRES_EQUIPO = { equipo_A: 'Equipo A', equipo_B: 'Equipo B' };
const ETIQUETAS_GENOMA = ['w1 puntos', 'w2 cercania', 'w3 agresividad', 'w4 coordinacion', 'w5 refuerzo'];
const ETIQUETAS_FUENTE = {
  'castillo': 'Castillo', 'otros edificios': 'Otros edificios',
  'campamentos': 'Campamentos', 'bono observatorio': 'Bono observatorio',
};
const ESTADO_INFO = {
  en_base: 'En base, listo para una orden nueva',
  viajando_ataque: 'En camino a capturar/atacar un edificio',
  viajando_ataque_jugador: 'En camino a atacar a un jugador enemigo',
  defendiendo: 'Defendiendo un edificio capturado',
  esperando_rally: 'Esperando a que el rally salga junto con el resto del grupo',
  regresando_base: 'Regresando a base (perdio su ultimo combate)',
  llego_a_destino: 'Acaba de llegar a su destino',
};
// Datos reales del edificio (tasas y efecto) -- estaticos durante toda la
// partida, así que se guardan una sola vez aquí en vez de repetirlos en
// cada fotograma del replay.
const INFO_EDIFICIOS = {
  'tienda de curacion #1': { tipo: 'Tienda de Curacion', alianza: 30, personal: 30,
    efecto: 'Regenera soldados perdidos a la reserva de cada jugador del equipo que la controla.' },
  'tienda de curacion #2': { tipo: 'Tienda de Curacion', alianza: 30, personal: 30,
    efecto: 'Regenera soldados perdidos a la reserva de cada jugador del equipo que la controla.' },
  'tienda de curacion #3': { tipo: 'Tienda de Curacion', alianza: 30, personal: 30,
    efecto: 'Regenera soldados perdidos a la reserva de cada jugador del equipo que la controla.' },
  'tienda de curacion #4': { tipo: 'Tienda de Curacion', alianza: 30, personal: 30,
    efecto: 'Regenera soldados perdidos a la reserva de cada jugador del equipo que la controla.' },
  'taller de alquimia #1': { tipo: 'Taller de Alquimia', alianza: 50, personal: 30,
    efecto: 'Sin efecto especial -- alto valor en puntos puros.' },
  'taller de alquimia #2': { tipo: 'Taller de Alquimia', alianza: 50, personal: 30,
    efecto: 'Sin efecto especial -- alto valor en puntos puros.' },
  'observatorio': { tipo: 'Observatorio', alianza: 10, personal: 30,
    efecto: '+10% a los puntos de ALIANZA de todos los edificios del equipo.' },
  'portal de migracion': { tipo: 'Portal de Migracion', alianza: 10, personal: 30,
    efecto: '-50% al cooldown de teletransporte del equipo.' },
  'altar maldito': { tipo: 'Altar Maldito', alianza: 10, personal: 30,
    efecto: '-15% ATK/DEF/HP a los escuadrones enemigos.' },
  'reliquias de guerra': { tipo: 'Reliquias de Guerra', alianza: 10, personal: 30,
    efecto: '+15% ATK/DEF/HP a los escuadrones aliados.' },
  'castillo': { tipo: 'Castillo de Elixir', alianza: 80, personal: 30,
    efecto: 'Sin efecto especial -- el edificio mas valioso en puntos puros.' },
  'campamento #1': { tipo: 'Campamento', alianza: 5, personal: 5,
    efecto: 'Un mismo jugador puede mandar varios escuadrones aqui a la vez (unica excepcion a esa regla).' },
  'campamento #2': { tipo: 'Campamento', alianza: 5, personal: 5,
    efecto: 'Un mismo jugador puede mandar varios escuadrones aqui a la vez (unica excepcion a esa regla).' },
};

// Hitboxes del ultimo fotograma dibujado, en coordenadas de pantalla --
// se usan para saber sobre qué elemento está el mouse (tooltip on hover).
let hbEdificios = [], hbJugadores = [], hbEscuadrones = [];

function escalar(v) { return v / MAPA_MAX * W; }
function getCss(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }
function colorEquipo(equipo) {
  if (equipo === 'equipo_A') return getCss('--team-a');
  if (equipo === 'equipo_B') return getCss('--team-b');
  return getCss('--free');
}
function lerp(a, b, t) { return a + (b - a) * t; }

// Interpola posiciones entre el frame idx y el idx+1 con factor t (0..1).
// Si la distancia del salto es enorme (teletransporte), no interpola: salta.
function dibujar(idx, t) {
  const f0 = replay[Math.floor(idx)];
  const f1 = replay[Math.min(Math.floor(idx) + 1, replay.length - 1)];
  ctx.clearRect(0, 0, W, H);
  hbEdificios = []; hbJugadores = []; hbEscuadrones = [];

  ctx.strokeStyle = 'rgba(255,255,255,0.04)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 10; i++) {
    const p = i / 10 * W;
    ctx.beginPath(); ctx.moveTo(p, 0); ctx.lineTo(p, H); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, p); ctx.lineTo(W, p); ctx.stroke();
  }

  // Edificios: activos rellenos, inactivos punteados y tenues
  f0.edificios.forEach(e => {
    const x = escalar(e.x), y = escalar(e.y);
    let color = getCss('--free');
    if (e.dueño === 'equipo_A') color = getCss('--team-a');
    if (e.dueño === 'equipo_B') color = getCss('--team-b');

    ctx.beginPath();
    ctx.arc(x, y, 10, 0, Math.PI * 2);
    if (e.activo) {
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.85;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.setLineDash([]);
      ctx.strokeStyle = 'rgba(255,255,255,0.25)';
      ctx.stroke();
    } else {
      ctx.setLineDash([3, 3]);
      ctx.strokeStyle = 'rgba(124,138,153,0.5)';
      ctx.stroke();
      ctx.setLineDash([]);
    }

    ctx.fillStyle = e.activo ? 'rgba(215,222,230,0.55)' : 'rgba(124,138,153,0.4)';
    ctx.font = '9px sans-serif';
    ctx.textAlign = 'center';
    let nombre = e.nombre.replace('tienda de curacion', 'curacion').replace('taller de alquimia', 'alquimia');
    ctx.fillText(nombre, x, y - 14);

    hbEdificios.push({ x, y, r: 11, data: e });
  });

  // Jugadores (bases): cuadraditos, interpolados salvo teletransporte.
  // Cuando hay teletransporte, se dibuja un anillo que se expande en el
  // punto de llegada para que el salto sea visible. Si varios jugadores
  // saltan cerca uno del otro (comun apenas arranca la partida, cuando
  // muchos saltan hacia la misma zona buena), los anillos se separan un
  // poco en espiral -- si no, se amontonan en una maraña como los
  // escuadrones apilados (ver mas abajo).
  const dibujadosTeleport = {};
  const pos1J = {};
  f1.jugadores_pos.forEach(j => pos1J[j.nombre] = j);
  f0.jugadores_pos.forEach(j => {
    const jn = pos1J[j.nombre] || j;
    let jx = j.x, jy = j.y;
    const salto = Math.hypot(jn.x - j.x, jn.y - j.y);
    const esTeletransporte = salto >= 30;
    if (!esTeletransporte) { jx = lerp(j.x, jn.x, t); jy = lerp(j.y, jn.y, t); }
    else if (t > 0.5) { jx = jn.x; jy = jn.y; }
    const x = escalar(jx), y = escalar(jy);

    if (esTeletransporte) {
      // anillo expandiéndose en el destino durante la transición
      let rx = escalar(jn.x), ry = escalar(jn.y);
      const claveT = Math.round(jn.x) + ',' + Math.round(jn.y);
      const nT = dibujadosTeleport[claveT] || 0;
      dibujadosTeleport[claveT] = nT + 1;
      if (nT > 0) {
        const distT = 6 + nT * 3;
        rx += distT * Math.cos(nT * 2.399963);
        ry += distT * Math.sin(nT * 2.399963);
      }
      // varios jugadores pueden saltar a puntos distintos pero cercanos
      // entre si (comun al arrancar la partida) -- no hay forma limpia de
      // despegarlos a todos sin un layout mas elaborado, asi que el
      // anillo se deja fino y tenue: superpuestos leen como una "rafaga"
      // en vez de una maraña de bordes duros.
      const progreso = Math.min(1, t * 1.6);
      ctx.beginPath();
      ctx.arc(rx, ry, 4 + progreso * 10, 0, Math.PI * 2);
      ctx.strokeStyle = colorEquipo(j.equipo);
      ctx.globalAlpha = 0.35 * (1 - progreso);
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    ctx.beginPath();
    ctx.rect(x - 4, y - 4, 8, 8);
    ctx.fillStyle = colorEquipo(j.equipo);
    ctx.globalAlpha = 0.9;
    ctx.fill();
    ctx.globalAlpha = 1;

    // pips de vidas: solo si esta herido (4/4 es el caso comun, no aporta
    // verlo siempre -- y con jugadores cercanos entre si, una fila de pips
    // por cada uno se amontona rapido). Fila angosta, centrada.
    if (j.hits < 4) {
      const inicioPip = x - 6;
      for (let h = 0; h < 4; h++) {
        ctx.beginPath();
        ctx.arc(inicioPip + h * 4, y - 9, 1.3, 0, Math.PI * 2);
        ctx.fillStyle = h < j.hits ? colorEquipo(j.equipo) : 'rgba(255,255,255,0.18)';
        ctx.fill();
      }
    }

    hbJugadores.push({ x, y, r: 8, data: j });
  });

  // Escuadrones: interpolados; los apilados en el mismo punto se separan
  // visualmente en un pequeno circulo para poder distinguirlos
  const pos1E = {};
  f1.escuadrones.forEach((e, i) => pos1E[e.jugador + '_' + i] = e);
  const dibujados = {};
  f0.escuadrones.forEach((e, i) => {
    const en = pos1E[e.jugador + '_' + i] || e;
    let ex = e.x, ey = e.y;
    const salto = Math.hypot(en.x - e.x, en.y - e.y);
    if (salto < 30) { ex = lerp(e.x, en.x, t); ey = lerp(e.y, en.y, t); }
    else if (t > 0.5) { ex = en.x; ey = en.y; }

    // tamano proporcional a los soldados que le quedan (mas fuerte = mas
    // grande, pero con poco rango -- un circulo mucho mas grande que el
    // viejo 3.5px fijo se solapa demasiado cuando hay varios jugadores
    // cerca, ya que el juego solo garantiza SEPARACION_MINIMA=10 unidades
    // entre ellos (~7px en pantalla)).
    const radio = 2.2 + Math.min(1, e.soldados / CAPACIDAD_MAX_ESTIMADA) * 1.8;

    // separacion visual de apilados EXACTOS (mismo edificio/rally, mismo
    // punto): el primero se queda en el centro, el resto se reparte en
    // espiral (angulo dorado, radio creciente) para que no se tapen.
    const clave = Math.round(ex) + ',' + Math.round(ey);
    const n = dibujados[clave] || 0;
    dibujados[clave] = n + 1;
    const distOffset = n > 0 ? radio + 5 + n * 2.2 : 0;
    const offx = n > 0 ? distOffset * Math.cos(n * 2.399963) : 0;
    const offy = n > 0 ? distOffset * Math.sin(n * 2.399963) : 0;

    const x = escalar(ex) + offx, y = escalar(ey) + offy;

    // el estado se marca en el BORDE del mismo circulo (no un anillo
    // extra aparte) para no aumentar el area que puede solaparse con
    // escuadrones de otros jugadores cercanos: relleno normal = viajando;
    // borde claro solido = defendiendo; borde dorado punteado = esperando
    // rally; mas transparente = regresando a base.
    ctx.beginPath();
    ctx.arc(x, y, radio, 0, Math.PI * 2);
    ctx.fillStyle = colorEquipo(e.equipo);
    ctx.globalAlpha = e.estado === 'regresando_base' ? 0.4 : 0.95;
    ctx.fill();
    if (e.estado === 'defendiendo') {
      ctx.lineWidth = 1;
      ctx.strokeStyle = 'rgba(255,255,255,0.85)';
      ctx.stroke();
    } else if (e.estado === 'esperando_rally') {
      ctx.setLineDash([1.4, 1.4]);
      ctx.lineWidth = 1;
      ctx.strokeStyle = getCss('--accent');
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.globalAlpha = 1;

    hbEscuadrones.push({ x, y, r: Math.max(6, radio + 1.5), data: e });
  });

  const mins = String(f0.minuto).padStart(2, '0');
  const segs = String(Math.max(0, f0.tick) % 60).padStart(2, '0');
  document.getElementById('reloj').textContent = mins + ':' + segs;
  document.getElementById('pa').textContent = f0.puntos_A.toLocaleString();
  document.getElementById('pb').textContent = f0.puntos_B.toLocaleString();
  document.getElementById('slider').value = Math.floor(idx);
}

// ---- Tooltip on hover: busca el elemento mas cercano al mouse entre las
// hitboxes del ultimo fotograma dibujado (escuadrones primero, son los
// mas pequenos y quedan encima) y arma su contenido segun el tipo. ----
function masCercano(lista, mx, my) {
  let mejor = null, mejorDist = Infinity;
  for (const h of lista) {
    const d = Math.hypot(mx - h.x, my - h.y);
    if (d <= h.r && d < mejorDist) { mejor = h.data; mejorDist = d; }
  }
  return mejor;
}

function contenidoTooltipEdificio(e) {
  const info = INFO_EDIFICIOS[e.nombre] || { tipo: e.nombre, alianza: '?', personal: '?' };
  const dueño = e.dueño ? NOMBRES_EQUIPO[e.dueño] : 'Libre (sin capturar)';
  return `<b>${info.tipo}</b>`
    + `<div class="fila"><span>Estado</span><span>${e.activo ? dueño : 'Aun bloqueado'}</span></div>`
    + `<div class="fila"><span>Alianza/seg</span><span>${info.alianza}</span></div>`
    + `<div class="fila"><span>Personal/seg</span><span>${info.personal}</span></div>`
    + (info.efecto ? `<div class="efecto">${info.efecto}</div>` : '');
}
function contenidoTooltipJugador(j) {
  return `<b>${j.nombre}</b> -- ${NOMBRES_EQUIPO[j.equipo] || j.equipo}`
    + `<div class="fila"><span>Vidas</span><span>${'\\u25cf'.repeat(j.hits)}${'\\u25cb'.repeat(Math.max(0, 4 - j.hits))}</span></div>`;
}
function contenidoTooltipEscuadron(e) {
  return `<b>Escuadron de ${e.jugador}</b> -- ${NOMBRES_EQUIPO[e.equipo] || e.equipo}`
    + `<div class="fila"><span>Soldados</span><span>${e.soldados.toLocaleString()}</span></div>`
    + `<div class="efecto">${ESTADO_INFO[e.estado] || e.estado}</div>`;
}

const tooltipEl = document.getElementById('tooltip');
canvas.addEventListener('mousemove', (ev) => {
  const rect = canvas.getBoundingClientRect();
  const mx = ev.clientX - rect.left, my = ev.clientY - rect.top;

  let html = null;
  const esc = masCercano(hbEscuadrones, mx, my);
  if (esc) html = contenidoTooltipEscuadron(esc);
  if (!html) { const j = masCercano(hbJugadores, mx, my); if (j) html = contenidoTooltipJugador(j); }
  if (!html) { const ed = masCercano(hbEdificios, mx, my); if (ed) html = contenidoTooltipEdificio(ed); }

  if (!html) { tooltipEl.style.display = 'none'; return; }
  tooltipEl.innerHTML = html;
  tooltipEl.style.display = 'block';
  const margen = 14;
  let left = ev.clientX + margen, top = ev.clientY + margen;
  if (left + 230 > window.innerWidth) left = ev.clientX - 230 - margen;
  tooltipEl.style.left = left + 'px';
  tooltipEl.style.top = top + 'px';
});
canvas.addEventListener('mouseleave', () => { tooltipEl.style.display = 'none'; });

// ---- Panel de resumen final: desglose de puntos de alianza por fuente,
// pesos del genoma de cada equipo, y top jugadores por puntos personales.
function renderResumen(r) {
  const cont = document.getElementById('resumenBody');
  if (!r || !r.desglose_alianza) {
    cont.innerHTML = '<div style="color:var(--text-dim)">Esta batalla no trae desglose de puntos.</div>';
    return;
  }
  let html = '<div class="resumen-equipos">';
  ['equipo_A', 'equipo_B'].forEach((eq, idx) => {
    const letra = idx === 0 ? 'a' : 'b';
    const d = r.desglose_alianza[eq] || {};
    const total = Object.values(d).reduce((a, b) => a + b, 0);
    const color = colorEquipo(eq);

    html += `<div class="resumen-equipo ${letra}">`
      + `<h3><span class="dot ${letra}"></span>${NOMBRES_EQUIPO[eq]} -- ${Math.round(total).toLocaleString()} pts de alianza</h3>`;

    for (const [clave, etiqueta] of Object.entries(ETIQUETAS_FUENTE)) {
      const v = d[clave] || 0;
      const pct = total > 0 ? (v / total * 100) : 0;
      html += `<div class="barra-fuente">`
        + `<div class="etq"><span>${etiqueta}</span><span>${Math.round(v).toLocaleString()} (${pct.toFixed(0)}%)</span></div>`
        + `<div class="pista"><div class="relleno" style="width:${pct}%;background:${color}"></div></div>`
        + `</div>`;
    }

    const genoma = idx === 0 ? r.genoma_1 : r.genoma_2;
    if (genoma) {
      html += '<div class="genoma-pesos">' + genoma.map((g, i) =>
        `<span>${ETIQUETAS_GENOMA[i] || ('w' + (i + 1))}: ${g.toFixed(2)}</span>`).join('') + '</div>';
    }

    if (r.jugadores) {
      const js = r.jugadores.filter(j => j.equipo === eq);
      const defensa = js.reduce((a, j) => a + j.puntos_por_defensa, 0);
      const kills = js.reduce((a, j) => a + j.puntos_por_kills, 0);
      html += '<div class="top-jugadores">'
        + `<div class="fila"><span>Puntos personales -- defensa</span><b>${Math.round(defensa).toLocaleString()}</b></div>`
        + `<div class="fila"><span>Puntos personales -- combate</span><b>${Math.round(kills).toLocaleString()}</b></div>`
        + '</div>';

      const top3 = [...js].sort((a, b) => b.puntos_personales - a.puntos_personales).slice(0, 3);
      if (top3.length) {
        html += '<div class="top-jugadores" style="margin-top:6px">'
          + top3.map(j => `<div class="fila"><span>${j.nombre}</span><b>${Math.round(j.puntos_personales).toLocaleString()} pts</b></div>`).join('')
          + '</div>';
      }
    }

    html += '</div>';
  });
  html += '</div>';
  cont.innerHTML = html;
}

let cursor = 0;          // posicion continua entre frames
let reproduciendo = false;
let ultimoTiempo = null;

const slider = document.getElementById('slider');
slider.max = replay.length - 1;

function loop(ahora) {
  if (!reproduciendo) return;
  if (ultimoTiempo === null) ultimoTiempo = ahora;
  const dt = (ahora - ultimoTiempo) / 1000;
  ultimoTiempo = ahora;

  const velocidad = parseFloat(document.getElementById('velocidad').value);
  // cada frame de replay representa `intervalo` seg de juego; avanzamos
  // en "frames por segundo real" segun la velocidad elegida
  cursor += dt * velocidad;
  if (cursor >= replay.length - 1) { cursor = replay.length - 1; pause(); }

  dibujar(Math.floor(cursor), cursor - Math.floor(cursor));
  requestAnimationFrame(loop);
}

function play() {
  reproduciendo = true;
  ultimoTiempo = null;
  document.getElementById('btnPlay').textContent = 'Pausar';
  requestAnimationFrame(loop);
}
function pause() {
  reproduciendo = false;
  document.getElementById('btnPlay').textContent = 'Reproducir';
}

document.getElementById('btnPlay').addEventListener('click', () => {
  if (reproduciendo) pause(); else play();
});
slider.addEventListener('input', () => {
  pause();
  cursor = parseInt(slider.value);
  dibujar(cursor, 0);
});

dibujar(0, 0);
renderResumen(resumen);
</script>
</body>
</html>
"""

# ============================================================
# PARÁMETROS -- todo lo ajustable del proyecto vive aquí.
# Cambia cualquier número de este bloque para calibrar el juego.
# ============================================================

# --- Movimiento y mapa ---
VELOCIDAD_TROPAS = 2.2            # unidades de distancia por segundo que caminan los escuadrones
COOLDOWN_TELETRANSPORTE = 120     # segundos de espera entre teletransportes de un jugador
UMBRAL_TELETRANSPORTE = 1         # distancia mínima al objetivo para que valga la pena saltar
SEPARACION_MINIMA = 10            # nadie puede pararse a menos de esto de otro jugador/edificio
MAX_ESCUADRONES_POR_EDIFICIO = 6  # límite de defensores Y de ataque conjunto por edificio/jugador

# --- Rally (ataque conjunto sincronizado) ---
DURACION_RALLY_SEGUNDOS = 60      # ventana para sumarse antes de que el grupo salga junto
CAPACIDAD_RALLY = MAX_ESCUADRONES_POR_EDIFICIO  # mismo límite que defensa (6, incluye al líder)

# --- Combate ---
K_COMBATE = 1.5                         # agresividad de la curva de probabilidad (más alto = más determinista)
FRACCION_SOLDADOS_SOBREVIVIENTES = 0.5  # qué % de sus soldados conserva el GANADOR de un combate
FRACCION_PUNTOS_PERDEDOR = 0.5          # qué % de los puntos del combate gana el PERDEDOR

# --- Puntuación ---
ESCALA_PUNTOS_KILL = 10_000       # divisor del poder eliminado -> puntos personales por matar soldados
PUNTOS_POR_HIT = 500              # puntos por quitarle 1 hit a un jugador enemigo
PUNTOS_POR_MUERTE = 2_000         # bono extra por completar la muerte (4to hit)
# NOTA: estos dos son valores calibrados a ojo (no hay dato del juego real);
# ajústalos cuando consigas el número verdadero.
BONO_VICTORIA = 1_000_000         # bono de fitness por pertenecer al equipo ganador

# --- Duración y mapa ---
DURACION_PARTIDA_SEGUNDOS = 1800  # 30 minutos
SPAWN_EQUIPO_A = (0, 500)
SPAWN_EQUIPO_B = (1000, 500)

# --- Algoritmo genético ---
RUIDO_MUTACION = 0.05             # cuánto puede variar un gen al cruzar
CANTIDAD_ELITE = 15               # cuántos genomas top pasan intactos a la siguiente generación
FRACCION_POOL_PADRES = 0.25       # qué % de la población (los mejores) puede ser padre

# --- Curación (Tienda de Curación) ---
SOLDADOS_CURADOS_POR_TICK = 15    # soldados que regenera CADA tienda controlada
INTERVALO_CURACION_SEGUNDOS = 10  # cada cuántos segundos se aplica la curación

# --- Teletransporte inteligente ---
CANTIDAD_OBJETIVOS_TELEPORT = 3   # a cuántos objetivos buenos apunta el salto (centroide)

# --- Archivos / Salón de la fama ---
ARCHIVO_SALON_FAMA = "salon_fama.json"
TAMANO_SALON_FAMA = 3              # cuántos campeones históricos se conservan


# ============================================================
# PASO 1: MAPA (ya construido, se deja tal cual)
# ============================================================

class Edificio:
    def __init__(self, nombre, x, y, tasa_alianza, tasa_personal,
                 efecto_especial=None, valor_efecto=None, minuto_aparicion=0):
        self.nombre = nombre
        self.x = x
        self.y = y
        self.tasa_alianza = tasa_alianza
        self.tasa_personal = tasa_personal
        self.efecto_especial = efecto_especial
        self.valor_efecto = valor_efecto
        self.minuto_aparicion = minuto_aparicion
        self.dueño = None

    def __repr__(self):
        return (f"Edificio({self.nombre}, dueño={self.dueño}, "
                f"tasa_alianza={self.tasa_alianza}/s, efecto={self.efecto_especial})")


def distancia(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)


def tiempo_de_viaje(pos1, pos2, velocidad):
    if velocidad == 0:
        return None
    return distancia(pos1, pos2) / velocidad


def crear_mapa():
    mapa = [
        Edificio(nombre="tienda de curacion #1", x=300, y=100, tasa_alianza=30,
                 tasa_personal=30, efecto_especial="curacion", valor_efecto=None),
        Edificio(nombre="tienda de curacion #2", x=150, y=350, tasa_alianza=30,
                 tasa_personal=30, efecto_especial="curacion", valor_efecto=None),
        Edificio(nombre="tienda de curacion #3", x=850, y=650, tasa_alianza=30,
                 tasa_personal=30, efecto_especial="curacion", valor_efecto=None),
        Edificio(nombre="tienda de curacion #4", x=700, y=900, tasa_alianza=30,
                 tasa_personal=30, efecto_especial="curacion", valor_efecto=None),
        Edificio(nombre="taller de alquimia #1", x=150, y=650, tasa_alianza=50,
                 tasa_personal=30),
        Edificio(nombre="taller de alquimia #2", x=850, y=350, tasa_alianza=50,
                 tasa_personal=30),
        Edificio(nombre="observatorio", x=300, y=900, tasa_alianza=10,
                 tasa_personal=30, efecto_especial="multiplicador_puntos", valor_efecto=0.10),
        Edificio(nombre="portal de migracion", x=700, y=100, tasa_alianza=10,
                 tasa_personal=30, efecto_especial="reduccion_cooldown", valor_efecto=0.50),
        Edificio(nombre="altar maldito", x=500, y=250, tasa_alianza=10,
                 tasa_personal=30, efecto_especial="debuff_enemigos", valor_efecto=0.15,
                 minuto_aparicion=10),
        Edificio(nombre="reliquias de guerra", x=500, y=750, tasa_alianza=10,
                 tasa_personal=30, efecto_especial="buff_aliados", valor_efecto=0.15,
                 minuto_aparicion=10),
        Edificio(nombre="castillo", x=500, y=500, tasa_alianza=80, tasa_personal=30,
                 minuto_aparicion=10),
        Edificio(nombre="campamento #1", x=700, y=700, tasa_alianza=5, tasa_personal=5,
                 minuto_aparicion=13),
        Edificio(nombre="campamento #2", x=300, y=300, tasa_alianza=5, tasa_personal=5,
                 minuto_aparicion=13),
    ]
    return mapa


def calcular_puntos_equipo_por_segundo(mapa, nombre_equipo):
    total_base = 0
    bono = 0

    for edificio in mapa:
        if edificio.dueño == nombre_equipo:
            total_base += edificio.tasa_alianza
            if edificio.efecto_especial == "multiplicador_puntos":
                bono = edificio.valor_efecto

    total_base += total_base * bono
    return total_base


# ============================================================
# PASO 2: COMBATE (ya construido, se deja tal cual)
# ============================================================

def probabilidad_de_ganar(poder_a, poder_b, k=K_COMBATE):
    diferencia = (poder_a - poder_b) / 1_000_000
    exponente = -k * diferencia
    resultado = 1 / (1 + math.exp(exponente))
    return resultado


def resolver_combate(poder_a, poder_b, k=K_COMBATE):
    """Retorna "A" o "B" según quién gana esta pelea puntual."""
    prob_a_gana = probabilidad_de_ganar(poder_a, poder_b, k)
    aleatorio = random.random()
    if aleatorio <= prob_a_gana:
        return "A"
    else:
        return "B"


# ============================================================
# ESCUADRON
# ============================================================

class Escuadron:
    def __init__(self, jugador_dueño, capacidad_maxima, poder_por_soldado):
        self.jugador_dueño = jugador_dueño
        self.capacidad_maxima = capacidad_maxima
        self.poder_por_soldado = poder_por_soldado
        self.soldados_actuales = capacidad_maxima
        self.estado = "en_base"
        self.destino = None
        self.x = jugador_dueño.x
        self.y = jugador_dueño.y
        self.rally = None  # objeto Rally al que pertenece, si está en uno

    def poder_actual(self):
        return self.poder_por_soldado * self.soldados_actuales

    def avanzar_un_tick(self):
        """Mueve el escuadrón un paso hacia su destino, si tiene uno."""
        if self.destino is None:
            return

        pos_actual = (self.x, self.y)
        pos_destino = (self.destino.x, self.destino.y)
        dist_restante = distancia(pos_actual, pos_destino)

        if dist_restante <= VELOCIDAD_TROPAS:
            self.x = self.destino.x
            self.y = self.destino.y
            self.estado = "llego_a_destino"
        else:
            direccion_x = (pos_destino[0] - pos_actual[0]) / dist_restante
            direccion_y = (pos_destino[1] - pos_actual[1]) / dist_restante
            self.x = self.x + VELOCIDAD_TROPAS * direccion_x
            self.y = self.y + VELOCIDAD_TROPAS * direccion_y

    def enviar_a_atacar(self, edificio_objetivo):
        """Manda el escuadrón a capturar/defender un edificio, SOLO (sin rally)."""
        self.salir_de_rally()
        self.destino = edificio_objetivo
        self.estado = "viajando_ataque"

    def enviar_a_atacar_jugador(self, jugador_objetivo):
        """Manda el escuadrón a atacar directamente a un jugador (Sistema 2)."""
        self.salir_de_rally()
        self.destino = jugador_objetivo
        self.estado = "viajando_ataque_jugador"

    def unirse_a_rally(self, rally):
        """Se suma a un rally en formación -- espera a que el grupo salga junto."""
        self.destino = rally.objetivo
        self.estado = "esperando_rally"
        self.rally = rally
        rally.miembros.append(self)

    def salir_de_rally(self):
        """Se retira de cualquier rally al que perteneciera (si aplica)."""
        if self.rally is not None:
            if self in self.rally.miembros:
                self.rally.miembros.remove(self)
            self.rally = None

    def regresar_a_base(self):
        """El escuadrón perdió una pelea -- vuelve caminando a su jugador."""
        self.salir_de_rally()
        self.destino = self.jugador_dueño
        self.estado = "regresando_base"

    def teletransportar_con_jugador(self, nueva_x, nueva_y):
        """
        Usado cuando el jugador dueño se teletransporta o muere.
        Si el escuadrón no venía lleno (ej. estaba regresando vacío
        tras perder una pelea), se rellena de inmediato con lo que
        la reserva del jugador permita -- igual que si hubiera
        llegado caminando a base.
        """
        self.salir_de_rally()
        self.x = nueva_x
        self.y = nueva_y
        self.destino = None
        self.estado = "en_base"
        self.rellenar_desde_reserva()

    def rellenar_desde_reserva(self):
        """
        Al llegar de vuelta a la base, se rellena con lo que quede
        disponible en la reserva del jugador (hasta su capacidad máxima).
        """
        jugador = self.jugador_dueño
        faltantes = self.capacidad_maxima - self.soldados_actuales
        disponibles = jugador.reserva_disponible()
        a_rellenar = min(faltantes, disponibles)
        self.soldados_actuales += a_rellenar
        jugador.total_soldados_reserva -= a_rellenar


# ============================================================
# RALLY (ataque conjunto sincronizado)
# ============================================================

class Rally:
    """
    Representa un punto de reunión abierto por un jugador hacia un
    OBJETIVO (un Edificio enemigo defendido, o un Jugador enemigo).
    Otros escuadrones del mismo equipo pueden sumarse durante
    DURACION_RALLY_SEGUNDOS (o hasta llenar CAPACIDAD_RALLY). Cuando se
    cumple el plazo o el cupo, todos los miembros parten JUNTOS desde
    el mismo punto (la posición del líder en ese instante) hacia el
    mismo objetivo -- como recorren la misma distancia a la misma
    velocidad, llegan exactamente al mismo tick, y el ataque se
    resuelve como un solo evento conjunto, no en cadena uno por uno.
    """

    def __init__(self, objetivo, equipo, tick_apertura, lider_escuadron):
        self.objetivo = objetivo  # Edificio o Jugador
        self.equipo = equipo
        self.tick_apertura = tick_apertura
        self.miembros = [lider_escuadron]
        self.partido = False

    def esta_lleno(self):
        return len(self.miembros) >= CAPACIDAD_RALLY

    def listo_para_partir(self, tick_actual):
        return self.esta_lleno() or (tick_actual - self.tick_apertura) >= DURACION_RALLY_SEGUNDOS

    def partir(self):
        """Todos los miembros salen juntos desde la posición actual del líder."""
        if not self.miembros:
            self.partido = True
            return
        lider = self.miembros[0]
        origen_x, origen_y = lider.x, lider.y
        es_edificio = isinstance(self.objetivo, Edificio)
        for esc in self.miembros:
            esc.x = origen_x
            esc.y = origen_y
            esc.destino = self.objetivo
            esc.estado = "viajando_ataque" if es_edificio else "viajando_ataque_jugador"
            # esc.rally se conserva (no se limpia) para que procesar_llegadas
            # los reconozca como grupo al llegar y los resuelva juntos
        self.partido = True


def gestionar_rallies(rallies, tick_actual):
    """
    Se llama una vez por tick. Revisa todos los rallies activos y hace
    partir a los que ya cumplieron su ventana de tiempo o llenaron el
    cupo. Elimina de la lista los que ya partieron o quedaron vacíos
    (todos sus miembros se fueron por otra razón, ej. teletransporte).
    """
    for rally in rallies:
        if rally.partido:
            continue
        if not rally.miembros:
            rally.partido = True
            continue
        if rally.listo_para_partir(tick_actual):
            rally.partir()

    rallies[:] = [r for r in rallies if not r.partido]


def buscar_rally_abierto(rallies, objetivo, equipo):
    """Busca un rally del mismo equipo hacia el mismo objetivo que aún
    no haya partido y tenga cupo. Retorna None si no existe."""
    for r in rallies:
        if not r.partido and r.objetivo is objetivo and r.equipo == equipo and not r.esta_lleno():
            return r
    return None


# ============================================================
# JUGADOR
# ============================================================

class Jugador:
    def __init__(self, nombre, equipo, x, y, genoma=None):
        self.nombre = nombre
        self.equipo = equipo
        self.x = x
        self.y = y
        self.hits = 4
        self.puntos_personales = 0
        self.puntos_por_kills = 0      # desglose: puntos ganados en combates
        self.puntos_por_defensa = 0    # desglose: puntos por sostener edificios
        self.destino = None
        self.cooldown_teletransporte_restante = 0

        # Genoma: [w1, w2, w3, w4, w5] -- si no se pasa uno ya evolucionado,
        # arranca con valores aleatorios (generación 0)
        self.genoma = genoma if genoma is not None else [random.uniform(-1, 1) for _ in range(5)]

        total_soldados = random.randint(18462, 26000)
        self.total_soldados_reserva = total_soldados  # baja cuando muere gente
        self.total_soldados_original = total_soldados  # referencia fija, no cambia

        if total_soldados < 21962:
            self.tier = "T7"
            poder_por_soldado = 915
        elif total_soldados < 25462:
            self.tier = "T8"
            poder_por_soldado = 1100
        else:
            self.tier = "T9"
            poder_por_soldado = 1350
        self.poder_por_soldado = poder_por_soldado
        self.poder_total = total_soldados * poder_por_soldado

        capacidad_1 = round(total_soldados * random.uniform(0.104, 0.164))
        self.escuadron_1 = Escuadron(self, capacidad_1, poder_por_soldado)
        capacidad_2 = round(total_soldados * random.uniform(0.065, 0.125))
        self.escuadron_2 = Escuadron(self, capacidad_2, poder_por_soldado)
        capacidad_3 = round(total_soldados * random.uniform(0.050, 0.110))
        self.escuadron_3 = Escuadron(self, capacidad_3, poder_por_soldado)

        # Ya restamos lo que salió con los 3 escuadrones de la reserva,
        # porque salen llenos desde el inicio
        self.total_soldados_reserva -= (capacidad_1 + capacidad_2 + capacidad_3)

    def escuadrones(self):
        return [self.escuadron_1, self.escuadron_2, self.escuadron_3]

    def reserva_disponible(self):
        return max(0, self.total_soldados_reserva)

    def esta_eliminado(self):
        """
        Un jugador queda fuera de juego solo si ya no le queda NINGÚN
        soldado -- ni en reserva ni en ningún escuadrón.
        """
        en_escuadrones = sum(e.soldados_actuales for e in self.escuadrones())
        return (self.total_soldados_reserva <= 0) and (en_escuadrones <= 0)

    def spawn_del_equipo(self):
        if self.equipo == "equipo_A":
            return SPAWN_EQUIPO_A
        else:
            return SPAWN_EQUIPO_B

    def teletransportarse(self, nueva_x, nueva_y, mapa):
        """
        Teletransporta al jugador (si no está en cooldown) y arrastra
        a sus 3 escuadrones con él, sin importar su estado actual.
        """
        if self.cooldown_teletransporte_restante > 0:
            return False

        self.x = nueva_x
        self.y = nueva_y

        for escuadron in self.escuadrones():
            escuadron.teletransportar_con_jugador(nueva_x, nueva_y)

        tiene_portal = False
        for edificio in mapa:
            if edificio.dueño == self.equipo and edificio.efecto_especial == "reduccion_cooldown":
                tiene_portal = True

        if tiene_portal:
            self.cooldown_teletransporte_restante = COOLDOWN_TELETRANSPORTE * 0.5
        else:
            self.cooldown_teletransporte_restante = COOLDOWN_TELETRANSPORTE

        return True

    def morir(self):
        """
        El jugador perdió su último hit. Vuelve al spawn de su equipo,
        sus hits se resetean a 4, y TODOS sus escuadrones se van con él
        de forma instantánea, sin importar en qué estaban.
        """
        spawn_x, spawn_y = self.spawn_del_equipo()
        self.x = spawn_x
        self.y = spawn_y
        self.hits = 4

        for escuadron in self.escuadrones():
            escuadron.teletransportar_con_jugador(spawn_x, spawn_y)

    def recibir_ataque_directo(self, jugador_atacante=None):
        """
        Sistema 2: un escuadrón enemigo llegó hasta el jugador.
        Siempre resta 1 hit, sin importar si tenía defensa o no.
        El atacante gana puntos por el hit, y un bono si completa la muerte.
        """
        self.hits -= 1

        if jugador_atacante is not None:
            jugador_atacante.puntos_personales += PUNTOS_POR_HIT
            jugador_atacante.puntos_por_kills += PUNTOS_POR_HIT

        if self.hits <= 0:
            if jugador_atacante is not None:
                jugador_atacante.puntos_personales += PUNTOS_POR_MUERTE
                jugador_atacante.puntos_por_kills += PUNTOS_POR_MUERTE
            self.morir()

    def actualizar_cooldown(self):
        if self.cooldown_teletransporte_restante > 0:
            self.cooldown_teletransporte_restante -= 1


# ============================================================
# DETECCIÓN Y RESOLUCIÓN DE COMBATE
# ============================================================

def buscar_defensores_en_edificio(edificio, equipo_atacante, todos_los_jugadores):
    """
    Retorna la lista de TODOS los escuadrones enemigos defendiendo
    activamente este edificio (puede haber hasta MAX_ESCUADRONES_POR_EDIFICIO).
    """
    defensores = []
    for jugador in todos_los_jugadores:
        if jugador.equipo == equipo_atacante:
            continue
        for escuadron in jugador.escuadrones():
            if escuadron.estado == "defendiendo" and escuadron.destino is edificio:
                defensores.append(escuadron)
    return defensores


def buscar_defensor_en_edificio(edificio, equipo_atacante, todos_los_jugadores):
    """Compatibilidad: retorna el primer defensor o None."""
    defensores = buscar_defensores_en_edificio(edificio, equipo_atacante, todos_los_jugadores)
    return defensores[0] if defensores else None


def calcular_poder_combate(escuadron, mapa):
    """
    Poder de combate REAL de un escuadrón en este instante, incluyendo
    los buffs/debuffs de los edificios especiales:
    - Reliquias de Guerra: +valor_efecto al poder de los ALIADOS que
      controlan el edificio (aplica a todo el equipo, no solo a quien
      lo defiende).
    - Altar Maldito: -valor_efecto al poder de los ENEMIGOS de quien
      lo controla.
    Ambos multiplicadores se acumulan sobre el poder base (soldados *
    poder_por_soldado).
    """
    equipo = escuadron.jugador_dueño.equipo
    equipo_enemigo = "equipo_B" if equipo == "equipo_A" else "equipo_A"
    poder = escuadron.poder_actual()

    for edificio in mapa:
        if edificio.dueño == equipo and edificio.efecto_especial == "buff_aliados":
            poder *= (1 + edificio.valor_efecto)
        if edificio.dueño == equipo_enemigo and edificio.efecto_especial == "debuff_enemigos":
            poder *= (1 - edificio.valor_efecto)

    return poder


def resolver_llegada_a_edificio(escuadron_atacante, edificio, todos_los_jugadores, mapa, minuto_actual=None):
    """
    Se llama cuando un escuadrón termina su viaje hacia un Edificio.

    Reglas (según el juego real):
    - Si el edificio aún no está desbloqueado, no se puede esperar encima:
      el escuadrón se regresa a base.
    - Si no hay defensores: captura automática, se queda defendiendo.
    - Si hay VARIOS defensores enemigos: el atacante los enfrenta EN
      SECUENCIA con el poder que le vaya quedando. Solo captura el
      edificio si elimina a todos; si pierde en cualquier pelea, se
      regresa. Nunca coexisten defensores de equipos distintos.

    El poder usado en combate incluye los buffs/debuffs activos
    (Reliquias de Guerra, Altar Maldito) -- ver calcular_poder_combate().
    """
    equipo_atacante = escuadron_atacante.jugador_dueño.equipo

    # Edificio aún no desbloqueado: no existe "esperar al lado"
    if minuto_actual is not None and edificio.minuto_aparicion > minuto_actual:
        escuadron_atacante.regresar_a_base()
        return

    defensores = buscar_defensores_en_edificio(edificio, equipo_atacante, todos_los_jugadores)

    if not defensores:
        # Nadie defendiendo -> captura automática
        edificio.dueño = equipo_atacante
        escuadron_atacante.destino = edificio
        escuadron_atacante.estado = "defendiendo"
        return

    # Combates en secuencia contra cada defensor, con el poder restante
    for defensor in defensores:
        poder_a = calcular_poder_combate(escuadron_atacante, mapa)
        poder_b = calcular_poder_combate(defensor, mapa)

        if poder_a <= 0:
            break  # ya no le queda nada con qué pelear

        ganador = resolver_combate(poder_a, poder_b)

        # Puntos por matar: el GANADOR gana los puntos completos del
        # combate; el PERDEDOR gana solo una fracción (FRACCION_PUNTOS_PERDEDOR).
        poder_eliminado = min(poder_a, poder_b)
        puntos_combate = poder_eliminado / ESCALA_PUNTOS_KILL

        if ganador == "A":
            # El defensor cae; el ganador conserva una fracción de sus soldados
            escuadron_atacante.jugador_dueño.puntos_personales += puntos_combate
            escuadron_atacante.jugador_dueño.puntos_por_kills += puntos_combate
            defensor.jugador_dueño.puntos_personales += puntos_combate * FRACCION_PUNTOS_PERDEDOR
            defensor.jugador_dueño.puntos_por_kills += puntos_combate * FRACCION_PUNTOS_PERDEDOR

            defensor.soldados_actuales = 0
            defensor.regresar_a_base()
            escuadron_atacante.soldados_actuales = round(
                escuadron_atacante.soldados_actuales * FRACCION_SOLDADOS_SOBREVIVIENTES)
        else:
            # El atacante cae; el defensor (ganador) conserva una fracción
            defensor.jugador_dueño.puntos_personales += puntos_combate
            defensor.jugador_dueño.puntos_por_kills += puntos_combate
            escuadron_atacante.jugador_dueño.puntos_personales += puntos_combate * FRACCION_PUNTOS_PERDEDOR
            escuadron_atacante.jugador_dueño.puntos_por_kills += puntos_combate * FRACCION_PUNTOS_PERDEDOR

            escuadron_atacante.soldados_actuales = 0
            escuadron_atacante.regresar_a_base()
            defensor.soldados_actuales = round(
                defensor.soldados_actuales * FRACCION_SOLDADOS_SOBREVIVIENTES)
            return  # perdió: se va, el edificio queda como estaba

    # Si llegó aquí, eliminó a TODOS los defensores (y le queda algo)
    if escuadron_atacante.poder_actual() > 0:
        edificio.dueño = equipo_atacante
        escuadron_atacante.destino = edificio
        escuadron_atacante.estado = "defendiendo"
    else:
        # Caso límite: ganó la última pelea pero quedó exactamente en 0
        escuadron_atacante.regresar_a_base()


def resolver_llegada_a_jugador(escuadron_atacante, jugador_destino, mapa):
    """
    Se llama cuando un escuadrón termina su viaje hacia un Jugador.
    Puede ser: (a) está regresando a SU PROPIO jugador (relleno de base),
    o (b) llegó a atacar a un jugador ENEMIGO (Sistema 2), en solitario.

    El ataque a un jugador enemigo SÍ pelea contra su mejor escuadrón
    disponible en base (ver escuadron_defensor_disponible): si no tiene
    ninguno, el golpe es gratis (queda expuesto); si tiene uno y lo
    vence, el golpe conecta igual y la defensa cae; si el defensor
    gana, repele el ataque -- el atacante cae sin conectar ningún golpe.
    """
    equipo_atacante = escuadron_atacante.jugador_dueño.equipo

    if jugador_destino.equipo == equipo_atacante:
        # Es su propio jugador -> llegó de vuelta a la base, se rellena
        escuadron_atacante.estado = "en_base"
        escuadron_atacante.destino = None
        escuadron_atacante.rellenar_desde_reserva()
        return

    defensor = escuadron_defensor_disponible(jugador_destino, mapa)

    if defensor is None:
        # Sin defensa disponible -> expuesto, golpe gratis
        jugador_destino.recibir_ataque_directo(escuadron_atacante.jugador_dueño)
        escuadron_atacante.regresar_a_base()
        return

    poder_atacante = calcular_poder_combate(escuadron_atacante, mapa)
    poder_defensor = calcular_poder_combate(defensor, mapa)
    ganador = resolver_combate(poder_atacante, poder_defensor)
    poder_eliminado = min(poder_atacante, poder_defensor)
    puntos_combate = poder_eliminado / ESCALA_PUNTOS_KILL

    if ganador == "A":
        # El atacante vence a la defensa: el golpe conecta Y cae el defensor
        escuadron_atacante.jugador_dueño.puntos_personales += puntos_combate
        escuadron_atacante.jugador_dueño.puntos_por_kills += puntos_combate
        defensor.jugador_dueño.puntos_personales += puntos_combate * FRACCION_PUNTOS_PERDEDOR
        defensor.jugador_dueño.puntos_por_kills += puntos_combate * FRACCION_PUNTOS_PERDEDOR

        defensor.soldados_actuales = 0
        defensor.regresar_a_base()
        escuadron_atacante.soldados_actuales = round(
            escuadron_atacante.soldados_actuales * FRACCION_SOLDADOS_SOBREVIVIENTES)

        jugador_destino.recibir_ataque_directo(escuadron_atacante.jugador_dueño)
        escuadron_atacante.regresar_a_base()
    else:
        # La defensa repele: ningún golpe conecta, el atacante cae
        defensor.jugador_dueño.puntos_personales += puntos_combate
        defensor.jugador_dueño.puntos_por_kills += puntos_combate
        escuadron_atacante.jugador_dueño.puntos_personales += puntos_combate * FRACCION_PUNTOS_PERDEDOR
        escuadron_atacante.jugador_dueño.puntos_por_kills += puntos_combate * FRACCION_PUNTOS_PERDEDOR

        defensor.soldados_actuales = round(defensor.soldados_actuales * FRACCION_SOLDADOS_SOBREVIVIENTES)
        escuadron_atacante.soldados_actuales = 0
        escuadron_atacante.regresar_a_base()


def resolver_llegada_grupal_edificio(escuadrones_grupo, edificio, todos_los_jugadores, mapa, minuto_actual=None):
    """
    Versión de resolver_llegada_a_edificio para un RALLY: varios
    escuadrones llegan al mismo tick y pelean como UNA sola fuerza
    combinada contra el poder combinado de todos los defensores,
    en un único enfrentamiento (no en cadena uno por uno).
    """
    equipo_atacante = escuadrones_grupo[0].jugador_dueño.equipo
    for esc in escuadrones_grupo:
        esc.rally = None  # el rally ya cumplió su propósito

    if minuto_actual is not None and edificio.minuto_aparicion > minuto_actual:
        for esc in escuadrones_grupo:
            esc.regresar_a_base()
        return

    defensores = buscar_defensores_en_edificio(edificio, equipo_atacante, todos_los_jugadores)

    if not defensores:
        # Nadie defendiendo -> captura automática, todo el grupo se queda
        edificio.dueño = equipo_atacante
        for esc in escuadrones_grupo:
            esc.destino = edificio
            esc.estado = "defendiendo"
        return

    poder_atacante_total = sum(calcular_poder_combate(e, mapa) for e in escuadrones_grupo)
    poder_defensor_total = sum(calcular_poder_combate(d, mapa) for d in defensores)

    ganador = resolver_combate(poder_atacante_total, poder_defensor_total)
    poder_eliminado = min(poder_atacante_total, poder_defensor_total)
    puntos_combate_total = poder_eliminado / ESCALA_PUNTOS_KILL

    if ganador == "A":
        # Gana el grupo atacante: cada defensor cae; cada atacante conserva
        # una fracción de SUS PROPIOS soldados (misma regla que 1 vs 1,
        # aplicada individualmente a cada miembro del grupo)
        parte_ganador = puntos_combate_total / len(escuadrones_grupo)
        parte_perdedor = (puntos_combate_total * FRACCION_PUNTOS_PERDEDOR) / len(defensores)

        for esc in escuadrones_grupo:
            esc.jugador_dueño.puntos_personales += parte_ganador
            esc.jugador_dueño.puntos_por_kills += parte_ganador
            esc.soldados_actuales = round(esc.soldados_actuales * FRACCION_SOLDADOS_SOBREVIVIENTES)
            esc.destino = edificio
            esc.estado = "defendiendo"

        for d in defensores:
            d.jugador_dueño.puntos_personales += parte_perdedor
            d.jugador_dueño.puntos_por_kills += parte_perdedor
            d.soldados_actuales = 0
            d.regresar_a_base()

        edificio.dueño = equipo_atacante
    else:
        # Gana el grupo defensor: cada atacante cae; cada defensor
        # conserva una fracción de sus propios soldados
        parte_ganador = puntos_combate_total / len(defensores)
        parte_perdedor = (puntos_combate_total * FRACCION_PUNTOS_PERDEDOR) / len(escuadrones_grupo)

        for d in defensores:
            d.jugador_dueño.puntos_personales += parte_ganador
            d.jugador_dueño.puntos_por_kills += parte_ganador
            d.soldados_actuales = round(d.soldados_actuales * FRACCION_SOLDADOS_SOBREVIVIENTES)

        for esc in escuadrones_grupo:
            esc.jugador_dueño.puntos_personales += parte_perdedor
            esc.jugador_dueño.puntos_por_kills += parte_perdedor
            esc.soldados_actuales = 0
            esc.regresar_a_base()
        # el edificio se queda como estaba


def resolver_llegada_grupal_jugador(escuadrones_grupo, jugador_destino, mapa):
    """
    Versión de resolver_llegada_a_jugador para un RALLY: todo el grupo
    pelea como una sola fuerza combinada contra el mejor escuadrón que
    el jugador enemigo tenga disponible en base (ver
    escuadron_defensor_disponible). Si el grupo vence (o no había
    defensa disponible), aplica tantos hits como escuadrones lo
    componen -- golpe combinado, puede tumbarlo de una en vez de
    necesitar varias oleadas espaciadas en el tiempo. Si el defensor
    gana, repele TODO el rally sin que conecte ningún golpe.
    """
    equipo_atacante = escuadrones_grupo[0].jugador_dueño.equipo

    if jugador_destino.equipo == equipo_atacante:
        # No debería pasar (los rallies solo se abren contra enemigos),
        # pero por seguridad: cada uno vuelve y se rellena individualmente
        for esc in escuadrones_grupo:
            esc.estado = "en_base"
            esc.destino = None
            esc.rellenar_desde_reserva()
        return

    def _aplicar_golpes_combinados():
        total_hits_grupo = len(escuadrones_grupo)
        for esc in escuadrones_grupo:
            esc.jugador_dueño.puntos_personales += PUNTOS_POR_HIT
            esc.jugador_dueño.puntos_por_kills += PUNTOS_POR_HIT
        if total_hits_grupo >= jugador_destino.hits:
            bono_repartido = PUNTOS_POR_MUERTE / len(escuadrones_grupo)
            for esc in escuadrones_grupo:
                esc.jugador_dueño.puntos_personales += bono_repartido
                esc.jugador_dueño.puntos_por_kills += bono_repartido
            jugador_destino.morir()
        else:
            jugador_destino.hits -= total_hits_grupo

    defensor = escuadron_defensor_disponible(jugador_destino, mapa)

    if defensor is None:
        # Sin defensa disponible -> expuesto, golpe combinado gratis
        _aplicar_golpes_combinados()
        for esc in escuadrones_grupo:
            esc.regresar_a_base()
        return

    poder_atacante_total = sum(calcular_poder_combate(e, mapa) for e in escuadrones_grupo)
    poder_defensor = calcular_poder_combate(defensor, mapa)
    ganador = resolver_combate(poder_atacante_total, poder_defensor)
    poder_eliminado = min(poder_atacante_total, poder_defensor)
    puntos_combate_total = poder_eliminado / ESCALA_PUNTOS_KILL

    if ganador == "A":
        # El grupo vence a la defensa: el golpe combinado conecta Y cae el defensor
        parte_ganador = puntos_combate_total / len(escuadrones_grupo)
        for esc in escuadrones_grupo:
            esc.jugador_dueño.puntos_personales += parte_ganador
            esc.jugador_dueño.puntos_por_kills += parte_ganador
            esc.soldados_actuales = round(esc.soldados_actuales * FRACCION_SOLDADOS_SOBREVIVIENTES)

        defensor.jugador_dueño.puntos_personales += puntos_combate_total * FRACCION_PUNTOS_PERDEDOR
        defensor.jugador_dueño.puntos_por_kills += puntos_combate_total * FRACCION_PUNTOS_PERDEDOR
        defensor.soldados_actuales = 0
        defensor.regresar_a_base()

        _aplicar_golpes_combinados()
        for esc in escuadrones_grupo:
            esc.regresar_a_base()
    else:
        # La defensa repele TODO el rally: ningún golpe conecta
        defensor.jugador_dueño.puntos_personales += puntos_combate_total
        defensor.jugador_dueño.puntos_por_kills += puntos_combate_total
        defensor.soldados_actuales = round(defensor.soldados_actuales * FRACCION_SOLDADOS_SOBREVIVIENTES)

        parte_perdedor = (puntos_combate_total * FRACCION_PUNTOS_PERDEDOR) / len(escuadrones_grupo)
        for esc in escuadrones_grupo:
            esc.jugador_dueño.puntos_personales += parte_perdedor
            esc.jugador_dueño.puntos_por_kills += parte_perdedor
            esc.soldados_actuales = 0
            esc.regresar_a_base()


def sumar_puntos_personales(mapa_activo, todos_los_jugadores):
    """
    Se llama una vez por tick. Cada jugador con un escuadrón defendiendo
    un edificio gana la tasa_personal completa de ese edificio (no se
    divide entre varios defensores).
    """
    for edificio in mapa_activo:
        if edificio.dueño is None:
            continue
        for jugador in todos_los_jugadores:
            for escuadron in jugador.escuadrones():
                if escuadron.estado == "defendiendo" and escuadron.destino is edificio:
                    jugador.puntos_personales += edificio.tasa_personal
                    jugador.puntos_por_defensa += edificio.tasa_personal


def sanar_reservas(mapa_activo, todos_los_jugadores, tick):
    """
    Se llama una vez por tick. Cada `INTERVALO_CURACION_SEGUNDOS`, cada
    Tienda de Curación que un equipo controle regenera
    SOLDADOS_CURADOS_POR_TICK soldados a la RESERVA de cada jugador de
    ese equipo (no a los escuadrones directamente). Si el equipo controla
    varias tiendas, el efecto se suma (ej. 4 tiendas -> 60 cada 10 seg).
    Nunca supera la reserva original del jugador.
    """
    if tick % INTERVALO_CURACION_SEGUNDOS != 0:
        return

    for equipo in ("equipo_A", "equipo_B"):
        tiendas_controladas = sum(
            1 for e in mapa_activo
            if e.dueño == equipo and e.efecto_especial == "curacion"
        )
        if tiendas_controladas == 0:
            continue

        regen = tiendas_controladas * SOLDADOS_CURADOS_POR_TICK
        for jugador in todos_los_jugadores:
            if jugador.equipo == equipo:
                jugador.total_soldados_reserva = min(
                    jugador.total_soldados_original,
                    jugador.total_soldados_reserva + regen,
                )


def procesar_llegadas(todos_los_jugadores, mapa, minuto_actual=None):
    """
    Recorre todos los escuadrones del mapa; los que llegaron a destino
    este tick ("llego_a_destino") se resuelven según el tipo de destino.

    Los que llegaron como parte de un RALLY (esc.rally is not None) se
    agrupan por rally y se resuelven JUNTOS en un solo evento (combate
    combinado o ataque conjunto a jugador). Los que llegaron solos se
    resuelven individualmente, como siempre.
    """
    solos = []
    por_rally = {}

    for jugador in todos_los_jugadores:
        for escuadron in jugador.escuadrones():
            if escuadron.estado == "llego_a_destino":
                if escuadron.rally is not None:
                    por_rally.setdefault(escuadron.rally, []).append(escuadron)
                else:
                    solos.append(escuadron)

    for escuadron in solos:
        if isinstance(escuadron.destino, Edificio):
            resolver_llegada_a_edificio(escuadron, escuadron.destino,
                                         todos_los_jugadores, mapa, minuto_actual)
        elif isinstance(escuadron.destino, Jugador):
            resolver_llegada_a_jugador(escuadron, escuadron.destino, mapa)

    for rally_obj, grupo in por_rally.items():
        objetivo = grupo[0].destino
        if isinstance(objetivo, Edificio):
            resolver_llegada_grupal_edificio(grupo, objetivo, todos_los_jugadores, mapa, minuto_actual)
        elif isinstance(objetivo, Jugador):
            resolver_llegada_grupal_jugador(grupo, objetivo, mapa)


# ============================================================
# AGENTE EVOLUTIVO (basado en genoma)
# ============================================================

def decidir_accion_genoma(jugador, mapa, todos_los_jugadores, rallies, tick_actual):
    """
    Reemplazo del agente tonto: cada escuadrón "en_base" evalúa TODAS
    las opciones disponibles (edificios libres, edificios enemigos
    defendidos, jugadores enemigos) usando el genoma del jugador, y
    elige la de mayor puntaje.

    - Edificio LIBRE: captura instantánea al llegar, sin necesidad de
      grupo -- va solo.
    - Edificio ENEMIGO defendido: se ataca vía RALLY (se une a uno
      existente del equipo hacia ese edificio, o abre uno nuevo) --
      atacarlo en solitario contra varios defensores casi siempre pierde.
    - Edificio PROPIO ya controlado: puede reforzarlo mandando un
      escuadrón adicional como defensor (hasta MAX_ESCUADRONES_POR_EDIFICIO),
      valorado por w5 -- sin esto, cada edificio quedaba con un único
      defensor para siempre, sin importar cuánto valiera, porque el
      agente nunca volvía a evaluar los edificios que ya tenía.
    - Jugador enemigo: si el genoma valora la coordinación (w4 > 0),
      intenta usar rally también (golpe combinado = más probable que
      lo saque de combate de una vez); si no, ataca solo como siempre.
    """
    w1, w2, w3, w4 = jugador.genoma[:4]

    for escuadron in jugador.escuadrones():
        if escuadron.estado != "en_base":
            continue

        mejor_opcion = None
        mejor_score = None
        mejor_tipo = None  # "edificio_libre", "edificio_enemigo" o "jugador"

        for edificio in mapa:
            if edificio.dueño is None:
                asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)
                if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                    continue
                if jugador_ya_asignado_a(edificio, jugador):
                    continue  # un escuadrón por jugador por edificio (salvo camps)
                score = puntaje_edificio(escuadron, jugador, edificio, todos_los_jugadores)
                if mejor_score is None or score > mejor_score:
                    mejor_score = score
                    mejor_opcion = edificio
                    mejor_tipo = "edificio_libre"
            elif edificio.dueño != jugador.equipo:
                asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)
                if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                    continue
                if jugador_ya_asignado_a(edificio, jugador):
                    continue
                score = puntaje_edificio_enemigo(escuadron, jugador, edificio, mapa, todos_los_jugadores)
                if mejor_score is None or score > mejor_score:
                    mejor_score = score
                    mejor_opcion = edificio
                    mejor_tipo = "edificio_enemigo"
            else:  # edificio.dueño == jugador.equipo -- ya es mío, ¿reforzarlo?
                asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)
                if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                    continue
                if jugador_ya_asignado_a(edificio, jugador):
                    continue
                score = puntaje_reforzar_edificio_propio(escuadron, jugador, edificio, todos_los_jugadores)
                if mejor_score is None or score > mejor_score:
                    mejor_score = score
                    mejor_opcion = edificio
                    mejor_tipo = "edificio_propio"

        for enemigo in todos_los_jugadores:
            if enemigo.equipo == jugador.equipo:
                continue
            asignados = contar_escuadrones_asignados(enemigo, jugador.equipo, todos_los_jugadores)
            if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                continue
            if jugador_ya_asignado_a(enemigo, jugador):
                continue  # tampoco puede mandar 2 escuadrones al mismo jugador
            score = puntaje_jugador_enemigo(escuadron, jugador, enemigo, mapa, todos_los_jugadores)
            if mejor_score is None or score > mejor_score:
                mejor_score = score
                mejor_opcion = enemigo
                mejor_tipo = "jugador"

        if mejor_opcion is None:
            continue

        if mejor_tipo == "edificio_libre" or mejor_tipo == "edificio_propio":
            escuadron.enviar_a_atacar(mejor_opcion)

        elif mejor_tipo == "edificio_enemigo":
            defensores = buscar_defensores_en_edificio(mejor_opcion, jugador.equipo, todos_los_jugadores)
            if not defensores:
                # sin defensores reales (huérfano) -> captura directa, no hace falta rally
                escuadron.enviar_a_atacar(mejor_opcion)
            else:
                rally = buscar_rally_abierto(rallies, mejor_opcion, jugador.equipo)
                if rally is not None:
                    escuadron.unirse_a_rally(rally)
                else:
                    nuevo_rally = Rally(mejor_opcion, jugador.equipo, tick_actual, escuadron)
                    escuadron.destino = mejor_opcion
                    escuadron.estado = "esperando_rally"
                    escuadron.rally = nuevo_rally
                    rallies.append(nuevo_rally)

        else:  # "jugador"
            if w4 > 0:
                rally = buscar_rally_abierto(rallies, mejor_opcion, jugador.equipo)
                if rally is not None:
                    escuadron.unirse_a_rally(rally)
                else:
                    nuevo_rally = Rally(mejor_opcion, jugador.equipo, tick_actual, escuadron)
                    escuadron.destino = mejor_opcion
                    escuadron.estado = "esperando_rally"
                    escuadron.rally = nuevo_rally
                    rallies.append(nuevo_rally)
            else:
                escuadron.enviar_a_atacar_jugador(mejor_opcion)


def posicion_libre_cercana(x, y, mapa, todos_los_jugadores):
    """
    Busca la posición libre más cercana a (x, y) respetando la separación
    mínima con todos los edificios y jugadores. Prueba en anillos cada vez
    más amplios alrededor del punto deseado.
    """
    ocupados = [(e.x, e.y) for e in mapa] + [(j.x, j.y) for j in todos_los_jugadores]

    def esta_libre(px, py):
        for ox, oy in ocupados:
            if distancia((px, py), (ox, oy)) < SEPARACION_MINIMA:
                return False
        return True

    if esta_libre(x, y):
        return max(0, min(1000, x)), max(0, min(1000, y))

    # Buscar en anillos alrededor: radio 15, 30, 45... y 8 direcciones por anillo
    for radio in range(15, 200, 15):
        for angulo_paso in range(8):
            angulo = angulo_paso * (math.pi / 4)
            px = x + radio * math.cos(angulo)
            py = y + radio * math.sin(angulo)
            px = max(0, min(1000, px))
            py = max(0, min(1000, py))
            if esta_libre(px, py):
                return px, py

    return max(0, min(1000, x)), max(0, min(1000, y))  # último recurso


def decidir_teletransporte(jugador, mapa, todos_los_jugadores):
    """
    Si el jugador no está en cooldown, revisa si vale la pena reposicionarse.

    En vez de saltar al ÚNICO mejor objetivo (lo cual dejaba a los otros
    2 escuadrones caminando desde ahí hacia sus propios objetivos), evalúa
    los CANTIDAD_OBJETIVOS_TELEPORT mejores objetivos distintos disponibles
    y salta al CENTROIDE (punto promedio) de esos objetivos -- una posición
    que acorta el viaje de varios escuadrones a la vez, no solo de uno.

    Solo se BLOQUEA si tiene un escuadrón "defendiendo" -- eso sí es una
    conquista ya lograda que se perdería si lo arrastra. Escuadrones
    "viajando_ataque" / "viajando_ataque_jugador" / "regresando_base" NO
    bloquean: interrumpir un viaje a pie para saltar más cerca del
    objetivo y llegar antes es estrictamente mejor que seguir caminando
    toda la distancia original. Al llegar, decidir_accion() vuelve a
    evaluar el mejor objetivo desde la nueva posición (puede ser el
    mismo que ya llevaba, ahora mucho más cerca, u otro mejor).
    """
    if jugador.cooldown_teletransporte_restante > 0:
        return

    escuadrones = jugador.escuadrones()
    ESTADOS_QUE_BLOQUEAN = ("defendiendo",)
    if any(e.estado in ESTADOS_QUE_BLOQUEAN for e in escuadrones):
        return  # ya conquistó algo -- no vale la pena arrastrarlo

    # El salto siempre parte de la posición ACTUAL del jugador (no de la
    # de un escuadrón específico, que ahora puede estar a medio camino
    # viajando). Usamos un objeto liviano con esa posición y el poder
    # del escuadrón más fuerte disponible, solo para que las funciones
    # de puntaje (que esperan un "escuadron" con .x/.y/.poder_actual())
    # puedan reusarse sin cambios.
    class _ReferenciaSalto:
        def __init__(self, x, y, poder, jugador_dueño):
            self.x = x
            self.y = y
            self._poder = poder
            self.jugador_dueño = jugador_dueño

        def poder_actual(self):
            return self._poder

    mas_fuerte = max(escuadrones, key=lambda e: e.poder_actual())
    referencia = _ReferenciaSalto(jugador.x, jugador.y, mas_fuerte.poder_actual(), jugador)

    candidatos = []  # (score, x, y)

    for edificio in mapa:
        if edificio.dueño is None:
            asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)
            if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                continue
            score = puntaje_edificio(referencia, jugador, edificio, todos_los_jugadores)
            candidatos.append((score, edificio.x, edificio.y))
        elif edificio.dueño == jugador.equipo:
            asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)
            if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                continue
            score = puntaje_reforzar_edificio_propio(referencia, jugador, edificio, todos_los_jugadores)
            candidatos.append((score, edificio.x, edificio.y))

    for enemigo in todos_los_jugadores:
        if enemigo.equipo == jugador.equipo:
            continue
        asignados = contar_escuadrones_asignados(enemigo, jugador.equipo, todos_los_jugadores)
        if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
            continue
        score = puntaje_jugador_enemigo(referencia, jugador, enemigo, mapa, todos_los_jugadores)
        candidatos.append((score, enemigo.x, enemigo.y))

    if not candidatos:
        return

    candidatos.sort(key=lambda c: c[0], reverse=True)
    cuantos = min(CANTIDAD_OBJETIVOS_TELEPORT, len(candidatos), len(escuadrones))
    mejores = candidatos[:cuantos]

    centro_x = sum(c[1] for c in mejores) / len(mejores)
    centro_y = sum(c[2] for c in mejores) / len(mejores)

    dist_actual = distancia((jugador.x, jugador.y), (centro_x, centro_y))
    if dist_actual > UMBRAL_TELETRANSPORTE:
        nueva_x, nueva_y = posicion_libre_cercana(centro_x, centro_y, mapa, todos_los_jugadores)
        jugador.teletransportarse(nueva_x, nueva_y, mapa)


# ============================================================
# AGENTE TONTO -- se deja como referencia / comparación
# ============================================================

ESTADOS_COMPROMETIDOS = ("viajando_ataque", "defendiendo", "viajando_ataque_jugador", "esperando_rally")


def contar_escuadrones_asignados(destino_objetivo, equipo, todos_los_jugadores):
    """
    Cuenta cuántos escuadrones de un equipo ya están yendo hacia,
    defendiendo/atacando, o REUNIÉNDOSE (rally) hacia este destino
    (edificio o jugador enemigo). Sirve para el límite de defensa, el
    límite de ataque conjunto, y para el término w4 del genoma
    (coordinación).
    """
    contador = 0
    for j in todos_los_jugadores:
        if j.equipo != equipo:
            continue
        for esc in j.escuadrones():
            if esc.destino is destino_objetivo and esc.estado in ESTADOS_COMPROMETIDOS:
                contador += 1
    return contador


def jugador_ya_asignado_a(destino_objetivo, jugador):
    """
    Regla del juego: un jugador solo puede mandar UN escuadrón a cada
    edificio/objetivo... EXCEPTO a los campamentos, donde sí puede mandar
    varios a la vez (para recolectar más).
    Retorna True si este jugador ya tiene un escuadrón asignado a ese
    destino y por lo tanto NO puede mandar otro.
    """
    if isinstance(destino_objetivo, Edificio) and "campamento" in destino_objetivo.nombre:
        return False  # los campamentos no tienen esta restricción
    for esc in jugador.escuadrones():
        if esc.destino is destino_objetivo and esc.estado in ESTADOS_COMPROMETIDOS:
            return True
    return False


def puntaje_edificio(escuadron, jugador, edificio, todos_los_jugadores):
    """Qué tan atractivo le parece a este genoma ir a este edificio (LIBRE)."""
    w1, w2, w3, w4 = jugador.genoma[:4]

    valor_puntos = edificio.tasa_alianza
    try:
        cercania = 15 / distancia((escuadron.x, escuadron.y), (edificio.x, edificio.y))
    except ZeroDivisionError:
        cercania = 15

    aliados_ya_asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)

    score = w1 * valor_puntos + w2 * cercania + w4 * aliados_ya_asignados
    return score


def puntaje_reforzar_edificio_propio(escuadron, jugador, edificio, todos_los_jugadores):
    """
    Qué tan atractivo le parece a este genoma mandar un escuadrón
    ADICIONAL a un edificio que su equipo ya controla, sumándose como
    defensor (hasta MAX_ESCUADRONES_POR_EDIFICIO). w5 gobierna esto de
    forma independiente a w1 (que solo mide qué tanto valora CAPTURAR
    edificios libres) -- un genoma puede evolucionar para valorar
    capturar y defender de forma distinta.
    """
    w1, w2, w3, w4, w5 = jugador.genoma

    valor_puntos = edificio.tasa_alianza
    try:
        cercania = 15 / distancia((escuadron.x, escuadron.y), (edificio.x, edificio.y))
    except ZeroDivisionError:
        cercania = 15

    defensores_propios_ya_asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)

    score = w5 * valor_puntos + w2 * cercania + w4 * defensores_propios_ya_asignados
    return score


def puntaje_edificio_enemigo(escuadron, jugador, edificio, mapa, todos_los_jugadores):
    """
    Qué tan atractivo le parece a este genoma intentar RECAPTURAR un
    edificio que ya controla el equipo enemigo. Considera el poder
    combinado de TODOS sus defensores actuales (no solo uno), ya que
    el ataque se va a resolver en grupo vía rally.
    """
    w1, w2, w3, w4 = jugador.genoma[:4]

    valor_puntos = edificio.tasa_alianza
    try:
        cercania = 15 / distancia((escuadron.x, escuadron.y), (edificio.x, edificio.y))
    except ZeroDivisionError:
        cercania = 15

    defensores = buscar_defensores_en_edificio(edificio, jugador.equipo, todos_los_jugadores)
    poder_defensa_total = sum(calcular_poder_combate(d, mapa) for d in defensores)
    mi_poder = calcular_poder_combate(escuadron, mapa)
    poder_relativo = (mi_poder - poder_defensa_total) / 1_000_000

    aliados_ya_asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)

    score = w1 * valor_puntos + w2 * cercania + w3 * poder_relativo + w4 * aliados_ya_asignados
    return score


def escuadron_defensor_disponible(jugador_enemigo, mapa):
    """
    Retorna el escuadrón más fuerte que el jugador enemigo tiene
    disponible AHORA MISMO en su base (listo para defenderlo si lo
    atacan directamente), o None si no tiene ninguno -- en ese caso
    queda totalmente expuesto y el golpe es gratis, igual que un
    edificio sin defensores.

    Es el mismo escuadrón que de verdad pelea en
    resolver_llegada_a_jugador()/resolver_llegada_grupal_jugador()
    cuando lo alcanza un ataque directo (confirmado que en el juego
    real SÍ hay combate real, no un golpe garantizado). Antes de esto,
    la "defensa disponible" solo se usaba para puntuar la decisión de
    atacar (puntaje_jugador_enemigo) pero el combate real nunca la
    consultaba -- un genoma podía evitar "por las puras" a alguien
    bien defendido sin que esa defensa tuviera ningún efecto real.
    """
    mejor = None
    mejor_poder = 0
    for esc in jugador_enemigo.escuadrones():
        if esc.estado == "en_base":
            poder = calcular_poder_combate(esc, mapa)
            if poder > mejor_poder:
                mejor_poder = poder
                mejor = esc
    return mejor


def poder_maximo_disponible(jugador_enemigo, mapa):
    """
    Retorna el poder de combate (ya con buffs/debuffs aplicados) del
    escuadrón más fuerte que tiene el jugador enemigo disponible AHORA
    MISMO en su base (listo para defenderse). Si no tiene ninguno en
    base, retorna 0 (está totalmente expuesto). Envoltorio de
    escuadron_defensor_disponible() para quien solo necesita el número.
    """
    defensor = escuadron_defensor_disponible(jugador_enemigo, mapa)
    return calcular_poder_combate(defensor, mapa) if defensor is not None else 0


def puntaje_jugador_enemigo(escuadron, jugador, enemigo, mapa, todos_los_jugadores):
    """Qué tan atractivo le parece a este genoma atacar a este jugador enemigo."""
    w1, w2, w3, w4 = jugador.genoma[:4]

    valor_puntos = 0  # atacar un jugador no da puntos de edificio directos
    try:
        cercania = 15 / distancia((escuadron.x, escuadron.y), (enemigo.x, enemigo.y))
    except ZeroDivisionError:
        cercania = 15

    mi_poder = calcular_poder_combate(escuadron, mapa)
    poder_defensa_enemiga = poder_maximo_disponible(enemigo, mapa)
    poder_relativo = (mi_poder - poder_defensa_enemiga) / 1_000_000

    aliados_ya_asignados = contar_escuadrones_asignados(enemigo, jugador.equipo, todos_los_jugadores)

    score = w1 * valor_puntos + w2 * cercania + w3 * poder_relativo + w4 * aliados_ya_asignados
    return score


def decidir_accion_agente_tonto(jugador, mapa, todos_los_jugadores, rallies=None, tick_actual=None):
    """
    Regla fija (agente de referencia, sin rally ni recaptura de edificios
    enemigos -- se deja simple a propósito para comparar contra el
    agente evolutivo). `rallies` y `tick_actual` se ignoran, están solo
    para que la firma sea intercambiable con decidir_accion_genoma.

    Cada escuadrón "en_base" va al edificio libre más cercano que no
    haya alcanzado el límite de escuadrones asignados; si no hay
    ninguno libre disponible, va al jugador enemigo más cercano.
    """
    for escuadron in jugador.escuadrones():
        if escuadron.estado != "en_base":
            continue

        mejor_libre = None
        menor_distancia_libre = None
        for edificio in mapa:
            if edificio.dueño is None:
                ya_asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)
                if ya_asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                    continue
                if jugador_ya_asignado_a(edificio, jugador):
                    continue  # un escuadrón por jugador por edificio (salvo camps)
                d = distancia((escuadron.x, escuadron.y), (edificio.x, edificio.y))
                if menor_distancia_libre is None or d < menor_distancia_libre:
                    menor_distancia_libre = d
                    mejor_libre = edificio
        if mejor_libre is not None:
            escuadron.enviar_a_atacar(mejor_libre)
            continue

        mejor_enemigo = None
        menor_distancia_enemigo = None
        for k in todos_los_jugadores:
            if k.equipo != jugador.equipo:
                d = distancia((escuadron.x, escuadron.y), (k.x, k.y))
                if menor_distancia_enemigo is None or d < menor_distancia_enemigo:
                    menor_distancia_enemigo = d
                    mejor_enemigo = k
        if mejor_enemigo is not None:
            escuadron.enviar_a_atacar_jugador(mejor_enemigo)


# ============================================================
# BUCLE PRINCIPAL DE SIMULACIÓN
# ============================================================

def _foto_del_estado(tick, minuto_actual, puntos_A, puntos_B, mapa, jugadores):
    return {
        "tick": tick,
        "minuto": minuto_actual,
        "puntos_A": round(puntos_A),
        "puntos_B": round(puntos_B),
        "edificios": [
            {"nombre": e.nombre, "x": e.x, "y": e.y, "dueño": e.dueño,
             "activo": e.minuto_aparicion <= minuto_actual}
            for e in mapa
        ],
        "escuadrones": [
            {"jugador": j.nombre, "equipo": j.equipo, "x": round(esc.x, 1),
             "y": round(esc.y, 1), "estado": esc.estado,
             "soldados": esc.soldados_actuales}
            for j in jugadores for esc in j.escuadrones()
            if esc.estado != "en_base"
        ],
        "jugadores_pos": [
            {"nombre": j.nombre, "equipo": j.equipo, "x": round(j.x, 1),
             "y": round(j.y, 1), "hits": j.hits}
            for j in jugadores
        ],
    }


def simular_partida_con_replay(jugadores, duracion_segundos=DURACION_PARTIDA_SEGUNDOS,
                                usar_genoma=True, intervalo_grabacion=5):
    """
    Igual que simular_partida_con_jugadores, pero además graba una
    "foto" del estado del mapa cada `intervalo_grabacion` ticks, para
    poder reproducir la partida después como time-lapse.
    """
    mapa = crear_mapa()
    puntos_equipo_A = 0
    puntos_equipo_B = 0
    decidir_accion = decidir_accion_genoma if usar_genoma else decidir_accion_agente_tonto
    rallies = []

    # Desglose de puntos de ALIANZA por fuente (para el reporte final)
    def categoria_de(edificio):
        n = edificio.nombre
        if "campamento" in n:
            return "campamentos"
        if n == "castillo":
            return "castillo"
        return "otros edificios"

    desglose_alianza = {
        "equipo_A": {"castillo": 0.0, "otros edificios": 0.0, "campamentos": 0.0, "bono observatorio": 0.0},
        "equipo_B": {"castillo": 0.0, "otros edificios": 0.0, "campamentos": 0.0, "bono observatorio": 0.0},
    }

    # Foto del estado inicial (todos en su spawn, antes de cualquier decisión)
    replay = [_foto_del_estado(-1, 0, 0, 0, mapa, jugadores)]

    for tick in range(duracion_segundos):
        minuto_actual = tick // 60

        for jugador in jugadores:
            for escuadron in jugador.escuadrones():
                if escuadron.estado in ("viajando_ataque", "viajando_ataque_jugador", "regresando_base"):
                    escuadron.avanzar_un_tick()

        mapa_activo = [e for e in mapa if e.minuto_aparicion <= minuto_actual]

        procesar_llegadas(jugadores, mapa, minuto_actual)

        for jugador in jugadores:
            jugador.actualizar_cooldown()

        for jugador in jugadores:
            decidir_teletransporte(jugador, mapa_activo, jugadores)

        for jugador in jugadores:
            decidir_accion(jugador, mapa_activo, jugadores, rallies, tick)

        gestionar_rallies(rallies, tick)

        for equipo in ("equipo_A", "equipo_B"):
            total_con_bono = calcular_puntos_equipo_por_segundo(mapa_activo, equipo)
            total_base = 0
            for e in mapa_activo:
                if e.dueño == equipo:
                    desglose_alianza[equipo][categoria_de(e)] += e.tasa_alianza
                    total_base += e.tasa_alianza
            desglose_alianza[equipo]["bono observatorio"] += total_con_bono - total_base
            if equipo == "equipo_A":
                puntos_equipo_A += total_con_bono
            else:
                puntos_equipo_B += total_con_bono
        sumar_puntos_personales(mapa_activo, jugadores)
        sanar_reservas(mapa_activo, jugadores, tick)

        if tick % intervalo_grabacion == 0:
            replay.append(_foto_del_estado(tick, minuto_actual, puntos_equipo_A,
                                            puntos_equipo_B, mapa, jugadores))

    return {
        "puntos_equipo_A": puntos_equipo_A,
        "puntos_equipo_B": puntos_equipo_B,
        "jugadores": jugadores,
        "mapa": mapa,
        "replay": replay,
        "desglose_alianza": desglose_alianza,
    }


def crear_jugadores(cantidad_por_equipo):
    jugadores = []
    for i in range(cantidad_por_equipo):
        x, y = SPAWN_EQUIPO_A
        jugadores.append(Jugador(nombre=f"A_{i}", equipo="equipo_A", x=x, y=y))
    for i in range(cantidad_por_equipo):
        x, y = SPAWN_EQUIPO_B
        jugadores.append(Jugador(nombre=f"B_{i}", equipo="equipo_B", x=x, y=y))
    return jugadores


def crear_jugadores_con_genomas(genomas_equipo_A, genomas_equipo_B):
    """Igual que crear_jugadores, pero cada jugador recibe un genoma específico."""
    jugadores = []
    for i, genoma in enumerate(genomas_equipo_A):
        x, y = SPAWN_EQUIPO_A
        jugadores.append(Jugador(nombre=f"A_{i}", equipo="equipo_A", x=x, y=y, genoma=genoma))
    for i, genoma in enumerate(genomas_equipo_B):
        x, y = SPAWN_EQUIPO_B
        jugadores.append(Jugador(nombre=f"B_{i}", equipo="equipo_B", x=x, y=y, genoma=genoma))
    return jugadores


def calcular_fitness(jugador, equipo_ganador):
    """
    Fitness individual: domina el resultado del equipo (bono grande si
    tu equipo tuvo más puntos totales), y los puntos personales sirven
    de desempate/ajuste fino dentro del mismo equipo.
    """
    fitness = jugador.puntos_personales
    if jugador.equipo == equipo_ganador:
        fitness += BONO_VICTORIA
    return fitness


def simular_partida_con_jugadores(jugadores, duracion_segundos=DURACION_PARTIDA_SEGUNDOS,
                                   usar_genoma=True, verbose=False):
    """
    Corre una partida completa con jugadores ya creados (con o sin
    genoma específico). Es el motor real -- simular_partida() de abajo
    es solo un envoltorio de conveniencia para pruebas rápidas.
    """
    mapa = crear_mapa()

    puntos_equipo_A = 0
    puntos_equipo_B = 0

    decidir_accion = decidir_accion_genoma if usar_genoma else decidir_accion_agente_tonto
    rallies = []

    for tick in range(duracion_segundos):
        minuto_actual = tick // 60

        for jugador in jugadores:
            for escuadron in jugador.escuadrones():
                if escuadron.estado in ("viajando_ataque", "viajando_ataque_jugador", "regresando_base"):
                    escuadron.avanzar_un_tick()

        mapa_activo = [e for e in mapa if e.minuto_aparicion <= minuto_actual]

        procesar_llegadas(jugadores, mapa, minuto_actual)

        for jugador in jugadores:
            jugador.actualizar_cooldown()

        for jugador in jugadores:
            decidir_teletransporte(jugador, mapa_activo, jugadores)

        for jugador in jugadores:
            decidir_accion(jugador, mapa_activo, jugadores, rallies, tick)

        gestionar_rallies(rallies, tick)

        puntos_equipo_A += calcular_puntos_equipo_por_segundo(mapa_activo, "equipo_A")
        puntos_equipo_B += calcular_puntos_equipo_por_segundo(mapa_activo, "equipo_B")
        sumar_puntos_personales(mapa_activo, jugadores)
        sanar_reservas(mapa_activo, jugadores, tick)

        if verbose and tick % 300 == 0:
            print(f"  Tick {tick} (min {minuto_actual}): A={puntos_equipo_A:.0f}  B={puntos_equipo_B:.0f}")

    return {
        "puntos_equipo_A": puntos_equipo_A,
        "puntos_equipo_B": puntos_equipo_B,
        "jugadores": jugadores,
        "mapa": mapa,
    }


def simular_partida(cantidad_por_equipo=5, duracion_segundos=DURACION_PARTIDA_SEGUNDOS,
                     usar_genoma=False, verbose=False):
    """Envoltorio de conveniencia: crea jugadores random y corre una partida."""
    jugadores = crear_jugadores(cantidad_por_equipo)
    return simular_partida_con_jugadores(jugadores, duracion_segundos, usar_genoma, verbose)


# ============================================================
# ALGORITMO GENÉTICO: torneo, selección, cruce, mutación
# ============================================================

def generar_genoma_aleatorio():
    return [random.uniform(-1, 1) for _ in range(5)]


def crear_poblacion_inicial(tamano, genomas_semilla=None, fraccion_sembrada=0.3):
    """
    Genera la población inicial (generación 0).

    Si se pasan `genomas_semilla` (ej. los campeones del salón de la
    fama), hasta `fraccion_sembrada` de la población arranca de ahí en
    vez de ser 100% aleatoria -- así la evolución parte de estrategias
    ya fuertes en vez de tener que redescubrirlas desde cero en cada
    corrida (una corrida random-desde-cero de 59 generaciones no logró
    superar a campeones ya refinados por 51-113 generaciones en
    corridas anteriores -- ver guia_contexto).

    Por cada semilla se generan 3 variantes:
      - un clon exacto (preserva la estrategia probada, por si nada la
        mejora en esta corrida),
      - un clon con mutación amplia en los 5 genes (explora su
        vecindario),
      - un clon que conserva w1-w4 tal cual pero con w5 (refuerzo)
        redibujado desde cero -- prueba directamente "esta estrategia
        ya fuerte + refuerzo" en vez de esperar a que la mutación
        normal, de paso pequeño, lo encuentre por casualidad.

    El resto de la población se completa con genomas aleatorios, para
    no perder diversidad genética y no converger prematuro sobre las
    semillas.
    """
    poblacion = []
    if genomas_semilla:
        limite_sembrado = max(1, int(tamano * fraccion_sembrada))
        for genoma in genomas_semilla:
            if len(poblacion) >= limite_sembrado:
                break
            poblacion.append(list(genoma))
            poblacion.append(cruzar_genomas(genoma, genoma, ruido=RUIDO_MUTACION * 4))
            variante_w5 = list(genoma[:4]) + [random.uniform(-1, 1)]
            poblacion.append(variante_w5)
        poblacion = poblacion[:limite_sembrado]

    while len(poblacion) < tamano:
        poblacion.append(generar_genoma_aleatorio())
    return poblacion


def cruzar_genomas(genoma_a, genoma_b, ruido=RUIDO_MUTACION):
    """
    El hijo hereda cada gen COMPLETO de uno de los dos padres (al azar),
    y se le agrega un poco de ruido (mutación) a cada gen.
    """
    hijo = []
    for i in range(len(genoma_a)):
        gen_heredado = random.choice([genoma_a[i], genoma_b[i]])
        gen_mutado = gen_heredado + random.uniform(-ruido, ruido)
        hijo.append(gen_mutado)
    return hijo


def ejecutar_torneo(poblacion, jugadores_por_equipo=5, partidas_por_genoma=3, verbose=False):
    """
    Cada "ronda" arma 8 equipos aleatorios a partir de la población y corre
    4 partidas. Esto se repite `partidas_por_genoma` veces (rebarajando la
    población cada vez), de modo que cada genoma juega varias partidas con
    compañeros y rivales distintos. El fitness final de cada genoma es el
    PROMEDIO de sus partidas -- mucho menos ruidoso que una sola partida.

    Devuelve: [(genoma, fitness_promedio), ...]
    """
    acumulado = {}  # id(genoma) -> [genoma, suma_fitness, cantidad_partidas]

    for ronda in range(partidas_por_genoma):
        poblacion_barajada = poblacion.copy()
        random.shuffle(poblacion_barajada)

        equipos = [
            poblacion_barajada[i * jugadores_por_equipo:(i + 1) * jugadores_por_equipo]
            for i in range(8)
        ]

        for num_partida in range(4):
            genomas_A = equipos[num_partida * 2]
            genomas_B = equipos[num_partida * 2 + 1]

            jugadores = crear_jugadores_con_genomas(genomas_A, genomas_B)
            resultado = simular_partida_con_jugadores(jugadores, usar_genoma=True, verbose=False)

            if resultado["puntos_equipo_A"] > resultado["puntos_equipo_B"]:
                equipo_ganador = "equipo_A"
            else:
                equipo_ganador = "equipo_B"

            if verbose:
                print(f"  Ronda {ronda + 1} partida {num_partida + 1}: "
                      f"A={resultado['puntos_equipo_A']:.0f} B={resultado['puntos_equipo_B']:.0f}  "
                      f"Gana {equipo_ganador}")

            for jugador in jugadores:
                fit = calcular_fitness(jugador, equipo_ganador)
                clave = id(jugador.genoma)
                if clave not in acumulado:
                    acumulado[clave] = [jugador.genoma, 0.0, 0]
                acumulado[clave][1] += fit
                acumulado[clave][2] += 1

    resultados_fitness = [
        (genoma, suma / cantidad)
        for genoma, suma, cantidad in acumulado.values()
    ]
    return resultados_fitness


def crear_siguiente_generacion(resultados_fitness, tamano_poblacion):
    """
    Selecciona a los mejores genomas (por fitness individual, sin
    importar de qué equipo vinieron), conserva una élite intacta, y
    genera el resto de la población nueva por cruce + mutación.
    """
    ordenados = sorted(resultados_fitness, key=lambda par: par[1], reverse=True)
    genomas_ordenados = [genoma for genoma, fit in ordenados]

    elite = genomas_ordenados[:CANTIDAD_ELITE]

    mitad = max(2, int(len(genomas_ordenados) * FRACCION_POOL_PADRES))
    pool_padres = genomas_ordenados[:mitad]

    nueva_poblacion = list(elite)
    while len(nueva_poblacion) < tamano_poblacion:
        padre_a = random.choice(pool_padres)
        padre_b = random.choice(pool_padres)
        hijo = cruzar_genomas(padre_a, padre_b)
        nueva_poblacion.append(hijo)

    return nueva_poblacion


def evolucionar(tamano_poblacion=80, jugadores_por_equipo=5, max_generaciones=200,
                 generaciones_sin_mejora_limite=25, partidas_por_genoma=3,
                 umbral_mejora=0.002, genomas_semilla=None, fraccion_sembrada=0.3,
                 verbose=True):
    """
    Ciclo completo de evolución.

    Criterio de parada: se detiene cuando el FITNESS PROMEDIO de la
    población no mejora (en al menos `umbral_mejora`, proporcional) durante
    `generaciones_sin_mejora_limite` generaciones seguidas, o al llegar a
    `max_generaciones`. Se usa el promedio y no el mejor porque el mejor
    fitness toca su techo casi de inmediato (bono de victoria + máximo
    natural de puntos personales) y no refleja el aprendizaje real de la
    población.

    Cada genoma juega `partidas_por_genoma` partidas por generación con
    equipos rebarajados, y su fitness es el promedio -- menos ruido que
    una sola partida.

    `genomas_semilla` (opcional, ej. los genomas del salón de la fama):
    si se pasa, la población inicial no arranca 100% aleatoria -- ver
    `crear_poblacion_inicial()`.
    """
    poblacion = crear_poblacion_inicial(tamano_poblacion, genomas_semilla, fraccion_sembrada)
    mejor_promedio_historico = None
    generaciones_sin_mejora = 0
    historial = []
    mejor_genoma_gen0 = None

    for gen in range(max_generaciones):
        resultados = ejecutar_torneo(poblacion, jugadores_por_equipo,
                                      partidas_por_genoma=partidas_por_genoma)

        if gen == 0:
            mejor_genoma_gen0 = max(resultados, key=lambda par: par[1])[0]

        fitness_valores = [fit for genoma, fit in resultados]
        fitness_promedio = sum(fitness_valores) / len(fitness_valores)
        mejor_fitness_gen = max(fitness_valores)

        historial.append({
            "generacion": gen,
            "promedio": fitness_promedio,
            "mejor": mejor_fitness_gen,
            "pesos_promedio": [sum(g[i] for g in poblacion) / len(poblacion) for i in range(4)],
        })

        if verbose:
            print(f"Generación {gen}: promedio={fitness_promedio:.0f}  mejor={mejor_fitness_gen:.0f}")

        if mejor_promedio_historico is None or fitness_promedio > mejor_promedio_historico * (1 + umbral_mejora):
            mejor_promedio_historico = max(fitness_promedio, mejor_promedio_historico or 0)
            generaciones_sin_mejora = 0
        else:
            generaciones_sin_mejora += 1

        if generaciones_sin_mejora >= generaciones_sin_mejora_limite:
            if verbose:
                print(f"Promedio sin mejorar por {generaciones_sin_mejora_limite} generaciones. Deteniendo.")
            break

        poblacion = crear_siguiente_generacion(resultados, tamano_poblacion)

    mejor_genoma = max(resultados, key=lambda par: par[1])[0]
    return {
        "poblacion_final": poblacion,
        "mejor_genoma": mejor_genoma,
        "mejor_genoma_gen0": mejor_genoma_gen0,  # el mejor "ancestro" sin evolucionar
        "historial": historial,
        "ultimos_resultados": resultados,  # (genoma, fitness) de la última generación evaluada
    }


def jugar_gran_final(ultimos_resultados, jugadores_por_equipo=5, intervalo_grabacion=5,
                      n_candidatos=8, verbose=True):
    """
    Selecciona a los finalistas con un PLAYOFF real, no solo por fitness:

    1. Toma los `n_candidatos` mejores genomas por fitness (preselección).
    2. Los enfrenta todos-contra-todos con equipos de CLONES (cada equipo
       lleno de copias del mismo genoma) -- así se elimina la suerte de
       "me tocaron buenos compañeros" que contamina el fitness del torneo.
    3. Los 2 con más victorias en el playoff (desempate por diferencia de
       puntos) juegan la gran final, que se graba con replay.
    """
    ordenados = sorted(ultimos_resultados, key=lambda par: par[1], reverse=True)
    candidatos = [genoma for genoma, fit in ordenados[:n_candidatos]]

    # Playoff todos-contra-todos
    victorias = [0] * len(candidatos)
    diferencia_puntos = [0.0] * len(candidatos)

    for i in range(len(candidatos)):
        for j in range(i + 1, len(candidatos)):
            jugadores = crear_jugadores_con_genomas(
                [candidatos[i]] * jugadores_por_equipo,
                [candidatos[j]] * jugadores_por_equipo,
            )
            r = simular_partida_con_jugadores(jugadores, usar_genoma=True, verbose=False)
            dif = r["puntos_equipo_A"] - r["puntos_equipo_B"]
            diferencia_puntos[i] += dif
            diferencia_puntos[j] -= dif
            if dif > 0:
                victorias[i] += 1
            else:
                victorias[j] += 1

    ranking = sorted(range(len(candidatos)),
                     key=lambda k: (victorias[k], diferencia_puntos[k]), reverse=True)

    if verbose:
        print(f"  === PLAYOFF ({n_candidatos} candidatos, todos contra todos) ===")
        for pos, k in enumerate(ranking, 1):
            print(f"  {pos}. victorias={victorias[k]}  dif_puntos={diferencia_puntos[k]:+.0f}  "
                  f"genoma={[round(g, 2) for g in candidatos[k]]}")
        print()

    genoma_1 = candidatos[ranking[0]]
    genoma_2 = candidatos[ranking[1]]

    genomas_A = [genoma_1] * jugadores_por_equipo
    genomas_B = [genoma_2] * jugadores_por_equipo

    jugadores = crear_jugadores_con_genomas(genomas_A, genomas_B)
    resultado = simular_partida_con_replay(jugadores, usar_genoma=True,
                                            intervalo_grabacion=intervalo_grabacion)

    if verbose:
        print(f"GRAN FINAL -- genoma #1 (equipo_A) vs genoma #2 (equipo_B)")
        print(f"  genoma #1: {[round(g, 3) for g in genoma_1]}")
        print(f"  genoma #2: {[round(g, 3) for g in genoma_2]}")
        print(f"  Resultado: A={resultado['puntos_equipo_A']:.0f}  B={resultado['puntos_equipo_B']:.0f}")
        print()
        print("  === DESGLOSE DE PUNTOS DE ALIANZA POR FUENTE ===")
        for equipo in ("equipo_A", "equipo_B"):
            d = resultado["desglose_alianza"][equipo]
            total = sum(d.values())
            print(f"  {equipo} (total {total:.0f}):")
            for fuente, pts in d.items():
                pct = (pts / total * 100) if total > 0 else 0
                print(f"    {fuente}: {pts:.0f}  ({pct:.1f}%)")
        print()
        print("  === PUNTOS PERSONALES POR FUENTE (suma del equipo) ===")
        for equipo in ("equipo_A", "equipo_B"):
            jugadores_eq = [j for j in resultado["jugadores"] if j.equipo == equipo]
            defensa = sum(j.puntos_por_defensa for j in jugadores_eq)
            kills = sum(j.puntos_por_kills for j in jugadores_eq)
            print(f"  {equipo}: defensa de edificios={defensa:.0f}  batallas={kills:.0f}")

    resultado["genoma_1"] = genoma_1
    resultado["genoma_2"] = genoma_2
    return resultado


def jugar_batalla(genoma_equipo_A, genoma_equipo_B, jugadores_por_equipo=5,
                   intervalo_grabacion=5, titulo="Batalla", verbose=True):
    """
    Enfrenta dos genomas específicos: cada equipo se llena con copias del
    suyo. Devuelve el resultado completo con replay, listo para visualizar.
    """
    genomas_A = [genoma_equipo_A] * jugadores_por_equipo
    genomas_B = [genoma_equipo_B] * jugadores_por_equipo

    jugadores = crear_jugadores_con_genomas(genomas_A, genomas_B)
    resultado = simular_partida_con_replay(jugadores, usar_genoma=True,
                                            intervalo_grabacion=intervalo_grabacion)
    if verbose:
        print(f"{titulo}: A={resultado['puntos_equipo_A']:.0f}  B={resultado['puntos_equipo_B']:.0f}")

    resultado["titulo"] = titulo
    resultado["genoma_1"] = genoma_equipo_A
    resultado["genoma_2"] = genoma_equipo_B
    return resultado


def _resumen_serializable(resultado):
    """
    Extrae del resultado de una partida (el dict que devuelven
    simular_partida_con_replay/jugar_batalla/jugar_gran_final) solo lo
    que hace falta para el panel de resumen del HTML -- desglose de
    puntos de alianza por fuente, genomas de cada equipo, y estadísticas
    personales por jugador. Cualquier clave ausente en `resultado` se
    omite (el HTML ya sabe mostrar "sin datos" si falta algo).
    """
    resumen = {}
    if "desglose_alianza" in resultado:
        resumen["desglose_alianza"] = resultado["desglose_alianza"]
    if "genoma_1" in resultado:
        resumen["genoma_1"] = [round(g, 3) for g in resultado["genoma_1"]]
    if "genoma_2" in resultado:
        resumen["genoma_2"] = [round(g, 3) for g in resultado["genoma_2"]]
    if "jugadores" in resultado:
        resumen["jugadores"] = [
            {
                "nombre": j.nombre,
                "equipo": j.equipo,
                "puntos_personales": round(j.puntos_personales),
                "puntos_por_kills": round(j.puntos_por_kills),
                "puntos_por_defensa": round(j.puntos_por_defensa),
            }
            for j in resultado["jugadores"]
        ]
    return resumen


def generar_replay_html_multiple(batallas, ruta_salida):
    """
    Genera un solo HTML con VARIAS batallas y un selector para cambiar
    entre ellas. `batallas` es una lista de dicts -- típicamente los
    resultados completos que devuelven jugar_batalla()/jugar_gran_final()
    (con "titulo" agregado), aunque solo "titulo" y "replay" son
    obligatorios. Si además trae "desglose_alianza"/"jugadores"/
    "genoma_1"/"genoma_2", el HTML muestra un panel de resumen final
    (puntos de alianza por fuente, pesos del genoma, top jugadores).
    """
    datos = [
        {"titulo": b["titulo"], "replay": b["replay"], "resumen": _resumen_serializable(b)}
        for b in batallas
    ]
    datos_json = json.dumps(datos)

    plantilla = _PLANTILLA_HTML_REPLAY.replace(
        "const replay = REPLAY_DATA_PLACEHOLDER;\nconst resumen = RESUMEN_DATA_PLACEHOLDER;",
        "const batallas = " + datos_json + ";\n"
        "let replay = batallas[0].replay;\n"
        "let resumen = batallas[0].resumen;"
    )

    plantilla = plantilla.replace(
        '<button id="btnPlay">Reproducir</button>',
        '<select id="selBatalla"></select>\n  <button id="btnPlay">Reproducir</button>'
    )

    plantilla = plantilla.replace(
        "dibujar(0, 0);\nrenderResumen(resumen);",
        """const selBatalla = document.getElementById('selBatalla');
batallas.forEach((b, i) => {
  const op = document.createElement('option');
  op.value = i; op.textContent = b.titulo;
  selBatalla.appendChild(op);
});
selBatalla.addEventListener('change', () => {
  pause();
  const b = batallas[parseInt(selBatalla.value)];
  replay = b.replay;
  resumen = b.resumen;
  slider.max = replay.length - 1;
  cursor = 0;
  dibujar(0, 0);
  renderResumen(resumen);
});

dibujar(0, 0);
renderResumen(resumen);"""
    )

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(plantilla)

    return ruta_salida


def generar_replay_html(replay, ruta_salida, resultado=None):
    """
    Toma la lista `replay` (de simular_partida_con_replay) y genera un
    archivo HTML autocontenido con el visualizador de time-lapse, listo
    para abrir en el navegador. Si además se pasa `resultado` (el dict
    completo que devuelve simular_partida_con_replay/jugar_batalla),
    se agrega el panel de resumen final -- opcional, para no romper
    llamadas existentes que solo tenían el replay a mano.
    """
    replay_json = json.dumps(replay)
    resumen_json = json.dumps(_resumen_serializable(resultado) if resultado else {})

    plantilla = _PLANTILLA_HTML_REPLAY.replace("REPLAY_DATA_PLACEHOLDER", replay_json)
    plantilla = plantilla.replace("RESUMEN_DATA_PLACEHOLDER", resumen_json)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(plantilla)

    return ruta_salida


def cargar_salon_fama(archivo=ARCHIVO_SALON_FAMA):
    if not os.path.exists(archivo):
        return []
    with open(archivo) as f:
        historial = json.load(f)
    # Compatibilidad: genomas guardados antes de agregar w5 (refuerzo de
    # edificios propios) solo tienen 4 genes -- se completan con 0.0
    # (neutral: nunca refuerza) para que sigan siendo jugables.
    for entrada in historial:
        while len(entrada["genoma"]) < 5:
            entrada["genoma"].append(0.0)
    return historial


def _round_robin_victorias(genomas, jugadores_por_equipo, partidas_por_par=5):
    """
    Enfrenta una lista de genomas todos-contra-todos (con clones),
    jugando `partidas_por_par` partidas por cada par en vez de una sola.

    Una sola partida se decide en buena parte por azar (soldados totales
    aleatorios entre 18,462-26,000, capacidades de escuadrón con
    variación ±3%, orden de evaluación) -- no solo por qué tan buena es
    la estrategia. Con un único partido, un genoma realmente más fuerte
    puede perder por mala suerte y quedar descartado del salón de la
    fama injustamente (confirmado en la práctica: un campeón nuevo con
    ~47% de winrate contra el salón de la fama en 15 semillas había
    perdido 0/3 en la comparación de un solo partido por par). Retorna
    las victorias acumuladas de cada genoma en el mismo orden que
    `genomas`.
    """
    victorias = [0] * len(genomas)
    for i in range(len(genomas)):
        for j in range(i + 1, len(genomas)):
            for _ in range(partidas_por_par):
                jugadores = crear_jugadores_con_genomas(
                    [genomas[i]] * jugadores_por_equipo, [genomas[j]] * jugadores_por_equipo)
                r = simular_partida_con_jugadores(jugadores, usar_genoma=True, verbose=False)
                if r["puntos_equipo_A"] > r["puntos_equipo_B"]:
                    victorias[i] += 1
                else:
                    victorias[j] += 1
    return victorias


def actualizar_salon_fama(genoma_nuevo, jugadores_por_equipo=5, parametros=None,
                           archivo=ARCHIVO_SALON_FAMA, tamano=TAMANO_SALON_FAMA,
                           partidas_por_par=5, verbose=True):
    """
    Compara el campeón de esta corrida contra los que ya estaban guardados
    (hasta `tamano`, por defecto 3) mediante un mini-playoff round-robin
    con clones (`partidas_por_par` partidas por cada par, no una sola --
    ver `_round_robin_victorias`), y conserva solo a los `tamano` mejores
    de TODOS ellos juntos -- el salón de la fama nunca crece más de
    `tamano` entradas.

    Retorna la lista final (ordenada de mejor a peor) que quedó guardada.
    """
    historial_previo = cargar_salon_fama(archivo)

    entrada_nueva = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "genoma": genoma_nuevo,
        "parametros": parametros or {},
    }

    candidatos = historial_previo + [entrada_nueva]
    genomas = [c["genoma"] for c in candidatos]

    if len(genomas) == 1:
        nuevo_historial = candidatos
    else:
        victorias = _round_robin_victorias(genomas, jugadores_por_equipo, partidas_por_par)
        orden = sorted(range(len(candidatos)), key=lambda k: victorias[k], reverse=True)
        nuevo_historial = [candidatos[i] for i in orden[:tamano]]

        if verbose:
            partidos_jugados_c_uno = (len(candidatos) - 1) * partidas_por_par
            print(f"  === ACTUALIZANDO SALÓN DE LA FAMA ({len(candidatos)} candidatos, "
                  f"{partidas_por_par} partidas/par, se conservan los "
                  f"{min(tamano, len(candidatos))} mejores) ===")
            for pos, i in enumerate(orden[:tamano], 1):
                marca = " <- campeón de esta corrida" if candidatos[i] is entrada_nueva else ""
                print(f"  {pos}. victorias={victorias[i]}/{partidos_jugados_c_uno}  "
                      f"genoma={[round(g, 2) for g in genomas[i]]}{marca}")

    with open(archivo, "w") as f:
        json.dump(nuevo_historial, f, indent=2)

    return nuevo_historial


def jugar_duelo_personalizado(mi_genoma, rivales, jugadores_por_equipo=5, verbose=True):
    """
    Enfrenta un genoma definido a mano (`mi_genoma`) contra una lista de
    genomas rivales (ej. el salón de la fama). `rivales` es una lista de
    dicts con al menos la clave "genoma" (y opcionalmente "titulo").

    Retorna una lista de resultados de batalla (con replay), listos para
    agregar al HTML.
    """
    resultados = []
    for i, rival in enumerate(rivales, 1):
        titulo = rival.get("titulo") or f"Mi genoma (A) vs rival #{i} (B)"
        resultado = jugar_batalla(
            mi_genoma, rival["genoma"],
            jugadores_por_equipo=jugadores_por_equipo,
            titulo=titulo, verbose=verbose,
        )
        resultados.append(resultado)
    return resultados


# ============================================================
# HERRAMIENTAS DE ANÁLISIS: sensibilidad y robustez
# ============================================================

def analizar_sensibilidad(nombre_parametro, valores, genoma_A, genoma_B,
                           jugadores_por_equipo=5, repeticiones=5, verbose=True):
    """
    Corre la MISMA batalla (genoma_A vs genoma_B) variando UN SOLO
    parámetro global (ej. "ESCALA_PUNTOS_KILL") por los valores que le
    pases, para ver qué tan sensible es el resultado a ese número.

    Cada valor se repite `repeticiones` veces y se promedia, para no
    confundir "el parámetro importa" con "esta partida tuvo suerte". Las
    `repeticiones` usan las MISMAS semillas para todos los valores del
    parámetro (semilla 0, 1, 2...) -- así los rosters (soldados totales,
    capacidades de escuadrón) son idénticos entre un valor y otro, y la
    diferencia observada se debe solo al parámetro, no al azar de quién
    le tocó más soldados. Sin esto, con pocas repeticiones el ruido de
    roster (partidas con márgenes de hasta 3x solo por suerte) puede ser
    más grande que el efecto real del parámetro y esconderlo.

    Ejemplo:
        analizar_sensibilidad("ESCALA_PUNTOS_KILL", [5000, 10000, 20000, 40000],
                               genoma_agresivo, genoma_defensivo)

    Retorna una lista de dicts: [{"valor":..., "promedio_A":..., "promedio_B":...}, ...]
    Modifica el parámetro global temporalmente y lo restaura al final.
    """
    if nombre_parametro not in globals():
        raise ValueError(f"No existe un parámetro global llamado '{nombre_parametro}'")

    valor_original = globals()[nombre_parametro]
    resultados = []
    estado_random_previo = random.getstate()

    try:
        for valor in valores:
            globals()[nombre_parametro] = valor
            puntos_A_total = 0
            puntos_B_total = 0
            for semilla in range(repeticiones):
                random.seed(semilla)
                jugadores = crear_jugadores_con_genomas(
                    [genoma_A] * jugadores_por_equipo, [genoma_B] * jugadores_por_equipo)
                r = simular_partida_con_jugadores(jugadores, usar_genoma=True, verbose=False)
                puntos_A_total += r["puntos_equipo_A"]
                puntos_B_total += r["puntos_equipo_B"]

            promedio_A = puntos_A_total / repeticiones
            promedio_B = puntos_B_total / repeticiones
            resultados.append({"valor": valor, "promedio_A": promedio_A, "promedio_B": promedio_B})

            if verbose:
                print(f"  {nombre_parametro}={valor}: A={promedio_A:.0f}  B={promedio_B:.0f}  "
                      f"(promedio de {repeticiones} partidas, mismas semillas)")
    finally:
        globals()[nombre_parametro] = valor_original  # siempre se restaura, incluso si hay error
        random.setstate(estado_random_previo)  # no contaminar el azar de lo que siga después

    return resultados


def evaluar_robustez(genoma, genoma_rival, jugadores_por_equipo=5, n_semillas=10, verbose=True):
    """
    Enfrenta el mismo par de genomas `n_semillas` veces, cada una con
    una semilla aleatoria distinta, para ver qué tan CONSISTENTE es el
    resultado -- si `genoma` le gana a `genoma_rival` en casi todas las
    corridas, es una ventaja real; si el resultado varía mucho de
    semilla a semilla, la diferencia observada en una sola partida no
    es confiable.

    Retorna un dict con victorias, empates (no debería haber, pero se
    cuentan por seguridad) y la lista de diferencias de puntos de cada
    corrida.
    """
    victorias_genoma = 0
    victorias_rival = 0
    diferencias = []

    estado_random_previo = random.getstate()

    for semilla in range(n_semillas):
        random.seed(semilla)
        jugadores = crear_jugadores_con_genomas(
            [genoma] * jugadores_por_equipo, [genoma_rival] * jugadores_por_equipo)
        r = simular_partida_con_jugadores(jugadores, usar_genoma=True, verbose=False)
        dif = r["puntos_equipo_A"] - r["puntos_equipo_B"]
        diferencias.append(dif)
        if dif > 0:
            victorias_genoma += 1
        elif dif < 0:
            victorias_rival += 1

        if verbose:
            print(f"  Semilla {semilla}: A={r['puntos_equipo_A']:.0f}  B={r['puntos_equipo_B']:.0f}  "
                  f"({'gana mi genoma' if dif > 0 else 'gana el rival'})")

    random.setstate(estado_random_previo)  # no contaminar el azar de lo que siga después

    if verbose:
        print()
        print(f"  Resultado: mi genoma ganó {victorias_genoma}/{n_semillas} corridas "
              f"({victorias_genoma/n_semillas*100:.0f}%)")

    return {
        "victorias_genoma": victorias_genoma,
        "victorias_rival": victorias_rival,
        "n_semillas": n_semillas,
        "diferencias": diferencias,
    }


if __name__ == "__main__":
    # ==========================================================
    # DUELO PERSONALIZADO -- opcional. Si defines tu propio genoma
    # aquí (5 números w1,w2,w3,w4,w5), al final de la corrida se
    # enfrentará contra el campeón de esta corrida y contra los
    # campeones guardados en el salón de la fama. Déjalo en None
    # para omitir esta sección.
    #
    # Qué es cada peso:
    #   w1 -- qué tanto valora los puntos que da un edificio LIBRE (al
    #         capturarlo por primera vez). Un w1 alto hace que prefiera
    #         edificios de tasa alta (como el Castillo, 80/seg) sobre
    #         uno chico, aunque esté más lejos.
    #   w2 -- qué tanto valora la cercanía. Un w2 alto prioriza lo que
    #         tiene cerca, aunque valga menos, para no perder tiempo
    #         viajando.
    #   w3 -- qué tan agresivo es (aplica al evaluar atacar jugadores
    #         y al evaluar recapturar edificios enemigos defendidos).
    #         Se combina con la diferencia de poder entre tu fuerza y
    #         la defensa enemiga disponible. Positivo = le gusta
    #         atacar cuando tiene ventaja; negativo = evita el combate
    #         directo casi siempre.
    #   w4 -- qué tanto le importa la coordinación con sus aliados
    #         (incluye la decisión de usar RALLY -- ataque conjunto
    #         sincronizado -- contra jugadores enemigos, y la de
    #         amontonar defensores extra en un mismo edificio propio).
    #         Positivo = prefiere ir donde ya hay compañeros suyos
    #         asignados (agruparse); negativo = prefiere repartirse y
    #         evitar duplicar esfuerzo en el mismo objetivo.
    #   w5 -- qué tanto valora REFORZAR un edificio que su equipo ya
    #         controla, mandando un escuadrón adicional como defensor
    #         (hasta 6 por edificio). Es independiente de w1: un genoma
    #         puede valorar capturar territorio nuevo distinto de
    #         defender el que ya tiene. Positivo = blinda sus edificios
    #         valiosos; 0 o negativo = nunca vuelve a un edificio propio
    #         una vez capturado (comportamiento anterior a este cambio).
    # ==========================================================
    MI_GENOMA = None
    # Ejemplo: MI_GENOMA = [0.5, 0.4, -0.6, 0.1, 0.3]

    # ==========================================================
    # CONFIGURACIÓN DE LA CORRIDA -- cambia estos valores a lo que
    # quieras. Para calibrar reglas del JUEGO (combate, puntuación,
    # movimiento, algoritmo genético, curación), ve al bloque
    # "PARÁMETROS" al inicio del archivo -- todo lo demás vive ahí,
    # en un solo lugar.
    #
    # IMPORTANTE: tamano_poblacion debe ser >= 8 * jugadores_por_equipo
    # (el torneo arma 8 equipos por ronda). Ej: 11 por equipo -> mínimo 88.
    # ==========================================================
    TAMANO_POBLACION = 150
    JUGADORES_POR_EQUIPO = 11
    MAX_GENERACIONES = 250
    PACIENCIA = 40            # generaciones sin mejora del promedio antes de parar
    PARTIDAS_POR_GENOMA = 10  # más partidas = menos ruido, más lento

    # Sembrar la población inicial con los campeones del salón de la fama
    # (en vez de arrancar 100% aleatoria) -- así la evolución parte de
    # estrategias ya fuertes y las combina con genes nuevos (como w5) en
    # vez de tener que redescubrirlas desde cero cada corrida. Ver
    # crear_poblacion_inicial(). Desactivar poniendo esto en False.
    SEMBRAR_DESDE_SALON_FAMA = True
    FRACCION_SEMBRADA = 0.3   # como mucho el 30% de la población inicial viene de semillas

    if TAMANO_POBLACION < 8 * JUGADORES_POR_EQUIPO:
        raise SystemExit(f"tamano_poblacion ({TAMANO_POBLACION}) debe ser >= "
                         f"8 * jugadores_por_equipo ({8 * JUGADORES_POR_EQUIPO})")

    genomas_semilla = None
    if SEMBRAR_DESDE_SALON_FAMA:
        genomas_semilla = [entrada["genoma"] for entrada in cargar_salon_fama()]

    print(f"Evolucionando: población={TAMANO_POBLACION}, "
          f"{JUGADORES_POR_EQUIPO} por equipo, {PARTIDAS_POR_GENOMA} partidas/genoma")
    if genomas_semilla:
        print(f"  sembrando desde {len(genomas_semilla)} campeón(es) del salón de la fama "
              f"(hasta {FRACCION_SEMBRADA:.0%} de la población inicial)")
    print()

    res = evolucionar(
        tamano_poblacion=TAMANO_POBLACION,
        jugadores_por_equipo=JUGADORES_POR_EQUIPO,
        max_generaciones=MAX_GENERACIONES,
        generaciones_sin_mejora_limite=PACIENCIA,
        partidas_por_genoma=PARTIDAS_POR_GENOMA,
        genomas_semilla=genomas_semilla,
        fraccion_sembrada=FRACCION_SEMBRADA,
        verbose=True,
    )

    print()
    print("Mejor genoma encontrado:", [round(g, 3) for g in res["mejor_genoma"]])
    print()

    res_final = jugar_gran_final(res["ultimos_resultados"],
                                  jugadores_por_equipo=JUGADORES_POR_EQUIPO)

    # Batalla extra: el CAMPEÓN DEL PLAYOFF contra el mejor "ancestro"
    # de la generación 0 -- mide cuánto aprendió la evolución en absoluto.
    res_vs_origen = jugar_batalla(
        res_final["genoma_1"], res["mejor_genoma_gen0"],
        jugadores_por_equipo=JUGADORES_POR_EQUIPO,
        titulo="Campeón del playoff (A) vs mejor de generación 0 (B)",
    )

    batallas = [
        {**res_final, "titulo": "Gran final: campeón vs subcampeón del playoff"},
        {**res_vs_origen, "titulo": "Campeón vs mejor de generación 0"},
    ]

    # Salón de la fama: se compara el campeón de esta corrida contra los
    # que ya estaban guardados, y se conservan solo los TAMANO_SALON_FAMA
    # mejores en total (por defecto 3).
    print()
    top_salon_fama = actualizar_salon_fama(
        res_final["genoma_1"],
        jugadores_por_equipo=JUGADORES_POR_EQUIPO,
        parametros={
            "tamano_poblacion": TAMANO_POBLACION,
            "jugadores_por_equipo": JUGADORES_POR_EQUIPO,
            "partidas_por_genoma": PARTIDAS_POR_GENOMA,
            "generaciones_corridas": len(res["historial"]),
        },
    )

    # Duelo personalizado (si definiste MI_GENOMA arriba)
    if MI_GENOMA is not None:
        print()
        print("  === DUELO PERSONALIZADO ===")
        rivales = [{"titulo": "Mi genoma (A) vs campeón de esta corrida (B)",
                    "genoma": res_final["genoma_1"]}]
        for i, entrada in enumerate(top_salon_fama, 1):
            rivales.append({
                "titulo": f"Mi genoma (A) vs salón de la fama #{i} (B)",
                "genoma": entrada["genoma"],
            })
        resultados_duelo = jugar_duelo_personalizado(
            MI_GENOMA, rivales, jugadores_por_equipo=JUGADORES_POR_EQUIPO, verbose=True)
        batallas.extend(resultados_duelo)

    generar_replay_html_multiple(batallas, "gran_final.html")
    print()
    print(f"Replay con {len(batallas)} batalla(s) guardado en: gran_final.html")