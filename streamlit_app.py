import streamlit as st

class EditorConfig:
    """Configuración Maestra Blindada."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E" # Gris
    COLOR_LETRA = "#16213E" # Azul
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleEngine:
    """Anula capas de Streamlit y fuerza visibilidad de fondo y texto."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* 1. LIMPIEZA TOTAL: Forzamos transparencia en TODAS las capas internas */
            [data-testid="stTextArea"] div, 
            [data-testid="stTextArea"] textarea,
            div[data-baseweb="textarea"],
            div[data-baseweb="textarea"] > div {{
                background-color: transparent !important;
                background-image: none !important;
            }}

            /* 2. EL RAYADO: Se aplica al contenedor raíz que sí tiene el tamaño correcto */
            div[data-baseweb="textarea"] {{
                background-color: {EditorConfig.COLOR_NOTAS} !important;
                background-image: linear-gradient(
                    {EditorConfig.COLOR_NOTAS} 50%, 
                    {EditorConfig.COLOR_LETRA} 50%
                ) !important;
                background-size: {EditorConfig.ANCHO} {EditorConfig.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
                border: 1px solid #444 !important;
            }}

            /* 3. VISIBILIDAD DEL TEXTO */
            textarea {{
                color: {EditorConfig.TEXTO};
                -webkit-text-fill-color: {EditorConfig.TEXTO};
                caret-color: white !important;
                font-family: 'Courier New', monospace !important;
                font-size: 18px !important;
                line-height: {EditorConfig.LH}px !important;
                width: {EditorConfig.ANCHO} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;
                padding: 0px !important;
                border: none !important;
            }}
            
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        if "txt" not in st.session_state: st.session_state.txt = ""
        if "v" not in st.session_state: st.session_state.v = 0
        StyleEngine.aplicar()

    def gestionar_datos(self):
        f = st.file_uploader("Cargar", type=['txt'], key="u_file", label_visibility="collapsed")
        if f:
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c
                st.session_state.v += 1
                st.rerun()
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""
            st.session_state.v += 1
            st.rerun()

    def render(self):
        n = len(st.session_state.txt.split("\n"))
        h = (n * EditorConfig.LH) + 40
        # Usamos key dinámica para el reset total al borrar archivo
        st.session_state.txt = st.text_area(
            "Editor", value=st.session_state.txt, height=h,
            key=f"ed_{st.session_state.v}", label_visibility="collapsed"
        )

# --- INICIO ---
st.title("🎸 Editor Sincronizado 2026")
app = MusicEditorApp()
app.gestionar_datos()
app.render()
