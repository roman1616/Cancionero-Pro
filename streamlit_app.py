import streamlit as st

class EditorConfig:
    """Configuración maestra para evitar errores de sincronización."""
    LH = 32
    GRIS = "#1E1E1E"
    AZUL = "#252A34"
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleEngine:
    """Inyección de CSS para visibilidad absoluta y fondo sincronizado."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* VISIBILIDAD TOTAL */
            div[data-baseweb="textarea"] textarea {{
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
                padding: 0 !important;
            }}
            /* CONTENEDOR Y RAYADO */
            div[data-baseweb="textarea"] {{
                background-color: {EditorConfig.GRIS} !important;
                background-image: linear-gradient({EditorConfig.GRIS} 50%, {EditorConfig.AZUL} 50%) !important;
                background-size: {EditorConfig.ANCHO} {EditorConfig.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
                padding: 0 !important;
            }}
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        # Estado maestro
        if "texto_maestro" not in st.session_state:
            st.session_state.texto_maestro = ""
        StyleEngine.aplicar()

    def gestionar_entrada(self):
        # 1. Cargador de archivos
        archivo = st.file_uploader("Subir", type=['txt'], key="u_file", label_visibility="collapsed")
        
        # 2. Lógica de Sincronización Forzada
        if archivo is not None:
            contenido_subido = archivo.read().decode("utf-8")
            if st.session_state.texto_maestro != contenido_subido:
                st.session_state.texto_maestro = contenido_subido
                st.rerun()
        else:
            # ANTICIPACIÓN: Si el uploader está vacío pero hay texto, LIMPIAMOS TODO
            if st.session_state.texto_maestro != "":
                st.session_state.texto_maestro = ""
                # Borramos también la memoria interna del widget
                if "main_editor" in st.session_state:
                    del st.session_state["main_editor"]
                st.rerun()

    def mostrar_editor(self):
        n_lineas = len(st.session_state.texto_maestro.split("\n"))
        altura = (n_lineas * EditorConfig.LH) + 40
        
        # El valor del editor siempre sigue al estado maestro
        st.session_state.texto_maestro = st.text_area(
            "Editor Musical",
            value=st.session_state.texto_maestro,
            height=altura,
            key="main_editor",
            label_visibility="collapsed"
        )

# --- EJECUCIÓN ---
st.title("🎸 Editor Pro Sincronizado")
app = MusicEditorApp()
app.gestionar_entrada()
app.mostrar_editor()
