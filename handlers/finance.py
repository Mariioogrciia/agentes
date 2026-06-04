"""
Controlador de Finanzas — Envía un mensaje de ayuda estático con ejemplos sobre finanzas de fichajes.
Este módulo orienta al usuario sobre cómo realizar consultas de conversión de divisas, sueldos y costes de fichaje.
"""

from telegram import Update
from telegram.ext import ContextTypes

# Mensaje predefinido sobre las capacidades financieras del bot y ejemplos prácticos
FINANCE_MESSAGE = (
    "💷 Finanzas de fichajes\n\n"
    "Puedo ayudarte con:\n"
    "- conversión de divisas\n"
    "- estimación de sueldo\n"
    "- cálculo de coste total de fichaje\n\n"
    "Ejemplos:\n"
    "- convierte 50 millones de euros a libras\n"
    "- cuánto son 120000 euros al mes al año\n"
    "- coste de fichaje de 25M + sueldo de 5M por 4 años"
)


async def handle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    classification: dict,
) -> None:
    """
    Maneja las consultas de finanzas respondiendo con la guía estática de formato.
    """
    # Enviar el mensaje explicativo de finanzas al chat del usuario
    await update.message.reply_text(FINANCE_MESSAGE)

