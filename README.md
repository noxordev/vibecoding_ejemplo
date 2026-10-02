# API de Tareas

API REST sencilla para gestionar una lista de tareas (crear, listar, consultar, actualizar y borrar), construida con **FastAPI**, **Pydantic** y **SQLite** (módulo `sqlite3` de la librería estándar de Python).

## Tecnologías


| Herramienta                              | Para qué se usa                                      |
| ---------------------------------------- | ---------------------------------------------------- |
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web para definir los endpoints             |
| [Pydantic](https://docs.pydantic.dev/)   | Validación de los datos de entrada y salida          |
| `sqlite3`                                | Base de datos en un único fichero, sin instalar nada |
| [Uvicorn](https://www.uvicorn.org/)      | Servidor que ejecuta la aplicación                   |
| [pytest](https://docs.pytest.org/)       | Tests automáticos                                    |




## Estructura del proyecto

```
vibecoding_ejemplo/
├── app/
│   ├── main.py          # Punto de entrada: crea la app y registra los routers
│   ├── config.py        # Configuración (ruta de la base de datos)
│   ├── database.py      # Conexión a SQLite y creación de tablas
│   ├── schemas.py       # Modelos Pydantic (validación de datos)
│   ├── repository.py    # Consultas SQL (acceso a datos)
│   └── routers/
│       └── tareas.py    # Endpoints HTTP /tareas
├── tests/
│   ├── conftest.py      # Configuración de los tests (BD temporal)
│   └── test_tareas.py   # Tests de los endpoints
├── pyproject.toml       # Configuración de pytest
├── requirements.txt     # Dependencias
└── README.md
```

El código está organizado en **capas**, cada una con una única responsabilidad:

1. **Router** (`routers/tareas.py`): habla HTTP. Recibe la petición y devuelve la respuesta con el código adecuado (200, 201, 404...).
2. **Esquemas** (`schemas.py`): definen qué datos son válidos. Si el JSON recibido no cumple las reglas, FastAPI responde automáticamente con un error `422`.
3. **Repositorio** (`repository.py`): contiene todo el SQL. Los endpoints nunca escriben SQL directamente.
4. **Base de datos** (`database.py`): abre y cierra conexiones. Cada petición recibe su propia conexión mediante la *inyección de dependencias* de FastAPI (`Depends(get_db)`).

Gracias a esta separación, cambiar SQLite por otra base de datos solo afectaría a `database.py` y `repository.py`.

## Instalación

Requisitos: **Python 3.10 o superior**.

### 1. Crear el entorno virtual

```bash
python -m venv .venv
```



### 2. Activarlo


| Sistema              | Comando                      |
| -------------------- | ---------------------------- |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (CMD)        | `.venv\Scripts\activate.bat` |
| macOS / Linux        | `source .venv/bin/activate`  |


> Si PowerShell muestra un error de "ejecución de scripts deshabilitada", ejecuta una vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

Sabrás que está activo porque el prompt de la terminal empieza por `(.venv)`.

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```



## Ejecutar la API

```bash
uvicorn app.main:app --reload
```

- `--reload` reinicia el servidor automáticamente cada vez que guardas un cambio en el código.
- La base de datos `tareas.db` se crea sola la primera vez que se arranca.

Una vez arrancado, abre en el navegador:

- **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**: documentación interactiva (Swagger UI). Desde aquí puedes probar todos los endpoints sin escribir código.
- **[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)**: documentación alternativa.



## Endpoints


| Método   | Ruta                      | Descripción                                                | Respuesta correcta |
| -------- | ------------------------- | ---------------------------------------------------------- | ------------------ |
| `GET`    | `/tareas`                 | Lista todas las tareas                                     | `200 OK`           |
| `GET`    | `/tareas?completada=true` | Lista solo las completadas (o `false` para las pendientes) | `200 OK`           |
| `GET`    | `/tareas/{id}`            | Obtiene una tarea                                          | `200 OK`           |
| `POST`   | `/tareas`                 | Crea una tarea                                             | `201 Created`      |
| `PUT`    | `/tareas/{id}`            | Reemplaza todos los datos de una tarea                     | `200 OK`           |
| `PUT`    | `/tareas/{id}/completar`  | Marca una tarea como completada (sin cuerpo)               | `200 OK`           |
| `DELETE` | `/tareas/{id}`            | Elimina una tarea                                          | `204 No Content`   |


Si el `id` no existe, la API responde `404 Not Found`. Si los datos enviados no son válidos, responde `422 Unprocessable Entity`.

### Modelo de una tarea

```json
{
  "id": 1,
  "titulo": "Comprar pan",
  "descripcion": "Integral, en la panadería de la esquina",
  "completada": false,
  "fecha_creacion": "2026-10-02T11:56:21Z"
}
```


| Campo            | Tipo           | Reglas                                 |
| ---------------- | -------------- | -------------------------------------- |
| `id`             | entero         | Lo genera la base de datos             |
| `titulo`         | texto          | Obligatorio, de 1 a 100 caracteres     |
| `descripcion`    | texto o `null` | Opcional, máximo 500 caracteres        |
| `completada`     | booleano       | `false` al crear; obligatorio en `PUT` |
| `fecha_creacion` | fecha (UTC)    | La genera la base de datos             |




## Base de datos (SQLite)

Los datos se guardan en un único fichero, `tareas.db`, que se crea automáticamente al arrancar la API. La tabla está definida en `app/database.py`:

```sql
CREATE TABLE IF NOT EXISTS tareas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT    NOT NULL,
    descripcion    TEXT,
    completada     INTEGER NOT NULL DEFAULT 0,
    fecha_creacion TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
)
```

Reglas de la tabla:

- **`id` incremental**: SQLite asigna 1, 2, 3… automáticamente. Con `AUTOINCREMENT`, el id de una tarea borrada nunca se reutiliza.
- **`titulo` obligatorio** (`NOT NULL`). Los límites de longitud no están en la tabla: los comprueba Pydantic antes de llegar a la base de datos.
- **`completada` se guarda como `0` o `1`**, porque SQLite no tiene tipo booleano. Vale `0` (pendiente) al crear la tarea, y la API lo devuelve como `false`/`true`.
- **`fecha_creacion` la pone SQLite** al insertar, en UTC y formato ISO 8601 (`2026-10-02T11:56:21Z`).

Cómo se usa desde el código:

- Cada petición HTTP abre su propia conexión y la cierra al terminar.
- Todas las consultas pasan los valores como parámetros (`?`), nunca pegados al texto del SQL, para evitar inyección SQL.
- `CREATE TABLE IF NOT EXISTS` hace que reiniciar el servidor no borre los datos. Por eso, si cambias la definición de la tabla, tienes que borrar `tareas.db` (perdiendo su contenido) para que se cree de nuevo.

`tareas.db` es un fichero binario, así que no se puede leer como texto. Para ver su contenido puedes usar una extensión del editor como *SQLite Viewer*.

## Ejemplos de uso



### Con curl (macOS, Linux o Git Bash)

```bash
# Crear una tarea (POST)
curl -X POST http://127.0.0.1:8000/tareas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Comprar pan", "descripcion": "Integral"}'

# Listar todas las tareas (GET)
curl http://127.0.0.1:8000/tareas

# Listar solo las pendientes (GET con filtro)
curl "http://127.0.0.1:8000/tareas?completada=false"

# Obtener la tarea 1 (GET)
curl http://127.0.0.1:8000/tareas/1

# Actualizar la tarea 1 (PUT: hay que enviar todos los campos)
curl -X PUT http://127.0.0.1:8000/tareas/1 \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Comprar pan integral", "descripcion": "Dos barras", "completada": false}'

# Marcar la tarea 1 como completada (PUT sin cuerpo)
curl -X PUT http://127.0.0.1:8000/tareas/1/completar

# Borrar la tarea 1 (DELETE)
curl -X DELETE http://127.0.0.1:8000/tareas/1
```



### Con PowerShell (Windows)

```powershell
$base = "http://127.0.0.1:8000"

# Crear una tarea (POST)
Invoke-RestMethod "$base/tareas" -Method Post -ContentType "application/json" `
  -Body '{"titulo": "Comprar pan", "descripcion": "Integral"}'

# Listar todas las tareas (GET)
Invoke-RestMethod "$base/tareas"

# Obtener la tarea 1 (GET)
Invoke-RestMethod "$base/tareas/1"

# Actualizar la tarea 1 (PUT: hay que enviar todos los campos)
Invoke-RestMethod "$base/tareas/1" -Method Put -ContentType "application/json" `
  -Body '{"titulo": "Comprar pan integral", "descripcion": "Dos barras", "completada": false}'

# Marcar la tarea 1 como completada (PUT sin cuerpo)
Invoke-RestMethod "$base/tareas/1/completar" -Method Put

# Borrar la tarea 1 (DELETE)
Invoke-RestMethod "$base/tareas/1" -Method Delete
```

> En Windows PowerShell 5.1 las tildes de las respuestas pueden verse mal (por ejemplo `DocumentaciÃ³n`). Es un problema de cómo PowerShell muestra el texto, no de la API: en `/docs` se ven correctamente.



## Tests

Con el entorno virtual activado:

```bash
pytest
```

Los tests usan una base de datos temporal distinta para cada test, así que no modifican tu `tareas.db`.

## Configuración


| Variable de entorno | Valor por defecto | Descripción                                 |
| ------------------- | ----------------- | ------------------------------------------- |
| `TAREAS_DB_PATH`    | `tareas.db`       | Ruta del fichero de la base de datos SQLite |


Ejemplo en PowerShell: `$env:TAREAS_DB_PATH = "mis_tareas.db"` antes de arrancar el servidor. Si indicas una carpeta, debe existir previamente.