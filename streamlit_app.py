import streamlit as st

class Config:
    """Configuración de medidas y colores."""
    LINE_HEIGHT = 32  
    FONT_SIZE = 18
    BG_NOTAS = "#1E1E1E" # Gris Notas
    BG_LETRA = "#252A34" # Azul Letra
    TEXT_COLOR = "#FFFFFF" # Blanco puro para el texto
    ANCHO_VIRTUAL = "2500px"

class StyleEngine:
    """Gestiona el CSS inyectado con corrección de visibilidad."""
    @staticmethod
    def get_css():
        return f"""
        <style>
        /* 1. Forzar visibilidad y alineación en el área de texto */
        .stTextArea textarea {{
            line-height: {Config.LINE_HEIGHT}px !important;
            font-family: 'Courier New', monospace !important;
            font-size: {Config.FONT_SIZE}px !important;
            
            /* Corrección de Color: Forzamos blanco */
            color: {Config.TEXT_COLOR} !important;
            -webkit-text-fill-color: {Config.TEXT_COLOR} !important;
            
            /* Scroll lateral: Evitamos que el texto salte de línea */
            width: {Config.ANCHO_VIRTUAL} !important;
            white-space: pre !important;
            overflow-wrap: normal !important;

            /* Fondo rayado sincronizado */
            background-image: linear-gradient(
                {Config.BG_NOTAS} 50%, 
                {Config.BG_LETRA} 50%
            ) !important;
            background-size: {Config.ANCHO_VIRTUAL} {Config.LINE_HEIGHT * 2}px !important;
            background-attachment: local !important;
            background-position: 0 0 !important;
            
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            border: none !important;
            caret-color: white !important; /* Color del cursor */
        }}
        
        /* 2. Contenedor del scroll lateral */
        .stTextArea div[data-baseweb="textarea"] {{
            overflow-x: auto !important;
            background-color: {Config.BG_NOTAS} !important;
        }}

        /* 3. Ajuste del botón de carga */
        section[data-testid="stFileUploader"] label {{ display: none; }}
        </style>
        """

class MusicEditor:
    """Componente Editor orientado a objetos."""
    def __init__(self):
        if "content" not in st.session_state:
            st.session_state.content = ""
        st.markdown(StyleEngine.get_css(), unsafe_allow_html=True)

    def draw_uploader(self):
        file = st.file_uploader("Subir", type=['txt'], key="u_file", label_visibility="collapsed")
        if file:
            # Al subir, actualizamos el estado maestro
            st.session_state.content = file.read().decode("utf-8")

    def draw_editor(self):
        # Calcular líneas para altura dinámica
        lines = st.session_state.content.split("\n")
        calc_height = (len(lines) * Config.LINE_HEIGHT) + 40
        
        # El text_area debe estar vinculado a session_state.content
        st.session_state.content = st.text_area(
            label="Editor de Canciones",
            value=st.session_state.content,
            height=calc_height,
            key="main_editor_v2",
            label_visibility="collapsed"
        )

# --- APP EXECUTION ---
st.title("🎸 Editor Pro Sincronizado")
app = MusicEditor()

# Layout de botones superiores
c1, _ = st.columns([1, 3])
with c1:
    app.draw_uploader()

# Área del Editor
app.draw_editor()

# Botones inferiores
if st.button("🗑️ Limpiar Todo"):
    st.session_state.content = ""
    st.rerun()
