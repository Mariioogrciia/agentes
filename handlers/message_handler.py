"""
Controlador Principal de Mensajes.

Orquesta todo el flujo (pipeline) de procesamiento de un mensaje de Telegram:
  Mensaje de Telegram → Clasificación de intención (con IA) → Enrutamiento al controlador específico → Respuesta al usuario
"""

# Importamos la librería de registro estándar
import logging

# Importamos los tipos y estructuras necesarias de la biblioteca python-telegram-bot
from telegram import Update
from telegram.ext import ContextTypes

# Importamos la función de clasificación que interactúa con Azure OpenAI
from services.classifier import classify_message

# Importamos todos los sub-manejadores específicos para cada intención de usuario
from handlers import rumours, scouting, finance, fallback

# Creamos un logger para registrar eventos específicos de este módulo
logger = logging.getLogger(__name__)

# Diccionario de enrutamiento que vincula la cadena de intención (intent) con la función 'handle' del módulo adecuado
INTENT_HANDLERS = {
    "rumours": rumours.handle,     # Si es 'rumours', se enruta al módulo de rumores de fichajes
    "scouting": scouting.handle,   # Si es 'scouting', se enruta al módulo de ficha técnica del jugador
    "finance": finance.handle,     # Si es 'finance', se enruta al módulo de finanzas de contratos
    "fallback": fallback.handle,   # Si es 'fallback' (desconocido), se va al módulo de ayuda genérico
}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Función controladora principal que procesa cada actualización (mensaje) de Telegram.
    Obtiene el texto del usuario, llama al clasificador y enruta a la función handler correspondiente.
    """
    # Extraemos el texto crudo del mensaje recibido
    user_text = update.message.text
    # Extraemos el identificador numérico único del chat de la conversación
    chat_id = update.message.chat_id

    # Registramos en el log la recepción del mensaje
    logger.info("Mensaje recibido de %s: %s", chat_id, user_text)

    # Paso 1 — Clasificación del mensaje para identificar intención, jugador, etc.
    try:
        # Hacemos llamada asíncrona al servicio de Azure OpenAI para analizar la intención del usuario
        classification = await classify_message(user_text)
    except Exception as exc:
        # En caso de excepción al conectar con Azure OpenAI o decodificar su respuesta
        logger.error("Fallo la clasificación: %s", exc)
        
        # Respondemos de forma controlada al usuario final indicándole que hay un problema temporal
        await update.message.reply_text(
            "⚠️ Hubo un error procesando tu mensaje. Inténtalo de nuevo."
        )
        return

    # Extraemos la clave 'intent' del diccionario devuelto por la IA (usando 'fallback' por defecto)
    intent = classification.get("intent", "fallback")
    
    # Registramos la intención detectada en consola
    logger.info("Intención detectada: %s | clasificación: %s", intent, classification)

    # Paso 2 — Enrutamiento al controlador de la intención clasificada
    # Si la clave no está en el diccionario INTENT_HANDLERS, se usa fallback.handle por defecto
    handler = INTENT_HANDLERS.get(intent, fallback.handle)
    
    # Ejecutamos asíncronamente el handler correspondiente pasándole el update, context y los datos estructurados
    await handler(update, context, classification)


