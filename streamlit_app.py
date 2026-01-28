import streamlit as st

class EditorSettings:
    """Configuración técnica blindada."""
    LH = 32
    GRIS = "#1E1E1E"
    AZUL = "#252A34"
    BLANCO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleEngine:
    """Inyector de CSS con selectores de alta prioridad."""
    @staticmethod
    def inyectar():
        st.markdown(f"""
            <style>
            textarea {{
                color: {EditorSettings.BLANCO};
                -webkit-text-fill-color: {EditorSettings.BLANCO};
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
                caret-color: white !important;
            }}
            div[data-baseweb="textarea"] {{
                background-color: {EditorSettings.GRIS} !important;
                overflow-x: auto !important;
            }}
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        if "txt" not in st.session_state:
            st.session_state.txt = ""
        StyleEngine.inyectar()

    def gestionar_archivo(self):
        # Usamos on_change para disparar el refresco inmediato
        archivo = st.file_uploader("Cargar", type=['txt'], key="u_file", label_visibility="collapsed")
        
        if archivo is not None:
            contenido = archivo.read().decode("utf-8")
            if st.session_state.txt != contenido:
                st.session_state.txt = contenido
                st.rerun() # Refresco necesario para actualizar el área de texto
        else:
            # Si el uploader está vacío pero el texto no, limpiamos y refrescamos
            if st.session_state.txt != "":
                st.session_state.txt = ""
                st.rerun() # Esto borra visualmente el editor al quitar el archivo

    def mostrar_editor(self):
        # Calculamos altura según contenido
        n_lineas = len(st.session_state.txt.split("\n"))
        h = (n_lineas * EditorSettings.LH) + 40
        
        # Área de edición
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
