# Retrospectiva

La tabla conserva la síntesis que ya existía en el repositorio. El equipo debe confirmar estas observaciones y registrar la reunión real; no se dispone de acta con fecha y participantes. Según la distribución de entregables compartida, esta evidencia corresponde a Osvaldo Emilio Marin y aún no se ha entregado académicamente.

| Pregunta | Respuesta del equipo |
|---|---|
| **¿Qué salió bien / qué funcionó?** | La estructura TDSP y el código en `src/` permitieron que notebook y script den exactamente los mismos números. Fijar la semilla y estratificar desde el Sprint 1 evitó discusiones sobre resultados distintos entre integrantes. El baseline evitó que eligiéramos un modelo más complejo sin justificación. |
| **¿Qué fue difícil / qué no funcionó?** | Esperábamos que Random Forest mejorara claramente y no fue así; tampoco el GridSearch. Los notebooks generan conflictos de merge en Git. Las dos fuentes de datos (UCI y `.xlsx`) tenían nombres de columna distintos y lo descubrimos tarde, cuando una prueba falló. |
| **¿Qué cambiaríamos en el siguiente sprint / qué mejoraríamos?** | Escribir las pruebas de datos desde el Sprint 1 (habrían detectado antes lo de las columnas). Mover la lógica a `src/` y dejar el notebook solo para narrativa, para reducir conflictos. Definir con el PO, antes de modelar, qué mejora mínima justifica un modelo más complejo. |
| **¿Qué aprendizaje técnico obtuvimos?** | El modelo más complejo no mejoró en este experimento. El solapamiento sugiere investigar nuevas variables, pero no prueba un límite de rendimiento. F1 macro y la matriz de confusión permiten inspeccionar errores por clase. Los outliers no siempre son errores (BOMBAY, SEKER). Escalar dentro de un `Pipeline` evita ajustar el preprocesamiento con el test. |

## Observaciones técnicas del incremento de API — Sprint 4

Estas observaciones provienen de la implementación y sus comprobaciones; la retrospectiva del equipo y la aceptación del PO están pendientes.

- Los modelos históricos usaban scikit-learn 1.9.1 y el entorno disponible, 1.7.1. Se preparó una regresión logística en el entorno fijado, separada de la evidencia histórica; su evaluación se registra en su propio manifiesto.
- La paridad sobre todo el test permitió verificar clase, probabilidad y orden de variables sin depender de una sola predicción de ejemplo.
- La comprobación del tamaño recibió fragmentos ASGI para verificar el límite incluso sin `Content-Length`.
- Las huellas del código normalizan CRLF/LF; las huellas del modelo y del Excel conservan los bytes exactos. Esto evita que un checkout en Linux parezca cambiar el código de entrenamiento.
- El siguiente incremento debe validar los bloqueos y artefactos en Linux/Docker, además de integrar el dashboard mediante HTTP.

## Observaciones técnicas del incremento de dashboard y Docker — Sprint 5

La review y retrospectiva del equipo siguen pendientes; estas son observaciones verificadas durante la implementación.

- El dashboard reutiliza los contratos de validación y consulta las métricas del artefacto servido. Esto evita asociar matrices de confusión antiguas con el modelo activo.
- Las pruebas detectaron una incompatibilidad de ejecución entre PyArrow 26 y NumPy 1.26 que `pip check` no detectaba. PyArrow quedó fijado en 19.0.1 y se validó ejecutando la interfaz.
- Una red Docker completamente interna impedía publicar los puertos al host en este entorno. La API queda en `app` y el dashboard también usa `web`; el override local conecta la API a `web` para exponerla en localhost.
- Se probaron el formulario y la descarga CSV desde la imagen del dashboard contra la API real. La imagen de interfaz no contiene el modelo ni scikit-learn.
- El próximo incremento debe abordar registro de imágenes, configuración de Azure, acceso externo y operación en el destino elegido.

## Observaciones del despliegue de Azure — Sprint 6

- La política de Azure for Students limita las regiones disponibles. Se comprobó la política antes de crear recursos; East US no estaba permitida.
- El modo predeterminado Express rechazó los sufijos de revisión del diseño. Se fijó explícitamente Workload Profiles con API `2026-07-01`.
- La actualización del entorno inicial de Brazil South se prolongó sin finalizar. Se creó un entorno nuevo en North Central US, que terminó correctamente, conservando ACR, identidad, logs e imágenes. El intento vacío anterior se canceló y se solicitó su eliminación.
- El token de ACR canalizado por PowerShell fallaba al autenticar Docker. Un helper que entrega directamente los bytes por stdin resolvió la publicación sin exponer credenciales; se agregaron pruebas de ese contrato.
- La verificación remota recorrió el formulario real por WebSocket y comprobó una predicción mediante la API interna. La reversión, CSV manual en nube y review del equipo siguen pendientes.
