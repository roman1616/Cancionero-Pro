import streamlit as st

class EditorConfig:
    """Valores constantes para garantizar la alineación y visibilidad."""
    LH = 32
    GRIS = "#1E1E1E"
    AZUL = "#252A34"
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleManager:
    """Inyecta CSS con máxima prioridad para evitar cambios visuales inesperados."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* VISIBILIDAD: Forzamos el color blanco en el nivel más profundo */
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
                background: transparent !important;
                padding: 0px !important;
            }}
            /* FONDO: Sincronización milimétrica de las franjas */
            div[data-baseweb="textarea"] {{
                background-color: {EditorConfig.GRIS} !important;
                background-image: linear-gradient(
                    {EditorConfig.GRIS} 50%, 
                    {EditorConfig.AZUL} 50%
                ) !important;
                background-size: {EditorConfig.ANCHO} {EditorConfig.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
                border: 1px solid #444 !important;
            }}
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        # Inicializamos el texto y una versión para forzar el reset del widget
        if "texto_maestro" not in st.session_state:
            st.session_state.texto_maestro = ""
        if "editor_version" not in st.session_state:
            st.session_state.editor_version = 0
        StyleManager.aplicar()

    def gestionar_archivo(self):
        """Maneja la carga y limpieza total al quitar el archivo."""
        archivo = st.file_uploader("Subir", type=['txt'], key="u_file", label_visibility="collapsed")
        
        if archivo is not None:
            contenido = archivo.read().decode("utf-8")
            if st.session_state.texto_maestro != contenido:
                st.session_state.texto_maestro = contenido
                st.session_state.editor_version += 1 # Cambia la identidad del editor
                st.rerun()
        else:
            # Si se quita el archivo, reseteamos todo
            if st.session_state.texto_maestro != "":
                st.session_state.texto_maestro = ""
                st.session_state.editor_version += 1
                st.rerun()

    def mostrar_editor(self):
        """Dibuja el editor con una clave única para evitar que retenga basura."""
        n_lineas = len(st.session_state.texto_maestro.split("\n"))
        altura = (n_lineas * EditorConfig.LH) + 40
        
        # Al añadir 'editor_version' a la key, el widget se destruye y recrea al limpiar
        st.session_state.texto_maestro = st.text_area(
            "Editor Musical",
            value=st.session_state.texto_maestro,
            height=altura,
            key=f"editor_v{st.session_state.editor_version}",
            label_visibility="collapsed"
        )

# --- EJECUCIÓN ---
st.title("🎸 Editor Blindado 2026")
app = MusicEditorApp()
app.gestionar_archivo()
app.mostrar_editor()
