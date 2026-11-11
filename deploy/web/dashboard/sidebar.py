"""Identidad del proyecto, estado del modelo e integrantes de la barra lateral."""
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

TEAM_MEMBERS = (
    "Osvaldo Emilio Marin",
    "Nilson Jacobo Gonzales",
    "Edgar Adrián Ortiz",
    "Juan Andres Ruiz",
)


def render() -> DeltaGenerator:
    """Reserva el estado del modelo antes del equipo, incluso si falla la conexión."""
    with st.sidebar:
        st.markdown("### Dry Bean")
        st.write("Universidad Autónoma de Occidente")
        st.caption("CRISP-DM · TDSP · Scrum ML")
        st.divider()
        st.write("16 características · 7 variedades")
        st.caption("BARBUNYA · BOMBAY · CALI · DERMASON · HOROZ · SEKER · SIRA")
        model_status = st.container()
        st.divider()
        st.markdown("**Equipo del proyecto**")
        st.caption("  \n".join(TEAM_MEMBERS))
    return model_status
