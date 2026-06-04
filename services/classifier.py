"""
Servicio de Clasificación con Microsoft Agent Framework (Semantic Kernel).

Utiliza un ChatCompletionAgent de Semantic Kernel para clasificar los mensajes del usuario.
El agente analiza el texto del usuario y retorna un diccionario estructurado con:
intent (intención), query (búsqueda), player (jugador) y reply_intro (introducción de respuesta).
"""

import json
import logging
import re

# Importamos los componentes de Semantic Kernel para crear el agente clasificador
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

# Cargar variables de configuración para inicializar el servicio de Azure OpenAI
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
)

# Creamos un logger para registrar eventos específicos de este módulo
logger = logging.getLogger(__name__)

# Prompt del sistema que define el rol del clasificador y las reglas de formato del JSON de salida
SYSTEM_PROMPT = """Eres un clasificador para un bot de Telegram sobre fútbol y mercado de fichajes.

Tu trabajo NO es responder al usuario con información final.
Tu trabajo es analizar el mensaje del usuario y devolver SOLO un JSON válido.

Debes devolver siempre estos campos:
- intent
- query
- player
- reply_intro

Valores permitidos para "intent":
- rumours
- scouting
- finance
- fallback

Reglas:
- rumours: si el usuario pide rumores, noticias, fichajes, mercado, oficiales, "here we go", últimas noticias.
- scouting: si el usuario pregunta por un jugador, su edad, posición, trayectoria, club actual o perfil.
- finance: si el usuario pregunta por precio, salario, sueldo, cláusula, valor o conversión de moneda.
- fallback: si no está claro lo que quiere.

Reglas extra:
- "query" debe ser un texto limpio para buscar.
- "player" debe contener el nombre del jugador si aparece, o vacío si no aparece.
- "reply_intro" debe ser una frase muy corta y amigable en español.
- No escribas explicaciones.
- No escribas Markdown.
- No escribas texto fuera del JSON.

Obviamente mensajes de saludo y despedida puedes responderlos con normalidad"""

# Expresión regular para buscar y extraer el bloque JSON del resultado del LLM
_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

# --- Inicialización del Kernel y el Agente Clasificador ---

# Crear el kernel de Semantic Kernel (núcleo central del framework)
_kernel = Kernel()

# Identificador único para el servicio de IA dentro del kernel
_SERVICE_ID = "classifier"

# Registrar el servicio de Azure OpenAI Chat Completion en el kernel
# Esto conecta Semantic Kernel con nuestro despliegue de Azure OpenAI
_kernel.add_service(
    AzureChatCompletion(
        service_id=_SERVICE_ID,
        deployment_name=AZURE_OPENAI_DEPLOYMENT,  # Nombre del modelo desplegado en Azure
        endpoint=AZURE_OPENAI_ENDPOINT,            # URL del endpoint de Azure
        api_key=AZURE_OPENAI_API_KEY,              # Clave de API de Azure
        api_version=AZURE_OPENAI_API_VERSION,      # Versión de la API
    )
)

# Crear el agente clasificador usando ChatCompletionAgent del Microsoft Agent Framework
# Este agente recibe un nombre descriptivo y las instrucciones del sistema (prompt)
_classifier_agent = ChatCompletionAgent(
    kernel=_kernel,
    service=_kernel.get_service(_SERVICE_ID),
    name="ClassifierAgent",
    instructions=SYSTEM_PROMPT,
)


async def classify_message(user_text: str) -> dict:
    """
    Clasifica el mensaje del usuario utilizando el agente ChatCompletionAgent de Semantic Kernel.
    Retorna un diccionario con las claves: intent, query, player, reply_intro.
    """
    # Creamos un historial de chat nuevo para cada clasificación
    chat_history = ChatHistory()

    # Añadimos el mensaje del usuario al historial
    chat_history.add_user_message(user_text)

    # Invocamos al agente clasificador y obtenemos su respuesta
    # El agente procesa el mensaje según las instrucciones del SYSTEM_PROMPT
    response = await _classifier_agent.get_response(messages=chat_history)

    # Extraemos el contenido textual de la respuesta del agente
    raw = str(response) if response else ""
    logger.debug("Respuesta sin procesar del clasificador: %s", raw)

    # Extraemos el bloque JSON utilizando la expresión regular definida
    match = _JSON_RE.search(raw)
    if match:
        try:
            # Parseamos el JSON extraído y lo retornamos como diccionario
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # En caso de fallo o respuesta no válida, retornamos un fallback seguro
    logger.warning("No se pudo parsear el JSON del clasificador; usando fallback. Raw: %s", raw)
    return {
        "intent": "fallback",
        "query": user_text,
        "player": "",
        "reply_intro": "",
    }
