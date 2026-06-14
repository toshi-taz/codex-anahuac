# =============================================================================
# CODEX ANÁHUAC — Servidor MCP de Mecánicas RPG
# Herramientas que el Tlacuilo invoca durante la partida
# =============================================================================

from fastmcp import FastMCP
import random
import json

mcp = FastMCP(name="MecanicasAnahuac")

# ─── ESTADO GLOBAL DE LA PARTIDA ─────────────────────────────────────────────
estado_partida = {
    "guerrero_aguila": {"nombre": "Cuauhtli", "vida": 20, "energia": 15, "cautivos": 0, "orden": "Águila"},
    "tlamatini":       {"nombre": "Itzcoatl",  "vida": 15, "energia": 20, "conocimiento": 10, "orden": "Sacerdote"},
    "curandera":       {"nombre": "Xochitl",   "vida": 18, "energia": 18, "plantas": 5, "orden": "Ticitl"},
    "coyote":          {"nombre": "Tlacaelel", "vida": 16, "energia": 17, "oro": 50, "orden": "Mercader"},
}

# Signos del Tonalpohualli
SIGNOS = [
    "Cipactli", "Ehecatl", "Calli", "Cuetzpalin", "Coatl",
    "Miquiztli", "Mazatl", "Tochtli", "Atl", "Itzcuintli",
    "Ozomatli", "Malinalli", "Acatl", "Ocelotl", "Cuauhtli",
    "Cozcacuauhtli", "Ollin", "Tecpatl", "Quiahuitl", "Xochitl"
]

AUGURIOS = {
    "Cipactli": ("favorable", "Energía primordial. Buen día para iniciar empresas."),
    "Ehecatl":  ("neutro",    "El viento cambia. Cuidado con decisiones apresuradas."),
    "Calli":    ("favorable", "Protección del hogar. Fuerza defensiva."),
    "Cuetzpalin":("favorable","Agilidad y cambio. Ideal para maniobras rápidas."),
    "Coatl":    ("adverso",   "La serpiente acecha. Alerta ante traiciones."),
    "Miquiztli":("adverso",   "Día de la muerte. Evitar combates innecesarios."),
    "Mazatl":   ("neutro",    "El venado huye. Día para la observación, no la acción."),
    "Tochtli":  ("favorable", "Fertilidad y abundancia. Recursos se multiplican."),
    "Atl":      ("favorable", "Purificación. Bueno para curación y rituales."),
    "Itzcuintli":("neutro",   "El perro guía. Fidelidad y seguir el rastro."),
    "Ozomatli": ("favorable", "Alegría y astucia. Engaños y estrategias funcionan."),
    "Malinalli": ("adverso",  "Hierba que corta. Conflictos internos posibles."),
    "Acatl":    ("favorable", "La caña es firme. Excelente para alianzas."),
    "Ocelotl":  ("favorable", "El jaguar domina la noche. Poder máximo en sigilo."),
    "Cuauhtli": ("favorable", "El águila vuela alto. Victoria en combate directo."),
    "Cozcacuauhtli":("neutro","Sabiduría del zopilote. Ver lo que otros ignoran."),
    "Ollin":    ("adverso",   "Movimiento sísmico. Cambios drásticos e inevitables."),
    "Tecpatl":  ("adverso",   "El pedernal corta. Sacrificio y decisiones duras."),
    "Quiahuitl":("neutro",    "La lluvia purifica. Renovación tras el caos."),
    "Xochitl":  ("favorable", "La flor de la vida. Arte, amor y creatividad florecen."),
}

NUMERALES_PODER = {
    1: "inicio, potencia pura",
    2: "dualidad, equilibrio",
    3: "movimiento, acción",
    4: "estabilidad, los cuatro rumbos",
    5: "centro, poder del quinto sol",
    6: "flujo, transición",
    7: "misticismo, conexión divina",
    8: "abundancia, completitud",
    9: "misterio, el inframundo",
    10: "retorno, ciclo",
    11: "tensión, prueba",
    12: "transformación",
    13: "sagrado máximo, plenitud cósmica",
}


# ─── HERRAMIENTAS MCP ─────────────────────────────────────────────────────────

@mcp.tool()
async def tirar_dados_combate(atacante: str, tipo_ataque: str) -> dict:
    """
    Tira dados para resolver combate según las reglas mexicas.
    El objetivo en la xochiyaoyotl es capturar, no matar.
    
    Args:
        atacante: nombre del personaje que ataca
        tipo_ataque: 'captura' | 'defensa' | 'habilidad_especial'
    
    Returns:
        resultado del dado, modificadores y narrativa del combate
    """
    dado_base = random.randint(1, 20)
    
    modificadores = {
        "captura": +3,      # capturar enemigos es más honorable
        "defensa": +2,
        "habilidad_especial": +5,
    }
    mod = modificadores.get(tipo_ataque, 0)
    total = min(dado_base + mod, 20)
    
    # Determinar resultado
    if total >= 18:
        resultado = "exito_critico"
        narrativa = f"¡{atacante} ejecuta una maniobra magistral digna de los mejores guerreros del Quinto Sol!"
    elif total >= 13:
        resultado = "exito"
        narrativa = f"{atacante} logra su objetivo con destreza y valor."
    elif total >= 8:
        resultado = "exito_parcial"
        narrativa = f"{atacante} avanza, pero no sin dificultad. El enemigo ofrece resistencia."
    elif total >= 4:
        resultado = "fallo"
        narrativa = f"{atacante} falla en su intento. El enemigo aprovecha la apertura."
    else:
        resultado = "fallo_critico"
        narrativa = f"¡Desastre! {atacante} comete un error grave. Tezcatlipoca observa desde su espejo."

    return {
        "dado": dado_base,
        "modificador": mod,
        "total": total,
        "tipo_ataque": tipo_ataque,
        "resultado": resultado,
        "narrativa": narrativa,
        "honor_ganado": 2 if tipo_ataque == "captura" and resultado in ["exito", "exito_critico"] else 0
    }


@mcp.tool()
async def consultar_tonalpohualli() -> dict:
    """
    Consulta el día actual en el calendario sagrado Tonalpohualli.
    Determina los augurios y la energía del día para la partida.
    
    Returns:
        signo del día, numeral, augurio y recomendaciones rituales
    """
    signo = random.choice(SIGNOS)
    numeral = random.randint(1, 13)
    tipo_augurio, descripcion = AUGURIOS[signo]
    poder_numeral = NUMERALES_PODER[numeral]

    # Calcular bonificación según augurio
    bonos = {
        "favorable": {"combate": +2, "magia": +2, "comercio": +1},
        "neutro":    {"combate":  0, "magia":  0, "comercio":  0},
        "adverso":   {"combate": -1, "magia": +1, "comercio": -1},
    }
    bono = bonos[tipo_augurio]

    return {
        "fecha": f"{numeral} {signo}",
        "signo": signo,
        "numeral": numeral,
        "augurio": tipo_augurio,
        "descripcion": descripcion,
        "poder_numeral": poder_numeral,
        "bonificaciones": bono,
        "recomendacion": (
            "Los dioses sonríen hoy. Actúa con determinación." if tipo_augurio == "favorable"
            else "Procede con cautela. Los presagios son complejos." if tipo_augurio == "neutro"
            else "Día difícil. Consulta al Tlamatini antes de actuar."
        )
    }


@mcp.tool()
def estado_personaje(personaje: str) -> dict:
    """
    Retorna el estado actual de un personaje jugador.
    
    Args:
        personaje: 'guerrero_aguila' | 'tlamatini' | 'curandera' | 'coyote'
    
    Returns:
        estadísticas actuales del personaje
    """
    p = estado_partida.get(personaje.lower())
    if not p:
        return {
            "error": f"Personaje '{personaje}' no encontrado",
            "disponibles": list(estado_partida.keys())
        }

    vida_pct = (p["vida"] / 20) * 100
    estado_fisico = (
        "Óptimo — listo para la batalla" if vida_pct >= 75
        else "Herido — necesita atención" if vida_pct >= 40
        else "Crítico — requiere curación urgente"
    )

    return {
        **p,
        "estado_fisico": estado_fisico,
        "vida_porcentaje": vida_pct,
        "puede_combatir": p["vida"] > 5,
        "necesita_curacion": p["vida"] < 10,
    }


@mcp.tool()
def aplicar_curacion(paciente: str, planta: str) -> dict:
    """
    La Curandera aplica medicina tradicional mexica.
    
    Args:
        paciente: nombre del personaje a curar
        planta: 'nopal' | 'maguey' | 'yoloxochitl' | 'copal' | 'chian'
    
    Returns:
        resultado de la curación y puntos de vida recuperados
    """
    plantas_poder = {
        "nopal":       {"cura": 3, "efecto": "Limpia heridas. Detiene hemorragias menores."},
        "maguey":      {"cura": 5, "efecto": "Extrae venenos. Regenera tejido dañado."},
        "yoloxochitl": {"cura": 4, "efecto": "Fortalece el corazón. Restaura energía vital."},
        "copal":       {"cura": 2, "efecto": "Purificación espiritual. Aleja males del tonal."},
        "chian":       {"cura": 3, "efecto": "Nutre profundamente. Restaura resistencia física."},
    }

    planta_data = plantas_poder.get(planta.lower())
    if not planta_data:
        return {"error": f"Planta '{planta}' desconocida", "disponibles": list(plantas_poder.keys())}

    p_key = paciente.lower().replace(" ", "_")
    if p_key in estado_partida:
        vida_anterior = estado_partida[p_key]["vida"]
        estado_partida[p_key]["vida"] = min(20, vida_anterior + planta_data["cura"])
        vida_nueva = estado_partida[p_key]["vida"]
    else:
        vida_anterior = vida_nueva = "desconocido"

    return {
        "paciente": paciente,
        "planta_usada": planta,
        "puntos_curados": planta_data["cura"],
        "efecto": planta_data["efecto"],
        "vida_anterior": vida_anterior,
        "vida_actual": vida_nueva,
        "narrativa": f"Las manos expertas de la Curandera aplican {planta}. {planta_data['efecto']}"
    }


@mcp.tool()
async def consultar_mercado(ciudad: str) -> dict:
    """
    El Coyote consulta precios y disponibilidad en el tianguis.
    
    Args:
        ciudad: 'tenochtitlan' | 'tlatelolco' | 'texcoco' | 'chalco'
    
    Returns:
        precios actuales, objetos disponibles y rumores del mercado
    """
    mercados = {
        "tenochtitlan": {
            "especialidad": "Armas y equipamiento guerrero",
            "objetos": [
                {"nombre": "Macuahuitl de obsidiana fina", "precio": 20, "disponible": True},
                {"nombre": "Yelmo de águila", "precio": 35, "disponible": True},
                {"nombre": "Ichcahuipilli reforzado", "precio": 25, "disponible": False},
                {"nombre": "Escudo de plumas quetzal", "precio": 50, "disponible": True},
            ],
            "rumor": "Se habla de movimientos de tropas hacia Chalco. El Tlatoani está inquieto.",
        },
        "tlatelolco": {
            "especialidad": "Hierbas, joyas y productos exóticos",
            "objetos": [
                {"nombre": "Bolsa de copal sagrado", "precio": 5, "disponible": True},
                {"nombre": "Yoloxochitl seco", "precio": 8, "disponible": True},
                {"nombre": "Turquesa fina (collar)", "precio": 40, "disponible": True},
                {"nombre": "Cacao de calidad superior", "precio": 15, "disponible": True},
            ],
            "rumor": "Un mercader de Oaxaca trae noticias de alianzas secretas en el sur.",
        },
        "texcoco": {
            "especialidad": "Conocimiento, manuscritos y astronomía",
            "objetos": [
                {"nombre": "Amatl con mapa estelar", "precio": 30, "disponible": True},
                {"nombre": "Códice del tonalpohualli", "precio": 45, "disponible": False},
                {"nombre": "Cristal de cuarzo para adivinación", "precio": 20, "disponible": True},
            ],
            "rumor": "Los astrólogos de Texcoco predicen un eclipse. Mal augurio para el Quinto Sol.",
        },
        "chalco": {
            "especialidad": "Información y contactos del inframundo político",
            "objetos": [
                {"nombre": "Información sobre patrullas enemigas", "precio": 10, "disponible": True},
                {"nombre": "Mapa de rutas secretas", "precio": 25, "disponible": True},
                {"nombre": "Salvoconducto falsificado", "precio": 30, "disponible": True},
            ],
            "rumor": "¡Cuidado! Hay espías de los rebeldes infiltrados en el mercado.",
        },
    }

    mercado = mercados.get(ciudad.lower())
    if not mercado:
        return {"error": f"Ciudad '{ciudad}' no encontrada", "disponibles": list(mercados.keys())}

    return {
        "ciudad": ciudad.title(),
        **mercado,
        "consejo_coyote": "Recuerda: en el tianguis, quien tiene información tiene poder."
    }


if __name__ == "__main__":
    print("🐍 Servidor MCP 'MecanicasAnahuac' iniciado")
    print("Herramientas disponibles:")
    print("  - tirar_dados_combate(atacante, tipo_ataque)")
    print("  - consultar_tonalpohualli()")
    print("  - estado_personaje(personaje)")
    print("  - aplicar_curacion(paciente, planta)")
    print("  - consultar_mercado(ciudad)")
    mcp.run()
