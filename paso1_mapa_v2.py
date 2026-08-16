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

# ============================================================
# CONSTANTES GLOBALES
# ============================================================

VELOCIDAD_TROPAS = 2.2          # unidades de distancia por segundo
COOLDOWN_TELETRANSPORTE = 120   # segundos
K_COMBATE = 1.5                 # constante de la fórmula logística
DURACION_PARTIDA_SEGUNDOS = 1800  # 30 minutos

SPAWN_EQUIPO_A = (500, 0)
SPAWN_EQUIPO_B = (500, 1000)

RADIO_DETECCION_COMBATE = 5  # distancia máxima para considerar "cerca"
                              # (ajustable -- si el mapa se siente muy
                              # disperso o muy apretado, cambia este número)


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
    def __init__(self, nombre, equipo, x, y):
        self.nombre = nombre
        self.equipo = equipo
        self.x = x
        self.y = y
        self.hits = 4
        self.puntos_personales = 0
        self.destino = None
        self.cooldown_teletransporte_restante = 0

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
# AGENTE TONTO -- TODO: PENDIENTE, LO ARMAMOS JUNTOS DESPUÉS
# ============================================================

def decidir_accion_agente_tonto(jugador, mapa, todos_los_jugadores):
    for escuadron in jugador.escuadrones():
        if escuadron.estado != "en_base":
            continue

        mejor_libre = None
        menor_distancia_libre = None
        for edificio in mapa:
            if edificio.dueño == None:
                if menor_distancia_libre == None or distancia([escuadron.x, escuadron.y], [edificio.x, edificio.y]) < menor_distancia_libre:
                    menor_distancia_libre = distancia([escuadron.x, escuadron.y], [edificio.x, edificio.y])
                    mejor_libre = edificio
                    print(mejor_libre)   
        if mejor_libre is not None:
            escuadron.enviar_a_atacar(mejor_libre)
            continue  # ya decidido, pasa al siguiente escuadrón

        mejor_enemigo = None
        menor_distancia_enemigo = None
        for k in todos_los_jugadores:
            if k.equipo != jugador.equipo:
                if menor_distancia_enemigo == None or distancia([escuadron.x, escuadron.y], [k.x, k.y]) < menor_distancia_enemigo:
                    menor_distancia_enemigo = distancia([escuadron.x, escuadron.y], [k.x, k.y])
                    mejor_enemigo = k
                    print(mejor_enemigo)
        if mejor_enemigo is not None:
            escuadron.enviar_a_atacar_jugador(mejor_enemigo)


# ============================================================
# BUCLE PRINCIPAL DE SIMULACIÓN
# ============================================================

def crear_jugadores(cantidad_por_equipo):
    jugadores = []
    for i in range(cantidad_por_equipo):
        x, y = SPAWN_EQUIPO_A
        jugadores.append(Jugador(nombre=f"A_{i}", equipo="equipo_A", x=x, y=y))
    for i in range(cantidad_por_equipo):
        x, y = SPAWN_EQUIPO_B
        jugadores.append(Jugador(nombre=f"B_{i}", equipo="equipo_B", x=x, y=y))
    return jugadores


def simular_partida(cantidad_por_equipo=5, duracion_segundos=DURACION_PARTIDA_SEGUNDOS, verbose=False):
    mapa = crear_mapa()
    jugadores = crear_jugadores(cantidad_por_equipo)

    puntos_equipo_A = 0
    puntos_equipo_B = 0

    for tick in range(duracion_segundos):
        minuto_actual = tick // 60

        # 1. Mover todos los escuadrones que tengan destino
        for jugador in jugadores:
            for escuadron in jugador.escuadrones():
                if escuadron.estado in ("viajando_ataque", "viajando_ataque_jugador", "regresando_base"):
                    escuadron.avanzar_un_tick()

        # 2. Resolver llegadas (combates / capturas / relleno)
        procesar_llegadas(jugadores, mapa)

        # 3. Actualizar cooldowns de teletransporte
        for jugador in jugadores:
            jugador.actualizar_cooldown()

        # 4. Decisiones del agente (pendiente de implementar)
        for jugador in jugadores:
            decidir_accion_agente_tonto(jugador, mapa, jugadores)

        # 5. Sumar puntos de este segundo (solo edificios ya desbloqueados)
        mapa_activo = [e for e in mapa if e.minuto_aparicion <= minuto_actual]
        puntos_equipo_A += calcular_puntos_equipo_por_segundo(mapa_activo, "equipo_A")
        puntos_equipo_B += calcular_puntos_equipo_por_segundo(mapa_activo, "equipo_B")

        if verbose and tick % 300 == 0:
            print(f"Tick {tick} (min {minuto_actual}): A={puntos_equipo_A:.0f}  B={puntos_equipo_B:.0f}")

    return {
        "puntos_equipo_A": puntos_equipo_A,
        "puntos_equipo_B": puntos_equipo_B,
        "jugadores": jugadores,
        "mapa": mapa,
    }


if __name__ == "__main__":
    resultado = simular_partida(cantidad_por_equipo=5, verbose=True)
    print()
    print("=== RESULTADO FINAL ===")
    print("Equipo A:", resultado["puntos_equipo_A"])
    print("Equipo B:", resultado["puntos_equipo_B"])