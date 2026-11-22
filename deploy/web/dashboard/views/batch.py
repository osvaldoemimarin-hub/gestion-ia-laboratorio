"""Carga, validación y descarga del lote dentro de la sesión de Streamlit."""
import hashlib

import pandas as pd
import streamlit as st

from deploy.web.api.schemas import ModelInfo
from deploy.web.dashboard.api_client import APIClient, APIError
from deploy.web.dashboard.data import CSVError, prepare_csv, results_frame
from deploy.web.dashboard.features import EXAMPLE
from deploy.web.dashboard.settings import DashboardSettings


def render(client: APIClient, settings: DashboardSettings, info: ModelInfo) -> None:
    st.subheader("Clasifica un lote de granos")
    st.write(f"Carga un CSV UTF-8 separado por comas: hasta {settings.max_batch_size:,} filas y 2 MiB. Incluye las 16 variables; Class es opcional.")
    template = pd.DataFrame([EXAMPLE]).to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV de ejemplo", template, "ejemplo_frijol.csv", "text/csv", key="template_csv")
    uploaded = st.file_uploader("Archivo de medidas", type=["csv"], max_upload_size=2, key="batch_upload")
    if uploaded is None:
        st.session_state.pop("batch_result", None)
        return
    content = uploaded.getvalue()
    fingerprint = hashlib.sha256(content).hexdigest() + info.model_version
    previous = st.session_state.get("batch_result")
    if previous and previous[0] != fingerprint:
        st.session_state.pop("batch_result", None)
    try:
        batch = prepare_csv(content, settings, info.classes)
    except CSVError as exc:
        st.error(str(exc))
        return
    st.success(f"Archivo válido: {len(batch.original):,} granos listos para clasificar.")
    st.dataframe(batch.original.head(10), hide_index=True, width="stretch")
    if st.button("Clasificar lote", key="predict_batch", type="primary"):
        st.session_state.pop("batch_result", None)
        try:
            with st.spinner("Clasificando el lote…"):
                response = client.predict(batch.instances)
            st.session_state.batch_result = (fingerprint, results_frame(batch, response), response)
        except APIError as exc:
            st.error(str(exc))
    saved = st.session_state.get("batch_result")
    if saved:
        _, result, response = saved
        st.subheader("Resultados del lote")
        st.dataframe(result, hide_index=True, width="stretch")
        st.bar_chart(result["predicted_class"].value_counts().rename("Granos"))
        if "Class" in result:
            st.metric("Acierto en este archivo", f"{(result['Class'] == result['predicted_class']).mean():.1%}")
            st.caption("Comparación de esta sesión con las etiquetas aportadas en Class. No reemplaza la evaluación histórica.")
        st.download_button(
            "Descargar predicciones", result.to_csv(index=False).encode("utf-8-sig"),
            "predicciones_frijol.csv", "text/csv", key="download_predictions",
        )
        st.caption(f"Modelo: {response.model_version}. Probabilidades sin garantía de acierto. Los resultados se conservan en esta sesión.")
