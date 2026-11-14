# Sprints

Los sprints 1–3 corresponden a la planificación académica del PDF de equipos (pp. 2–3). Los resultados técnicos se documentan con los artefactos del repositorio; no hay actas que permitan verificar fecha, participantes o aceptación de las reviews. Las iteraciones 4–6 describen la extensión web. Faltan fechas, duración acordada y registros de eventos reales para acreditar la ejecución completa de Scrum; no se deducen a partir de que el código funcione.

## Sprint 1 — Comprensión y preparación

**Objetivo:** tener datos confiables y una partición reproducible.

| Tarea | Historia | Resultado |
|---|---|---|
| Crear repositorio GitHub y estructura TDSP | PB-00 | `data/`, `notebooks/`, `outputs/`, `src/`, `docs/`, `tests/` |
| Configurar entorno virtual | PB-00 | `requirements.txt` |
| Cargar dataset desde UCI | PB-01 | 13.611 × 17, con respaldo local en `data/raw/` |
| Explorar y revisar calidad | PB-02 | 0 nulos, 68 duplicados, desbalance ≈7:1, outliers legítimos |
| Limpiar y separar train/test | PB-02 | 13.543 filas; 80/20 estratificado, semilla 42 |

**Entregables:** dataset limpio, notebook inicial, repositorio configurado.

**Resultado documentado:** el `.xlsx` local y la API de UCI usan nombres de columna distintos (`AspectRation`/`AspectRatio`, `roundness`/`Roundness`); se agregó normalización en `src/data.py` para que el modelo funcione con ambas fuentes. No se conserva un acta de Sprint Review que acredite aceptación del equipo.

---

## Sprint 2 — Modelado y evaluación

**Objetivo:** entrenar baseline y modelo alternativo, y decidir con datos.

| Tarea | Historia | Resultado |
|---|---|---|
| Entrenar Logistic Regression | PB-03 | Accuracy 0,9195 · F1 macro 0,9306 |
| Entrenar Random Forest | PB-04 | Accuracy 0,9192 · F1 macro 0,9303 |
| Comparar métricas + validación cruzada | PB-05 | Empate técnico (CV: LR 0,936 vs RF 0,934) |
| Matriz de confusión e importancia | PB-06 | Errores concentrados en SIRA–DERMASON y BARBUNYA–CALI |

**Entregables:** comparación de modelos, métricas y gráficas en `outputs/reports/`.

**Decisión documentada:** Random Forest no mejoró claramente en este experimento. Se aplicó la regla "preferir el modelo más simple" y se recomendó la regresión logística. Se añadió al backlog PB-10 (GridSearch) para comprobar si una búsqueda de hiperparámetros cambiaba la comparación. La participación o aceptación del PO queda por confirmar.

---

## Sprint 3 — Despliegue y documentación

**Objetivo:** dejar el modelo usable y el proyecto reproducible por terceros.

| Tarea | Historia | Resultado |
|---|---|---|
| Guardar modelos `.joblib` | PB-07 | RF (≈4,4 MB comprimido) y LR (≈3 KB) |
| Función y CLI de predicción | PB-07 | `src/predict.py` |
| Pruebas automáticas | PB-09 | 5 pruebas `pytest` en verde |
| GridSearchCV | PB-10 | No mejora en el test de este experimento (0,927); no demuestra un techo de rendimiento |
| README y reporte | PB-08 | `README.md`, `docs/reporte_final.md` |

**Entregables:** modelo final, README profesional, entrega final.

**Verificación técnica:** los criterios del laboratorio figuran comprobados en la [Definition of Done](definition_of_done.md). Se propusieron PB-11 y PB-12 como trabajo futuro. No hay acta que permita confirmar una Sprint Review o aceptación del PO.

---

## Sprint 4 — Artefacto reproducible y API (implementado técnicamente)

**Objetivo:** servir la regresión logística mediante un contrato HTTP validado.

**Historias:** PB-13, PB-14 y PB-15. **Entregables:** manifiesto del modelo, dependencias fijadas, FastAPI, OpenAPI, sondas y pruebas de paridad y errores. Uso: [README](../../README.md).

**Validación técnica:** paridad HTTP sobre 2.709 filas de test; rechazo de entradas inválidas y límites, incluyendo transferencia fragmentada; carga del modelo del servicio sin incompatibilidades. Se comprobó el arranque real con Uvicorn y una predicción HTTP en localhost. El artefacto preparado obtiene accuracy 0,919158 y F1 macro 0,930237; los resultados históricos se conservan aparte.

**Review con el PO:** pendiente. Presentar predicción individual, lote y errores, y registrar aceptación. Las observaciones técnicas están en la [retrospectiva](retrospectiva.md); no sustituyen una reunión del equipo.

## Sprint 5 — Dashboard y contenedores (implementado técnicamente)

**Objetivo:** permitir que un operario use el servicio y que el equipo ejecute el conjunto con Docker.

**Historias:** PB-16 y PB-17. **Entregables:** Streamlit, importación y descarga CSV, cliente HTTP, dos imágenes y Compose. Uso: [README](../../README.md).

**Validación histórica de esa iteración:** pasaban 75 pruebas, incluidas pruebas AppTest de formulario, CSV, descarga y errores. Se construyeron imágenes Linux y Compose inició ambos servicios con healthchecks; se probaron HTTP, WebSocket y flujos del dashboard. En la simplificación posterior se retiraron los archivos `test_dashboard_*`; la cifra no describe la batería actual, de 43 pruebas. Las imágenes reorganizadas se construyeron y ambas quedaron saludables en Compose; el dashboard consultó la API interna. El recorrido de formulario y CSV se comprobó localmente con AppTest, sin conservar esas pruebas como archivos.

**Hallazgo:** PyArrow 26 exigía NumPy 2 aunque su metadato no impedía la instalación con NumPy 1.26. Se fijó PyArrow 19.0.1 y se comprobó su ejecución. La red interna se complementa con una red de publicación del dashboard; el override conecta y expone la API únicamente para desarrollo local.

**Review con el PO:** pendiente. El equipo debe revisar la experiencia visual. En esta iteración todavía no se había desplegado en Azure; el avance posterior consta en la iteración 6.

## Sprint 6 — Azure y operación (en progreso)

**Objetivo:** publicar una demo operable en Azure y documentar la alternativa de VM.

**Historias:** PB-18, PB-19 y PB-20. **Entregables previstos:** imágenes en ACR, dos Container Apps, guía de VM, mediciones, procedimiento de reinicio y reversión.

**Avance técnico de la imagen publicada:** plantillas `foundation.bicep` y `apps.bicep`, script PowerShell de publicación por digest, estado local y procedimiento de reversión. Aplicaciones desplegadas en North Central US; registro, identidad y logs en Brazil South. `Verify.py` confirmó HTTPS 200, WebSocket y predicción real SEKER. Antes de la simplificación pasaban 77 pruebas; ahora pasan 43. Los scripts y digests están en la [guía de Azure](../../deploy/azure/README.md). El 11 de noviembre de 2026 se publicó la nueva estructura (revisión `r20261111024909-43fca417`) y `Verify.py` volvió a confirmar SEKER.

**Pendientes:** recorrido manual de CSV en nube, mediciones de capacidad, prueba de reversión con una entrega anterior, guía alternativa de VM y review del equipo. No se consideran completados por haber desplegado la demo.

**Review prevista:** recorrido por HTTPS en Azure, verificación de API interna y reversión. La ejecución alternativa en VM se registra solo si se dispone de esa infraestructura; documentarla no equivale a haberla probado.

El [README](../../README.md) y la extensión de la [Definition of Done](definition_of_done.md) definen el alcance. No se asignan fechas ni se registran entregas como completadas antes de obtener evidencia.

## Daily Scrum (plantilla; no es acta de una reunión)

Completar únicamente con hechos y participantes reales. La asistencia a la reunión no se acredita mediante esta plantilla. El formato de tres preguntas procede del laboratorio; no es un formato obligatorio de Scrum.

| Integrante | ¿Qué hice? | ¿Qué haré? | ¿Bloqueos? |
|---|---|---|---|
| Nilson Jacobo Gonzales (Data Engineer / Analyst) | Por registrar | Por registrar | Por registrar |
| Juan Andrés Ruiz Muñoz (ML Engineer) | Por registrar | Por registrar | Por registrar |

El PO (Edgar Adrian Ortiz) y el Scrum Master (Osvaldo Emilio Marin) participan como Developers si trabajan activamente en el Sprint Backlog. Registrar su participación cuando corresponda, sin asumirla.

## Flujo Git propuesto por el plan del laboratorio

Estos comandos describen el procedimiento; no demuestran que hayan existido ramas, Pull Requests o revisiones. La extensión web mantiene cambios sin commit al momento de esta revisión.

```bash
git checkout -b feature/limpieza-datos      # una rama por historia
git add . && git commit -m "PB-02: reporte de calidad"
git push origin feature/limpieza-datos      # luego Pull Request → revisión → merge a main
git pull origin main
```
