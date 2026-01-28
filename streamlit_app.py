import streamlit as st

class EditorConfig:
    """Configuración única para evitar discrepancias."""
    LH = 32
    GRIS = "#1E1E1E"
    AZUL = "#252A34"
    TEXTO_HEX = "#FFFFFF"
    ANCHO = "2500px"

class StyleEngine:
    """Anula absolutamente todos los estilos internos de Streamlit."""
    @staticmethod
    def aplicar():
        # Atacamos incluso las clases internas dinámicas (.st-ae, .st-af, etc.)
        st.markdown(f"""
            <style>
            /* 1. BLINDAJE TOTAL DE VISIBILIDAD */
            div[data-baseweb="textarea"] textarea {{
                color: {EditorConfig.TEXTO_HEX} !important;
                -webkit-text-fill-color: {EditorConfig.TEXTO_HEX} !important;
                fill: {EditorConfig.TEXTO_HEX} !important;
                opacity: 1 !important;
                caret-color: white !important;
                -webkit-opacity: 1 !important;
            }}

            /* 2. ELIMINAR CAPAS INTERNAS QUE OCULTAN EL TEXTO */
            div[data-baseweb="textarea"] div {{
                background-color: transparent !important;
            }}

            /* 3. CONTENEDOR Y RAYADO (Sincronización de líneas) */
            div[data-baseweb="textarea"] {{
                background-color: {EditorConfig.GRIS} !important;
                background-image: linear-gradient(
                    {EditorConfig.GRIS} 50%, 
                    {EditorSettings.AZUL if 'EditorSettings' in globals() else EditorConfig.AZUL} 50%
                ) !important;
                background-size: {EditorConfig.ANCHO} {EditorConfig.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
                padding: 0 !important;
                border: 1px solid #444 !important;
            }}

            /* 4. ESTRUCTURA PARA SCROLL */
            textarea {{
                line-height: {EditorConfig.LH}px !important;
                font-family: 'Courier New', monospace !important;
                font-size: 18px !important;
                width: {EditorConfig.ANCHO} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;
                padding: 0px !important;
            }}
            
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditor:
    def __init__(self):
        if "content" not in st.session_state:
            st.session_state.content = ""
        StyleEngine.aplicar()

    def sync_data(self):
        # Cargador
        f = st.file_uploader("Subir", type=['txt'], key="u_file", label_visibility="collapsed")
        
        # Lógica de limpieza y carga anticipada
        if f:
            new = f.read().decode("utf-8")
            if st.session_state.content != new:
                st.session_state.content = new
                st.rerun()
        elif st.session_state.content != "" and f is None:
            # Si el uploader se vacía, borramos el editor
            st.session_state.content = ""
            st.rerun()

    def draw(self):
        n = len(st.session_state.content.split("\n"))
        h = (n * EditorConfig.LH) + 40
        
        # Renderizado
        st.session_state.content = st.text_area(
            "Editor",
            value=st.session_state.content,
            height=h,
            key="v_editor",
            label_visibility="collapsed"
        )

# --- START ---
st.title("🎸 Editor Sincronizado 2026")
app = MusicEditor()
app.sync_data()
app.draw()

