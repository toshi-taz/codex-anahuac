# 🏺 Codex Anáhuac — Multi-Agent RPG System
![Codex Anáhuac Banner](banner.jpg)

> **Microsoft Agents League Hackathon 2026**  
> Track: 🧠 Reasoning Agents | Challenge B: Role Play Game System  
> Built with: Microsoft Foundry · Foundry IQ · MCP · Azure AI Search  

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Azure AI Foundry](https://img.shields.io/badge/Azure-AI%20Foundry-0078d4)](https://ai.azure.com)
[![Foundry IQ](https://img.shields.io/badge/Foundry-IQ-purple)](https://aka.ms/iq-series)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-green)](https://gofastmcp.com)
[![Security](https://img.shields.io/badge/Security-OWASP%20LLM-red)](https://owasp.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 Qué es Codex Anáhuac

**Codex Anáhuac** es un sistema de RPG multi-agente ambientado en el México prehispánico del Quinto Sol (siglo XV). Cinco agentes de inteligencia artificial encarnan a personajes históricos que colaboran para guiar al jugador a través de aventuras en el Imperio Mexica.

El sistema demuestra **razonamiento multi-paso real**: el agente orquestador (Tlacuilo) analiza cada input del jugador, decide qué agentes deben responder, los invoca en paralelo, y sintetiza una narrativa coherente grounded en una base de conocimiento histórico.

> 🎬 **Demo Video:** [Ver en YouTube](https://youtube.com/TU_VIDEO_AQUI)  
> 📦 **Repositorio:** [github.com/toshi-taz/codex-anahuac](https://github.com/toshi-taz/codex-anahuac)

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        JUGADOR (Human)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ input validado
                    ┌──────▼──────┐
                    │  GUARDRAILS │ OWASP LLM01/02/04/06/08
                    │  (guardrails.py)                    │
                    └──────┬──────┘
                           │ input seguro
          ┌────────────────▼────────────────────────┐
          │         TLACUILO  🧙                     │
          │    Game Master Agent (Orquestador)       │
          │    Microsoft Foundry + Foundry IQ        │
          │                                          │
          │  1. Analiza input del jugador             │
          │  2. Decide qué agentes invocar            │
          │  3. Sintetiza narrativa final             │
          └──┬─────────┬──────────┬──────────┬───────┘
             │         │          │          │
     ┌───────▼──┐ ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
     │GUERRERO  │ │TLAMATI │ │CURAND. │ │ COYOTE │
     │ÁGUILA 🦅 │ │NI  📚  │ │🌿      │ │🦊      │
     │Cuauhtli  │ │Itzcoatl│ │Xochitl │ │Tlacaelel│
     │combate   │ │sabiduría│ │curación│ │mercados│
     └──────────┘ └────────┘ └────────┘ └────────┘
             │         │          │          │
             └─────────┴──────────┴──────────┘
                              │
              ┌───────────────▼────────────────┐
              │      MCP SERVER  🐍             │
              │   MecanicasAnahuac (FastMCP)    │
              │                                 │
              │  • tirar_dados_combate()        │
              │  • consultar_tonalpohualli()    │
              │  • estado_personaje()           │
              │  • aplicar_curacion()           │
              │  • consultar_mercado()          │
              └───────────────┬────────────────┘
                              │
              ┌───────────────▼────────────────┐
              │      FOUNDRY IQ  🔮             │
              │   Knowledge Base (8 docs)       │
              │                                 │
              │  PDFs: cosmología, guerreros,   │
              │        botánica ritual          │
              │  MDs:  world_overview, factions,│
              │        quests, characters,      │
              │        homebrew_rules           │
              └────────────────────────────────┘
```

### Flujo de Razonamiento Multi-paso

```
Input jugador → [Guardrails] → Tlacuilo analiza
    → JSON: {agentes_necesarios, tipo_escena, contexto}
    → Agentes responden en carácter (paralelo)
    → Tlacuilo consulta Foundry IQ para lore
    → Tlacuilo sintetiza narrativa final
    → [Sanitización output] → Respuesta al jugador
```

---

## 🤖 Los 5 Agentes

| Agente | Rol | Especialidad | Foundry IQ |
|--------|-----|--------------|------------|
| 🧙 **Tlacuilo** | Game Master / Orquestador | Narración, coordinación | ✅ Grounding en lore histórico |
| 🦅 **Guerrero Águila** | Combate | Tácticas, xochiyaoyotl | ✅ Órdenes guerreras |
| 📚 **Tlamatini** | Sabiduría | Tonalpohualli, astronomía | ✅ Cosmología mexica |
| 🌿 **Curandera** | Medicina | Plantas, temazcal | ✅ Botánica ritual |
| 🦊 **Coyote** | Información | Mercados, espionaje | ✅ Rutas y facciones |

---

## 🔮 Integración Foundry IQ

La base de conocimiento contiene **8 documentos** indexados en Azure AI Search:

| Documento | Contenido | Tipo |
|-----------|-----------|------|
| `anahuac-cosmologia.pdf` | Dioses, calendario, inframundo | PDF |
| `anahuac-guerreros.pdf` | Órdenes guerreras, armas, combate | PDF |
| `anahuac-botanica.pdf` | Plantas medicinales, venenos, curanderismo | PDF |
| `world_overview.md` | Geografía, leyes del mundo, año del juego | Markdown |
| `factions.md` | Triple Alianza, Rebeldes Chalco, Pochteca | Markdown |
| `quests.md` | Misiones activas y secundarias | Markdown |
| `characters.md` | Perfiles de los 5 agentes y NPCs | Markdown |
| `homebrew_rules.md` | Reglas RPG, dados, estadísticas | Markdown |

El Tlacuilo **siempre consulta Foundry IQ** antes de narrar escenas históricas, asegurando respuestas grounded con citas precisas.

---

## 🛡️ Seguridad — OWASP LLM Top 10

El sistema implementa guardrails basados en el estándar OWASP para Agentes LLM:

| OWASP | Vulnerabilidad | Implementación |
|-------|----------------|----------------|
| **LLM01** | Prompt Injection directa | Regex patterns + ban temporal tras 3 intentos |
| **LLM02** | Jailbreak / salida de personaje | Sanitización de outputs + detección de señales |
| **LLM04** | Denial of Wallet | Rate limit: 15 req/min, 100 req/hora |
| **LLM06** | Tool Abuse (MCP) | Allowlist de 5 herramientas permitidas |
| **LLM08** | Memory/Context Poisoning | Sanitización de lore antes de pasarlo a agentes |
| **SEC01** | Credential leak | Redacción automática de credenciales en outputs |

```python
# Ejemplo de guardrail en acción
is_valid, rejection_msg, reason = validate_input(user_input, SESSION_ID)
if not is_valid:
    print(rejection_msg)  # Respuesta en personaje
    # Log: 🛡️ BLOCKED [PROMPT_INJECTION]
```

---

## ⚙️ MCP Server — MecanicasAnahuac

Servidor MCP personalizado con 5 herramientas de mecánicas RPG:

```python
@mcp.tool()
def tirar_dados_combate(atacante: str, tipo_ataque: str) -> dict:
    """d20 + modificadores según reglas de la xochiyaoyotl"""

@mcp.tool()
def consultar_tonalpohualli() -> dict:
    """Retorna el signo del día y sus augurios para la partida"""

@mcp.tool()
def consultar_mercado(ciudad: str) -> dict:
    """Precios, objetos disponibles y rumores del tianguis"""

@mcp.tool()
def aplicar_curacion(paciente: str, planta: str) -> dict:
    """Medicina tradicional mexica con plantas reales"""

@mcp.tool()
def estado_personaje(personaje: str) -> dict:
    """Estado actual de vida, energía e inventario"""
```

---

## 🚀 Setup e Instalación

### Prerrequisitos
- Python 3.12+
- Azure for Students / Azure subscription
- Azure AI Foundry project
- Git

### 1. Clonar el repositorio
```bash
git clone https://github.com/toshi-taz/codex-anahuac.git
cd codex-anahuac
```

### 2. Entorno virtual
```bash
python -m venv labenv
source labenv/bin/activate  # Linux/Mac
# labenv\Scripts\activate   # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp env.template .env
# Edita .env con tu Project Endpoint de Azure AI Foundry
```

```env
PROJECT_ENDPOINT=https://TU-PROYECTO.services.ai.azure.com/api/projects/TU-ID
AGENT_NAME=Tlacuilo
```

### 5. Autenticarse con Azure
```bash
az login
az account set --subscription "Azure for Students"
```

### 6. Crear los 5 agentes en Foundry
```bash
python create_agents.py
```

### 7. Lanzar el sistema
```bash
python orchestrator.py
```

---

## 🎮 Uso

```
╔══════════════════════════════════════════════════════════════╗
║         C Ó D E X   A N Á H U A C  — Sistema Multi-Agente  ║
╠══════════════════════════════════════════════════════════════╣
║  COMENZAR          → Iniciar nueva partida                   ║
║  hablar <agente>   → Hablar con un personaje directamente    ║
║  estado            → Ver estado del grupo                    ║
║  dados             → Tirar dados de combate (MCP)           ║
║  calendario        → Consultar Tonalpohualli (MCP)          ║
║  mercado <ciudad>  → Consultar tianguis (MCP)               ║
║  lore <tema>       → Consultar Foundry IQ directamente      ║
║  seguridad         → Ver log de eventos de seguridad        ║
╚══════════════════════════════════════════════════════════════╝
```

### Ejemplo de sesión

```
⚔️  Tú: COMENZAR

⚙️  [Multi-agent reasoning — Turno 1]
   1️⃣  Tlacuilo analiza la situación...
   📋 Agentes: ['Guerrero_Aguila', 'Tlamatini'] | Escena: exploración
   2️⃣  🦅 Guerrero_Aguila responde...
   2️⃣  📚 Tlamatini responde...
   3️⃣  Tlacuilo narra la escena final...

🧙 TLACUILO:
🌄 Amanece en Tenochtitlan. El copal asciende desde el Templo Mayor...
📜 CUAUHTLI: "El Tlatoani nos espera. Hoy es 1 Coatl — día de cautela."
    ITZCOATL: "El calendario advierte traición. Procedamos con sabiduría."
⚔️  ¿Qué decides?
    1. Ir directamente al palacio del Tlatoani
    2. Consultar primero al mercader Mazatl en Tlatelolco
    3. Enviar al Coyote a espiar los movimientos en Chalco
```

---

## 📁 Estructura del Proyecto

```
codex-anahuac/
├── orchestrator.py          # Orquestador multi-agente principal
├── mcp_server.py            # Servidor MCP con mecánicas RPG
├── guardrails.py            # Seguridad OWASP LLM
├── create_agents.py         # Script para crear agentes en Foundry
├── agent_client.py          # Cliente legacy (v1)
├── tlacuilo_system_prompt.txt
├── requirements.txt
├── env.template
├── .gitignore               # .env excluido
└── lore_docs/               # Documentos para Foundry IQ
    ├── world_overview.md
    ├── factions.md
    ├── quests.md
    ├── characters.md
    └── homebrew_rules.md
```

---

## 🛠️ Stack Tecnológico

| Tecnología | Uso |
|-----------|-----|
| **Microsoft Azure AI Foundry** | Hosting y orquestación de los 5 agentes |
| **Foundry IQ** | Knowledge base con lore mesoamericano (8 docs) |
| **Azure AI Search** | Indexación y búsqueda semántica del lore |
| **Azure Blob Storage** | Almacenamiento de documentos del knowledge base |
| **FastMCP** | Servidor MCP con mecánicas RPG |
| **Azure Identity** | Autenticación con DefaultAzureCredential |
| **Python 3.12** | Lenguaje principal |

---

## 🔒 Seguridad y Datos Sintéticos

> ⚠️ **IMPORTANTE:** Este proyecto usa exclusivamente **datos sintéticos**.
> No contiene información confidencial, datos reales de personas,
> credenciales, ni información propietaria de ninguna organización.

- El lore mesoamericano está basado en fuentes históricas públicas
- Los personajes son ficticios aunque históricamente inspirados
- Las credenciales se gestionan via variables de entorno (`.env` en `.gitignore`)
- Los guardrails previenen la extracción de información del sistema

---

## 👤 Autor

**Abatazl** — Estudiante IPN, Ciudad de México  
Azure for Students · Microsoft AI Skills Fest 2026  

---

## 📄 Licencia

MIT License — ver [LICENSE](LICENSE)

---

*Ometeotl — Que los dioses del Quinto Sol guíen este proyecto* 🌄
