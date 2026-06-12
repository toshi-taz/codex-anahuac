# CODEX ANÁHUAC — Reglas del Juego (Synthetic Data)

> NOTA: Datos sintéticos para el hackathon. No contiene información real o confidencial.
> Sistema de reglas simplificado inspirado en mecánicas de RPG de mesa.

## Sistema de Dados

Todos los checks usan un dado de 20 caras (d20):

| Total | Resultado | Descripción |
|---|---|---|
| 18-20 | Éxito Crítico | Resultado excepcional, bonus narrativo |
| 13-17 | Éxito | Logra el objetivo limpiamente |
| 8-12 | Éxito Parcial | Logra el objetivo pero con complicación |
| 4-7 | Fallo | No logra el objetivo |
| 1-3 | Fallo Crítico | Fallo con consecuencia negativa adicional |

## Modificadores por Personaje

```
Cuauhtli (Guerrero Águila):
  Combate/Captura:    +3
  Intimidación:       +2
  Sigilo:             -1

Itzcoatl (Tlamatini):
  Conocimiento/Lore:  +4
  Adivinación:        +3
  Combate:            -1

Xochitl (Curandera):
  Curación:           +4
  Persuasión:         +2
  Plantas/Venenos:    +3

Tlacaelel (Coyote):
  Sigilo:             +3
  Engaño/Disfraz:     +4
  Información:        +3
  Combate:            +0
```

## Modificadores por Augurio del Día

El Tonalpohualli afecta todos los checks del día:

- **Augurio Favorable:** +2 a todos los checks
- **Augurio Neutro:** Sin modificador
- **Augurio Adverso:** -1 a combate, +1 a conocimiento y rituales

## Sistema de Vida y Energía

- **Vida (VP):** Daño físico. A 0 VP el personaje cae inconsciente.
- **Energía (EP):** Recursos mágicos y espirituales para habilidades especiales.
- **Recuperación:** Descanso completo restaura 5 VP. Temazcal restaura 5 VP a todo el grupo.

## Habilidades Especiales

### Guerrero Águila — Captura Honorable
- **Costo:** 3 EP
- **Efecto:** Tira el dado dos veces, usa el mejor resultado
- **Condición:** Solo en intentos de captura (xochiyaoyotl), no en combate a muerte

### Tlamatini — Lectura del Tonalpohualli
- **Costo:** 2 EP
- **Efecto:** Consulta el MCP para obtener el augurio del día con sus modificadores exactos
- **Condición:** Solo 1 vez por escena

### Curandera — Temazcal Ritual
- **Costo:** 4 EP + 1 planta
- **Efecto:** Restaura 5 VP a todos los personajes del grupo
- **Condición:** Requiere acceso a un temazcal (disponible en ciudades)
- **Cooldown:** 1 vez por sesión de juego

### Coyote — Contacto en el Mercado
- **Costo:** 10 granos de cacao (moneda del juego)
- **Efecto:** Consulta el MCP para obtener información de cualquier ciudad
- **Condición:** Solo en ciudades o cerca de rutas de comercio

## Combate

El combate en el Anáhuac sigue la xochiyaoyotl (Guerra Florida):

1. **Iniciativa:** Cada personaje tira d20 + modificador de sigilo
2. **Acción:** Atacar, Capturar, Defender, Usar habilidad, Huir
3. **Capturar** (objetivo preferido): d20 + mod vs Dificultad del enemigo
4. **Matar** (deshonroso): Penalización de -2 a reputación en la orden

### Dificultades de Enemigos

| Tipo de enemigo | Dificultad | VP |
|---|---|---|
| Guarda común | 8 | 10 |
| Guerrero jaguar | 14 | 16 |
| Comandante rebelde | 17 | 20 |
| Guardián sobrenatural | 19 | 30 |

## Inventario y Economía

**Moneda:** Granos de cacao (el oro equivale a 20 cacaos)

| Objeto | Precio |
|---|---|
| Macuahuitl de obsidiana fina | 20 cacaos |
| Ichcahuipilli (armadura) | 25 cacaos |
| Bolsa de plantas medicinales | 8 cacaos |
| Información de mercado | 10 cacaos |
| Soborno a guardia común | 5 cacaos |

## Estado de la Partida (Template JSON)

```json
{
  "sesion": 1,
  "turno": 0,
  "ubicacion": "Plaza Central de Tenochtitlan",
  "mision_activa": "Investigar conspiración en Chalco",
  "dias_restantes": 10,
  "party": {
    "guerrero_aguila": {"vida": 20, "energia": 15, "cautivos": 0, "cacaos": 20},
    "tlamatini": {"vida": 15, "energia": 20, "conocimiento": 10, "cacaos": 15},
    "curandera": {"vida": 18, "energia": 18, "plantas": 5, "cacaos": 12},
    "coyote": {"vida": 16, "energia": 17, "cacaos": 50, "deuda": 50}
  },
  "flags": {
    "conspiracion_revelada": false,
    "alianza_chalco": false,
    "mapa_recuperado": false,
    "deuda_coyote_resuelta": false
  }
}
```
