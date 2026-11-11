# Tablero Scrum

Estado al cierre del Sprint 3. (También se puede replicar en *GitHub Projects* con estas mismas columnas.)

Este es el estado técnico declarado en la documentación existente. Según la tabla de entregables compartida, el paquete de evidencia Scrum **no se ha entregado**. Responsable de consolidarlo: Osvaldo Emilio Marin. Los archivos locales y las tareas marcadas «Hecho» no certifican la presentación académica ni las reuniones del equipo.

| Por hacer | En progreso | Hecho |
|---|---|---|
| PB-11 Variables de color/textura para separar SIRA–DERMASON y BARBUNYA–CALI | — | PB-00 Repositorio y estructura TDSP |
| PB-12 Umbral de confianza + revisión manual | | PB-01 Carga del dataset desde UCI |
| | | PB-02 Reporte de calidad de datos |
| | | PB-03 Baseline Logistic Regression |
| | | PB-04 Random Forest |
| | | PB-05 Comparación y decisión de modelo |
| | | PB-06 Matriz de confusión e importancia de variables |
| | | PB-07 Modelo guardado + `predict_bean_class` + CLI |
| | | PB-08 README y reporte final |
| | | PB-09 Pruebas automáticas |
| | | PB-10 GridSearchCV |

## Extensión de despliegue web

La tabla de cierre anterior conserva la evidencia del Sprint 3. La extensión de despliegue tiene el siguiente estado técnico; la aceptación del PO de los sprints 4–5 está pendiente:

| Por hacer | En progreso | Hecho |
|---|---|---|
| PB-19 Alternativa de VM | PB-18 Azure desplegado y verificado; reversión pendiente | PB-13 Artefacto reproducible |
| | | PB-14 API de predicción |
| PB-20 Validación y entrega operativa | | PB-15 Salud, validación y operación de la API |
| | | PB-16 Dashboard Streamlit |
| | | PB-17 Docker y Compose |

PB-11 y PB-12 siguen pendientes como trabajo futuro. La extensión web se documenta en el [README](../../README.md) y Azure en su [guía opcional](../../deploy/azure/README.md). La iteración 6 está en progreso. Las imágenes reorganizadas ya se construyeron y pasaron healthchecks locales; la aceptación del equipo y una publicación de esta versión en Azure siguen pendientes. Los pendientes de calidad y operación se detallan en la [DoD](definition_of_done.md).

## Evolución por sprint

| Momento | Por hacer | En progreso | Hecho |
|---|---|---|---|
| Inicio Sprint 1 | PB-00 … PB-10 | — | — |
| Fin Sprint 1 | PB-03 … PB-10 | — | PB-00, PB-01, PB-02 |
| Fin Sprint 2 | PB-07 … PB-10 | — | + PB-03, PB-04, PB-05, PB-06 |
| Fin Sprint 3 | PB-11, PB-12 (nuevas) | — | + PB-07, PB-08, PB-09, PB-10 |
