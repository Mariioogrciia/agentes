"""
Plugin de SerpAPI para Semantic Kernel.

Encapsula las búsquedas en Google (SerpAPI) como un plugin con decorador @kernel_function,
para que los agentes de Semantic Kernel puedan invocar estas funciones automáticamente como herramientas.
"""

import logging
from typing import Annotated

import aiohttp
from semantic_kernel.functions import kernel_function

# Importamos la clave de SerpAPI de nuestra configuración
from config import SERPAPI_KEY

# Creamos un logger para registrar eventos específicos de este módulo
logger = logging.getLogger(__name__)

# URL del endpoint para búsquedas en SerpAPI
SERPAPI_URL = "https://serpapi.com/search.json"


class SerpAPIPlugin:
    """
    Plugin de Semantic Kernel que expone la búsqueda de Google como herramienta.
    Los agentes de IA pueden llamar a este plugin automáticamente cuando necesitan buscar información en internet.
    """

    @kernel_function(
        name="google_search",
        description="Busca en Google usando SerpAPI. Devuelve los resultados orgánicos más relevantes para la consulta proporcionada."
    )
    async def google_search(
        self,
        query: Annotated[str, "La consulta de búsqueda a realizar en Google"],
        location: Annotated[str, "Ubicación geográfica para la búsqueda"] = "Spain",
        hl: Annotated[str, "Código de idioma para los resultados"] = "es",
    ) -> str:
        """
        Realiza una búsqueda asíncrona en Google a través de SerpAPI.
        Retorna los resultados orgánicos formateados como texto para el agente.
        """
        # Definimos los parámetros de búsqueda requeridos por SerpAPI
        params = {
            "q": query,                 # Consulta a buscar
            "location": location,       # Ubicación geográfica
            "google_domain": "google.com",
            "hl": hl,                   # Idioma de los resultados (es = Español)
            "device": "desktop",        # Simulación de dispositivo
            "api_key": SERPAPI_KEY,     # Clave de API
        }

        try:
            # Iniciamos una sesión HTTP asíncrona usando aiohttp
            async with aiohttp.ClientSession() as session:
                # Realizamos la petición GET asíncrona con un tiempo límite total de 15 segundos
                async with session.get(SERPAPI_URL, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    # Levanta una excepción si la respuesta no es exitosa (código HTTP 200)
                    resp.raise_for_status()
                    # Leemos y deserializamos la respuesta en JSON
                    data = await resp.json()
        except Exception as exc:
            logger.error("Error en SerpAPI: %s", exc)
            return "No se pudieron obtener resultados de búsqueda."

        # Extraemos la lista de resultados orgánicos de la respuesta estructurada de SerpAPI
        results = data.get("organic_results", [])
        logger.debug("SerpAPI retornó %d resultados para la consulta: %s", len(results), query)

        # Si no hay resultados, devolver un mensaje informativo
        if not results:
            return f"No se encontraron resultados para: {query}"

        # Formateamos los resultados como texto legible para que el agente los pueda procesar
        formatted = []
        for i, r in enumerate(results[:5], 1):  # Tomamos máximo los 5 primeros resultados
            title = r.get("title", "Sin título")
            snippet = r.get("snippet", "")
            link = r.get("link", "")
            formatted.append(f"{i}. {title}\n   {snippet}\n   {link}")

        return "\n\n".join(formatted)
