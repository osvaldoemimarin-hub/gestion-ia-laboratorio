# Sprints

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

**Sprint review:** se aceptan los entregables. Hallazgo: el `.xlsx` local y la API de UCI usan nombres de columna distintos (`AspectRation`/`AspectRatio`, `roundness`/`Roundness`); se agrega normalización en `src/data.py` para que el modelo funcione con ambas fuentes.

---

## Sprint 2 — Modelado y evaluación

**Objetivo:** entrenar baseline y modelo alternativo, y decidir con datos.

| Tarea | Historia | Resultado |
|---|---|---|
| Entrenar Logistic Regression | PB-03 | Accuracy 0,9195 · F1 macro 0,9306 |
| Entrenar Random Forest | PB-04 | Accuracy 0,9195 · F1 macro 0,9310 |
| Comparar métricas + validación cruzada | PB-05 | Empate técnico (CV: LR 0,936 vs RF 0,934) |
| Matriz de confusión e importancia | PB-06 | Errores concentrados en SIRA–DERMASON y BARBUNYA–CALI |

**Entregables:** comparación de modelos, métricas y gráficas en `outputs/reports/`.

**Sprint review:** el PO esperaba que el Random Forest mejorara claramente; no ocurrió. Se aplica la regla "preferir el modelo más simple" y se recomienda la regresión logística. Se añade al backlog PB-10 (GridSearch) para confirmar que no es un problema de hiperparámetros.

---

## Sprint 3 — Despliegue y documentación

**Objetivo:** dejar el modelo usable y el proyecto reproducible por terceros.

| Tarea | Historia | Resultado |
|---|---|---|
| Guardar modelos `.joblib` | PB-07 | RF (≈4,4 MB comprimido) y LR (≈3 KB) |
| Función y CLI de predicción | PB-07 | `src/predict.py` |
| Pruebas automáticas | PB-09 | 5 pruebas `pytest` en verde |
| GridSearchCV | PB-10 | No mejora en test (0,927) → el techo viene de los datos |
| README y reporte | PB-08 | `README.md`, `docs/reporte_final.md` |

**Entregables:** modelo final, README profesional, entrega final.

**Sprint review:** se cumple la Definition of Done. Se crean PB-11 y PB-12 como trabajo futuro.

---

## Daily Scrum (registro de ejemplo — Sprint 2)

| Integrante | ¿Qué hice? | ¿Qué haré? | ¿Bloqueos? |
|---|---|---|---|
| Nilson Jacobo Gonzales (PO) | Validé el criterio F1 macro con el "cliente" | Revisar la comparación de modelos | Ninguno |
| Osvaldo Emilio Marin (SM / ML) | Revisé y fusioné el PR de limpieza de datos; entrené el baseline | Entrenar Random Forest y matriz de confusión; actualizar el tablero | Nombres de columnas distintos entre fuentes (resuelto en `src/data.py`) |
| Edgar Adrian Ortiz (Data) | Reporte de calidad y outliers | Gráficas de medias por clase para explicar confusiones | Conflicto de merge en el notebook (resuelto ejecutando y guardando una sola versión) |

## Flujo Git usado

```bash
git checkout -b feature/limpieza-datos      # una rama por historia
git add . && git commit -m "PB-02: reporte de calidad"
git push origin feature/limpieza-datos      # luego Pull Request → revisión → merge a main
git pull origin main
```
