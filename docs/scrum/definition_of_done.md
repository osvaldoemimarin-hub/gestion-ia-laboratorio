# Definition of Done — verificación

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
