# Product Backlog

## Roles del equipo

| Rol | Integrante | Responsabilidades |
|---|---|---|
| Product Owner | Nilson Jacobo Gonzales | Define objetivos, prioriza el backlog, valida la entrega final |
| Scrum Master | Osvaldo Emilio Marin | Coordina reuniones, mantiene el tablero, README y flujo Git |
| Data Engineer / Analyst | Edgar Adrian Ortiz | Descarga, calidad, limpieza y EDA |
| ML Engineer | Osvaldo Emilio Marin | Entrenamiento, evaluación y despliegue del modelo |

> El equipo tiene 3 integrantes; el Scrum Master asume también el rol de ML Engineer. Las historias marcadas "Todo el equipo" se trabajan entre los tres.

## Historias de usuario

| ID | Historia de usuario | Tarea técnica | Criterio de aceptación | Prioridad | Responsable | Sprint | Estado |
|---|---|---|---|---|---|---|---|
| PB-00 | Como equipo, queremos un repositorio ordenado para colaborar. | Crear repo GitHub, estructura TDSP, entorno virtual, `requirements.txt` | Cualquier integrante clona e instala sin errores | Alta | Scrum Master | 1 | Hecho |
| PB-01 | Como analista, quiero cargar datos reales para analizarlos. | Descargar el dataset con `ucimlrepo` (fallback local) | El dataframe se carga sin errores (13.611 × 17) | Alta | Data Engineer | 1 | Hecho |
| PB-02 | Como científico de datos, quiero revisar la calidad de los datos. | Nulos, duplicados, tipos, outliers y clases | Hay resumen de calidad documentado | Alta | Data Analyst | 1 | Hecho |
| PB-03 | Como equipo, queremos un modelo base. | Entrenar `LogisticRegression` en `Pipeline` | Se reporta accuracy y F1 macro | Alta | ML Engineer | 2 | Hecho |
| PB-04 | Como equipo, queremos mejorar el desempeño. | Entrenar `RandomForestClassifier` | Se compara contra baseline | Media | ML Engineer | 2 | Hecho |
| PB-05 | Como equipo, queremos elegir el mejor modelo. | Tabla comparativa, F1 por clase, validación cruzada | Decisión documentada con criterio explícito | Alta | Todo el equipo (3) | 2 | Hecho |
| PB-06 | Como usuario final, quiero entender el resultado. | Matriz de confusión, importancia de variables, reporte | Se documentan hallazgos en lenguaje claro | Alta | Data Analyst + ML Engineer | 2 | Hecho |
| PB-07 | Como equipo técnico, quiero reproducibilidad. | Guardar modelo con `joblib`, función `predict_bean_class`, CLI | El modelo se puede cargar y usar | Alta | ML Engineer | 3 | Hecho |
| PB-08 | Como equipo, queremos documentación profesional. | README, reporte final, evidencia Scrum | README explica cómo reproducir todo | Alta | Scrum Master | 3 | Hecho |
| PB-09 | Como equipo técnico, queremos detectar regresiones. | Pruebas `pytest` de datos, partición y modelo | `pytest` pasa en verde | Media | ML Engineer | 3 | Hecho |
| PB-10 | Como PO, quiero saber si se puede mejorar más. | `GridSearchCV` sobre Random Forest | Se reporta si mejora o no en test | Baja | ML Engineer | 3 | Hecho |
| PB-11 | Como PO, quiero distinguir mejor SIRA/DERMASON y BARBUNYA/CALI. | Explorar variables de color/textura desde las imágenes | F1 de SIRA > 0,90 | Media | — | Futuro | Por hacer |
| PB-12 | Como operario, quiero revisar a mano los casos dudosos. | Umbral de confianza y cola de revisión manual | Granos con confianza < umbral se marcan | Media | — | Futuro | Por hacer |
