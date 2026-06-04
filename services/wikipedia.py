"""
Plugin de Wikipedia para Semantic Kernel.

Obtiene el resumen de la página de un jugador desde la Wikipedia en español.
Expuesto como plugin con @kernel_function para que los agentes de IA puedan
consultar Wikipedia automáticamente cuando necesiten información biográfica.
"""

import logging
from typing import Annotated

import aiohttp
from urllib.parse import quote
from semantic_kernel.functions import kernel_function

# Creamos un logger para registrar eventos específicos de este módulo
logger = logging.getLogger(__name__)

# Endpoint de la API REST de Wikipedia en español para obtener el resumen de una página por título
WIKI_API = "https://es.wikipedia.org/api/rest_v1/page/summary/{title}"


class WikipediaPlugin:
    """
    Plugin de Semantic Kernel que expone la consulta a Wikipedia como herramienta.
    Los agentes pueden llamar a este plugin para obtener información biográfica de jugadores.
    """

    @kernel_function(
        name="get_wikipedia_summary",
        description="Obtiene el resumen de un artículo de Wikipedia en español dado el nombre de una persona o tema."
    )
    async def get_wikipedia_summary(
        self,
        title: Annotated[str, "El título del artículo de Wikipedia a buscar (usar guiones bajos en vez de espacios)"],
    ) -> str:
        """
        Obtiene asíncronamente el resumen de Wikipedia para un título dado.
        Retorna el texto del extracto o un mensaje indicando que no se encontró la página.
        """
        # Codificamos el título de forma segura para usarlo como parámetro en la URL
        url = WIKI_API.format(title=quote(title, safe=""))
        try:
            # Iniciamos sesión HTTP asíncrona
            async with aiohttp.ClientSession() as session:
                # Petición GET con un tiempo límite (timeout) de 10 segundos
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    # Si la página no existe en Wikipedia (código 404), retornamos un mensaje informativo
                    if resp.status == 404:
                        logger.info("Wikipedia: no se encontró página para %s", title)
                        return f"No se encontró artículo de Wikipedia para: {title}"
                    # Verificamos si hubo otro tipo de error HTTP
                    resp.raise_for_status()
                    # Parseamos la respuesta JSON
                    data = await resp.json()
        except Exception as exc:
            # En caso de fallo de red u otros errores inesperados, registramos una advertencia
            logger.warning("Fallo la petición a Wikipedia para %s: %s", title, exc)
            return f"Error al consultar Wikipedia para: {title}"

        # Extraemos el campo 'extract' que contiene el resumen textual del artículo
        extract = data.get("extract", "")
        if extract:
            return extract
        return f"No se encontró resumen en Wikipedia para: {title}"
