import json
import os
import urllib.request

import streamlit as st

AGENT_ID = "agent-84759f0c-8215-4ce0-8a0e-1d899ae1e372"  # Consejero Político GT
API_URL = f"https://api.letta.com/v1/agents/{AGENT_ID}/messages"


def obtener_api_key():
    """La key vive en los Secrets de Streamlit Cloud o en una variable de entorno.
    Nunca se pega en el codigo."""
    try:
        return st.secrets["LETTA_API_KEY"]
    except Exception:
        return os.environ.get("LETTA_API_KEY")


def preguntar(texto, api_key):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({"input": texto}).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "consejero-gt-streamlit",  # Cloudflare bloquea el UA por defecto de Python
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    for m in data["messages"]:
        if m["message_type"] == "assistant_message":
            return m["content"]
    return "El agente no devolvio respuesta."


st.set_page_config(page_title="Consejero Politico GT", page_icon=":classical_building:", layout="centered")

st.title("🏛️ Consejero Político GT")

st.markdown(
    """
**¿Qué es esta app?** Es una ventana directa a un **asesor de IA especializado en la
política partidista de Guatemala**: el Tribunal Supremo Electoral (TSE), la Ley
Electoral y de Partidos Políticos (LEPP), la organización del Congreso y el ciclo
electoral 2027.

El cerebro detrás es un agente con memoria propia, creado en la plataforma
[Letta](https://letta.com). Tú escribes la pregunta; la app se la envía al agente
por su API y te devuelve la respuesta.
"""
)

with st.expander("Ejemplos de preguntas"):
    st.markdown(
        """
- ¿Qué requisitos pide la LEPP para inscribir un nuevo partido político?
- ¿Cuántos afiliados necesita un comité cívico para convertirse en partido?
- ¿Qué plazos del TSE aplican para la convocatoria a elecciones generales?
"""
    )

api_key = obtener_api_key()
if not api_key:
    st.warning("Falta configurar la API key de Letta (LETTA_API_KEY).")
    api_key = st.text_input("Pégala aquí para probar (no se guarda)", type="password")

pregunta = st.text_area(
    "Tu pregunta",
    placeholder="Escribe aquí tu consulta sobre política guatemalteca…",
    height=120,
)

if st.button("Preguntar al Consejero", type="primary", disabled=not api_key):
    if not pregunta.strip():
        st.warning("Escribe una pregunta primero.")
    else:
        with st.spinner("Consultando al Consejero…"):
            try:
                respuesta = preguntar(pregunta.strip(), api_key)
            except Exception as e:
                st.error(f"Error al consultar la API: {e}")
                st.stop()
        st.divider()
        st.subheader("Respuesta del Consejero")
        st.markdown(respuesta)
