"""Evaluación histórica del modelo que responde a la API."""
import pandas as pd
import streamlit as st

from deploy.web.api.schemas import ModelInfo


def render(info: ModelInfo) -> None:
    st.subheader("Evaluación del modelo activo")
    st.write("Resultados históricos sobre el conjunto de prueba reservado durante el entrenamiento.")
    st.caption("Estas métricas no miden la calidad de las predicciones que se están recibiendo en vivo.")
    first, second, third = st.columns(3)
    first.metric("Accuracy en test", f"{info.metrics['accuracy']:.2%}")
    second.metric("F1 macro en test", f"{info.metrics['f1_macro']:.4f}")
    third.metric("Granos de prueba", f"{info.evaluation['rows']:,}")
    st.write(f"**Algoritmo:** {info.algorithm}")
    st.caption(f"Versión: {info.model_version} · {info.evaluation['source']}")
    report = info.evaluation.get("classification_report", {})
    rows = {name: report[name] for name in info.classes if name in report}
    if rows:
        st.markdown("**Desempeño por variedad**")
        st.dataframe(pd.DataFrame.from_dict(rows, orient="index").round(4), width="stretch")
    matrix = info.evaluation.get("confusion_matrix")
    if matrix is not None:
        st.markdown("**Matriz de confusión**")
        st.caption("Filas: variedad real. Columnas: variedad predicha. La diagonal contiene los aciertos.")
        frame = pd.DataFrame(matrix, index=info.classes, columns=info.classes)
        maximum = max(max(row) for row in matrix) or 1
        styled = frame.style.map(lambda value: f"background-color: rgba(40,115,76,{0.1 + 0.5 * value / maximum:.3f})")
        st.dataframe(styled, width="stretch")
    st.info("Las confusiones más frecuentes del laboratorio aparecen entre SIRA y DERMASON. El modelo utiliza tamaño y forma; no analiza color, textura ni fotografías.")
