"""Pipeline completo del laboratorio Dry Bean (CRISP-DM de extremo a extremo).

Ejecutar desde la raíz del repositorio:
    python -m src.laboratorio_drybean            # pipeline principal
    python -m src.laboratorio_drybean --extras   # + validación cruzada y GridSearchCV
"""
from __future__ import annotations

import argparse
import json

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score

from src import config
from src.data import clean_data, load_data, quality_report, split_data
from src.evaluate import compute_metrics, report_df, save_confusion_matrix, top_confusions
from src.models import build_baseline, build_forest
from src.predict import load_model, predict_bean_class


def run(extras: bool = False) -> dict:
    config.ensure_dirs()

    # --- Fase 2: comprensión de los datos ---------------------------------
    df = load_data()
    print(f"Fuente: {df.attrs.get('source')}")
    quality = quality_report(df)
    print(f"Shape: {df.shape} | nulos: {quality['nulos_totales']} | duplicados: {quality['duplicados']}")

    fig, ax = plt.subplots(figsize=(8, 5))
    df[config.TARGET].value_counts().plot(kind="bar", ax=ax, color="#2b6cb0")
    ax.set_title("Distribución de clases")
    ax.set_xlabel("Clase de frijol")
    ax.set_ylabel("Cantidad de registros")
    plt.setp(ax.get_xticklabels(), rotation=45)
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / "distribucion_clases.png", dpi=120)
    plt.close(fig)

    # --- Fase 3: preparación ----------------------------------------------
    df = clean_data(df)
    X_train, X_test, y_train, y_test = split_data(df)
    print(f"Tras limpieza: {df.shape} | train={len(X_train)} test={len(X_test)}")

    # --- Fase 4: modelado -------------------------------------------------
    baseline = build_baseline().fit(X_train, y_train)
    forest = build_forest().fit(X_train, y_train)

    # --- Fase 5: evaluación -----------------------------------------------
    y_pred_base = baseline.predict(X_test)
    y_pred_rf = forest.predict(X_test)
    m_base = compute_metrics(y_test, y_pred_base)
    m_rf = compute_metrics(y_test, y_pred_rf)

    results = pd.DataFrame({
        "modelo": ["Logistic Regression", "Random Forest"],
        "accuracy": [m_base["accuracy"], m_rf["accuracy"]],
        "f1_macro": [m_base["f1_macro"], m_rf["f1_macro"]],
    })
    results.to_csv(config.REPORTS_DIR / "comparacion_modelos.csv", index=False)
    print(results.round(4).to_string(index=False))

    report_df(y_test, y_pred_base).round(4).to_csv(config.REPORTS_DIR / "classification_report_baseline.csv")
    report_df(y_test, y_pred_rf).round(4).to_csv(config.REPORTS_DIR / "classification_report_random_forest.csv")
    save_confusion_matrix(y_test, y_pred_base, "Matriz de confusión - Logistic Regression",
                          config.FIGURES_DIR / "matriz_confusion_baseline.png")
    save_confusion_matrix(y_test, y_pred_rf, "Matriz de confusión - Random Forest",
                          config.FIGURES_DIR / "matriz_confusion_random_forest.png")
    top_confusions(y_test, y_pred_rf).to_csv(config.REPORTS_DIR / "top_confusiones_rf.csv", index=False)

    importance = (
        pd.DataFrame({"feature": X_train.columns, "importance": forest.feature_importances_})
        .sort_values("importance", ascending=False)
    )
    importance.to_csv(config.REPORTS_DIR / "importancia_variables.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    importance.head(10).plot(x="feature", y="importance", kind="bar", ax=ax, legend=False, color="#2f855a")
    ax.set_title("Top 10 variables más importantes")
    ax.set_xlabel("Variable")
    ax.set_ylabel("Importancia")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / "importancia_variables.png", dpi=120)
    plt.close(fig)

    # Opción C: archivo de predicciones
    predictions = X_test.copy()
    predictions["real_class"] = y_test.values
    predictions["predicted_class"] = y_pred_rf
    predictions.to_csv(config.REPORTS_DIR / "predicciones_drybean.csv", index=False)

    # --- Fase 6: despliegue -----------------------------------------------
    joblib.dump(forest, config.MODEL_PATH, compress=3)
    joblib.dump(baseline, config.BASELINE_PATH)
    loaded = load_model()
    sample = X_test.iloc[[0]]
    print(f"Predicción de prueba: {predict_bean_class(loaded, sample)} | real: {y_test.iloc[0]}")

    summary = {
        "fuente": df.attrs.get("source", ""),
        "calidad": {k: v for k, v in quality.items() if k != "nulos_por_columna"},
        "filas_limpias": int(df.shape[0]),
        "train": len(X_train),
        "test": len(X_test),
        "metricas": {"logistic_regression": m_base, "random_forest": m_rf},
    }

    if extras:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_STATE)
        X_all, y_all = df.drop(columns=config.TARGET), df[config.TARGET]
        cv_res = {}
        for name, model in (("logistic_regression", build_baseline()), ("random_forest", build_forest())):
            scores = cross_val_score(model, X_all, y_all, cv=cv, scoring="f1_macro", n_jobs=-1)
            cv_res[name] = {"f1_macro_mean": scores.mean(), "f1_macro_std": scores.std()}
            print(f"CV f1_macro {name}: {scores.mean():.4f} ± {scores.std():.4f}")
        summary["cross_validation"] = cv_res

        grid = GridSearchCV(
            build_forest(),
            param_grid={
                "n_estimators": [100, 200, 300],
                "max_depth": [None, 15, 25],
                "min_samples_split": [2, 5, 10],
            },
            scoring="f1_macro",
            cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=config.RANDOM_STATE),
            n_jobs=-1,
        ).fit(X_train, y_train)
        m_grid = compute_metrics(y_test, grid.best_estimator_.predict(X_test))
        summary["grid_search"] = {
            "best_params": grid.best_params_,
            "best_cv_f1_macro": grid.best_score_,
            "test": m_grid,
        }
        print(f"GridSearch best={grid.best_params_} test f1_macro={m_grid['f1_macro']:.4f}")

    with open(config.REPORTS_DIR / "metricas.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2, default=float)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extras", action="store_true", help="Validación cruzada y GridSearchCV")
    run(extras=parser.parse_args().extras)
