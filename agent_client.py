# =============================================================================
# CODEX ANÁHUAC — Cliente Multi-Agente con MCP + Foundry IQ
# Hackathon: Microsoft Agents League — Track: Reasoning Agents (Challenge B)
# Arquitectura: Tlacuilo (GM) + MCP Server (Mecánicas RPG) + Foundry IQ (Lore)
# =============================================================================

import os
import json
import asyncio
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition

load_dotenv()

project_endpoint = os.environ.get("PROJECT_ENDPOINT")
agent_name       = os.environ.get("AGENT_NAME", "Tlacuilo")

conversation_history = []

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║       C Ó D E X   A N Á H U A C  — Sistema Multi-Agente        ║
║   Tlacuilo (GM) + Foundry IQ (Lore) + MCP (Mecánicas RPG)       ║
╠══════════════════════════════════════════════════════════════════╣
║  Comandos:                                                       ║
║    COMENZAR        → Iniciar nueva partida                       ║
║    historial       → Ver conversación completa                   ║
║    lore <tema>     → Consultar base de lore directamente         ║
║    dados           → Tirar dados de combate                      ║
║    calendario      → Consultar el Tonalpohualli                  ║
║    mercado <ciudad>→ Consultar el tianguis                       ║
║    salir           → Terminar sesión                             ║
╚══════════════════════════════════════════════════════════════════╝
"""


def display_history():
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
    print(f"\n🔮 [El Tlacuilo consulta los registros ancestrales...]")
    try:
        args = json.loads(approval_request.arguments)
        query = args.get("query", args.get("search_query", "conocimiento sagrado"))
        print(f"   Consultando: '{query}'")
    except Exception:
        pass

    approval_response = {
        "type": "mcp_approval_response",
        "approval_request_id": approval_request.id,
        "approve": True
    }
    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[approval_response]
    )
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        input=""
    )
    return response


def send_message(user_message, openai_client, conversation, agent):
    """Envía un mensaje al Tlacuilo y retorna su respuesta."""
    conversation_history.append({"role": "user", "content": user_message})

    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": user_message}],
    )

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        input=""
    )

    # Verificar aprobación MCP (Foundry IQ)
    if hasattr(response, "output") and response.output:
        for item in response.output:
            if hasattr(item, "type") and item.type == "mcp_approval_request":
                response = handle_mcp_approval(item, openai_client, conversation, agent)
                break

    # Extraer texto
    reply_text = ""
    if hasattr(response, "output") and response.output:
        for item in response.output:
            if hasattr(item, "type") and item.type == "message":
                if hasattr(item, "content") and item.content:
                    for cb in item.content:
                        if hasattr(cb, "text"):
                            reply_text += cb.text
    elif hasattr(response, "output_text"):
        reply_text = response.output_text

    if not reply_text:
        reply_text = "(El códice no respondió — intenta de nuevo)"

    conversation_history.append({"role": "assistant", "content": reply_text})
    return reply_text


async def call_mcp_tool(tool_name: str, args: dict) -> str:
    """Llama directamente a una herramienta del servidor MCP."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )
    async with AsyncExitStack() as stack:
        transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = transport
        session = await stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()
        result = await session.call_tool(tool_name, args)
        return result.content[0].text if result.content else "{}"


def main():
    print(BANNER)

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

    try:
        conversation = openai_client.conversations.create(items=[])
        print(f"📜 Nueva sesión del códice iniciada (id: {conversation.id[:8]}...)\n")
    except Exception as e:
        print(f"❌ Error al crear conversación: {e}")
        return

    print("Escribe 'COMENZAR' para iniciar tu aventura.")
    print("-" * 60)

    while True:
        try:
            user_input = input("\n⚔️  Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n🌅 El sol se oculta. Hasta la próxima sesión.")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        # ── Comandos especiales de MCP ────────────────────────────────────
        if cmd in ["salir", "quit", "exit"]:
            print("\n🌅 ¡Hasta pronto, guerrero! Que Tonatiuh ilumine tu camino.")
            break

        elif cmd == "historial":
            display_history()
            continue

        elif cmd == "dados":
            print("\n🎲 Invocando los dados del destino...")
            try:
                resultado = asyncio.run(call_mcp_tool("tirar_dados_combate", {
                    "atacante": "Cuauhtli",
                    "tipo_ataque": "captura"
                }))
                datos = json.loads(resultado)
                print(f"   Dado: {datos['dado']} | Modificador: +{datos['modificador']} | Total: {datos['total']}")
                print(f"   Resultado: {datos['resultado'].upper()}")
                print(f"   {datos['narrativa']}")
                # Pasar resultado al Tlacuilo para que narre
                user_input = f"Los dados han hablado: {datos['narrativa']} (Resultado: {datos['resultado']}, total: {datos['total']}). Narra cómo afecta esto a la aventura."
            except Exception as e:
                print(f"   ⚠️ Error en dados: {e}")
                continue

        elif cmd == "calendario":
            print("\n🌙 Consultando el Tonalpohualli...")
            try:
                resultado = asyncio.run(call_mcp_tool("consultar_tonalpohualli", {}))
                datos = json.loads(resultado)
                print(f"   Fecha sagrada: {datos['fecha']}")
                print(f"   Augurio: {datos['augurio'].upper()} — {datos['descripcion']}")
                print(f"   Recomendación: {datos['recomendacion']}")
                user_input = f"El día sagrado es {datos['fecha']}. {datos['descripcion']} {datos['recomendacion']} Integra este augurio en la narrativa actual."
            except Exception as e:
                print(f"   ⚠️ Error en calendario: {e}")
                continue

        elif cmd.startswith("mercado "):
            ciudad = user_input[8:].strip()
            print(f"\n🏪 Consultando el tianguis de {ciudad}...")
            try:
                resultado = asyncio.run(call_mcp_tool("consultar_mercado", {"ciudad": ciudad}))
                datos = json.loads(resultado)
                if "error" in datos:
                    print(f"   ⚠️ {datos['error']}")
                    continue
                print(f"   Ciudad: {datos['ciudad']} — {datos['especialidad']}")
                print(f"   Rumor del mercado: {datos['rumor']}")
                objetos_disp = [o['nombre'] for o in datos['objetos'] if o['disponible']]
                print(f"   Disponible: {', '.join(objetos_disp)}")
                user_input = f"En el tianguis de {ciudad} se dice: '{datos['rumor']}'. Hay disponible: {', '.join(objetos_disp)}. Integra esto en la narrativa."
            except Exception as e:
                print(f"   ⚠️ Error en mercado: {e}")
                continue

        elif cmd.startswith("lore "):
            tema = user_input[5:].strip()
            user_input = (
                f"Sin narrativa de RPG, dame información directa de la base de conocimiento "
                f"sobre: {tema}"
            )

        # ── Enviar al Tlacuilo ────────────────────────────────────────────
        print("\n🌄 El Tlacuilo medita...\n")
        try:
            respuesta = send_message(user_input, openai_client, conversation, agent)
            print(f"🧙 TLACUILO:\n{respuesta}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
