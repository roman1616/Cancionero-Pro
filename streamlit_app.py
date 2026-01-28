import streamlit as st

class EditorConfig:
    """Configuración Maestra."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E" # Gris
    COLOR_LETRA = "#16213E" # Azul Profundo
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleManager:
    """Fuerza el coloreado de renglones y la visibilidad del texto."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* 1. VISIBILIDAD DEL TEXTO: Forzamos el color blanco */
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
                background: transparent !important;
                padding: 0px !important;
                border: none !important;
            }}

            /* 2. FORZAR COLOREADO DE RENGLONES */
            /* Atacamos el contenedor de control de Streamlit que suele tapar todo */
            div[data-baseweb="textarea"], div[data-testid="stTextArea"] > div {{
                background-color: {EditorConfig.COLOR_NOTAS} !important;
                background-image: linear-gradient(
                    {EditorConfig.COLOR_NOTAS} 50%, 
                    {EditorConfig.COLOR_LETRA} 50%
                ) !important;
                background-size: {EditorConfig.ANCHO} {EditorConfig.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
            }}

            /* 3. LIMPIEZA DE BORDES Y SOMBRAS */
            div[data-baseweb="textarea"] {{
                border: 1px solid #444 !important;
            }}
            
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        if "texto" not in st.session_state:
            st.session_state.texto = ""
        if "ver" not in st.session_state:
            st.session_state.ver = 0
        StyleManager.aplicar()

    def sync(self):
        """Sincroniza el cargador con el editor y limpia al cerrar."""
        f = st.file_uploader("Subir", type=['txt'], key="u_file", label_visibility="collapsed")
        if f:
            c = f.read().decode("utf-8")
            if st.session_state.texto != c:
                st.session_state.texto = c
                st.session_state.ver += 1
                st.rerun()
        elif st.session_state.texto != "" and f is None:
            st.session_state.texto = ""
            st.session_state.ver += 1
            st.rerun()

    def render(self):
        """Dibuja el editor con key dinámica."""
        n = len(st.session_state.texto.split("\n"))
        h = (n * EditorConfig.LH) + 40
        
        st.session_state.texto = st.text_area(
            "Editor",
            value=st.session_state.texto,
            height=h,
            key=f"ed_{st.session_state.ver}",
            label_visibility="collapsed"
        )

# --- APP ---
st.title("🎸 Editor Pro Sincronizado")
app = MusicEditorApp()
app.sync()
app.render()
