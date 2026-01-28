import streamlit as st

class Config:
    """Configuración única de medidas para sincronización total."""
    LINE_HEIGHT = 32  # Altura exacta de cada renglón en píxeles
    FONT_SIZE = 18
    BG_NOTAS = "#1E1E1E" # Gris
    BG_LETRA = "#252A34" # Azul oscuro
    TEXT_COLOR = "#FFFFFF"
    ANCHO_VIRTUAL = "2800px" # Espacio para scroll lateral sin cortes

class StyleEngine:
    """Gestiona el CSS inyectado garantizando la alineación."""
    @staticmethod
    def get_css():
        # El background-size debe ser exactamente el doble del LINE_HEIGHT (64px)
        # para cubrir un ciclo completo de (Notas + Letra).
        return f"""
        <style>
        .stTextArea textarea {{
            line-height: {Config.LINE_HEIGHT}px !important;
            font-family: 'Courier New', monospace !important;
            font-size: {Config.FONT_SIZE}px !important;
            color: {Config.TEXT_COLOR} !important;
            -webkit-text-fill-color: {Config.TEXT_COLOR} !important;
            
            /* Ajuste de scroll y ancho */
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
            
            /* Reset de paddings para evitar desfases */
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            border: none !important;
        }}
        
        /* Contenedor del scroll lateral con sombras de la Opción 3 */
        .stTextArea div[data-baseweb="textarea"] {{
            overflow-x: auto !important;
            background: 
                linear-gradient(to right, {Config.BG_NOTAS} 30%, rgba(0,0,0,0)),
                linear-gradient(to right, rgba(0,0,0,0), {Config.BG_NOTAS} 70%) 100% 0,
                radial-gradient(farthest-side at 100% 50%, rgba(0,0,0,.5), rgba(0,0,0,0)) 100% 0 !important;
            background-repeat: no-repeat !important;
            background-size: 40px 100%, 40px 100%, 14px 100% !important;
            background-attachment: local, local, scroll !important;
        }}
        </style>
        """

class MusicEditor:
    """Componente Editor orientado a objetos."""
    def __init__(self):
        if "content" not in st.session_state:
            st.session_state.content = ""
        st.markdown(StyleEngine.get_css(), unsafe_allow_html=True)

    def draw_uploader(self):
        # Botón de carga minimalista
        file = st.file_uploader("Subir", type=['txt'], key="u_file", label_visibility="collapsed")
        if file:
            st.session_state.content = file.read().decode("utf-8")

    def draw_editor(self):
        lines = st.session_state.content.split("\n")
        # Calculamos la altura exacta: número de líneas * LINE_HEIGHT
        calc_height = (len(lines) * Config.LINE_HEIGHT) + 20
        
        st.session_state.content = st.text_area(
            label="Editor",
            value=st.session_state.content,
            height=calc_height,
            key="main_editor",
            label_visibility="collapsed"
        )

# --- APP MAIN ---
st.title("🎸 Editor Pro Sincronizado")
editor = MusicEditor()

col_file, _ = st.columns([1, 3])
with col_file:
    editor.draw_uploader()

editor.draw_editor()

if st.button("🗑️ Limpiar"):
    st.session_state.content = ""
    st.rerun()
