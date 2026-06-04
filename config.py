"""
Configuración del sistema - Carga de variables de entorno.
Este módulo se encarga de cargar las variables de entorno necesarias para la aplicación,
por ejemplo, tokens y claves de acceso de APIs de servicios externos.
Se recomienda copiar el archivo `.env.example` como `.env` y rellenar los valores reales.
"""

import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env si existe en el directorio actual
load_dotenv()

# --- Configuración de Telegram ---
# Token de acceso para el bot de Telegram, obtenido a través de BotFather
TELEGRAM_TOKEN: str = os.environ["TELEGRAM_TOKEN"]

# --- Configuración de Azure OpenAI (para Semantic Kernel) ---
# Clave de API de Azure para interactuar con los servicios de OpenAI
AZURE_OPENAI_API_KEY: str = os.environ["AZURE_OPENAI_API_KEY"]
# URL del punto de conexión (endpoint) de Azure OpenAI, ej: https://<recurso>.openai.azure.com/
AZURE_OPENAI_ENDPOINT: str = os.environ["AZURE_OPENAI_ENDPOINT"]
# Versión de la API de Azure OpenAI a utilizar (por defecto "2025-03-01-preview")
AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
# Nombre del despliegue del modelo (deployment) en Azure, ej: "gpt-4o-mini"
# Semantic Kernel usa esta variable para identificar el modelo desplegado
AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

# --- Configuración de SerpAPI ---
# Clave de API para SerpAPI, utilizada para realizar búsquedas en Google
SERPAPI_KEY: str = os.environ["SERPAPI_KEY"]
