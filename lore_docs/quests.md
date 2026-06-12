# CODEX ANÁHUAC — Misiones y Aventuras (Synthetic Data)

> NOTA: Datos sintéticos para el hackathon. No contiene información real o confidencial.

## Misión Principal

---

### La Conspiración de Chalco

**Estado:** Activa
**Encargado por:** El Tlatoani Axayácatl de Tenochtitlan
**Objetivo:** Investigar el bloqueo de rutas de tributo hacia la capital

**Descripción:**
Desde hace tres meses, los cargamentos de tributo provenientes de Chalco
llegan incompletos o simplemente no llegan. Los mensajeros enviados no
regresan. El Tlatoani sospecha de una conspiración organizada, pero no
puede enviar un ejército sin evidencia — hacerlo provocaría la guerra abierta
que quiere evitar. Necesita un grupo pequeño y discreto.

**Pistas conocidas:**
1. El último mensajero llegó herido y murió diciendo "la serpiente azul"
2. Un mercader pochteca reportó ver soldados con marcas de Tlaxcala en Chalco
3. El noble chalca Itztli fue visto en Texcoco hace dos semanas sin razón aparente

**Obstáculos:**
- Los caminos a Chalco tienen patrullas enemigas
- No se sabe quién es aliado en Chalco y quién es enemigo
- El tiempo corre — el siguiente cargamento de tributo sale en 10 días

**Recompensa:** Rango militar elevado para Cuauhtli + 200 mantas de algodón
**Consecuencia de fallo:** Rebelión abierta en Chalco, posible guerra

**Tags:** misión_principal, Chalco, conspiración, tributo, urgente

---

## Misiones Secundarias

---

### El Mapa Perdido del Tlamatini

**Estado:** Disponible
**Encargado por:** Itzcoatl (el propio Tlamatini del grupo)
**Objetivo:** Recuperar un mapa estelar robado del calmecac de Texcoco

**Descripción:**
Antes de unirse al grupo, Itzcoatl guardaba un mapa estelar único que
mostraba la posición de Venus durante los próximos 52 años. Fue robado
por un alumno expulsado que ahora trabaja para los sacerdotes disidentes.
Sin el mapa, Itzcoatl no puede completar su gran obra astronómica.

**Pista:** El ladrón se esconde en el barrio de los tintoreros en Tlatelolco.

**Tags:** secundaria, Texcoco, conocimiento, robo

---

### Las Plantas de Xochitl

**Estado:** Disponible
**Encargado por:** Xochitl (la Curandera del grupo)
**Objetivo:** Conseguir yoloxochitl fresco de las laderas del Popocatépetl

**Descripción:**
Xochitl necesita yoloxochitl fresco para preparar un antídoto contra
el veneno con el que hirieron a un niño en Tenochtitlan. Las flores solo
crecen en altitud y la temporada termina pronto. El camino pasa cerca
de territorios con presencia rebelde.

**Tags:** secundaria, curación, botánica, urgente

---

### La Deuda de Tlacaelel

**Estado:** Activa (puede complicar la misión principal)
**Encargado por:** El gremio Pochteca
**Objetivo:** Tlacaelel debe 50 granos de cacao al pochteca Mazatl

**Descripción:**
Tlacaelel (Coyote) contrajo una deuda de información con el mercader
Mazatl durante su última misión. Mazatl ahora exige pago o información
sobre la misión actual en Chalco. Si Tlacaelel no paga, Mazatl podría
vender la información del grupo a los rebeldes.

**Tags:** secundaria, deuda, Coyote, peligro_para_grupo

---

## Sistema de Progreso de Misiones

```json
{
  "mision_principal": {
    "fase": 1,
    "pistas_descubiertas": 0,
    "dias_restantes": 10,
    "sospechosos_identificados": []
  },
  "mision_mapa": {"completada": false, "pista_conocida": false},
  "mision_plantas": {"completada": false, "urgente": true},
  "deuda_coyote": {"resuelta": false, "dias_limite": 5}
}
```
