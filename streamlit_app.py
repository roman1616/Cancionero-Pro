import streamlit as st

class EditorConfig:
    """Configuración maestra: Ajustes de color y medidas."""
    LH = 32
    # Colores de renglones: Gris (Notas), Azul (Letra)
    COLOR_NOTAS = "#1E1E1E" 
    COLOR_LETRA = "#1A2A40" # Un azul oscuro profundo para diferenciar
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleManager:
    """Gestiona el rayado de fondo y la visibilidad del texto."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* 1. VISIBILIDAD DEL TEXTO */
            [data-testid="stTextArea"] textarea {{
                color: {EditorConfig.TEXTO};
                -webkit-text-fill-color: {EditorConfig.TEXTO};
                caret-color: white !important;
                font-family: 'Courier New', monospace !important;
                font-size: 18px !important;
                line-height: {EditorConfig.LH}px !important;
                width: {EditorConfig.ANCHO} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;
                background: transparent !important; /* Texto sobre el fondo del div */
                padding: 0px !important;
                z-index: 2;
            }}

            /* 2. COLOREADO DE RENGLONES (Sincronización milimétrica) */
            div[data-baseweb="textarea"] {{
                background-color: {EditorConfig.COLOR_NOTAS} !important;
                background-image: linear-gradient(
                    {EditorConfig.COLOR_NOTAS} 50%, 
                    {EditorConfig.COLOR_LETRA} 50%
                ) !important;
                /* El tamaño del fondo debe ser el DOBLE del line-height (64px) */
                background-size: {EditorConfig.ANCHO} {EditorConfig.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
                border: 1px solid #444 !important;
                padding: 0 !important;
            }}

            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        if "texto_maestro" not in st.session_state:
            st.session_state.texto_maestro = ""
        if "editor_version" not in st.session_state:
            st.session_state.editor_version = 0
        StyleManager.aplicar()

    def gestionar_archivo(self):
        """Maneja carga y limpieza automática con refresco de versión."""
        archivo = st.file_uploader("Subir", type=['txt'], key="u_file", label_visibility="collapsed")
        
        if archivo is not None:
            contenido = archivo.read().decode("utf-8")
            if st.session_state.texto_maestro != contenido:
                st.session_state.texto_maestro = contenido
                st.session_state.editor_version += 1
                st.rerun()
        else:
            if st.session_state.texto_maestro != "":
                st.session_state.texto_maestro = ""
                st.session_state.editor_version += 1
                st.rerun()

    def mostrar_editor(self):
        """Dibuja el editor con key dinámica para limpieza total."""
        n_lineas = len(st.session_state.texto_maestro.split("\n"))
        # Altura dinámica: líneas * LH + margen de seguridad
        altura = (n_lineas * EditorConfig.LH) + 40
        
        st.session_state.texto_maestro = st.text_area(
            "Editor Musical",
            value=st.session_state.texto_maestro,
            height=altura,
            key=f"editor_v{st.session_state.editor_version}",
            label_visibility="collapsed"
        )

# --- EJECUCIÓN ---
st.title("🎸 Editor Renglones Sincronizados")
app = MusicEditorApp()
app.gestionar_archivo()
app.mostrar_editor()
