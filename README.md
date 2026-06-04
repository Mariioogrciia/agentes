# ⚽ Football Transfer Bot (Microsoft Agent Framework)

Bot de Telegram sobre fútbol y mercado de fichajes que implementa el workflow utilizando **Microsoft Semantic Kernel (Agent Framework)**.

---

## 🏗️ Arquitectura y Flujo Completo de Funcionamiento

El bot opera bajo una arquitectura de agentes y plugins guiada por eventos (mensajes de Telegram). El flujo completo paso a paso es el siguiente:

```
[ Usuario en Telegram ] 
       │
       │ (1) Envía mensaje: "¿Cuáles son los rumores de Mbappé?"
       ▼
 [ main.py (Polling) ] ──(2) Enruta mensaje plano──► [ handlers/message_handler.py ]
                                                            │
                                                            │ (3) Solicita clasificación
                                                            ▼
                                                   [ services/classifier.py ]
                                                    - ChatCompletionAgent
                                                    - Analiza intenciones
                                                            │
                                                            │ (4) Retorna JSON: { "intent": "rumours", ... }
                                                            ▼
 [ handlers/message_handler.py ] ◄──────────────────────────┘
       │
       │ (5) Enruta según Intent a través del diccionario INTENT_HANDLERS
       ├───────────────────────────────┬───────────────────────────────┐
       ▼ (Si es 'rumours')             ▼ (Si es 'scouting')            ▼ (Si es 'finance' o 'fallback')
 [ handlers/rumours.py ]         [ handlers/scouting.py ]        [ handlers/finance.py / fallback.py ]
       │                               │                               │
       │ Invoca plugin                 │ Invoca Scouting Agent         │ Genera mensaje estático
       ▼                               ▼                               ▼
 [ SerpAPIPlugin ]               [ ScoutingAgent (IA) ]          [ Mensaje de Texto Fijo ]
 (Busca en Google)               - Decide usar plugins           - "Finanzas no integradas" o
       │                         - Invoca SerpAPI + Wikipedia    - Plantilla de ayuda
       │                         - Genera perfil estructurado          │
       │                               │                               │
       ▼                               ▼                               │
 [ Maqueta Noticias ]            [ Maqueta Ficha Jugador ]             │
       │                               │                               │
       └───────────────────────┬───────┴───────────────────────────────┘
                               │
                               │ (6) Envía mensaje de respuesta al chat
                               ▼
                    [ update.message.reply_text ]
                               │
                               ▼
                    [ Usuario en Telegram ]
```

### Paso a Paso Detallado:

1. **Recepción del Mensaje**: El usuario envía un mensaje a Telegram. La librería en `main.py` mediante un bucle de escucha asíncrono (`run_polling()`) captura la actualización y delega el mensaje plano al controlador principal en `handlers/message_handler.py`.

2. **Clasificación del Intent (Entendimiento)**: El controlador llama al agente clasificador en `services/classifier.py`. Este es un agente inteligente (`ChatCompletionAgent`) de Semantic Kernel que evalúa si el mensaje es de rumores, scouting, finanzas o fallback, y extrae entidades clave (nombre del jugador). Devuelve un JSON estructurado.

3. **Decisión y Enrutamiento (Los "ifs" / Enrutador)**: En `message_handler.py` se toma la decisión de qué rama del flujo ejecutar buscando la función controladora correspondiente al intent en el mapeo `INTENT_HANDLERS`.

4. **Ejecución de Lógica y Llamada a Herramientas**:
   * **Rama Rumores**: El controlador `handlers/rumours.py` utiliza directamente el plugin `SerpAPIPlugin` para hacer una búsqueda asíncrona de noticias en Google.

   * **Rama Scouting**: El controlador `handlers/scouting.py` invoca al `ScoutingAgent` (`services/scouting_agent.py`). Este agente, gracias a su configuración de comportamiento `FunctionChoiceBehavior.Auto()`, evalúa y decide usar de forma autónoma las herramientas `WikipediaPlugin` (para biografía) y `SerpAPIPlugin` (para actualidad y valor de mercado) y unifica los resultados en un perfil estructurado.

5. **Formateo y Envío de Respuesta**: El controlador correspondiente toma la información recopilada por las APIs o los agentes, la maqueta usando emojis y formato legible de texto en español, y llama a la API de Telegram (`update.message.reply_text`) para responder al usuario.

---

## ¿Cómo se conecta a Telegram?

La conexión con Telegram se gestiona en [main.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/main.py) utilizando la librería `python-telegram-bot`:
1. **Inicialización**: Se construye la aplicación con `Application.builder().token(TELEGRAM_TOKEN).build()`.

2. **Filtro de Mensajes**: Se define un filtro para capturar únicamente mensajes de texto plano que no sean comandos barra (`filters.TEXT & ~filters.COMMAND`).

3. **Manejador**: Se registra `MessageHandler` apuntando a la función asíncrona `handle_message` en [handlers/message_handler.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/message_handler.py).

4. **Bucle de Escucha**: Se ejecuta `app.run_polling()`, lo que mantiene al bot escuchando activamente nuevos mensajes desde los servidores de Telegram mediante peticiones continuas (long polling).

---

## Estructura Lógica de Carpetas y Flujo

El proyecto sigue un patrón similar a un MVC (Modelo-Vista-Controlador), donde el controlador es Telegram (`handlers`) y el modelo/lógica de negocio son los agentes y APIs (`services`).

### 1. Carpeta `services/` (La Inteligencia y Herramientas)
Contiene todo lo relacionado con agentes de Inteligencia Artificial (Semantic Kernel) y llamadas a APIs de datos externas.

* **[classifier.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/services/classifier.py)**: Define el `ClassifierAgent` que analiza el texto del usuario y devuelve un JSON estructurado con la intención (`intent`), el jugador (`player`), la búsqueda (`query`) y un saludo corto (`reply_intro`).

* **[scouting_agent.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/services/scouting_agent.py)**: Define el `ScoutingAgent`. Este agente tiene registradas las herramientas de Wikipedia y SerpAPI. Al llamarlo con el nombre de un jugador, decide automáticamente qué herramientas usar para recopilar datos y estructurarlos en un JSON.

* **[serpapi.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/services/serpapi.py)**: Contiene `SerpAPIPlugin`, que expone una `@kernel_function` para buscar noticias en Google usando SerpAPI.

* **[wikipedia.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/services/wikipedia.py)**: Contiene `WikipediaPlugin`, que expone una `@kernel_function` para consultar biografías en la API de Wikipedia.

### 2. Carpeta `handlers/` (Los Controladores e Integración con Telegram)
Maneja la recepción del mensaje, la lógica condicional de enrutamiento y el envío de respuestas de vuelta a Telegram.

* **[message_handler.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/message_handler.py)**: El orquestador principal. Recibe el texto de Telegram, lo envía al clasificador y enruta la petición según el intent.

* **[scouting.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/scouting.py)**: Invoca al `ScoutingAgent`, recibe el JSON del perfil del jugador, lo maqueta en un formato bonito y lo envía a Telegram.

* **[rumours.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/rumours.py)**: Invoca al plugin de SerpAPI para buscar rumores, procesa las noticias y las envía a Telegram.

* **[finance.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/finance.py)** & **[fallback.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/fallback.py)**: Envían mensajes de texto fijos para intenciones de finanzas o cuando no se entiende la petición.

---

## ¿Dónde están las Decisiones Condicionales (los "ifs")?

Las decisiones lógicas y condicionales del bot están distribuidas estratégicamente en tres niveles:

1. **Clasificación y Enrutamiento Principal**:
   * En [message_handler.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/message_handler.py) se encuentra la lógica condicional que decide a qué handler enviar el mensaje. Se realiza mediante un diccionario de mapeo dinámico:
     ```python
     handler = INTENT_HANDLERS.get(intent, fallback.handle)
     await handler(update, context, classification)
     ```

2. **Validación del Nombre del Jugador**:
   * En [handlers/scouting.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/scouting.py), antes de consultar a la IA, validamos si el clasificador realmente detectó un jugador:
     ```python
     if not player:
         # Mensaje pidiendo que sea más específico
     ```

3. **Verificación de Resultados de Búsqueda**:
   * En [handlers/rumours.py](file:///c:/Users/Alumno_AI/Desktop/agenten8n/handlers/rumours.py), validamos si SerpAPI retornó noticias válidas o si dio error/sin resultados para responder en consecuencia:
     ```python
     if raw_results and "No se encontraron" not in raw_results ...:
         # Envía las noticias formateadas
     else:
         # Envía mensaje de alternativa amigable
     ```

---

## Prerrequisitos

| Servicio | Para qué |
|---|---|
| **Telegram Bot Token** | Recibir/enviar mensajes a través de la librería `python-telegram-bot` |
| **Azure OpenAI** (`gpt-4o-mini`) | Motor de IA para ejecutar los agentes y razonar sobre los perfiles |
| **SerpAPI** | Herramienta para realizar búsquedas orgánicas en Google |

---

## Instalación y Uso

1. **Clonar e instalar dependencias:**
   ```bash
   git clone https://github.com/TU_USUARIO/football-bot.git
   cd football-bot
   
   # Crear entorno virtual
   python -m venv venv
   # Activar en Windows:
   .\venv\Scripts\activate
   # Activar en Linux/macOS:
   source venv/bin/activate
   
   # Instalar paquetes requeridos (incluye semantic-kernel)
   pip install -r requirements.txt
   ```

2. **Configuración del Entorno (`.env`):**
   Crea un archivo `.env` en la raíz del proyecto con la siguiente estructura:
   ```dotenv
   TELEGRAM_TOKEN=tu_telegram_token
   AZURE_OPENAI_API_KEY=tu_azure_openai_key
   AZURE_OPENAI_ENDPOINT=https://tu-endpoint.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2025-03-01-preview
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
   SERPAPI_KEY=tu_serpapi_key
   ```

3. **Ejecutar el bot:**
   ```bash
   python main.py
   ```

---

## Flujo de Intents (Ejemplos)

| Entrada del Usuario | Intent Detectado | Comportamiento del Agente |
|---|---|---|
| `"Rumores sobre Haaland"` | `rumours` | Llama a SerpAPIPlugin para extraer las últimas noticias de Google y las responde. |
| `"Analiza el perfil de Gavi"` | `scouting` | `ScoutingAgent` decide llamar a Wikipedia (para biografía) y a Google (para actualidad), resume los datos en formato JSON y el handler pinta la ficha del jugador. |
| `"Convertir 10M euros"` | `finance` | Devuelve información fija de que las finanzas no están integradas aún. |
| `"Hola"` | `fallback` | Retorna una plantilla amistosa pidiendo que se le pregunte por fichajes o jugadores. |
