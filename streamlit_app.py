import streamlit as st

class Config:
    """Configuración Maestra de Sincronización."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E" # Gris
    COLOR_LETRA = "#16213E" # Azul
    BLANCO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleEngine:
    """Anula capas de Streamlit y fuerza visibilidad de fondo y texto."""
    @staticmethod
    def inyectar():
        st.markdown(f"""
            <style>
            /* 1. LIMPIEZA DE CAPAS INTERNAS: Quitamos todos los fondos de Streamlit */
            div[data-testid="stTextArea"], 
            div[data-testid="stTextArea"] > div, 
            div[data-baseweb="textarea"],
            div[data-baseweb="textarea"] > div {{
                background-color: transparent !important;
                background-image: none !important;
            }}

            /* 2. APLICACIÓN DEL RAYADO: En el nivel más profundo para que nada lo tape */
            div[data-baseweb="textarea"] {{
                background-color: {Config.COLOR_NOTAS} !important;
                background-image: linear-gradient(
                    {Config.COLOR_NOTAS} 50%, 
                    {Config.COLOR_LETRA} 50%
                ) !important;
                background-size: {Config.ANCHO} {Config.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
                border: 1px solid #444 !important;
            }}

            /* 3. VISIBILIDAD DEL TEXTO: Forzamos color y alineación */
            textarea {{
                color: {Config.BLANCO};
                -webkit-text-fill-color: {Config.BLANCO};
                caret-color: white !important;
                font-family: 'Courier New', Courier, monospace !important;
                font-size: 18px !important;
                line-height: {Config.LH}px !important;
                width: {Config.ANCHO} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;
                background: transparent !important;
                padding: 0px !important;
                border: none !important;
            }}

            /* Ocultar elementos del uploader */
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditor:
    def __init__(self):
        if "txt" not in st.session_state: st.session_state.txt = ""
        if "v" not in st.session_state: st.session_state.v = 0
        StyleEngine.inyectar()

    def gestionar_archivo(self):
        f = st.file_uploader("Cargar", type=['txt'], key="u_file", label_visibility="collapsed")
        # Si se carga archivo nuevo
        if f:
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c
                st.session_state.v += 1
                st.rerun()
        # ANTICIPACIÓN: Si se quita el archivo, limpieza total inmediata
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""
            st.session_state.v += 1
            st.rerun()

    def render(self):
        n = len(st.session_state.txt.split("\n"))
        h = (n * Config.LH) + 40
        # El widget usa una key dinámica para resetearse al limpiar
        st.session_state.txt = st.text_area(
            "Editor", value=st.session_state.txt, height=h,
            key=f"ed_{st.session_state.v}", label_visibility="collapsed"
        )

# --- EJECUCIÓN ---
st.title("🎸 Editor Pro Sincronizado")
app = MusicEditor()
app.gestionar_archivo()
app.render()
