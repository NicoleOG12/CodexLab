He revisado el repo antes de tocar nada y ya tengo claro el flujo de `GET /tasks`: las rutas están en `app/main.py`, los modelos en `app/schemas.py`, la lógica está en `app/service.py`, la persistencia en `app/store.py` y los datos de ejemplo en `data/tasks.json`.

He encontrado y corregido los dos bugs. El filtro por estado no funcionaba porque estaba comparando con el texto fijo `"status"` en vez de con el valor que llegaba por query. Ahora `status=open` devuelve las tareas 1, 3 y 4, y `status=done` devuelve la 2.

El otro problema era que al completar una tarea la respuesta parecía correcta, pero el cambio no se guardaba. He cambiado la lógica para actualizar la tarea dentro de la lista y guardar esa lista. Después de completar una tarea, al volver a consultarla mantiene `status: "done"` y `completed_at` con valor.

También he añadido el filtro `q` para buscar tareas. No distingue entre mayúsculas y minúsculas, busca tanto por título como por descripción y se puede combinar con el filtro de estado. Si no se pasa `q`, el endpoint sigue funcionando igual que antes.

He comprobado los casos principales: filtros `open` y `done`, búsquedas de `launch` y `report`, la combinación `status=open&q=plan` y la persistencia al completar la tarea 3. También pasé la comprobación de sintaxis y `git diff --check`, sin errores. Hice las pruebas con una copia temporal de los datos, así que `data/tasks.json` no ha quedado modificado.

No he podido lanzar Uvicorn y hacer los `curl` directamente porque este entorno no deja abrir puertos locales, pero sí he probado los mismos manejadores y la persistencia con datos temporales. El cambio está listo para revisar. Solo se ha tocado `app/service.py`, además de este documento, y `data/tasks.json` sigue limpio. He preparado la rama `codex/lab-fixes` y el commit final para dejarlo listo para PR.
