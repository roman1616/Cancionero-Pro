import streamlit as st

class EditorConfig:
    """Encapsula la configuración visual y constantes."""
    BG_NOTAS = "#1E1E1E"
    BG_LETRA = "#252A34"
    TEXT_COLOR = "#FFFFFF"
    LINE_HEIGHT = 32
    ANCHO_VIRTUAL = "2500px"
    CONVERSION = {
        "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B",
        "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#"
    }

class MusicProcessor:
    """Lógica pura de procesamiento de texto."""
    @staticmethod
    def transformar_linea(linea, es_nota):
        if es_nota:
            return "   ".join([EditorConfig.CONVERSION.get(p.upper(), p) for p in linea.split()])
        return linea

    @classmethod
    def procesar_texto_completo(cls, texto):
        lineas = texto.split('\n')
        return [cls.transformar_linea(l, (i % 2 == 0)) for i, l in enumerate(lineas)]

class UIStyleManager:
    """Gestiona exclusivamente el CSS inyectado."""
    @staticmethod
    def aplicar_estilos():
        st.markdown(f"""
            <style>
            /* Contenedor con Scroll y Sombra Inteligente */
            .stTextArea div[data-baseweb="textarea"] {{
                overflow-x: auto !important;
                background: 
                    linear-gradient(to right, {EditorConfig.BG_NOTAS} 30%, rgba(0,0,0,0)),
                    linear-gradient(to right, rgba(0,0,0,0), {EditorConfig.BG_NOTAS} 70%) 100% 0,
                    radial-gradient(farthest-side at 100% 50%, rgba(0,0,0,.5), rgba(0,0,0,0)) 100% 0 !important;
                background-repeat: no-repeat !important;
                background-size: 40px 100%, 40px 100%, 14px 100% !important;
                background-attachment: local, local, scroll !important;
            }}
            .stTextArea textarea {{
                line-height: {EditorConfig.LINE_HEIGHT}px !important; 
                font-family: 'Courier New', monospace !important;
                font-size: 18px !important;
                color: {EditorConfig.TEXT_COLOR} !important;
                width: {EditorConfig.ANCHO_VIRTUAL} !important; 
                white-space: pre !important;
                background-image: linear-gradient({EditorConfig.BG_NOTAS} 50%, {EditorConfig.BG_LETRA} 50%) !important;
                background-size: {EditorConfig.ANCHO_VIRTUAL} {EditorConfig.LINE_HEIGHT * 2}px !important; 
                background-attachment: local !important;
                border: none !important;
            }}
            /* Ocultar elementos innecesarios del uploader para que parezca un botón */
            section[data-testid="stFileUploader"] label, 
            section[data-testid="stFileUploader"] div[data-testid="stWebSidebar"] {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    """Clase principal que orquestra la aplicación."""
    def __init__(self):
        if "texto_maestro" not in st.session_state:
            st.session_state.texto_maestro = ""
        UIStyleManager.aplicar_estilos()

    def render_uploader(self):
        archivo = st.file_uploader("Subir", type=["txt"], key="u_key", label_visibility="collapsed")
        if archivo:
            st.session_state.texto_maestro = archivo.read().decode("utf-8")

    def render_editor(self):
        n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
        altura = (n_lineas * EditorConfig.LINE_HEIGHT) + 20
        st.session_state.texto_maestro = st.text_area(
            "Editor", value=st.session_state.texto_maestro, 
            height=altura, key="editor_v1", label_visibility="collapsed"
        )

    def render_controls(self):
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        if col2.button("🗑️ Limpiar", use_container_width=True):
            st.session_state.texto_maestro = ""
            st.rerun()

        if st.session_state.texto_maestro:
            resultado = MusicProcessor.procesar_texto_completo(st.session_state.texto_maestro)
            texto_descarga = "\n".join(resultado)
            col3.download_button("💾 Descargar", texto_descarga, "cancion.txt", use_container_width=True)

# --- EJECUCIÓN ---
app = MusicEditorApp()
st.title("🎸 Editor Transpositor POO")
app.render_uploader()
app.render_editor()
app.render_controls()
