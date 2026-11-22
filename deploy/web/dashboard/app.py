"""Coordina las vistas del dashboard y su conexión con FastAPI."""
import streamlit as st

from deploy.web.dashboard.api_client import APIClient, APIError
from deploy.web.dashboard.settings import DashboardSettings
from deploy.web.dashboard import sidebar
from deploy.web.dashboard.views import batch, evaluation, individual


def main() -> None:
    st.set_page_config(page_title="Dry Bean · Clasificación", page_icon="🌱", layout="wide")
    render_header()
    model_status = sidebar.render()
    try:
        settings = DashboardSettings.from_env()
        client = APIClient(settings)
        info = client.get_model()
    except (APIError, ValueError) as exc:
        st.error(str(exc))
        st.button("Reintentar conexión", key="retry_connection")
        return
    with model_status:
        st.success("Modelo disponible")
        st.caption(info.model_version)
    individual_tab, batch_tab, evaluation_tab = st.tabs(["Un grano", "Archivo CSV", "Modelo y evaluación"])
    with individual_tab:
        individual.render(client, info)
    with batch_tab:
        batch.render(client, settings, info)
    with evaluation_tab:
        evaluation.render(info)


def render_header() -> None:
    st.caption("LABORATORIO DE IA · CONTROL DE CALIDAD AGRÍCOLA")
    st.title("Clasificación de frijol seco")
    st.write("Identifica una de siete variedades a partir de las medidas geométricas del grano.")
