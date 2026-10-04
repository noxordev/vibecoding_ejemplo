"""Configuración de la aplicación.

Los valores se leen de variables de entorno para poder cambiarlos sin tocar
el código (por ejemplo, usar otro fichero de base de datos en producción).
"""

import os

# Ruta del fichero SQLite. Si no se define la variable de entorno
# TAREAS_DB_PATH, se usa "tareas.db" en la carpeta desde la que se lanza el servidor.
RUTA_DB: str = os.getenv("TAREAS_DB_PATH", "tareas.db")

# Orígenes (frontends) que pueden llamar a la API desde el navegador (CORS).
# "*" permite cualquier origen. Para restringirlo, se indica una lista separada
# por comas, por ejemplo: "http://localhost:5173,https://mi-web.com".
ORIGENES_CORS: list[str] = [
    origen.strip() for origen in os.getenv("TAREAS_CORS_ORIGINS", "*").split(",")
]
