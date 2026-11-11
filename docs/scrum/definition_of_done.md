# Definition of Done — verificación

Los nueve criterios del laboratorio proceden de `Lab1.pdf` (p. 16). Esta tabla conserva la verificación histórica del repositorio: los checks técnicos no acreditan envío académico, actas ni aceptación del equipo. En la revisión actual se comprobaron 28 celdas de código con contador de ejecución y sin salidas de error en el notebook guardado; esto no equivale a una nueva ejecución completa.

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| 1 | El notebook corre de inicio a fin sin errores | ✅ | `notebooks/01_laboratorio_drybean.ipynb` ejecutado con `nbconvert --execute`, 0 errores |
| 2 | El dataset se descarga o carga correctamente | ✅ | `fetch_ucirepo(id=602)` + respaldo `data/raw/Dry_Bean_Dataset.xlsx` |
| 3 | Se reportan valores nulos y duplicados | ✅ | Paso 5: 0 nulos, 68 duplicados |
| 4 | Baseline + modelo alternativo | ✅ | Logistic Regression y Random Forest (+ GridSearch) |
| 5 | Comparación con accuracy y F1 macro | ✅ | `outputs/reports/comparacion_modelos.csv`, `validacion_cruzada.csv` |
| 6 | Matriz de confusión | ✅ | `outputs/reports/figures/matrices_confusion.png` |
| 7 | Modelo final guardado | ✅ | `outputs/models/*.joblib` |
| 8 | Resultado explicado en lenguaje comprensible | ✅ | Conclusiones del notebook y `docs/reporte_final.md` |
| 9 | Relación con CRISP-DM, TDSP y Scrum ML documentada | ✅ | `README.md`, `docs/reporte_final.md`, `docs/scrum/` |
| + | Código reproducible y probado | ✅ | `python -m src.laboratorio_drybean`, `pytest` (5/5) |

## Extensión para despliegue web — verificación por incremento

Los criterios anteriores corresponden al laboratorio local. La extensión web y Azure son opcionales para esa entrega académica; sus criterios adicionales se registran aquí. La [ejecución local](../../README.md) y la [guía de Azure](../../deploy/azure/README.md) contienen las instrucciones vigentes.

La lista siguiente combina calidad técnica y pendientes de entrega/operación para facilitar seguimiento. No todos son criterios universales de Scrum: el equipo debe acordar cuáles integran la DoD de cada incremento. Una review o aceptación administrativa pendiente no es por sí sola una prohibición de publicación en Scrum; tampoco convierte una tarea con criterios de calidad incumplidos en Done. «Hecho técnico» es una etiqueta del repositorio.

| Criterio | Estado | Evidencia requerida |
|---|---|---|
| Artefacto de regresión logística trazable y compatible | Verificado local | `outputs/models/serving/`, versiones de inferencia fijadas en `requirements.txt`, manifiesto y prueba de carga sin incompatibilidades |
| Contrato HTTP validado y paridad de inferencia | Verificado local | OpenAPI y `tests/test_api.py`: 2.709 filas, tolerancia `1e-12`, orden de claves invertido |
| Entradas inválidas y límites controlados | Verificado local | `tests/test_api.py`: esquema, NaN, infinitos, lotes y bytes, también fragmentados |
| Dashboard individual y por CSV | Comprobado localmente | AppTest recorrió formulario y CSV contra la API; las pruebas persistentes `test_dashboard_*` se retiraron. La aceptación visual del equipo sigue pendiente |
| Contenedores reproducibles | Verificado localmente en la nueva estructura | Se construyeron ambas imágenes; `pip check`, Compose y sondas saludables. Dashboard HTTP 200 y API interna con la versión esperada del modelo |
| Azure accesible con topología prevista | Verificado | [Guía y digests](../../deploy/azure/README.md): HTTPS 200, WebSocket y predicción SEKER; dashboard público y API interna. Estructura actual publicada el 11/11/2026, revisión `r20261111024909-43fca417` |
| Operación y reversión documentadas y verificadas | Pendiente | Logs, métricas de servicio, reinicio y reversión en el destino elegido |
| Guía alternativa de VM | Pendiente | Configuración por digest, proxy y procedimiento; identificar si se ejecutó |
| Evidencia Scrum del incremento | Pendiente | Tablero actualizado, review y retrospectiva basadas en resultados reales |

Tras retirar las pruebas del dashboard y de autenticación del registro quedaron **43 pruebas automatizadas** (5 del pipeline original y 38 de la API). La cobertura retirada debe recuperarse o sustituirse por evidencia de validación al actualizar la aplicación; la comprobación de un único caso no equivale a cobertura de errores y límites.
