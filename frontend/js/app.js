// Lógica del frontend: se comunica con la API de Tareas y pinta los resultados en la página.

// Dirección de la API. Debe estar arrancada con: uvicorn app.main:app --reload
const API_URL = "http://127.0.0.1:8000";

// Elementos del HTML que vamos a usar
const formulario = document.getElementById("form-tarea");
const tituloFormulario = document.getElementById("titulo-formulario");
const inputTitulo = document.getElementById("titulo");
const inputDescripcion = document.getElementById("descripcion");
const botonGuardar = document.getElementById("boton-guardar");
const botonCancelar = document.getElementById("boton-cancelar");
const lista = document.getElementById("lista-tareas");
const mensajeError = document.getElementById("mensaje-error");

// Estado de la página
let tareas = [];             // Última lista de tareas recibida de la API
let tareaEnEdicion = null;   // Tarea que se está editando, o null si el formulario sirve para crear


// ---------- Llamadas a la API ----------

// Envoltorio de fetch: añade la URL base y convierte los fallos en errores con un mensaje claro.
async function peticion(ruta, opciones = {}) {
  let respuesta;
  try {
    respuesta = await fetch(API_URL + ruta, opciones);
  } catch {
    // fetch solo falla aquí si no llega a conectar (por ejemplo, la API no está arrancada).
    throw new Error(`No se pudo conectar con la API en ${API_URL}. ¿Está arrancada?`);
  }

  if (!respuesta.ok) {
    throw new Error(`La API ha respondido con un error ${respuesta.status}.`);
  }

  // DELETE responde 204 (sin cuerpo), así que no hay JSON que leer.
  return respuesta.status === 204 ? null : respuesta.json();
}

const obtenerTareas = () => peticion("/tareas");

const crearTarea = (titulo, descripcion) =>
  peticion("/tareas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titulo, descripcion: descripcion || null }),
  });

// PUT reemplaza la tarea entera, así que también hay que enviar su estado (completada o no).
const actualizarTarea = (id, titulo, descripcion, completada) =>
  peticion(`/tareas/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titulo, descripcion: descripcion || null, completada }),
  });

const completarTarea = (id) => peticion(`/tareas/${id}/completar`, { method: "PUT" });

const desmarcarTarea = (id) => peticion(`/tareas/${id}/desmarcar`, { method: "PUT" });

const eliminarTarea = (id) => peticion(`/tareas/${id}`, { method: "DELETE" });


// ---------- Modo edición del formulario ----------

// Rellena el formulario con los datos de la tarea y lo cambia a modo "editar".
function empezarEdicion(tarea) {
  tareaEnEdicion = tarea;
  inputTitulo.value = tarea.titulo;
  inputDescripcion.value = tarea.descripcion ?? "";
  tituloFormulario.textContent = "Editar tarea";
  botonGuardar.textContent = "Guardar cambios";
  botonCancelar.classList.remove("d-none");
  inputTitulo.focus();
  pintarTareas();
}

// Vacía el formulario y lo devuelve a modo "crear".
function terminarEdicion() {
  tareaEnEdicion = null;
  formulario.reset();
  tituloFormulario.textContent = "Nueva tarea";
  botonGuardar.textContent = "Añadir tarea";
  botonCancelar.classList.add("d-none");
  pintarTareas();
}


// ---------- Pintar la lista ----------

function crearBoton(texto, claseColor, alHacerClic) {
  const boton = document.createElement("button");
  boton.type = "button";
  boton.className = `btn btn-sm ${claseColor}`;
  boton.textContent = texto;
  boton.addEventListener("click", alHacerClic);
  return boton;
}

function crearElementoTarea(tarea) {
  const item = document.createElement("li");
  item.className = "list-group-item d-flex justify-content-between align-items-center gap-3";
  // Resalta la tarea que se está editando.
  if (tarea.id === tareaEnEdicion?.id) {
    item.classList.add("list-group-item-primary");
  }

  // Se usa textContent (y no innerHTML) para que, si un título contiene HTML,
  // se muestre como texto en lugar de ejecutarse en la página (ataque XSS).
  const titulo = document.createElement("div");
  titulo.className = "fw-semibold";
  titulo.textContent = tarea.titulo;
  if (tarea.completada) {
    titulo.classList.add("text-decoration-line-through", "text-body-secondary");
  }

  const textos = document.createElement("div");
  textos.append(titulo);
  if (tarea.descripcion) {
    const descripcion = document.createElement("small");
    descripcion.className = "text-body-secondary";
    descripcion.textContent = tarea.descripcion;
    textos.append(descripcion);
  }

  const botones = document.createElement("div");
  botones.className = "d-flex gap-2 flex-shrink-0";
  if (tarea.completada) {
    botones.append(crearBoton("Desmarcar", "btn-outline-secondary", () => ejecutar(() => desmarcarTarea(tarea.id))));
  } else {
    botones.append(crearBoton("Completar", "btn-outline-success", () => ejecutar(() => completarTarea(tarea.id))));
  }
  botones.append(
    crearBoton("Editar", "btn-outline-primary", () => empezarEdicion(tarea)),
    crearBoton("Eliminar", "btn-outline-danger", () => ejecutar(() => eliminarTarea(tarea.id))),
  );

  item.append(textos, botones);
  return item;
}

function pintarTareas() {
  if (tareas.length === 0) {
    const vacio = document.createElement("li");
    vacio.className = "list-group-item text-body-secondary";
    vacio.textContent = "No hay tareas todavía.";
    lista.replaceChildren(vacio);
    return;
  }

  lista.replaceChildren(...tareas.map(crearElementoTarea));
}

async function cargarTareas() {
  tareas = await obtenerTareas();

  // La tarea en edición puede haber cambiado mientras tanto (completada, desmarcada o
  // eliminada). Se actualiza para no guardar después un estado antiguo.
  if (tareaEnEdicion) {
    const actualizada = tareas.find((tarea) => tarea.id === tareaEnEdicion.id);
    if (actualizada) {
      tareaEnEdicion = actualizada;
    } else {
      terminarEdicion();
    }
  }

  pintarTareas();
}


// ---------- Acciones del usuario ----------

// Ejecuta una acción contra la API (si se indica), recarga la lista y muestra cualquier error.
async function ejecutar(accion) {
  mensajeError.classList.add("d-none");
  try {
    if (accion) {
      await accion();
    }
    await cargarTareas();
  } catch (error) {
    mensajeError.textContent = error.message;
    mensajeError.classList.remove("d-none");
  }
}

formulario.addEventListener("submit", (evento) => {
  // Evita el comportamiento por defecto del formulario (recargar la página).
  evento.preventDefault();
  const titulo = inputTitulo.value;
  const descripcion = inputDescripcion.value.trim();

  ejecutar(async () => {
    if (tareaEnEdicion) {
      await actualizarTarea(tareaEnEdicion.id, titulo, descripcion, tareaEnEdicion.completada);
    } else {
      await crearTarea(titulo, descripcion);
    }
    terminarEdicion();
  });
});

botonCancelar.addEventListener("click", terminarEdicion);

// Al abrir la página, carga las tareas que ya existen.
ejecutar();
