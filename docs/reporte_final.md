# Reporte final — Clasificación de variedades de frijol seco

**Laboratorio:** CRISP-DM + TDSP + Scrum ML con el Dry Bean Dataset (UCI, id 602)
**Curso:** Gestión de Proyectos de IA — Universidad Autónoma de Occidente

---

## 1. Comprensión del negocio

Una empresa agrícola clasifica parte de sus granos de frijol manualmente, lo que es lento y poco consistente. El objetivo es **automatizar la identificación de la variedad** a partir de 16 características geométricas extraídas de imágenes, para mejorar el control de calidad.

- **Tipo de problema:** clasificación supervisada multiclase (7 variedades).
- **Métrica de éxito:** F1 macro (todas las variedades pesan igual), complementada con accuracy y errores por clase.
- **Regla de decisión:** si dos modelos rinden parecido, se prefiere el más simple.

## 2. Comprensión de los datos

| Aspecto | Resultado |
|---|---|
| Registros | 13.611 |
| Variables | 16 predictoras numéricas (14 `float64`, 2 `int64`) + `Class` |
| Valores nulos | 0 |
| Filas duplicadas | 68 |
| Clases | DERMASON 3.546 · SIRA 2.636 · SEKER 2.027 · HOROZ 1.928 · CALI 1.630 · BARBUNYA 1.322 · BOMBAY 522 |
| Desbalance | ≈7:1 entre la clase mayor y la menor |

- Las escalas difieren mucho (`Area` ~10⁴–10⁵ vs `ShapeFactor1` ~10⁻³) → se estandariza para el modelo lineal.
- Los valores extremos son **legítimos**: de los 551 extremos de `Area`, 522 son BOMBAY (grano más grande); de los 843 de `Eccentricity`, 828 son SEKER (grano más redondo). No se eliminan.
- El `.xlsx` original trae dos columnas con nombre distinto a la versión de UCI (`AspectRation`, `roundness`); se normalizan en `src/data.py`.

![Distribución de clases](../outputs/reports/figures/distribucion_clases.png)

## 3. Preparación de los datos

1. Eliminación de 68 duplicados exactos → **13.543 filas** (`data/processed/dry_bean_clean.csv`).
2. Separación `X` / `y` (`Class`).
3. Partición **80/20 estratificada** con `random_state=42` → 10.834 train / 2.709 test.
4. Estandarización con `StandardScaler` **dentro de un `Pipeline`**, ajustada solo con train (sin fuga de información).

## 4. Modelado

| Modelo | Configuración | Rol |
|---|---|---|
| Logistic Regression | `StandardScaler` + `LogisticRegression(max_iter=1000)` | Baseline |
| Random Forest | 200 árboles, `class_weight="balanced"` | Modelo "mejorado" |
| Random Forest + GridSearchCV | `n_estimators`, `max_depth`, `min_samples_split` (27 combinaciones, CV 3) | Extensión B |

## 5. Evaluación

### Conjunto de prueba (2.709 granos)

| Modelo | Accuracy | F1 macro |
|---|---|---|
| Logistic Regression | **0,9195** | 0,9306 |
| Random Forest | **0,9195** | **0,9310** |
| RF optimizado (GridSearch) | — | 0,9269 |

### Validación cruzada estratificada (5 folds, F1 macro)

| Modelo | Media | Desv. estándar |
|---|---|---|
| Logistic Regression | **0,9359** | 0,0071 |
| Random Forest | 0,9343 | 0,0037 |

### F1 por clase (Random Forest)

| BARBUNYA | BOMBAY | CALI | DERMASON | HOROZ | SEKER | SIRA |
|---|---|---|---|---|---|---|
| 0,910 | 1,000 | 0,929 | 0,915 | 0,955 | 0,941 | 0,867 |

![Matrices de confusión](../outputs/reports/figures/matrices_confusion.png)

**Errores principales (RF, 218 en total):**

- **SIRA ↔ DERMASON: 95 errores (44 %).** Variedades pequeñas con compactness y redondez casi iguales y áreas que se solapan.
- **BARBUNYA ↔ CALI: 28 errores.** Ambas grandes y con perímetro similar; se diferencian sobre todo por el color/patrón, que no está en los datos.
- **BOMBAY:** clasificada perfectamente por su tamaño.

![Importancia de variables](../outputs/reports/figures/importancia_variables.png)

Variables más útiles: `Perimeter`, `ShapeFactor1`, `Compactness`, `ShapeFactor3`, `MinorAxisLength` (combinan tamaño y forma). La importancia explica el modelo; no prueba causalidad.

### Decisión

Random Forest **no supera de forma clara** al baseline (diferencia de 0,0004 en F1 macro en test y ligeramente inferior en CV). El ajuste de hiperparámetros tampoco mejora. Siguiendo el criterio del laboratorio, **se recomienda la regresión logística** para producción (≈3 KB, rápida, interpretable). Se guardan ambos modelos.

El techo de ≈93 % de F1 macro proviene de los **datos**: algunas variedades son geométricamente casi indistinguibles. Para mejorar se necesitan variables nuevas (color, textura), no un modelo más complejo.

## 6. Despliegue

- Modelos guardados con `joblib` en `outputs/models/` (`random_forest_drybean.joblib`, `logistic_regression_drybean.joblib`).
- Se verificó que el modelo cargado reproduce exactamente las predicciones del modelo entrenado.
- Función reutilizable `predict_bean_class()` y CLI en `src/predict.py`:

```bash
python -m src.predict --input data/processed/dry_bean_clean.csv --n 5
```

- Predicciones del test guardadas en `outputs/reports/predicciones_drybean.csv`.

**Antes de producción** se necesitaría: costo de cada tipo de error, validación con un lote real de planta (misma cámara/iluminación/segmentación), requisitos de latencia, plan de monitoreo de *drift* y una regla de revisión manual para predicciones con baja confianza.

## 7. Scrum ML

El trabajo se organizó en 3 sprints. La evidencia completa está en [`docs/scrum/`](scrum/):

- [Product backlog](scrum/product_backlog.md)
- [Tablero Por hacer / En progreso / Hecho](scrum/tablero.md)
- [Sprints, sprint reviews y daily](scrum/sprints.md)
- [Retrospectiva](scrum/retrospectiva.md)
- [Definition of Done](scrum/definition_of_done.md)

**Sprint review (resumen):** Sprint 1 entregó datos limpios y partición reproducible; Sprint 2 mostró que el modelo complejo no aporta sobre el baseline (hallazgo que cambió la recomendación); Sprint 3 dejó el modelo guardado, el CLI de predicción, pruebas automáticas y la documentación.

## Relación entre metodologías

| Metodología | Aporte en el proyecto |
|---|---|
| CRISP-DM | La lógica del proyecto: 6 fases, cada una visible en el notebook y en este reporte. |
| TDSP | El orden técnico: estructura de carpetas, código modular en `src/`, semilla fija, artefactos versionados, pruebas. |
| Scrum ML | La gestión del equipo: roles, backlog priorizado, sprints con entregables verificables, retrospectiva. |
