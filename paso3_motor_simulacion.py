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
    --team-a: #5aa9e6;
    --team-a-dim: #2d4f66;
    --team-b: #e6615a;
    --team-b-dim: #663333;
    --free: #4a5568;
    --text: #d7dee6;
    --text-dim: #7c8a99;
    --accent: #e6b85a;
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
  .sq { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
</style>
</head>
<body>

<h1>ELIXIR SCRAMBLE -- REPLAY DE PARTIDA</h1>
<div class="subt">Time-lapse de la simulacion, con interpolacion de movimiento entre fotogramas</div>

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
</div>

<script>
const replay = REPLAY_DATA_PLACEHOLDER;

const canvas = document.getElementById('mapa');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const MAPA_MAX = 1000;

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
  });

  // Jugadores (bases): cuadraditos, interpolados salvo teletransporte
  const pos1J = {};
  f1.jugadores_pos.forEach(j => pos1J[j.nombre] = j);
  f0.jugadores_pos.forEach(j => {
    const jn = pos1J[j.nombre] || j;
    let jx = j.x, jy = j.y;
    const salto = Math.hypot(jn.x - j.x, jn.y - j.y);
    if (salto < 30) { jx = lerp(j.x, jn.x, t); jy = lerp(j.y, jn.y, t); }
    else if (t > 0.5) { jx = jn.x; jy = jn.y; }
    const x = escalar(jx), y = escalar(jy);
    ctx.beginPath();
    ctx.rect(x - 4, y - 4, 8, 8);
    ctx.fillStyle = colorEquipo(j.equipo);
    ctx.globalAlpha = 0.9;
    ctx.fill();
    ctx.globalAlpha = 1;
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

    // separacion visual de apilados
    const clave = Math.round(ex) + ',' + Math.round(ey);
    const n = dibujados[clave] || 0;
    dibujados[clave] = n + 1;
    const offx = n > 0 ? 6 * Math.cos(n * 2.1) : 0;
    const offy = n > 0 ? 6 * Math.sin(n * 2.1) : 0;

    const x = escalar(ex) + offx, y = escalar(ey) + offy;
    ctx.beginPath();
    ctx.arc(x, y, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = colorEquipo(e.equipo);
    ctx.fill();
  });

  const mins = String(f0.minuto).padStart(2, '0');
  const segs = String(Math.max(0, f0.tick) % 60).padStart(2, '0');
  document.getElementById('reloj').textContent = mins + ':' + segs;
  document.getElementById('pa').textContent = f0.puntos_A.toLocaleString();
  document.getElementById('pb').textContent = f0.puntos_B.toLocaleString();
  document.getElementById('slider').value = Math.floor(idx);
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
</script>
</body>
</html>
"""

# ============================================================
# CONSTANTES GLOBALES
# ============================================================

VELOCIDAD_TROPAS = 2.2          # unidades de distancia por segundo
COOLDOWN_TELETRANSPORTE = 120   # segundos
K_COMBATE = 1.5                 # constante de la fórmula logística
ESCALA_PUNTOS_KILL = 10_000      # divisor del poder eliminado -> puntos personales
DURACION_PARTIDA_SEGUNDOS = 1800  # 30 minutos
BONO_VICTORIA = 1_000_000         # domina sobre los puntos_personales típicos

SPAWN_EQUIPO_A = (500, 0)
SPAWN_EQUIPO_B = (500, 1000)

RADIO_DETECCION_COMBATE = 5  # distancia máxima para considerar "cerca"
                              # (ajustable -- si el mapa se siente muy
                              # disperso o muy apretado, cambia este número)

MAX_ESCUADRONES_POR_EDIFICIO = 6  # límite de defensores Y de ataque conjunto


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
        """Manda el escuadrón a capturar/defender un edificio."""
        self.destino = edificio_objetivo
        self.estado = "viajando_ataque"

    def enviar_a_atacar_jugador(self, jugador_objetivo):
        """Manda el escuadrón a atacar directamente a un jugador (Sistema 2)."""
        self.destino = jugador_objetivo
        self.estado = "viajando_ataque_jugador"

    def regresar_a_base(self):
        """El escuadrón perdió una pelea -- vuelve caminando a su jugador."""
        self.destino = self.jugador_dueño
        self.estado = "regresando_base"

    def teletransportar_con_jugador(self, nueva_x, nueva_y):
        """Usado cuando el jugador dueño se teletransporta o muere."""
        self.x = nueva_x
        self.y = nueva_y
        self.destino = None
        self.estado = "en_base"

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
        self.destino = None
        self.cooldown_teletransporte_restante = 0

        # Genoma: [w1, w2, w3, w4] -- si no se pasa uno ya evolucionado,
        # arranca con valores aleatorios (generación 0)
        self.genoma = genoma if genoma is not None else [random.uniform(-1, 1) for _ in range(4)]

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

    def recibir_ataque_directo(self):
        """
        Sistema 2: un escuadrón enemigo llegó hasta el jugador.
        Siempre resta 1 hit, sin importar si tenía defensa o no.
        """
        self.hits -= 1
        if self.hits <= 0:
            self.morir()

    def actualizar_cooldown(self):
        if self.cooldown_teletransporte_restante > 0:
            self.cooldown_teletransporte_restante -= 1


# ============================================================
# DETECCIÓN Y RESOLUCIÓN DE COMBATE
# ============================================================

def buscar_defensor_en_edificio(edificio, equipo_atacante, todos_los_jugadores):
    """
    Busca si hay un escuadrón ENEMIGO defendiendo activamente este edificio.
    Retorna el objeto Escuadron defensor, o None si no hay nadie.
    """
    for jugador in todos_los_jugadores:
        if jugador.equipo == equipo_atacante:
            continue
        for escuadron in jugador.escuadrones():
            if escuadron.estado == "defendiendo" and escuadron.destino == edificio:
                return escuadron
    return None


def resolver_llegada_a_edificio(escuadron_atacante, edificio, todos_los_jugadores):
    """
    Se llama cuando un escuadrón termina su viaje hacia un Edificio.
    Resuelve captura automática o combate, según corresponda.
    """
    equipo_atacante = escuadron_atacante.jugador_dueño.equipo
    defensor = buscar_defensor_en_edificio(edificio, equipo_atacante, todos_los_jugadores)

    if defensor is None:
        # Nadie defendiendo -> captura automática
        edificio.dueño = equipo_atacante
        escuadron_atacante.destino = edificio
        escuadron_atacante.estado = "defendiendo"
        return

    # Hay combate
    poder_a = escuadron_atacante.poder_actual()
    poder_b = defensor.poder_actual()
    ganador = resolver_combate(poder_a, poder_b)

    poder_restante = abs(poder_a - poder_b)

    # Ambos bandos destruyen la misma cantidad de poder enemigo en esta
    # pelea (el poder inicial del que pierde, completo), así que ambos
    # ganan los mismos puntos personales por "matar", sin importar quién
    # se queda con el edificio al final.
    poder_eliminado = min(poder_a, poder_b)
    puntos_por_kill = poder_eliminado / ESCALA_PUNTOS_KILL
    escuadron_atacante.jugador_dueño.puntos_personales += puntos_por_kill
    defensor.jugador_dueño.puntos_personales += puntos_por_kill

    if ganador == "A":
        # Gana el atacante
        defensor.soldados_actuales = 0
        defensor.regresar_a_base()

        soldados_restantes = round(poder_restante / escuadron_atacante.poder_por_soldado)
        escuadron_atacante.soldados_actuales = soldados_restantes
        escuadron_atacante.destino = edificio
        escuadron_atacante.estado = "defendiendo"
        edificio.dueño = equipo_atacante
    else:
        # Gana el defensor
        escuadron_atacante.soldados_actuales = 0
        escuadron_atacante.regresar_a_base()

        soldados_restantes = round(poder_restante / defensor.poder_por_soldado)
        defensor.soldados_actuales = soldados_restantes
        # el edificio se queda igual, el defensor sigue ahí


def resolver_llegada_a_jugador(escuadron_atacante, jugador_destino):
    """
    Se llama cuando un escuadrón termina su viaje hacia un Jugador.
    Puede ser: (a) está regresando a SU PROPIO jugador (relleno de base),
    o (b) llegó a atacar a un jugador ENEMIGO (Sistema 2).
    """
    equipo_atacante = escuadron_atacante.jugador_dueño.equipo

    if jugador_destino.equipo == equipo_atacante:
        # Es su propio jugador -> llegó de vuelta a la base, se rellena
        escuadron_atacante.estado = "en_base"
        escuadron_atacante.destino = None
        escuadron_atacante.rellenar_desde_reserva()
    else:
        # Es un jugador enemigo -> Sistema 2, ataque directo
        jugador_destino.recibir_ataque_directo()
        escuadron_atacante.regresar_a_base()


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


def procesar_llegadas(todos_los_jugadores, mapa):
    """
    Recorre todos los escuadrones del mapa; los que llegaron a destino
    este tick ("llego_a_destino") se resuelven según el tipo de destino.
    """
    for jugador in todos_los_jugadores:
        for escuadron in jugador.escuadrones():
            if escuadron.estado == "llego_a_destino":
                if isinstance(escuadron.destino, Edificio):
                    resolver_llegada_a_edificio(escuadron, escuadron.destino, todos_los_jugadores)
                elif isinstance(escuadron.destino, Jugador):
                    resolver_llegada_a_jugador(escuadron, escuadron.destino)


# ============================================================
# AGENTE EVOLUTIVO (basado en genoma)
# ============================================================

def decidir_accion_genoma(jugador, mapa, todos_los_jugadores):
    """
    Reemplazo del agente tonto: cada escuadrón "en_base" evalúa TODAS
    las opciones disponibles (edificios libres + jugadores enemigos)
    usando el genoma del jugador, y elige la de mayor puntaje.
    """
    for escuadron in jugador.escuadrones():
        if escuadron.estado != "en_base":
            continue

        mejor_opcion = None
        mejor_score = None
        mejor_tipo = None  # "edificio" o "jugador"

        for edificio in mapa:
            if edificio.dueño is None:
                asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)
                if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                    continue
                score = puntaje_edificio(escuadron, jugador, edificio, todos_los_jugadores)
                if mejor_score is None or score > mejor_score:
                    mejor_score = score
                    mejor_opcion = edificio
                    mejor_tipo = "edificio"

        for enemigo in todos_los_jugadores:
            if enemigo.equipo == jugador.equipo:
                continue
            asignados = contar_escuadrones_asignados(enemigo, jugador.equipo, todos_los_jugadores)
            if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                continue
            score = puntaje_jugador_enemigo(escuadron, jugador, enemigo, todos_los_jugadores)
            if mejor_score is None or score > mejor_score:
                mejor_score = score
                mejor_opcion = enemigo
                mejor_tipo = "jugador"

        if mejor_opcion is not None:
            if mejor_tipo == "edificio":
                escuadron.enviar_a_atacar(mejor_opcion)
            else:
                escuadron.enviar_a_atacar_jugador(mejor_opcion)


UMBRAL_TELETRANSPORTE = 200  # solo se teletransporta si el objetivo está más lejos que esto


SEPARACION_MINIMA = 10  # nadie puede pararse a menos de esto de otro jugador/edificio


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
    Si el jugador no está en cooldown y tiene escuadrones libres en base,
    revisa si el mejor objetivo disponible está lejos -- si es así, se
    teletransporta cerca de él para que sus escuadrones lleguen más rápido.
    """
    if jugador.cooldown_teletransporte_restante > 0:
        return

    escuadrones_en_base = [e for e in jugador.escuadrones() if e.estado == "en_base"]
    if not escuadrones_en_base:
        return  # todos ocupados, no hace falta reposicionarse

    referencia = escuadrones_en_base[0]
    mejor_obj = None
    mejor_score = None
    for edificio in mapa:
        if edificio.dueño is None:
            asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)
            if asignados >= MAX_ESCUADRONES_POR_EDIFICIO:
                continue
            score = puntaje_edificio(referencia, jugador, edificio, todos_los_jugadores)
            if mejor_score is None or score > mejor_score:
                mejor_score = score
                mejor_obj = edificio

    if mejor_obj is None:
        return

    dist_actual = distancia((jugador.x, jugador.y), (mejor_obj.x, mejor_obj.y))
    if dist_actual > UMBRAL_TELETRANSPORTE:
        nueva_x, nueva_y = posicion_libre_cercana(mejor_obj.x, mejor_obj.y, mapa, todos_los_jugadores)
        jugador.teletransportarse(nueva_x, nueva_y, mapa)


# ============================================================
# AGENTE TONTO -- se deja como referencia / comparación
# ============================================================

def contar_escuadrones_asignados(destino_objetivo, equipo, todos_los_jugadores):
    """
    Cuenta cuántos escuadrones de un equipo ya están yendo hacia o
    defendiendo/atacando este destino (edificio o jugador enemigo).
    Sirve para el límite de defensa, el límite de ataque conjunto,
    y para el término w4 del genoma (coordinación).
    """
    contador = 0
    for j in todos_los_jugadores:
        if j.equipo != equipo:
            continue
        for esc in j.escuadrones():
            if esc.destino is destino_objetivo and esc.estado in (
                "viajando_ataque", "defendiendo", "viajando_ataque_jugador"
            ):
                contador += 1
    return contador


def puntaje_edificio(escuadron, jugador, edificio, todos_los_jugadores):
    """Qué tan atractivo le parece a este genoma ir a este edificio."""
    w1, w2, w3, w4 = jugador.genoma

    valor_puntos = edificio.tasa_alianza
    try:
        cercania = 15 / distancia((escuadron.x, escuadron.y), (edificio.x, edificio.y))
    except ZeroDivisionError:
        cercania = 15

    aliados_ya_asignados = contar_escuadrones_asignados(edificio, jugador.equipo, todos_los_jugadores)

    score = w1 * valor_puntos + w2 * cercania + w4 * aliados_ya_asignados
    return score


def poder_maximo_disponible(jugador_enemigo):
    """
    Retorna el poder del escuadrón más fuerte que tiene el jugador
    enemigo disponible AHORA MISMO en su base (listo para defenderse).
    Si no tiene ninguno en base, retorna 0 (está totalmente expuesto).
    """
    mejor_poder = 0
    for esc in jugador_enemigo.escuadrones():
        if esc.estado == "en_base":
            if esc.poder_actual() > mejor_poder:
                mejor_poder = esc.poder_actual()
    return mejor_poder


def puntaje_jugador_enemigo(escuadron, jugador, enemigo, todos_los_jugadores):
    """Qué tan atractivo le parece a este genoma atacar a este jugador enemigo."""
    w1, w2, w3, w4 = jugador.genoma

    valor_puntos = 0  # atacar un jugador no da puntos de edificio directos
    try:
        cercania = 15 / distancia((escuadron.x, escuadron.y), (enemigo.x, enemigo.y))
    except ZeroDivisionError:
        cercania = 15

    poder_defensa_enemiga = poder_maximo_disponible(enemigo)
    poder_relativo = (escuadron.poder_actual() - poder_defensa_enemiga) / 1_000_000

    aliados_ya_asignados = contar_escuadrones_asignados(enemigo, jugador.equipo, todos_los_jugadores)

    score = w1 * valor_puntos + w2 * cercania + w3 * poder_relativo + w4 * aliados_ya_asignados
    return score


def decidir_accion_agente_tonto(jugador, mapa, todos_los_jugadores):
    """
    Regla fija: cada escuadrón "en_base" va al edificio libre más cercano
    que no haya alcanzado el límite de escuadrones asignados; si no hay
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

    # Foto del estado inicial (todos en su spawn, antes de cualquier decisión)
    replay = [_foto_del_estado(-1, 0, 0, 0, mapa, jugadores)]

    for tick in range(duracion_segundos):
        minuto_actual = tick // 60

        for jugador in jugadores:
            for escuadron in jugador.escuadrones():
                if escuadron.estado in ("viajando_ataque", "viajando_ataque_jugador", "regresando_base"):
                    escuadron.avanzar_un_tick()

        procesar_llegadas(jugadores, mapa)

        for jugador in jugadores:
            jugador.actualizar_cooldown()

        for jugador in jugadores:
            decidir_teletransporte(jugador, mapa, jugadores)

        for jugador in jugadores:
            decidir_accion(jugador, mapa, jugadores)

        mapa_activo = [e for e in mapa if e.minuto_aparicion <= minuto_actual]
        puntos_equipo_A += calcular_puntos_equipo_por_segundo(mapa_activo, "equipo_A")
        puntos_equipo_B += calcular_puntos_equipo_por_segundo(mapa_activo, "equipo_B")
        sumar_puntos_personales(mapa_activo, jugadores)

        if tick % intervalo_grabacion == 0:
            replay.append(_foto_del_estado(tick, minuto_actual, puntos_equipo_A,
                                            puntos_equipo_B, mapa, jugadores))

    return {
        "puntos_equipo_A": puntos_equipo_A,
        "puntos_equipo_B": puntos_equipo_B,
        "jugadores": jugadores,
        "mapa": mapa,
        "replay": replay,
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

    for tick in range(duracion_segundos):
        minuto_actual = tick // 60

        for jugador in jugadores:
            for escuadron in jugador.escuadrones():
                if escuadron.estado in ("viajando_ataque", "viajando_ataque_jugador", "regresando_base"):
                    escuadron.avanzar_un_tick()

        procesar_llegadas(jugadores, mapa)

        for jugador in jugadores:
            jugador.actualizar_cooldown()

        for jugador in jugadores:
            decidir_teletransporte(jugador, mapa, jugadores)

        for jugador in jugadores:
            decidir_accion(jugador, mapa, jugadores)

        mapa_activo = [e for e in mapa if e.minuto_aparicion <= minuto_actual]
        puntos_equipo_A += calcular_puntos_equipo_por_segundo(mapa_activo, "equipo_A")
        puntos_equipo_B += calcular_puntos_equipo_por_segundo(mapa_activo, "equipo_B")
        sumar_puntos_personales(mapa_activo, jugadores)

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

RUIDO_MUTACION = 0.15   # cuánto puede variar un gen al cruzar
CANTIDAD_ELITE = 4       # cuántos genomas top pasan intactos a la siguiente gen.


def generar_genoma_aleatorio():
    return [random.uniform(-1, 1) for _ in range(4)]


def crear_poblacion_inicial(tamano):
    return [generar_genoma_aleatorio() for _ in range(tamano)]


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


def ejecutar_torneo(poblacion, jugadores_por_equipo=5, verbose=False):
    """
    Arma 8 equipos aleatorios a partir de la población completa,
    los empareja en 4 partidas (equipo_A vs equipo_B), corre cada
    simulación, y devuelve el fitness de TODOS los jugadores de las
    4 partidas juntos: [(genoma, fitness), (genoma, fitness), ...]
    """
    poblacion_barajada = poblacion.copy()
    random.shuffle(poblacion_barajada)

    equipos = [
        poblacion_barajada[i * jugadores_por_equipo:(i + 1) * jugadores_por_equipo]
        for i in range(8)
    ]

    resultados_fitness = []

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
            print(f"  Partida {num_partida + 1}: A={resultado['puntos_equipo_A']:.0f} "
                  f"B={resultado['puntos_equipo_B']:.0f}  Gana {equipo_ganador}")

        for jugador in jugadores:
            fit = calcular_fitness(jugador, equipo_ganador)
            resultados_fitness.append((jugador.genoma, fit))

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

    mitad = max(2, len(genomas_ordenados) // 2)
    pool_padres = genomas_ordenados[:mitad]

    nueva_poblacion = list(elite)
    while len(nueva_poblacion) < tamano_poblacion:
        padre_a = random.choice(pool_padres)
        padre_b = random.choice(pool_padres)
        hijo = cruzar_genomas(padre_a, padre_b)
        nueva_poblacion.append(hijo)

    return nueva_poblacion


def evolucionar(tamano_poblacion=80, jugadores_por_equipo=5, max_generaciones=200,
                 generaciones_sin_mejora_limite=15, verbose=True):
    """
    Ciclo completo de evolución. Se detiene cuando el mejor fitness no
    mejora durante `generaciones_sin_mejora_limite` generaciones seguidas,
    o al llegar a `max_generaciones` (límite de seguridad).
    """
    poblacion = crear_poblacion_inicial(tamano_poblacion)
    mejor_fitness_historico = None
    generaciones_sin_mejora = 0
    historial = []

    for gen in range(max_generaciones):
        resultados = ejecutar_torneo(poblacion, jugadores_por_equipo)

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

        if mejor_fitness_historico is None or mejor_fitness_gen > mejor_fitness_historico:
            mejor_fitness_historico = mejor_fitness_gen
            generaciones_sin_mejora = 0
        else:
            generaciones_sin_mejora += 1

        if generaciones_sin_mejora >= generaciones_sin_mejora_limite:
            if verbose:
                print(f"Fitness sin mejorar por {generaciones_sin_mejora_limite} generaciones. Deteniendo.")
            break

        poblacion = crear_siguiente_generacion(resultados, tamano_poblacion)

    mejor_genoma = max(resultados, key=lambda par: par[1])[0]
    return {
        "poblacion_final": poblacion,
        "mejor_genoma": mejor_genoma,
        "historial": historial,
        "ultimos_resultados": resultados,  # (genoma, fitness) de la última generación evaluada
    }


def jugar_gran_final(ultimos_resultados, jugadores_por_equipo=5, intervalo_grabacion=5, verbose=True):
    """
    Toma los 2 mejores genomas de la última generación evaluada y los
    enfrenta en una partida dedicada (cada equipo lleno de copias de
    "su" mejor genoma). Devuelve el resultado + el replay para visualizar.
    """
    ordenados = sorted(ultimos_resultados, key=lambda par: par[1], reverse=True)
    genoma_1 = ordenados[0][0]
    genoma_2 = ordenados[1][0]

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

    resultado["genoma_1"] = genoma_1
    resultado["genoma_2"] = genoma_2
    return resultado


def generar_replay_html(replay, ruta_salida):
    """
    Toma la lista `replay` (de simular_partida_con_replay) y genera un
    archivo HTML autocontenido con el visualizador de time-lapse, listo
    para abrir en el navegador.
    """
    import json

    replay_json = json.dumps(replay)

    plantilla = _PLANTILLA_HTML_REPLAY.replace("REPLAY_DATA_PLACEHOLDER", replay_json)

    with open(ruta_salida, "w") as f:
        f.write(plantilla)

    return ruta_salida


if __name__ == "__main__":
    resultado = simular_partida(cantidad_por_equipo=5, usar_genoma=False, verbose=True)
    print()
    print("=== RESULTADO (agente tonto, prueba rápida) ===")
    print("Equipo A:", resultado["puntos_equipo_A"])
    print("Equipo B:", resultado["puntos_equipo_B"])
