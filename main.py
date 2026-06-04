"""
Bot de Transferencias de Fútbol - Punto de entrada principal
Este script replica el flujo de trabajo de n8n para un bot de Telegram sobre fútbol y fichajes.
Inicializa el bot, configura el registrador de eventos (logger) y establece los controladores de mensajes.
"""

# Importamos el módulo nativo logging para registrar eventos y errores en la consola
import logging

# Importamos componentes clave de python-telegram-bot para gestionar la app, filtrar mensajes y manejarlos
from telegram.ext import Application, MessageHandler, filters

# Importamos la función controladora que procesa todos los mensajes entrantes
from handlers.message_handler import handle_message

# Importamos el token del bot de Telegram desde el módulo de configuración local
from config import TELEGRAM_TOKEN

# Configuración del sistema de registro (logging) para mostrar la fecha, hora, nivel de log y el mensaje
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", # Estructura visual de cada línea de log
    level=logging.INFO, # Nivel de severidad mínimo a registrar (INFO, WARNING, ERROR, CRITICAL)
)

# Creamos un logger específico para este archivo
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Función principal para inicializar y arrancar el bot de Telegram.
    """
    # Inicializa el constructor de la aplicación de Telegram utilizando el token único del bot
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Filtro: detecta mensajes de texto (filters.TEXT) que no comiencen con barra/diagonal (cmd) (~filters.COMMAND)
    filtro_texto_plano = filters.TEXT & ~filters.COMMAND
    
    # Crea un manejador de mensajes que asocia el filtro anterior con nuestra función controladora asíncrona
    manejador_mensajes = MessageHandler(filtro_texto_plano, handle_message)
    
    # Agrega el manejador a la aplicación para que empiece a procesar los mensajes recibidos
    app.add_handler(manejador_mensajes)

    # Registra en la consola un mensaje indicando que el bot se ha iniciado correctamente
    logger.info("Bot iniciado. Escuchando nuevos mensajes...")
    
    # Inicia el bucle de polling: realiza consultas constantes al servidor de Telegram para recibir mensajes nuevos
    app.run_polling()


# Comprobación de seguridad: asegura que la función main() solo se ejecute si este archivo se arranca directamente
if __name__ == "__main__":
    main()


