"""
Controlador de Respaldo (Fallback) — Se activa cuando la intención del usuario no está clara.
Proporciona un mensaje de ayuda instructivo indicando qué tipos de consultas soporta el bot.
"""

from telegram import Update
from telegram.ext import ContextTypes


async def handle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    classification: dict,
) -> None:
    """
    Maneja los mensajes cuya clasificación de intención es 'fallback'.
    Le indica al usuario qué comandos o formatos de mensaje puede intentar.
    """
    # Obtener el texto original enviado por el usuario
    original = update.message.text or ""

    # Construir el mensaje de respuesta con ejemplos de uso
    text = (
        f'No he entendido del todo tu petición: "{original}"\n\n'
        "Puedo ayudarte con:\n"
        "- rumores de fichajes\n"
        "- scouting de jugadores\n"
        "- cálculos financieros\n\n"
        "Prueba con ejemplos como:\n"
        "- rumores de hoy\n"
        "- Lamine Yamal\n"
        "- convierte 50 millones de euros a libras"
    )

    # Responder al usuario enviándole el texto de ayuda
    await update.message.reply_text(text)

