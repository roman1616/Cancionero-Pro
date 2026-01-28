import streamlit as st

class EditorSettings:
    """Configuración técnica de la interfaz."""
    LH = 32
    GRIS = "#1E1E1E"
    AZUL = "#252A34"
    BLANCO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleEngine:
    """Inyector de CSS con máxima prioridad (Brute Force)."""
    @staticmethod
    def inyectar():
        st.markdown(f"""
            <style>
            /* 1. VISIBILIDAD TOTAL: Forzamos el texto a ser blanco en todas las capas */
            textarea[data-testid="stTextArea"] {{
                color: {EditorSettings.BLANCO};
                -webkit-text-fill-color: {EditorSettings.BLANCO};
                filter: brightness(2); /* Realza el texto sobre fondos oscuros */
            }}

            /* 2. ESTRUCTURA: Scroll lateral y fondo sincronizado */
            div[data-baseweb="textarea"] {{
                background-color: {EditorSettings.GRIS} !important;
                overflow-x: auto !important;
                padding: 0 !important;
            }}

            textarea {{
                line-height: {EditorSettings.LH}px !important;
                font-family: 'Courier New', monospace !important;
                font-size: 18px !important;
                width: {EditorSettings.ANCHO} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;
                background-image: linear-gradient(
                    {EditorSettings.GRIS} 50%, 
                    {EditorSettings.AZUL} 50%
                ) !important;
                background-size: {EditorSettings.ANCHO} {EditorSettings.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                border: none !important;
                padding: 0px !important;
            }}

            /* Limpieza de interfaz del uploader */
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        if "txt" not in st.session_state:
            st.session_state.txt = ""
        StyleEngine.inyectar()

    def gestionar_archivo(self):
        # El uploader controla el estado
        f = st.file_uploader("Cargar", type=['txt'], key="u_file", label_visibility="collapsed")
        
        if f is not None:
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c
        else:
            # SI SE QUITA EL ARCHIVO, SE LIMPIA EL ÁREA
            if st.session_state.txt != "":
                st.session_state.txt = ""

    def mostrar_editor(self):
        n = len(st.session_state.txt.split("\n"))
        h = (n * EditorSettings.LH) + 32
        
        # Área de edición pura
        st.session_state.txt = st.text_area(
            "Editor",
            value=st.session_state.txt,
            height=h,
            key="area_edicion",
            label_visibility="collapsed"
        )

# --- EJECUCIÓN ---
st.title("🎸 Editor Musical 2026")
app = MusicEditorApp()
app.gestionar_archivo()
app.mostrar_editor()
