"""
PASO 1 (v2): El mapa con datos reales de Elixir Scramble
-----------------------------------------------------------
Ahora los edificios no solo dan puntos, algunos tienen efectos especiales
(el Observatorio multiplica los puntos de TODOS los edificios del equipo).

Todavía sin agentes, sin combate. Solo el "tablero" + cómo se calculan
los puntos de un equipo en un instante dado.
"""

import math, random

VELOCIDAD_TROPAS = 2.2


class Edificio:
    """
    TODO: agrega los atributos que necesitas en __init__.
    Basándote en la tabla que armamos, cada edificio necesita:
    - nombre
    - x, y (posición en el mapa, tú las inventas)
    - tasa_alianza (puntos/seg para el equipo)
    - tasa_personal (puntos/seg para el jugador que lo capturó)
    - efecto_especial: un string o None. Usa uno de estos valores:
        "multiplicador_puntos"  -> el Observatorio
        "buff_aliados"          -> Reliquias de Guerra
        "debuff_enemigos"       -> Altar Maldito
        "reduccion_cooldown"    -> Portal de Migración
        "curacion"              -> Tienda de Curación
        None                    -> Taller, Castillo, Camps (no tienen efecto)
    - valor_efecto: el número asociado (ej. 0.10 para el Observatorio,
        0.15 para Reliquias/Altar, 0.50 para el Portal). Usa None si
        efecto_especial es None.
    - minuto_aparicion: 0 para fase 1, 10 (o el minuto que decidas) para
        fase 2, 13 para camps.
    - dueño: None al inicio (nadie lo controla)
    """

    def __init__(self, nombre, x, y, tasa_alianza, tasa_personal,
                 efecto_especial=None, valor_efecto=None, minuto_aparicion=0):
        # TODO: completa las asignaciones self.xxx = xxx
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
    """Ya la resolviste en la v1 -- pégala aquí tal cual.""" 
    calc_distancia = math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
    return calc_distancia

def tiempo_de_viaje(pos1, pos2, velocidad):
    """Ya la resolviste en la v1 -- pégala aquí tal cual."""
    if velocidad == 0:
        return None
    else:
        calc_distancia = distancia(pos1, pos2)
        return calc_distancia/velocidad


def crear_mapa():
    """
    TODO: crea y retorna una lista con los edificios reales.
    Usa la tabla que armamos:

    Nombre                  | tasa_alianza | tasa_personal | efecto              | valor | minuto
    Tienda de Curación      | 30           | 30            | curacion            | ?     | 0
    Observatorio            | 10           | 30            | multiplicador_puntos| 0.10  | 0
    Taller de Alquimia      | 50           | 30            | None                | None  | 0
    Castillo de Elixir      | 80           | 30            | None                | None  | 10
    Altar Maldito           | 10           | 30            | debuff_enemigos     | 0.15  | 10
    Portal de Migración     | 10           | 30            | reduccion_cooldown  | 0.50  | 0
    Reliquias de Guerra     | 10           | 30            | buff_aliados        | 0.15  | 10
    Campamentos             | 5            | 5             | None                | None  | 13

    Posiciones (x, y): distribúyelas tú en un mapa, ej. de 0 a 1000
    en cada eje, con el Castillo cerca del centro.
    """
    mapa = [
    # TODO: agrega cada Edificio(...) a la lista mapa
    Edificio(nombre = "tienda de curacion #1", x = 300, y = 100, tasa_alianza = 30,
                                    tasa_personal = 30, efecto_especial = "curacion", valor_efecto = None),
    Edificio(nombre = "tienda de curacion #2", x = 150, y = 350, tasa_alianza = 30,
                                    tasa_personal = 30, efecto_especial = "curacion", valor_efecto = None),
    Edificio(nombre = "tienda de curacion #3", x = 850, y = 650, tasa_alianza = 30,
                                    tasa_personal = 30, efecto_especial = "curacion", valor_efecto = None),
    Edificio(nombre = "tienda de curacion #4", x = 700, y = 900, tasa_alianza = 30,
                                    tasa_personal = 30, efecto_especial = "curacion", valor_efecto = None),
    Edificio(nombre = "taller de alquimia #1", x = 150, y = 650, tasa_alianza = 50,
                                    tasa_personal = 30),
    Edificio(nombre = "taller de alquimia #2", x = 850, y = 350, tasa_alianza = 50,
                                    tasa_personal = 30),
    Edificio(nombre = "observatorio", x = 300, y = 900, tasa_alianza = 10,
                        tasa_personal = 30, efecto_especial = "multiplicador_puntos", valor_efecto = 0.10),
    Edificio(nombre = "portal de migracion", x = 700, y = 100, tasa_alianza = 10,
                        tasa_personal = 30, efecto_especial = "reduccion_cooldown", valor_efecto = 0.50),
    Edificio(nombre = "altar maldito", x = 500, y = 250, tasa_alianza = 10,
                        tasa_personal = 30, efecto_especial = "debuff_enemigos", valor_efecto = 0.15,
                        minuto_aparicion = 10),
    Edificio(nombre = "reliquias de guerra", x = 500, y = 750, tasa_alianza = 10,
                        tasa_personal = 30, efecto_especial = "buff_aliados", valor_efecto = 0.15,
                        minuto_aparicion = 10),
    Edificio(nombre = "castillo", x = 500, y = 500, tasa_alianza = 80, tasa_personal = 30,
                        minuto_aparicion = 10),
    Edificio(nombre = "campamento #1", x = 700, y = 700, tasa_alianza = 5, tasa_personal = 5,
                        minuto_aparicion = 13),
    Edificio(nombre = "campamento #2", x = 300, y = 300, tasa_alianza = 5, tasa_personal = 5,
                        minuto_aparicion = 13)
    ]
    return mapa


def calcular_puntos_equipo_por_segundo(mapa, nombre_equipo):
    """
    Calcula cuántos puntos de alianza por segundo está generando
    un equipo dado el estado actual del mapa (quién controla qué).

    Pasos que tienes que implementar:
    1. Filtra los edificios cuyo dueño == nombre_equipo
    2. Suma sus tasa_alianza -> esto es el total "base"
    3. Revisa si alguno de esos edificios controlados tiene
       efecto_especial == "multiplicador_puntos"
    4. Si lo tiene, aplica ese porcentaje extra al total base
       (ej. total_base * (1 + valor_efecto))
    5. Retorna el total final

    TODO: implementa esta función siguiendo esos 5 pasos.
    Pista: piensa qué pasaría si, por error de datos, hubiera más de
    un edificio con el mismo efecto_especial -- tu código no debería
    romperse, aunque en este mapa solo exista un Observatorio.
    """
    total_base = 0
    bonus = 0

    for Edificio in mapa:
        if Edificio.dueño == nombre_equipo:
            total_base += Edificio.tasa_alianza
            if Edificio.efecto_especial == "multiplicador_puntos":
                bonus = Edificio.valor_efecto
    
    total_base += total_base * bonus
                

    return total_base


def probabilidad_de_ganar(poder_a, poder_b, k=1.5):
    """
    Calcula la probabilidad de que A le gane a B, usando la diferencia
    de poder en millones y una función logística.

    poder_a, poder_b: vienen en unidades reales (ej. 8_000_000), no en millones.
    Tienes que convertirlos a millones tú dentro de la función.
    """
    # TODO: 1. calcula la diferencia en millones: (poder_a - poder_b) / 1_000_000
    diferencia = (poder_a - poder_b) / 1000000
    # TODO: 2. calcula el exponente: -k * diferencia
    exponente = -k * diferencia
    # TODO: 3. aplica la fórmula completa: 1 / (1 + math.exp(exponente))
    resultado = 1 / (1 + math.exp(exponente))
    # TODO: return del resultado
    return resultado


def resolver_combate(poder_a, poder_b, k=1.5):
    """
    Determina quién gana un combate, usando la probabilidad y una
    tirada aleatoria.

    Retorna "A" o "B" según quién ganó.
    """
    prob_a_gana = probabilidad_de_ganar(poder_a, poder_b, k)
    # TODO: usa random.random() (te da un número entre 0.0 y 1.0)
    aleatorio = random.random()
    # TODO: si ese número es MENOR que prob_a_gana, gana A; si no, gana B
    if aleatorio <= prob_a_gana:
        return "A"
    else:
        return "B"
    # TODO: return "A" o return "B" según corresponda


class Escuadron:
    """
    Representa uno de los 3 escuadrones de ataque de un jugador.

    Atributos que necesitas:
    - jugador_dueño: referencia al objeto Jugador al que pertenece
    - capacidad_maxima: cuántos soldados caben aquí como máximo (fijo)
    - soldados_actuales: cuántos soldados tiene AHORA (puede ser menos)
    - poder_por_soldado: lo copias del jugador dueño, para poder calcular
      el poder de este escuadrón sin tener que ir a buscar al jugador
      cada vez
    - estado: string, empieza en "en_base"
    - destino: el Edificio hacia el que va (None si está en base)
    - x, y: posición actual (empieza igual a la del jugador dueño)
    """

    def __init__(self, jugador_dueño, capacidad_maxima, poder_por_soldado):
        # TODO: completa las asignaciones self.xxx = xxx
        # Pista: soldados_actuales al crear el escuadrón por primera vez
        # debería ser igual a capacidad_maxima (sale lleno la primera vez)
        self.jugador_dueño = jugador_dueño
        self.capacidad_maxima = capacidad_maxima
        self.poder_por_soldado = poder_por_soldado
        self.soldados_actuales = capacidad_maxima
        self.estado = "en_base"
        self.destino = None
        self.x = jugador_dueño.x
        self.y = jugador_dueño.y

    def poder_actual(self):
        """
        TODO: retorna el poder de combate de este escuadrón AHORA MISMO.
        Pista: es una multiplicación simple de dos atributos que ya tienes.
        """
        return self.poder_por_soldado *  self.soldados_actuales

    def avanzar_un_tick(self):
        """
        Mueve el escuadrón un paso hacia su destino, si tiene uno.
        """
        if self.destino is None:
            return  # no hay a dónde ir, no hace nada
        
        pos_actual = (self.x, self.y)
        pos_destino = (self.destino.x, self.destino.y)

        dist_restante = distancia(pos_actual, pos_destino)

        if dist_restante <= VELOCIDAD_TROPAS:
            # TODO: ya llegó (o va a llegar este tick) -> "snapea" a la
            # posición exacta del destino, en vez de calcular una dirección
            # self.x = ..., self.y = ...
            # y aquí deberías cambiar self.estado también, piensa a qué valor
            self.x = self.destino.x
            self.y = self.destino.y
            self.estado = "llego_a_destino"
        else:
            # TODO: todavía no llega -> calcula la dirección y avanza
            # direccion_x = (pos_destino[0] - pos_actual[0]) / dist_restante
            # direccion_y = ...
            # self.x = self.x + velocidad * direccion_x
            # self.y = ...
            direccion_x = (pos_destino[0] - pos_actual[0]) / dist_restante
            direccion_y = (pos_destino[1] - pos_actual[1]) / dist_restante
            self.x = self.x + VELOCIDAD_TROPAS * direccion_x
            self.y = self.y + VELOCIDAD_TROPAS * direccion_y

    def enviar_a_atacar(self, edificio_objetivo):
        self.destino = edificio_objetivo
        self.estado = "viajando_ataque"


class Jugador:
    def __init__(self, nombre, equipo, x, y):
        self.nombre = nombre
        self.equipo = equipo
        self.x = x
        self.y = y
        self.vidas = 4
        self.puntos_personales = 0
        self.destino = None

        # TODO 1: genera total_soldados con random.randint(18462, 26000)
        total_soldados = random.randint(18462, 29000)
        self.total_soldados = total_soldados
        # TODO 2: determina el tier ("T7"/"T8"/"T9") usando los cortes de 3500
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
        # TODO 3: define poder_por_soldado según el tier (915/1100/1350)
        # TODO 4: calcula poder_total = total_soldados * poder_por_soldado
        self.poder_total = total_soldados * poder_por_soldado
        # TODO 5: calcula los 3 escuadrones (cantidad de soldados en cada uno)
        #         usando random.uniform con los rangos de variación que definimos
        capacidad_1 = round(total_soldados * random.uniform(0.104, 0.164))
        self.escuadron_1 = Escuadron(jugador_dueño=self, capacidad_maxima=capacidad_1, poder_por_soldado=poder_por_soldado)   
        capacidad_2 = round(total_soldados * random.uniform(0.065, 0.125))  # 9.5% ± 3%
        self.escuadron_2 = Escuadron(jugador_dueño=self, capacidad_maxima=capacidad_2, poder_por_soldado=poder_por_soldado)   
        capacidad_3 = round(total_soldados * random.uniform(0.050, 0.110))  # 8.0% ± 3%     
        self.escuadron_3 = Escuadron(jugador_dueño=self, capacidad_maxima=capacidad_3, poder_por_soldado=poder_por_soldado)   

        # TODO 6: guarda todo como atributos self.xxx para usar después

if __name__ == "__main__":

    mapa = crear_mapa()

    # --- Zona de pruebas manuales ---
    # TODO: simula manualmente que "equipo_A" capturó el Castillo y
    # el Observatorio (asigna edificio.dueño = "equipo_A" a esos dos).
    # Luego llama calcular_puntos_equipo_por_segundo(mapa, "equipo_A")
    # y verifica a mano que el resultado tenga sentido:
    #   base = 80 (castillo) + 10 (observatorio) = 90
    #   con +10% del observatorio = 90 * 1.10 = 99
    # Si tu función no da 99, hay un error en tu lógica.


    jugador_prueba = Jugador(nombre="Doctor1", equipo="equipo_A", x=0, y=0)
    castillo = Edificio(nombre="castillo", x=100, y=0, tasa_alianza=80, tasa_personal=30, minuto_aparicion=10)

    escuadron = jugador_prueba.escuadron_1
    escuadron.destino = castillo

    # Simula varios ticks seguidos
    for i in range(50):
        escuadron.avanzar_un_tick()
        print(f"Tick {i}: x={escuadron.x:.2f}, y={escuadron.y:.2f}, estado={escuadron.estado}")
        if escuadron.estado == "llego_a_destino":
            break