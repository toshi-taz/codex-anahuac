#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          CODEX ANÁHUAC — Interfaz Gradio 6                  ║
║   Sistema RPG Multi-Agente · Microsoft Agents League 2026   ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import asyncio
import json
import re
import uuid
import base64
import gradio as gr
from dotenv import load_dotenv

# ─── Carga de variables de entorno ───────────────────────────────────────────
load_dotenv()
PROJECT_ENDPOINT = os.getenv(
    "PROJECT_ENDPOINT",
    "https://codex-anahuac-resource.services.ai.azure.com/api/projects/codex-anahuac",
)

# ─── Importaciones con fallback ───────────────────────────────────────────────
try:
    from guardrails import validate_input, sanitize_agent_response, get_security_summary
    GUARDRAILS_OK = True
except ImportError:
    GUARDRAILS_OK = False
    def validate_input(msg, sid):        return (True, "", "ok")
    def sanitize_agent_response(t, n):  return t
    def get_security_summary():          return "⚠️  guardrails.py no encontrado — modo demo"

try:
    from mcp_server import tirar_dados_combate, consultar_tonalpohualli, consultar_mercado
    MCP_OK = True
except ImportError:
    MCP_OK = False
    async def tirar_dados_combate(a, t):
        return {"dado": 12, "modificador": 3, "total": 15,
                "resultado": "éxito", "narrativa": "demo — mcp_server.py no encontrado"}
    async def consultar_tonalpohualli():
        return {"fecha": "1 Cipactli", "augurio": "favorable",
                "descripcion": "demo — mcp_server.py no encontrado", "recomendacion": "avanzar"}
    async def consultar_mercado(c):
        return {"ciudad": c, "rumor": "demo — mcp_server.py no encontrado",
                "objetos": [{"nombre": "Macuahuitl", "disponible": True}]}

try:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    AZURE_OK = True
except ImportError:
    AZURE_OK = False

# ─── Estado global ────────────────────────────────────────────────────────────
world_state: dict = {
    "turn":           0,
    "scene_type":     "inicio",
    "active_agents":  [],
    "security_events": 0,
    "session_id":     str(uuid.uuid4()),
}

conversations: dict = {}   # agent_name → conversation_id (openai_client)
openai_client       = None
azure_client        = None
init_done           = False

AGENTS = ["Tlacuilo", "Guerrero-Aguila", "Tlamatini", "Curandera", "Coyote"]

PARTY = [
    {"emoji": "🧙", "name": "Tlacuilo",   "role": "Game Master",     "hp": None, "max_hp": None},
    {"emoji": "🦅", "name": "Cuauhtli",   "role": "Guerrero-Águila", "hp": 20,   "max_hp": 20},
    {"emoji": "📚", "name": "Itzcoatl",   "role": "Tlamatini",       "hp": 15,   "max_hp": 15},
    {"emoji": "🌿", "name": "Xochitl",    "role": "Curandera",       "hp": 18,   "max_hp": 18},
    {"emoji": "🦊", "name": "Tlacaelel",  "role": "Coyote",          "hp": 16,   "max_hp": 16},
]

# ─── CSS Mesoamericano Oscuro ─────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap');

/* ── Reset global ── */
*, *::before, *::after { box-sizing: border-box; }

body,
.gradio-container,
.gradio-container * {
    background-color: #0f0700;
    color: #D4A017;
    font-family: 'Cinzel', Georgia, serif;
}

/* ── Contenedor principal ── */
.gradio-container { padding: 0 !important; max-width: 100% !important; }
.contain { max-width: 100% !important; padding: 0 0.5rem !important; }
footer   { display: none !important; }

/* ── Header ── */
#codex-header {
    background: linear-gradient(180deg, #1a0a00 0%, #0f0700 100%);
    border-bottom: 2px solid #8B4513;
    padding: 1rem 1.5rem 0.75rem;
    text-align: center;
}

#codex-title {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    color: #D4A017 !important;
    letter-spacing: 0.22em;
    text-shadow: 0 0 22px rgba(212,160,23,0.55), 0 2px 4px #000;
    margin: 0;
    line-height: 1.2;
}

#codex-subtitle {
    font-family: 'IM Fell English', serif;
    font-size: 0.78rem;
    color: #8B6914;
    letter-spacing: 0.18em;
    margin-top: 0.25rem;
}

/* ── Badges de tecnología ── */
.badge-row {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 0.65rem;
}

.badge {
    font-family: 'Cinzel', serif;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 0.2rem 0.65rem;
    border-radius: 3px;
    border: 1px solid;
    background: transparent;
}

.badge-foundry { background: #173404 !important; color: #97C459 !important; border-color: #97C459 !important; }
.badge-mcp     { background: #26215C !important; color: #AFA9EC !important; border-color: #AFA9EC !important; }
.badge-owasp   { background: #501313 !important; color: #F09595 !important; border-color: #F09595 !important; }
.badge-azure   { background: #042C53 !important; color: #85B7EB !important; border-color: #85B7EB !important; }

/* ── Banner ── */
#banner-wrap { padding: 0 0.5rem; }
#banner-wrap img {
    border: 2px solid #8B4513;
    border-radius: 4px;
    width: 100%;
    max-height: 200px;
    object-fit: cover;
    display: block;
}

/* ── Sidebar ── */
#sidebar-col {
    background: #1a0a00 !important;
    border: 1px solid #3d1f00 !important;
    border-radius: 6px !important;
    padding: 0.75rem !important;
    min-height: 560px;
}

#sidebar-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.72rem;
    color: #D4A017;
    letter-spacing: 0.18em;
    text-align: center;
    border-bottom: 1px solid #3d1f00;
    padding-bottom: 0.5rem;
    margin-bottom: 0.75rem;
}

/* ── Party cards ── */
.party-card {
    background: #0f0700 !important;
    border: 1px solid #3d1f00 !important;
    border-radius: 4px;
    padding: 0.5rem 0.6rem;
    margin-bottom: 0.45rem;
    transition: border-color 0.2s;
}
.party-card:hover { border-color: #8B4513 !important; }

.party-name {
    font-size: 0.75rem;
    font-weight: 600;
    color: #D4A017;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.party-role  { font-size: 0.6rem; color: #8B6914; margin-top: 0.1rem; font-family: 'IM Fell English', serif; }
.hp-bar-bg   { background: #2a1000; border-radius: 2px; height: 6px; margin-top: 0.4rem; overflow: hidden; }
.hp-bar-fill { height: 100%; border-radius: 2px; transition: width 0.4s, background-color 0.4s; }
.hp-text     { font-size: 0.6rem; color: #8B6914; text-align: right; margin-top: 0.15rem; }

/* ── Separador ornamental ── */
.divider { border: none; border-top: 1px solid #3d1f00; margin: 0.6rem 0; }

/* ── Botones de acción rápida ── */
.action-btn {
    width: 100% !important;
    background: #1a0a00 !important;
    border: 1px solid #3d1f00 !important;
    color: #D4A017 !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    padding: 0.42rem 0.5rem !important;
    border-radius: 3px !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
    text-align: left !important;
    margin-bottom: 0.32rem !important;
    min-height: auto !important;
}
.action-btn:hover {
    background: #2a1200 !important;
    border-color: #8B4513 !important;
    color: #f0c040 !important;
    box-shadow: 0 0 8px rgba(212,160,23,0.18) !important;
}

/* ── Botón conectar ── */
.init-btn {
    width: 100% !important;
    background: linear-gradient(135deg, #042C53, #073a6e) !important;
    border: 1px solid #85B7EB !important;
    color: #85B7EB !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    padding: 0.38rem 0.5rem !important;
    border-radius: 3px !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
    min-height: auto !important;
}
.init-btn:hover {
    background: linear-gradient(135deg, #073a6e, #0a4a8c) !important;
    box-shadow: 0 0 8px rgba(133,183,235,0.25) !important;
}

/* ── Chat panel ── */
#chat-col {
    background: #1a0a00 !important;
    border: 1px solid #3d1f00 !important;
    border-radius: 6px !important;
    padding: 0.75rem !important;
    min-height: 560px;
    display: flex;
    flex-direction: column;
}

/* ── Chatbot ── */
#chatbot {
    background: #0f0700 !important;
    border: 1px solid #3d1f00 !important;
    border-radius: 4px !important;
}
#chatbot .message-wrap { padding: 0.5rem !important; }

/* Burbujas usuario */
#chatbot .user .message,
#chatbot [data-testid="user"] .message {
    background: #1a0a00 !important;
    border: 1px solid #8B4513 !important;
    color: #D4A017 !important;
    font-family: 'IM Fell English', serif !important;
    font-size: 0.88rem !important;
    border-radius: 4px !important;
}

/* Burbujas asistente */
#chatbot .bot .message,
#chatbot [data-testid="bot"] .message {
    background: #120800 !important;
    border: 1px solid #3d1f00 !important;
    color: #c8921a !important;
    font-family: 'IM Fell English', serif !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    border-radius: 4px !important;
}

/* ── Input de texto ── */
#msg-input textarea {
    background: #0f0700 !important;
    border: 1px solid #3d1f00 !important;
    color: #D4A017 !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.83rem !important;
    border-radius: 4px !important;
    padding: 0.5rem 0.75rem !important;
    resize: none !important;
}
#msg-input textarea::placeholder { color: #5a3a00 !important; }
#msg-input textarea:focus {
    border-color: #8B4513 !important;
    box-shadow: 0 0 8px rgba(139,69,19,0.3) !important;
    outline: none !important;
}

/* ── Botón enviar ── */
#send-btn {
    background: linear-gradient(135deg, #4a2000, #8B4513) !important;
    border: 1px solid #8B4513 !important;
    color: #D4A017 !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    border-radius: 3px !important;
    transition: all 0.18s !important;
    min-height: auto !important;
}
#send-btn:hover {
    background: linear-gradient(135deg, #8B4513, #c08000) !important;
    color: #0f0700 !important;
    box-shadow: 0 0 12px rgba(212,160,23,0.3) !important;
}

/* ── Status bar ── */
.status-bar {
    background: #0f0700 !important;
    border: 1px solid #3d1f00 !important;
    border-radius: 3px;
    padding: 0.4rem 0.75rem;
    margin-top: 0.5rem;
    font-size: 0.68rem;
    color: #8B6914;
    font-family: 'Cinzel', serif;
    letter-spacing: 0.06em;
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
}
.status-label { color: #5a3a00; }
.status-val   { color: #D4A017; font-weight: 600; }

/* ── Scrollbar temática ── */
::-webkit-scrollbar        { width: 6px; }
::-webkit-scrollbar-track  { background: #0f0700; }
::-webkit-scrollbar-thumb  { background: #3d1f00; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #8B4513; }

/* ── Ocultar botones nativos de Gradio sobre imagen ── */
#banner-wrap .icon-buttons,
#banner-wrap button,
#banner-wrap .download-link,
#banner-wrap [data-testid="block-label"],
.svelte-1occ011,
.image-button-row { display: none !important; }

/* ── Banner full-width sin espacios ── */
#banner-wrap { padding: 0 !important; margin: 0 !important; }
#banner-wrap > div { border-radius: 0 !important; }
#banner-wrap img {
    border-left: none !important;
    border-right: none !important;
    border-radius: 0 !important;
    max-height: 180px !important;
}

/* ── Chat: altura adaptativa, sin espacio muerto ── */
#chatbot { min-height: 200px !important; }
#chatbot > div { min-height: 200px !important; }

/* ── Mensaje de bienvenida más compacto visualmente ── */
#chatbot .message-wrap { gap: 0.4rem !important; }

/* ── Status bar más visible para los jueces ── */
.status-bar {
    border-color: #8B4513 !important;
    background: linear-gradient(90deg, #120800, #0f0700) !important;
    font-size: 0.72rem !important;
}
.status-val { font-size: 0.78rem !important; }

/* ── Sidebar: hacer partido más prominente ── */
.party-card { margin-bottom: 0.35rem !important; }
"""

# ─── Helpers HTML ─────────────────────────────────────────────────────────────

def _hp_color(hp: int, max_hp: int) -> str:
    pct = (hp / max_hp) if max_hp else 1.0
    if pct > 0.60: return "#4ade80"
    if pct > 0.30: return "#facc15"
    return "#f87171"


def build_party_html() -> str:
    """Genera el HTML del panel del grupo con barras de vida."""
    html = "<div id='sidebar-title'>⚔ GRUPO DE AVENTUREROS ⚔</div>"
    for p in PARTY:
        if p["hp"] is None:
            html += f"""
<div class='party-card'>
  <div class='party-name'>{p['emoji']} {p['name']}</div>
  <div class='party-role'>{p['role']}</div>
  <div class='party-role' style='color:#D4A017;margin-top:3px;font-size:0.62rem;'>
    ✦ Director de la narrativa ✦
  </div>
</div>"""
        else:
            pct   = p["hp"] / p["max_hp"] * 100
            color = _hp_color(p["hp"], p["max_hp"])
            html += f"""
<div class='party-card'>
  <div class='party-name'>{p['emoji']} {p['name']}</div>
  <div class='party-role'>{p['role']}</div>
  <div class='hp-bar-bg'>
    <div class='hp-bar-fill' style='width:{pct:.0f}%;background:{color};'></div>
  </div>
  <div class='hp-text'>{p['hp']}/{p['max_hp']} PV</div>
</div>"""
    return html


def build_status_html(turn: int, scene: str, agents: list, sec_events: int) -> str:
    """Genera la barra de estado inferior del chat."""
    agents_str   = ", ".join(agents) if agents else "—"
    alert_color  = "#f87171" if sec_events > 0 else "#4ade80"
    return f"""
<div class='status-bar'>
  <span><span class='status-label'>TURNO </span><span class='status-val'>{turn}</span></span>
  <span><span class='status-label'>ESCENA </span><span class='status-val'>{scene.upper()}</span></span>
  <span><span class='status-label'>AGENTES </span><span class='status-val'>{agents_str}</span></span>
  <span><span class='status-label'>ALERTAS OWASP </span>
        <span class='status-val' style='color:{alert_color};'>{sec_events}</span></span>
</div>"""


# ─── Inicialización de agentes Azure Foundry ──────────────────────────────────

def init_agents() -> tuple[bool, str]:
    """Patrón exacto de orchestrator.py del repo."""
    global openai_client, azure_client, init_done, conversations
    if init_done:
        return True, "Foundry ya conectado"

    if not AZURE_OK:
        return False, (
            "azure-ai-projects no instalado.\n"
            "Ejecuta: pip install azure-ai-projects azure-identity"
        )

    try:
        credential = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True,
        )
        azure_client  = AIProjectClient(credential=credential, endpoint=PROJECT_ENDPOINT)
        openai_client = azure_client.get_openai_client()

        found: list[str] = []
        for name in AGENTS:
            try:
                conv = openai_client.conversations.create(items=[])
                conversations[name] = conv.id
                found.append(name)
            except Exception:
                pass

        if not found:
            return False, "⚠️ No se pudieron crear conversaciones — revisa el endpoint"

        init_done = True
        return True, f"✅ Foundry conectado · {len(found)} agentes listos"
    except Exception as exc:
        return False, f"Error: {exc}"


# ─── call_agent ───────────────────────────────────────────────────────────────

_DEMOS = {
    "Tlacuilo":        '{"agentes_necesarios":["Guerrero-Aguila"],"tipo_escena":"exploracion","contexto":"El jugador inicia su aventura en Tenochtitlan."}',
    "Guerrero-Aguila": "⚔️ Cuauhtli desenvaina su macuahuitl — listo para el combate.",
    "Tlamatini":       "📚 Los glifos revelan sabiduría ancestral de los tlacuilos.",
    "Curandera":       "🌿 Xochitl prepara sus hierbas medicinales con destreza.",
    "Coyote":          "🦊 Tlacaelel observa desde las sombras, astuto y silencioso.",
}


def call_agent(agent_name: str, message: str) -> str:
    """
    Patrón exacto de orchestrator.py:
      1. conversations.items.create  → añade mensaje al hilo
      2. responses.create(conversation=, extra_body={agent_reference}, input="")
      3. Manejo automático de mcp_approval_request
      4. Extracción de texto de output[type==message].content[].text
    """
    # ── Modo demo si Foundry no está conectado ──
    if openai_client is None or agent_name not in conversations:
        raw = _DEMOS.get(agent_name, f"[{agent_name}: demo — Foundry no conectado]")
        return sanitize_agent_response(raw, agent_name)

    conv_id = conversations[agent_name]

    try:
        # 1. Agregar mensaje del usuario al hilo de conversación
        openai_client.conversations.items.create(
            conversation_id=conv_id,
            items=[{"type": "message", "role": "user", "content": message}],
        )

        # 2. Invocar al agente por nombre vía extra_body (agent_reference)
        response = openai_client.responses.create(
            conversation=conv_id,
            extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
            input="",
        )

        # 3. Aprobación automática de MCP tool calls (Foundry IQ)
        if hasattr(response, "output") and response.output:
            for item in response.output:
                if getattr(item, "type", "") == "mcp_approval_request":
                    openai_client.conversations.items.create(
                        conversation_id=conv_id,
                        items=[{
                            "type": "mcp_approval_response",
                            "approval_request_id": item.id,
                            "approve": True,
                        }],
                    )
                    response = openai_client.responses.create(
                        conversation=conv_id,
                        extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
                        input="",
                    )
                    break

        # 4. Extraer texto de la respuesta
        text = ""
        if hasattr(response, "output") and response.output:
            for item in response.output:
                if getattr(item, "type", "") == "message":
                    for cb in getattr(item, "content", []):
                        if hasattr(cb, "text"):
                            text += cb.text
        if not text:
            text = getattr(response, "output_text", "") or ""

        return sanitize_agent_response(
            text or f"[{agent_name}: sin respuesta]",
            agent_name,
        )

    except Exception as exc:
        return f"[{agent_name} — Error: {exc}]"


# ─── orchestrate ──────────────────────────────────────────────────────────────

def orchestrate(player_input: str) -> tuple[str, list, str]:
    """
    Orquesta los 5 agentes:
    1. Tlacuilo analiza → JSON con agentes_necesarios, tipo_escena, contexto
    2. Agentes seleccionados responden al contexto
    3. Tlacuilo sintetiza la narrativa final
    """
    world_state["turn"] += 1
    turn = world_state["turn"]

    # ── Paso 1: Análisis de Tlacuilo ──
    analysis_prompt = f"""Turno {turn}. El jugador dice: "{player_input}"
Responde ÚNICAMENTE con JSON válido, sin texto adicional:
{{
  "agentes_necesarios": ["lista de: Guerrero-Aguila, Tlamatini, Curandera, Coyote"],
  "tipo_escena": "combate|exploracion|dialogo|magia|mercado|inicio",
  "contexto": "resumen breve del contexto para los agentes"
}}"""

    analysis_raw = call_agent("Tlacuilo", analysis_prompt)

    agentes_necesarios: list = []
    tipo_escena = "exploracion"
    contexto    = player_input

    try:
        json_match = re.search(r'\{.*?\}', analysis_raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            agentes_necesarios = data.get("agentes_necesarios", [])
            tipo_escena        = data.get("tipo_escena", "exploracion")
            contexto           = data.get("contexto", player_input)
    except (json.JSONDecodeError, AttributeError):
        agentes_necesarios = ["Guerrero-Aguila"]
        tipo_escena        = "exploracion"

    # ── Paso 2: Respuestas de agentes seleccionados ──
    agent_responses: dict = {}
    for agent in agentes_necesarios:
        if agent in AGENTS and agent != "Tlacuilo":
            resp = call_agent(
                agent,
                f"Contexto de escena: {contexto}\nAcción del jugador: {player_input}"
            )
            agent_responses[agent] = resp

    # ── Paso 3: Síntesis narrativa de Tlacuilo ──
    synthesis_prompt = f"""Turno {turn} — Escena: {tipo_escena}
Acción del jugador: "{player_input}"
Perspectivas de los agentes: {json.dumps(agent_responses, ensure_ascii=False)}

Escribe la narrativa final en español con este formato exacto:
🌄 [Apertura — descripción evocadora del entorno mesoamericano]
📜 [Desarrollo — lo que ocurre con el grupo y sus personajes]
⚔️ [Consecuencias y opciones disponibles para el jugador]

Usa lenguaje épico y poético del México prehispánico. Máximo 250 palabras."""

    narrative = call_agent("Tlacuilo", synthesis_prompt)

    # Guardia: si Tlacuilo devuelve JSON crudo en lugar de narrativa
    if narrative.strip()[:1] in ("{", "["):
        voces = [r for r in agent_responses.values() if r and not r.startswith("[")]
        sep = "\n\n"
        narrative = (
            "\U0001f304 *Las estrellas sobre Tenochtitlan se alinean...*"
            + sep + "\U0001f4dc " + " \u00b7 ".join(voces) if voces else
            "\U0001f304 *El Templo Mayor vibra.*" + sep +
            "\u2694\ufe0f *Conecta Azure Foundry para la narrativa completa.*"
        )

    world_state["scene_type"]    = tipo_escena
    world_state["active_agents"] = agentes_necesarios

    return narrative, agentes_necesarios, tipo_escena


# ─── Handlers MCP ────────────────────────────────────────────────────────────

def handle_dados() -> str:
    if not MCP_OK:
        return "⚠️ `mcp_server.py` no encontrado — instalación requerida."
    try:
        result = asyncio.run(tirar_dados_combate("Cuauhtli", "ataque_normal"))
        return (
            f"🎲 **DADOS DE COMBATE**\n\n"
            f"Dado: `{result.get('dado', '?')}` + "
            f"Modificador: `{result.get('modificador', '?')}` = "
            f"**Total: {result.get('total', '?')}**\n\n"
            f"Resultado: *{result.get('resultado', '?')}*\n\n"
            f"_{result.get('narrativa', '')}_"
        )
    except Exception as exc:
        return f"❌ Error MCP dados: `{exc}`"


def handle_tonalpohualli() -> str:
    if not MCP_OK:
        return "⚠️ `mcp_server.py` no encontrado — instalación requerida."
    try:
        result = asyncio.run(consultar_tonalpohualli())
        return (
            f"🌙 **TONALPOHUALLI — CALENDARIO SAGRADO**\n\n"
            f"📅 Fecha: **{result.get('fecha', '?')}**\n"
            f"☀️ Augurio: *{result.get('augurio', '?')}*\n\n"
            f"{result.get('descripcion', '')}\n\n"
            f"💫 Recomendación: _{result.get('recomendacion', '')}_"
        )
    except Exception as exc:
        return f"❌ Error MCP calendario: `{exc}`"


def handle_mercado(ciudad: str = "Tenochtitlan") -> str:
    if not MCP_OK:
        return "⚠️ `mcp_server.py` no encontrado — instalación requerida."
    try:
        result  = asyncio.run(consultar_mercado(ciudad))
        objetos = result.get("objetos", [])
        obj_lines = "\n".join(
            f"{'✅' if o.get('disponible') else '❌'} {o.get('nombre', '?')}"
            for o in objetos
        ) if objetos else "_Sin artículos en este mercado._"
        return (
            f"🏪 **MERCADO DE {result.get('ciudad', ciudad).upper()}**\n\n"
            f"📣 Rumor del tianguis: _{result.get('rumor', '')}_\n\n"
            f"**Objetos disponibles:**\n{obj_lines}"
        )
    except Exception as exc:
        return f"❌ Error MCP mercado: `{exc}`"


def handle_seguridad() -> str:
    summary = get_security_summary()
    return f"🛡️ **LOG DE SEGURIDAD OWASP LLM**\n\n```\n{summary}\n```"


# ─── Handler principal del chat ───────────────────────────────────────────────

def chat_handler(message: str, history: list):
    """
    Procesa el mensaje del jugador:
    - Detecta comandos especiales (dados, calendario, mercado, seguridad)
    - Valida con guardrails OWASP
    - Orquesta agentes si pasa validación
    Retorna: (history, status_html, msg_clear)
    """
    history = list(history) if history else []

    if not message or not message.strip():
        return (
            history,
            build_status_html(
                world_state["turn"], world_state["scene_type"],
                world_state["active_agents"], world_state["security_events"]
            ),
            "",
        )

    msg       = message.strip()
    msg_lower = msg.lower()
    session_id = world_state["session_id"]

    # ── Comandos especiales ──────────────────────────────────────────────────
    if msg_lower in ("comenzar", "⚔️ comenzar partida", "comenzar partida"):
        response_text, agents, scene = orchestrate("COMENZAR")

    elif any(k in msg_lower for k in ("dados", "tirar dados", "🎲")):
        response_text = handle_dados()
        world_state["turn"] += 1
        world_state["scene_type"]    = "combate"
        world_state["active_agents"] = ["MCP:dados"]

    elif any(k in msg_lower for k in ("calendario", "tonalpohualli", "🌙")):
        response_text = handle_tonalpohualli()
        world_state["turn"] += 1
        world_state["scene_type"]    = "magia"
        world_state["active_agents"] = ["MCP:tonalpohualli"]

    elif msg_lower.startswith("mercado") or "🏪" in msg:
        partes = msg.split(None, 1)
        ciudad = partes[1].strip() if len(partes) > 1 else "Tenochtitlan"
        response_text = handle_mercado(ciudad)
        world_state["turn"] += 1
        world_state["scene_type"]    = "mercado"
        world_state["active_agents"] = ["MCP:mercado"]

    elif any(k in msg_lower for k in ("seguridad", "owasp", "🛡")):
        response_text = handle_seguridad()
        world_state["active_agents"] = ["OWASP"]

    else:
        # ── Validación guardrails ──
        is_valid, rejection_msg, reason = validate_input(msg, session_id)
        if not is_valid:
            world_state["security_events"] += 1
            response_text = (
                f"🔴 **[Tlacuilo detiene la narración]**\n\n"
                f"_{rejection_msg}_\n\n"
                f"*Las sombras del Mictlán susurran: «{reason}»*"
            )
            world_state["active_agents"] = ["OWASP:blocked"]
        else:
            response_text, agents, scene = orchestrate(msg)

    # ── Actualizar historial (Gradio 6.18: dicts {role, content} por defecto) ──
    history.append({"role": "user",      "content": msg})
    history.append({"role": "assistant", "content": response_text})

    status_html = build_status_html(
        world_state["turn"],
        world_state["scene_type"],
        world_state["active_agents"],
        world_state["security_events"],
    )

    return history, status_html, ""   # "" limpia el input


# ─── Construcción de la interfaz Gradio ──────────────────────────────────────

BANNER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.jpg")

_WELCOME = (
    "🌄 *Los tambores del Templo Mayor resuenan en la oscuridad de la noche...*\n\n"
    "Bienvenido, aventurero, al **Codex Anáhuac** — donde los dioses del México "
    "antiguo tejen el destino de los mortales a través de cinco agentes sagrados:\n\n"
    "🧙 **Tlacuilo** · 🦅 **Guerrero-Águila** · 📚 **Tlamatini** · 🌿 **Curandera** · 🦊 **Coyote**\n\n"
    "---\n"
    "📜 Escribe **`COMENZAR`** para iniciar tu aventura.\n"
    "🎲 Usa **`dados`** · **`calendario`** · **`mercado <ciudad>`** · **`seguridad`**\n"
    "🔌 Conecta Azure Foundry con el botón lateral antes de jugar.\n\n"
    "_「 Tlacuilo aguarda tu decisión, los glifos danzan en las paredes del templo... 」_"
)

with gr.Blocks(
    title="Codex Anáhuac — RPG Multi-Agente",
) as demo:

    # ── Header ──────────────────────────────────────────────────────────────
    gr.HTML("""
<div id='codex-header'>
  <div id='codex-title'>⚔ CODEX ANÁHUAC ⚔</div>
  <div id='codex-subtitle'>SISTEMA RPG MULTI-AGENTE &nbsp;·&nbsp; MICROSOFT AGENTS LEAGUE HACKATHON 2026</div>
  <div class='badge-row'>
    <span class='badge badge-foundry'>🧠 FOUNDRY IQ</span>
    <span class='badge badge-mcp'>⚡ MCP SERVER</span>
    <span class='badge badge-owasp'>🛡 OWASP LLM</span>
    <span class='badge badge-azure'>☁ AZURE AI</span>
  </div>
</div>""")

    # ── Banner: renderizado como HTML para control total y sin botones Gradio ──
    _banner_html = ""
    if os.path.exists(BANNER_PATH):
        import base64
        with open(BANNER_PATH, "rb") as _bf:
            _b64 = base64.b64encode(_bf.read()).decode()
        _ext = BANNER_PATH.rsplit(".", 1)[-1].lower()
        _mime = "image/jpeg" if _ext in ("jpg", "jpeg") else f"image/{_ext}"
        _banner_html = f"""
<div style='width:100%;margin:0;padding:0;line-height:0;'>
  <img src='data:{_mime};base64,{_b64}'
       style='width:100%;max-height:185px;object-fit:cover;
              border-top:2px solid #8B4513;
              border-bottom:2px solid #8B4513;
              display:block;'
       alt='Codex Anáhuac Banner'>
</div>"""
    if _banner_html:
        gr.HTML(_banner_html)

    # ── Layout principal ─────────────────────────────────────────────────────
    with gr.Row(equal_height=True):

        # ── Sidebar izquierda ──────────────────────────────────────────────
        with gr.Column(scale=1, elem_id="sidebar-col"):

            party_display = gr.HTML(value=build_party_html())

            gr.HTML("""<hr class='divider'>
<div style='font-size:0.68rem;color:#5a3a00;text-align:center;
            letter-spacing:0.14em;margin-bottom:0.45rem;'>
  ACCIONES RÁPIDAS
</div>""")

            btn_comenzar   = gr.Button("⚔️  Comenzar partida",         elem_classes=["action-btn"])
            btn_dados      = gr.Button("🎲  Tirar dados  (MCP)",        elem_classes=["action-btn"])
            btn_calendario = gr.Button("🌙  Tonalpohualli  (MCP)",      elem_classes=["action-btn"])
            btn_mercado    = gr.Button("🏪  Mercado Tenochtitlan",       elem_classes=["action-btn"])
            btn_seguridad  = gr.Button("🛡️  Log seguridad OWASP",       elem_classes=["action-btn"])

            gr.HTML("<hr class='divider'>")

            init_status = gr.HTML(
                "<div style='font-size:0.64rem;color:#5a3a00;text-align:center;"
                "padding:0.25rem;'>Azure Foundry: desconectado</div>"
            )
            btn_init = gr.Button("🔌 Conectar Azure Foundry", elem_classes=["init-btn"])

        # ── Panel de chat ──────────────────────────────────────────────────
        with gr.Column(scale=2, elem_id="chat-col"):

            # Gradio 6.18: sin type="messages" — usa tuplas (user_msg, bot_msg)
            # None en pos. user = solo mensaje del bot (bienvenida)
            chatbot = gr.Chatbot(
                label="",
                elem_id="chatbot",
                value=[{"role": "assistant", "content": _WELCOME}],
                height=420,
                show_label=False,
            )

            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder=(
                        "Escribe tu acción... "
                        "( COMENZAR · dados · calendario · mercado <ciudad> · seguridad )"
                    ),
                    elem_id="msg-input",
                    show_label=False,
                    scale=5,
                    lines=1,
                    max_lines=3,
                )
                send_btn = gr.Button("⚔ ENVIAR", elem_id="send-btn", scale=1)

            status_bar = gr.HTML(
                value=build_status_html(0, "inicio", [], 0)
            )

    # ── Wiring de eventos ────────────────────────────────────────────────────

    def do_init():
        ok, msg_txt = init_agents()
        color  = "#4ade80" if ok else "#f87171"
        icon   = "✅" if ok else "⚠️"
        border = f"1px solid {color}44"
        return (
            f"<div style='font-size:0.63rem;color:{color};text-align:center;"
            f"padding:0.28rem;border:{border};border-radius:3px;"
            f"word-break:break-word;'>{icon} {msg_txt}</div>"
        )

    btn_init.click(fn=do_init, outputs=[init_status])

    # Envío: botón y Enter  → outputs siempre en el mismo orden
    _inputs  = [msg_input, chatbot]
    _outputs = [chatbot, status_bar, msg_input]

    send_btn.click(fn=chat_handler, inputs=_inputs, outputs=_outputs)
    msg_input.submit(fn=chat_handler, inputs=_inputs, outputs=_outputs)

    # Botones de acción rápida (pasan el historial actual del chatbot)
    btn_comenzar.click(
        fn=lambda h: chat_handler("COMENZAR", h),
        inputs=[chatbot], outputs=_outputs,
    )
    btn_dados.click(
        fn=lambda h: chat_handler("dados", h),
        inputs=[chatbot], outputs=_outputs,
    )
    btn_calendario.click(
        fn=lambda h: chat_handler("calendario", h),
        inputs=[chatbot], outputs=_outputs,
    )
    btn_mercado.click(
        fn=lambda h: chat_handler("mercado Tenochtitlan", h),
        inputs=[chatbot], outputs=_outputs,
    )
    btn_seguridad.click(
        fn=lambda h: chat_handler("seguridad", h),
        inputs=[chatbot], outputs=_outputs,
    )


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("╔═══════════════════════════════════════════════════════╗")
    print("║         CODEX ANÁHUAC — RPG Multi-Agente             ║")
    print("║    Microsoft Agents League Hackathon 2026             ║")
    print("╠═══════════════════════════════════════════════════════╣")
    print(f"║  Gradio    : {gr.__version__:<42}║")
    print(f"║  Guardrails: {'✅ OK' if GUARDRAILS_OK else '⚠️  mock':<42}║")
    print(f"║  MCP server: {'✅ OK' if MCP_OK else '⚠️  mock':<42}║")
    print(f"║  Azure SDK : {'✅ OK' if AZURE_OK else '❌ pip install azure-ai-projects':<42}║")
    print("╠═══════════════════════════════════════════════════════╣")
    print("║  → http://localhost:7860                              ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=CSS,
    )
