"""
Controlador de Scouting (Exploración de Jugadores) con Microsoft Agent Framework.

Flujo de ejecución simplificado gracias a Semantic Kernel:
  Recibir nombre del jugador → Invocar ScoutingAgent (que usa plugins automáticamente) → Enviar perfil
  
El agente de scouting tiene registrados los plugins de Wikipedia y SerpAPI,
por lo que puede buscar información automáticamente sin necesidad de orquestación manual.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

# Importamos la función que invoca al agente de scouting de Semantic Kernel
from services.scouting_agent import extract_scouting_profile

# Creamos un logger para registrar eventos específicos de este módulo
logger = logging.getLogger(__name__)


async def handle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    classification: dict,
) -> None:
    """
    Controla la lógica de scouting de jugadores.
    Gracias al Microsoft Agent Framework, el agente busca automáticamente en Wikipedia y Google
    usando los plugins registrados, sin necesidad de orquestar las llamadas manualmente.
    """
    # Extraemos el nombre del jugador del diccionario de clasificación
    player: str = classification.get("player", "").strip()

    # Si no se detectó ningún jugador, se le pide al usuario que sea más específico
    if not player:
        await update.message.reply_text(
            "No he detectado el nombre del jugador. "
            "Escríbelo de forma completa, por ejemplo: *Lamine Yamal*",
            parse_mode="Markdown",
        )
        return

    # Invocamos al agente de scouting de Semantic Kernel
    # El agente usará automáticamente los plugins de Wikipedia y SerpAPI para recopilar datos
    try:
        profile = await extract_scouting_profile(player=player)
    except Exception as exc:
        logger.error("Error del agente de IA de scouting: %s", exc)
        await update.message.reply_text(
            f"⚠️ No pude generar el perfil de {player}. Inténtalo de nuevo."
        )
        return

    # Maquetamos el mensaje que se enviará al usuario con los datos recopilados por el agente
    text = (
        f"📋 Perfil de {profile.get('player', player)}\n\n"
        f"🏟️ Equipo: {profile.get('team', 'No encontrado')}\n"
        f"🎂 Edad: {profile.get('age', 'No encontrado')}\n"
        f"🌍 Nacionalidad: {profile.get('nationality', 'No encontrado')}\n"
        f"💶 Valor de mercado: {profile.get('market_value', 'No encontrado')}\n\n"
        f"📝 Perfil: {profile.get('profile', '')}"
    )

    # Enviamos el mensaje de respuesta al chat de Telegram
    await update.message.reply_text(text)
