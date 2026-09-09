# Advanced Codex Lab — entrega

He hecho el lab completo usando Codex para inspeccionar el repo, preparar el entorno, localizar los fallos, aplicar los cambios, revisar el diff y validar el resultado antes de dejar el commit y la rama listos para PR.

## Preparación

Partí del repositorio canónico `https://github.com/pavlinhristov/CodexLab`, creé el entorno virtual con `python3 -m venv .venv` e instalé las dependencias con `pip install -r requirements.txt`.

Intenté iniciar la aplicación con Uvicorn para ejecutar los `curl` del enunciado. Este entorno bloquea el enlace de puertos locales, por lo que Uvicorn no pudo abrir `127.0.0.1` ni en el puerto 8000 ni en uno alternativo. Para no dejar la verificación a medias, ejecuté los mismos manejadores de ruta y la capa de persistencia sobre una copia temporal de `data/tasks.json`. Así las comprobaciones no han alterado los datos que forman parte del repo.

## Entendimiento del código

El proyecto es una API pequeña de tareas hecha con FastAPI y persistencia en JSON. El flujo de `GET /tasks` es el siguiente:

1. `app/main.py` define la ruta y recibe los parámetros `status` y `q`.
2. `app/schemas.py` define los modelos y valida los valores de estado, prioridad y respuesta.
3. `app/service.py` contiene `list_tasks`, que carga las tareas y aplica los filtros.
4. `app/store.py` lee y guarda `data/tasks.json`.
5. `data/tasks.json` contiene las tareas de ejemplo.

## Bugs encontrados y solución

El filtro por estado estaba roto porque comparaba cada tarea con el literal `"status"` en vez de con el valor recibido en el parámetro. Lo he corregido para comparar con `status`.

El endpoint de completar una tarea devolvía una copia marcada como completada, pero no actualizaba la lista original ni la guardaba en el JSON. Ahora actualiza la tarea dentro de la lista y llama a `save_tasks(tasks)`, por lo que el estado `done` y `completed_at` se mantienen al consultar la tarea otra vez.

El parámetro `q` ya estaba declarado en la ruta, pero su lógica no existía en el servicio. He añadido una búsqueda opcional con `casefold()` en título y descripción. Funciona sin distinguir mayúsculas de minúsculas, se combina con `status` y no afecta al comportamiento si no se envía `q`.

## Verificación

Las comprobaciones realizadas sobre datos temporales han pasado:

| Comprobación | Resultado |
| --- | --- |
| Listado sin filtros | tareas `[1, 2, 3, 4]` |
| `GET /tasks?status=open` | tareas `[1, 3, 4]` |
| `GET /tasks?status=done` | tarea `[2]` |
| `GET /tasks?q=LaUnCh` | tarea `[1]` |
| `GET /tasks?q=REPORT` | tarea `[4]` |
| `GET /tasks?status=open&q=plan` | tarea `[3]` |
| Completar tarea 3 y consultarla de nuevo | mantiene `status: "done"` y `completed_at` no nulo |

También ejecuté `.venv/bin/python -m compileall -q app` y `git diff --check`, sin errores. Se comprobó igualmente que `data/tasks.json` no tenía cambios antes de preparar el commit.

En un entorno que permita abrir el servidor, los comandos equivalentes para la comprobación final son:

```bash
uvicorn app.main:app --reload
curl "http://127.0.0.1:8000/tasks?status=open"
curl "http://127.0.0.1:8000/tasks?status=done"
curl -X POST http://127.0.0.1:8000/tasks/3/complete
curl http://127.0.0.1:8000/tasks/3
curl "http://127.0.0.1:8000/tasks?q=launch"
curl "http://127.0.0.1:8000/tasks?status=open&q=plan"
```

## Git y entrega

Los cambios funcionales están en `app/service.py`. No se ha incluido ningún cambio accidental en `data/tasks.json`.

He creado y publicado la rama `codex/lab-fixes` en mi fork `jonruizcarrillo-rgb/CodexLab`. El commit principal de la solución es:

```text
dbb5c10 Fix task bugs and add search filter
```

La rama está lista para revisión mediante pull request. Con esto quedan cubiertos los criterios de aceptación: filtro de estado correcto, completado persistente con fecha, búsqueda insensible a mayúsculas y minúsculas, composición de filtros y un diff limitado a cambios intencionados.
