"""Formulario de un grano y presentación de su predicción."""
import pandas as pd
from pydantic import ValidationError
import streamlit as st

from deploy.web.dashboard.api_client import APIClient, APIError
from deploy.web.dashboard.features import EXAMPLE, LABELS, SIZE_FIELDS
from deploy.web.api.schemas import BeanFeatures, ModelInfo


def render(client: APIClient, info: ModelInfo) -> None:
    st.subheader("De las medidas a la variedad")
    st.write("Ingresa las características geométricas extraídas del grano, conservando su escala original.")
    st.caption("Los valores iniciales son una muestra del conjunto de test, disponibles como ejemplo de uso.")
    if st.button("Restablecer ejemplo", key="reset_example"):
        for name, value in EXAMPLE.items():
            st.session_state[f"feature_{name}"] = float(value)
        st.session_state.pop("single_result", None)
    with st.form("single_form"):
        size, shape = st.columns(2, gap="large")
        values = {}
        for column, title, is_size in ((size, "Tamaño", True), (shape, "Forma", False)):
            with column:
                st.markdown(f"**{title}**")
                for name in info.features:
                    if (name in SIZE_FIELDS) != is_size:
                        continue
                    values[name] = st.number_input(
                        LABELS[name], value=float(EXAMPLE[name]), format="%.10f",
                        key=f"feature_{name}", help=f"Variable: {name}. Usa el valor original, sin estandarizar.",
                    )
        submitted = st.form_submit_button("Clasificar grano", type="primary")
    if submitted:
        st.session_state.pop("single_result", None)
        try:
            features = BeanFeatures.model_validate(values)
            with st.spinner("Clasificando el grano…"):
                response = client.predict([features.model_dump()])
            st.session_state.single_result = response
        except ValidationError as exc:
            fields = ", ".join(LABELS[error["loc"][0]] for error in exc.errors())
            st.error(f"Revisa {fields}. Se requieren medidas finitas dentro de su dominio.")
        except APIError as exc:
            st.error(str(exc))
    response = st.session_state.get("single_result")
    if response:
        st.divider()
        st.subheader("Última predicción enviada")
        result = response.predictions[0]
        left, right = st.columns(2)
        left.metric("Variedad predicha", result.predicted_class)
        right.metric("Probabilidad del modelo", f"{result.confidence:.1%}")
        probabilities = pd.DataFrame.from_dict(result.probabilities, orient="index", columns=["Probabilidad"])
        st.bar_chart(probabilities.sort_values("Probabilidad", ascending=False))
        st.caption(f"Versión: {response.model_version}. La probabilidad no garantiza que la clasificación sea correcta.")
