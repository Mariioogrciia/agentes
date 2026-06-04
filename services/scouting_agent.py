"""
Servicio del Agente de IA para Scouting con Microsoft Agent Framework (Semantic Kernel).

Utiliza un ChatCompletionAgent de Semantic Kernel con los plugins de Wikipedia y SerpAPI
registrados como herramientas. El agente puede invocar automáticamente estas herramientas
para recopilar datos y generar un perfil de exploración estructurado en formato JSON.
"""

import json
import logging
import re

# Importamos los componentes de Semantic Kernel para crear el agente de scouting
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory

# Importamos los plugins que el agente usará como herramientas
from services.serpapi import SerpAPIPlugin
from services.wikipedia import WikipediaPlugin

# Cargar variables de configuración para el servicio de Azure OpenAI
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
)

# Creamos un logger para registrar eventos específicos de este módulo
logger = logging.getLogger(__name__)

# Expresión regular para buscar y extraer el bloque JSON de la respuesta del modelo
_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

# Instrucciones del sistema para el agente de scouting
# Define el comportamiento, las reglas y el formato de salida esperado
SCOUTING_INSTRUCTIONS = """Eres un agente de scouting deportivo especializado en fútbol.

Tu trabajo es generar un perfil estructurado de un jugador de fútbol.

Tienes acceso a dos herramientas:
1. Wikipedia: para obtener información biográfica del jugador
2. Google Search (SerpAPI): para buscar datos de mercado, valor, equipo actual, etc.

Proceso:
1. Usa la herramienta de Wikipedia para buscar el resumen del jugador (usa guiones bajos en vez de espacios en el nombre)
2. Usa la herramienta de Google Search para buscar "{jugador} FootballTransfers market value age team nationality"
3. Con la información recopilada, genera un JSON con estas claves exactas:
   - player: nombre completo del jugador
   - team: equipo actual
   - age: edad
   - nationality: nacionalidad
   - market_value: valor de mercado estimado
   - profile: una frase corta en español describiendo al jugador

Reglas:
- Responde SOLO con JSON válido al final
- No añadas texto antes ni después del JSON
- Si un dato no aparece claramente, escribe "No encontrado"
- No inventes datos
- profile debe ser una frase corta en español"""

# --- Inicialización del Kernel, Plugins y Agente de Scouting ---

# Crear el kernel de Semantic Kernel (núcleo central del framework)
_kernel = Kernel()

# Identificador único para el servicio de IA dentro del kernel
_SERVICE_ID = "scouting"

# Registrar el servicio de Azure OpenAI Chat Completion en el kernel
_kernel.add_service(
    AzureChatCompletion(
        service_id=_SERVICE_ID,
        deployment_name=AZURE_OPENAI_DEPLOYMENT,  # Nombre del modelo desplegado en Azure
        endpoint=AZURE_OPENAI_ENDPOINT,            # URL del endpoint de Azure
        api_key=AZURE_OPENAI_API_KEY,              # Clave de API de Azure
        api_version=AZURE_OPENAI_API_VERSION,      # Versión de la API
    )
)

# Registrar los plugins en el kernel para que el agente pueda usarlos como herramientas
# Plugin de SerpAPI: permite al agente buscar en Google automáticamente
_kernel.add_plugin(SerpAPIPlugin(), plugin_name="serpapi")
# Plugin de Wikipedia: permite al agente consultar Wikipedia automáticamente
_kernel.add_plugin(WikipediaPlugin(), plugin_name="wikipedia")

# Obtener la configuración de ejecución del servicio para activar la invocación automática de funciones
_settings = _kernel.get_prompt_execution_settings_from_service_id(service_id=_SERVICE_ID)
# FunctionChoiceBehavior.Auto() permite al agente decidir cuándo llamar a las herramientas registradas
_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

# Crear el agente de scouting usando ChatCompletionAgent del Microsoft Agent Framework
_scouting_agent = ChatCompletionAgent(
    kernel=_kernel,
    service=_kernel.get_service(_SERVICE_ID),
    name="ScoutingAgent",
    instructions=SCOUTING_INSTRUCTIONS,
)


async def extract_scouting_profile(player: str) -> dict:
    """
    Genera y retorna un diccionario con el perfil de scouting del jugador.
    El agente utiliza automáticamente los plugins de Wikipedia y SerpAPI para recopilar datos.
    """
    # Creamos un historial de chat con la solicitud del usuario
    chat_history = ChatHistory()
    chat_history.add_user_message(f"Genera el perfil de scouting para el jugador: {player}")

    # Invocamos al agente de scouting, que automáticamente usará los plugins si lo necesita
    response = await _scouting_agent.get_response(messages=chat_history)

    # Extraemos el contenido textual de la respuesta del agente
    raw = str(response) if response else ""
    logger.debug("Respuesta sin procesar del agente de scouting: %s", raw)

    # Intento de extracción del JSON de la respuesta
    match = _JSON_RE.search(raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # En caso de error de parseo del JSON, retornamos valores por defecto seguros
    logger.warning("No se pudo parsear el JSON de scouting. Raw: %s", raw)
    return {
        "player": player,
        "team": "No encontrado",
        "age": "No encontrado",
        "nationality": "No encontrado",
        "market_value": "No encontrado",
        "profile": "No se pudo generar el perfil.",
    }
