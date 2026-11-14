# Product Backlog

## Roles del equipo

| Rol | Integrante | Responsabilidades |
|---|---|---|
| Product Owner | Edgar Adrian Ortiz | Define objetivos, prioriza el backlog, valida la entrega final |
| Scrum Master | Osvaldo Emilio Marin | Coordina reuniones, mantiene el tablero, README y flujo Git |
| Data Engineer / Analyst | Nilson Jacobo Gonzales | Descarga, calidad, limpieza y EDA |
| ML Engineer | Juan Andrés Ruiz Muñoz | Entrenamiento, evaluación y despliegue del modelo |

El equipo tiene **4 integrantes**, según la distribución de entregables compartida. Data Engineer / Analyst y ML Engineer son especialidades de Developers en Scrum.

## Objetivo del producto

Construir una demo reproducible que clasifique siete variedades de frijol a partir de 16 medidas geométricas y permita consultar sus resultados y limitaciones. Este objetivo se explicita a partir del alcance existente; el PO debe validarlo con el equipo.

## Responsabilidad sobre los entregables académicos

| Entregable | Encargado | Estado comunicado |
|---|---|---|
| 1. Notebook ejecutado | Nilson Jacobo Gonzales | Sí |
| 2. Reporte: puntos 1–3 y 7 | Edgar Adrian Ortiz | Parcialmente, junto con puntos 4–6 |
| 2. Reporte: puntos 4–6 | Juan Andrés Ruiz Muñoz | Parcialmente, junto con puntos 1–3 y 7 |
| 3. Evidencia Scrum ML | Osvaldo Emilio Marin | No |

Estos estados corresponden a la tabla del equipo. Las historias siguientes describen trabajo y evidencia local; no certifican envío o calificación del entregable.

## Historias de usuario

| ID | Historia de usuario | Tarea técnica | Criterio de aceptación | Prioridad | Responsable | Sprint | Estado |
|---|---|---|---|---|---|---|---|
| PB-00 | Como equipo, queremos un repositorio ordenado para colaborar. | Crear repo GitHub, estructura TDSP, entorno virtual, `requirements.txt` | Cualquier integrante clona e instala sin errores | Alta | Scrum Master | 1 | Hecho |
| PB-01 | Como analista, quiero cargar datos reales para analizarlos. | Descargar el dataset con `ucimlrepo` (fallback local) | El dataframe se carga sin errores (13.611 × 17) | Alta | Data Engineer | 1 | Hecho |
| PB-02 | Como científico de datos, quiero revisar la calidad de los datos. | Nulos, duplicados, tipos, outliers y clases | Hay resumen de calidad documentado | Alta | Data Analyst | 1 | Hecho |
| PB-03 | Como equipo, queremos un modelo base. | Entrenar `LogisticRegression` en `Pipeline` | Se reporta accuracy y F1 macro | Alta | ML Engineer | 2 | Hecho |
| PB-04 | Como equipo, queremos mejorar el desempeño. | Entrenar `RandomForestClassifier` | Se compara contra baseline | Media | ML Engineer | 2 | Hecho |
| PB-05 | Como equipo, queremos elegir el mejor modelo. | Tabla comparativa, F1 por clase, validación cruzada | Decisión documentada con criterio explícito | Alta | Todo el equipo (4) | 2 | Hecho |
| PB-06 | Como usuario final, quiero entender el resultado. | Matriz de confusión, importancia de variables, reporte | Se documentan hallazgos en lenguaje claro | Alta | Data Analyst + ML Engineer | 2 | Hecho |
| PB-07 | Como equipo técnico, quiero reproducibilidad. | Guardar modelo con `joblib`, función `predict_bean_class`, CLI | El modelo se puede cargar y usar | Alta | ML Engineer | 3 | Hecho |
| PB-08 | Como equipo, queremos documentación profesional. | README, reporte final, evidencia Scrum | README explica cómo reproducir todo | Alta | Scrum Master | 3 | Hecho |
| PB-09 | Como equipo técnico, queremos detectar regresiones. | Pruebas `pytest` de datos, partición y modelo | `pytest` pasa en verde | Media | ML Engineer | 3 | Hecho |
| PB-10 | Como PO, quiero saber si se puede mejorar más. | `GridSearchCV` sobre Random Forest | Se reporta si mejora o no en test | Baja | ML Engineer | 3 | Hecho |
| PB-11 | Como PO, quiero distinguir mejor SIRA/DERMASON y BARBUNYA/CALI. | Explorar variables de color/textura desde las imágenes | F1 de SIRA > 0,90 | Media | — | Futuro | Por hacer |
| PB-12 | Como operario, quiero revisar a mano los casos dudosos. | Umbral de confianza y cola de revisión manual | Granos con confianza < umbral se marcan | Media | — | Futuro | Por hacer |

## Extensión: servicio web y despliegue

La extensión web es opcional para el laboratorio y está en `deploy/web/`; Azure, en `deploy/azure/`, es opcional incluso para usar la web local. El [README](../../README.md) documenta ejecución, contrato básico y estructura. Los responsables se expresan por rol; esta tabla no modifica la asignación de integrantes.

| ID | Historia de usuario | Tarea técnica | Criterio de aceptación | Prioridad | Responsable | Sprint | Estado |
|---|---|---|---|---|---|---|---|
| PB-13 | Como equipo técnico, quiero servir un artefacto reproducible. | Seleccionar LR, fijar dependencias y crear manifiesto con huellas y versiones | Carga sin incompatibilidades; métricas y esquema corresponden al artefacto | Alta | ML Engineer | 4 | Hecho técnico |
| PB-14 | Como consumidor técnico, quiero predecir mediante HTTP. | FastAPI, esquemas, endpoint individual/lote y consulta del modelo | Contrato v1 documentado; valida 16 variables; clase y probabilidades coinciden con inferencia directa | Alta | ML Engineer | 4 | Hecho técnico |
| PB-15 | Como operador, quiero detectar fallas del servicio. | Salud, disponibilidad, límites de petición, errores y logs | Pruebas de entradas inválidas, límites y modelo ausente; logs con versión y request_id | Alta | ML Engineer | 4 | Hecho técnico |
| PB-16 | Como operario, quiero clasificar granos desde una interfaz. | Streamlit con formulario, CSV, resultados y descarga | Flujo individual y lote funciona vía API; informa errores y muestra evaluación histórica identificada | Alta | ML Engineer + Data Analyst | 5 | Hecho técnico |
| PB-17 | Como equipo técnico, quiero ejecutar ambos servicios en contenedores. | Dockerfile con dos destinos, Compose y configuración | Arranque desde copia limpia; inferencia sin UCI; healthchecks y usuario sin privilegios | Alta | ML Engineer | 5 | Hecho técnico |
| PB-18 | Como PO, quiero una demostración accesible en Azure. | ACR, Container Apps, ingress, sondas y revisiones | Dashboard público por HTTPS; API interna; predicción completa y reversión probadas | Alta | ML Engineer + Scrum Master | 6 | En progreso |
| PB-19 | Como equipo técnico, quiero una alternativa en VM. | Documentar Compose, proxy HTTPS, reinicio y reversión | Guía con imágenes por digest y pasos verificables; ejecución en VM condicionada a disponer del destino | Media | ML Engineer | 6 | Por hacer |
| PB-20 | Como PO, quiero evidencia de una entrega operable. | Pruebas de integración, medición y guía de operación | Registrar destino, versiones, latencia y límites; review y retrospectiva con evidencia real | Alta | Todo el equipo | 6 | Por hacer |

**Evidencia de PB-13 a PB-15:** [ejecución y endpoints](../../README.md), `deploy/web/api/`, `outputs/models/serving/`, versiones directas en `requirements.txt` y `tests/test_api.py`. «Hecho técnico» es una etiqueta local de implementación verificada, no una certificación de cumplimiento integral de la DoD. La inspección del equipo y la entrega académica siguen pendientes; Scrum no impone la Sprint Review como autorización para publicar.

**Evidencia de PB-16 y PB-17:** [instrucciones](../../README.md), `deploy/web/dashboard/`, `deploy/web/Dockerfile` y `docker-compose.yaml` en la raíz. En la nueva estructura se construyeron ambas imágenes y se comprobaron healthchecks, dashboard HTTP 200 y la consulta de la API interna; AppTest recorrió formulario y CSV localmente. Las pruebas persistentes `test_dashboard_*` se retiraron, por lo que la cobertura automática es menor. La aceptación visual y review del PO siguen pendientes.

**Avance de PB-18:** la [guía y los digests del despliegue](../../deploy/azure/README.md) registran la versión actual de `deploy/web/` publicada en North Central US el 11 de noviembre de 2026. Se comprobaron HTTPS, WebSocket e inferencia real SEKER con la API interna. También se publicaron ambas imágenes en Docker Hub. La historia continúa en progreso porque faltan la prueba de reversión y el cierre de la aceptación operativa.
