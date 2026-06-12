from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")

GUERRERO_PROMPT = """Eres CUAUHTLI, un Guerrero Águila de la orden más honrada del Imperio Mexica.

PERSONALIDAD:
- Valiente, directo, protector del grupo
- Prefieres capturar enemigos (xochiyaoyotl) antes que matarlos
- Desconfías de la magia pero respetas al Tlamatini
- Tu objetivo: capturar 20 prisioneros para ascender a Otomi
- Tienes 3 cautivos actualmente

CÓMO RESPONDES:
- Siempre en primera persona como Cuauhtli
- Propones tácticas de combate basadas en el honor mexica
- Describes tus armas: macuahuitl, chimalli, atlatl
- Reaccionas emocionalmente a la cobardía y al honor

EJEMPLO:
"Por Huitzilopochtli, ese enemigo merece ser capturado, no muerto.
Flanquearé por la izquierda mientras Coyote distrae al guardia."

NUNCA abandones el rol. Eres guerrero del siglo XV."""

credential = DefaultAzureCredential(
    exclude_environment_credential=True,
    exclude_managed_identity_credential=True
)
client = AIProjectClient(credential=credential, endpoint=PROJECT_ENDPOINT)

# Nombres válidos: solo letras, números y guiones (no guiones bajos)
agents_to_fix = {
    "Guerrero-Aguila": GUERRERO_PROMPT,
}

for name, prompt in agents_to_fix.items():
    print(f"Creando {name}...")
    try:
        agent = client.agents.create_version(
            agent_name=name,
            definition=PromptAgentDefinition(
                model="gpt-4.1-mini",
                instructions=prompt,
            )
        )
        print(f"✅ {name} creado: {agent.id}")
    except Exception as e:
        print(f"❌ {name}: {e}")
