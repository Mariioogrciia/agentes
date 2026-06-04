"""
Controlador de Rumores de Fichajes.

Busca noticias recientes de transferencias y mercado utilizando el plugin de SerpAPI
(ahora integrado en el Microsoft Agent Framework / Semantic Kernel) y responde con el resultado más relevante.
Es la contraparte de la rama de n8n: Switch(rumours) → Búsqueda de Google → Condicional (Si hay resultados) → Enviar mensaje.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

# Importamos el plugin de SerpAPI de Semantic Kernel para realizar la búsqueda en Google
from services.serpapi import SerpAPIPlugin

# Creamos un logger para registrar eventos específicos de este módulo
logger = logging.getLogger(__name__)

# Instanciamos el plugin de SerpAPI para usarlo directamente en este handler
_serp_plugin = SerpAPIPlugin()


async def handle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    classification: dict,
) -> None:
    """
    Procesa las consultas de rumores de fichajes. Usa el plugin SerpAPIPlugin del
    Microsoft Agent Framework para realizar la búsqueda y maqueta una respuesta con
    el título, resumen y enlace del resultado más destacado.
    """
    # Extraemos el jugador identificado (si existe) y la consulta de búsqueda sugerida
    player = classification.get("player", "")
    query_text = classification.get("query", player or "transfer news")
    # Frase introductoria opcional generada por el clasificador
    reply_intro = classification.get("reply_intro", "Voy a revisar lo más reciente.")

    # Si hay un jugador específico, estructuramos la consulta agregándole "transfer news" para afinar el resultado
    search_query = f"{query_text} transfer news" if player else query_text

    try:
        # Llamamos al método google_search del plugin SerpAPIPlugin de Semantic Kernel
        # El plugin retorna texto formateado con los resultados
        raw_results = await _serp_plugin.google_search(query=search_query)
    except Exception as exc:
        logger.error("Error en SerpAPI: %s", exc)
        raw_results = ""

    # Verificamos si la búsqueda obtuvo resultados útiles
    if raw_results and "No se encontraron" not in raw_results and "No se pudieron" not in raw_results:
        # Formateamos el mensaje final con los resultados del plugin
        text = (
            f"📢 Rumores para: {player or query_text}\n\n"
            f"{reply_intro}\n\n"
            f"Resultados encontrados:\n{raw_results}"
        )
    else:
        # En caso de no encontrar ningún resultado fiable, mostramos una alternativa amigable al usuario
        text = (
            f"No he encontrado rumores recientes fiables sobre: {query_text}\n\n"
            "Prueba con:\n"
            "- rumores de hoy\n"
            "- here we go\n"
            "- nombre completo del jugador"
        )

    # Respondemos al usuario enviándole el texto formateado
    await update.message.reply_text(text)
