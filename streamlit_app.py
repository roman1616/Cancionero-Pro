import streamlit as st

class Config:
    """Configuración de estilos y sincronización."""
    LINE_HEIGHT = 32
    BG_NOTAS = "#1E1E1E"
    BG_LETRA = "#252A34"
    TEXT_COLOR = "#FFFFFF"
    ANCHO_VIRTUAL = "2500px"

class StyleEngine:
    """Motor CSS con alta especificidad para visibilidad y alineación."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* Reset del contenedor */
            div[data-baseweb="textarea"] {{
                background-color: {Config.BG_NOTAS} !important;
                border: 1px solid #444 !important;
                padding: 0 !important;
            }}

            /* Forzar visibilidad del texto y fondo sincronizado */
            .stTextArea textarea {{
                color: {Config.TEXT_COLOR} !important;
                -webkit-text-fill-color: {Config.TEXT_COLOR} !important;
                font-family: 'Courier New', monospace !important;
                font-size: 18px !important;
                line-height: {Config.LINE_HEIGHT}px !important;
                padding: 0px !important;
                width: {Config.ANCHO_VIRTUAL} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;
                background-image: linear-gradient(
                    {Config.BG_NOTAS} 50%, 
                    {Config.BG_LETRA} 50%
                ) !important;
                background-size: {Config.ANCHO_VIRTUAL} {Config.LINE_HEIGHT * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                border: none !important;
                caret-color: white !important;
            }}
            
            /* Ocultar etiquetas del uploader */
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditor:
    def __init__(self):
        # Inicializamos vacío para que no aparezca información al inicio
        if "content" not in st.session_state:
            st.session_state.content = ""
        StyleEngine.aplicar()

    def handle_file_logic(self):
        """Gestiona la carga y el borrado automático al quitar el archivo."""
        uploaded_file = st.file_uploader("Cargar", type=['txt'], key="u_file", label_visibility="collapsed")
        
        if uploaded_file is not None:
            # Solo actualizamos si el contenido es distinto (evita bucles)
            new_content = uploaded_file.read().decode("utf-8")
            if st.session_state.content != new_content:
                st.session_state.content = new_content
        else:
            # Si el cargador está vacío, borramos el contenido del editor
            if st.session_state.content != "":
                st.session_state.content = ""

    def render_editor(self):
        """Renderiza el área de edición con altura dinámica."""
        lines = st.session_state.content.split("\n")
        calc_height = (len(lines) * Config.LINE_HEIGHT) + 32
        
        # El área aparece vacía por defecto
        st.session_state.content = st.text_area(
            label="Editor",
            value=st.session_state.content,
            height=calc_height,
            key="main_editor_poo",
            label_visibility="collapsed"
        )

# --- EJECUCIÓN PRINCIPAL ---
st.title("🎸 Editor Pro Sincronizado")
app = MusicEditor()

app.handle_file_logic()
app.render_editor()

if st.button("🗑️ Limpiar Manual"):
    st.session_state.content = ""
    st.rerun()
