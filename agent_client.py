# =============================================================================
# CODEX ANÁHUAC — Cliente del Agente Tlacuilo
# Hackathon: Microsoft Agents League — Track: Reasoning Agents (Challenge B)
# =============================================================================

import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

project_endpoint = os.environ.get("PROJECT_ENDPOINT")
agent_name       = os.environ.get("AGENT_NAME", "Tlacuilo")

conversation_history = []

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║          C Ó D E X   A N Á H U A C  — Sistema Multi-Agente     ║
║          Maestro de Juego: TLACUILO (Foundry IQ enabled)        ║
╠══════════════════════════════════════════════════════════════════╣
║  Comandos especiales:                                            ║
║    COMENZAR        → Iniciar nueva partida                       ║
║    historial       → Ver conversación completa                   ║
║    lore <tema>     → Consultar directamente la base de lore      ║
║    salir           → Terminar sesión                             ║
╚══════════════════════════════════════════════════════════════════╝
"""

def display_history():
    """Muestra el historial completo de la conversación."""
    print("\n" + "="*60)
    print("📜 HISTORIAL DEL CÓDICE")
    print("="*60)
    if not conversation_history:
        print("  El códice está en blanco...")
    for i, msg in enumerate(conversation_history, 1):
        role_icon = "🧙 TLACUILO" if msg["role"] == "assistant" else "⚔️  TÚ"
        print(f"\n[{i}] {role_icon}:")
        print(f"  {msg['content'][:300]}{'...' if len(msg['content']) > 300 else ''}")
    print("="*60 + "\n")


def handle_mcp_approval(approval_request, openai_client, conversation, agent):
    """Maneja el flujo de aprobación MCP para acceso a Foundry IQ."""
    print(f"\n🔮 [El Tlacuilo consulta el conocimiento ancestral...]")
    print(f"   Servidor: {approval_request.server_label}")

    try:
        args = json.loads(approval_request.arguments)
        query = args.get("query", args.get("search_query", "conocimiento sagrado"))
        print(f"   Consultando: '{query}'")
    except Exception:
        print(f"   Argumentos: {approval_request.arguments}")

    # Auto-aprobamos consultas al knowledge base (es nuestro propio lore)
    print("   ✅ Acceso al códice ancestral concedido.\n")

    approval_response = {
        "type": "mcp_approval_response",
        "approval_request_id": approval_request.id,
        "approve": True
    }

    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[approval_response]
    )

    # Obtener respuesta tras aprobación
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        input=""
    )
    return response


def send_message(user_message, openai_client, conversation, agent):
    """Envía un mensaje al Tlacuilo y retorna su respuesta."""

    # Agregar al historial local
    conversation_history.append({"role": "user", "content": user_message})

    # Agregar mensaje a la conversación en Foundry
    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": user_message}],
    )

    # Obtener respuesta del agente
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        input=""
    )

    # Verificar si hay solicitud de aprobación MCP (acceso a Foundry IQ)
    if hasattr(response, "output") and response.output:
        for item in response.output:
            if hasattr(item, "type") and item.type == "mcp_approval_request":
                response = handle_mcp_approval(item, openai_client, conversation, agent)
                break

    # Extraer texto de la respuesta
    reply_text = ""
    if hasattr(response, "output") and response.output:
        for item in response.output:
            if hasattr(item, "type") and item.type == "message":
                if hasattr(item, "content") and item.content:
                    for content_block in item.content:
                        if hasattr(content_block, "text"):
                            reply_text += content_block.text
    elif hasattr(response, "output_text"):
        reply_text = response.output_text

    if not reply_text:
        reply_text = "(El códice no respondió — intenta de nuevo)"

    # Guardar en historial
    conversation_history.append({"role": "assistant", "content": reply_text})
    return reply_text


def main():
    print(BANNER)

    # ── Conectar al proyecto de Foundry ──────────────────────────────────────
    print("🔌 Conectando con el mundo del Quinto Sol...")
    try:
        credential = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        )
        project_client = AIProjectClient(
            credential=credential,
            endpoint=project_endpoint
        )
        openai_client = project_client.get_openai_client()
        agent = project_client.agents.get(agent_name=agent_name)
        print(f"✅ Tlacuilo invocado: {agent.name} (id: {agent.id})")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        print("   Verifica PROJECT_ENDPOINT en tu .env y que hayas hecho 'az login'")
        return

    # ── Crear nueva conversación ──────────────────────────────────────────────
    try:
        conversation = openai_client.conversations.create(items=[])
        print(f"📜 Nueva sesión del códice iniciada (id: {conversation.id[:8]}...)\n")
    except Exception as e:
        print(f"❌ Error al crear conversación: {e}")
        return

    print("Escribe 'COMENZAR' para iniciar tu aventura, o hazle una pregunta al Tlacuilo.")
    print("-" * 60)

    # ── Bucle principal ───────────────────────────────────────────────────────
    while True:
        try:
            user_input = input("\n⚔️  Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n🌅 El sol se oculta en el horizonte. Hasta la próxima sesión.")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ["salir", "quit", "exit", "q"]:
            print("\n🌅 Que Tonatiuh ilumine tu camino. ¡Hasta pronto, guerrero!")
            break

        elif cmd == "historial":
            display_history()
            continue

        elif cmd.startswith("lore "):
            # Consulta directa al lore sin narrativa
            tema = user_input[5:].strip()
            user_input = (
                f"Sin narrativa de RPG, dame información directa de la base de conocimiento "
                f"sobre: {tema}"
            )

        # Enviar al Tlacuilo
        print("\n🌄 El Tlacuilo medita...\n")
        try:
            respuesta = send_message(user_input, openai_client, conversation, agent)
            print(f"🧙 TLACUILO:\n{respuesta}")
        except Exception as e:
            print(f"❌ Error al comunicarse con el Tlacuilo: {e}")
            print("   Intenta de nuevo o escribe 'salir' para terminar.")


if __name__ == "__main__":
    main()
