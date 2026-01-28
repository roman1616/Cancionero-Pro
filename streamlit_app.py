import streamlit as st

class EditorConfig:
    """Configuración maestra para sincronización total."""
    LINE_HEIGHT = 32
    BG_NOTAS = "#1E1E1E"  # Gris casi negro
    BG_LETRA = "#252A34"  # Azul profundo
    TEXT_COLOR = "#FFFFFF" # Blanco puro forzado
    ANCHO_VIRTUAL = "2500px"

class StyleManager:
    """Gestiona el CSS inyectado con selectores de alta prioridad."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* 1. Forzamos el contenedor del textarea a ser oscuro */
            div[data-baseweb="textarea"] {{
                background-color: {EditorConfig.BG_NOTAS} !important;
                border: 1px solid #444 !important;
            }}

            /* 2. Estilo agresivo para el TEXTAREA (Cuerpo del texto) */
            .stTextArea textarea {{
                /* VISIBILIDAD CRÍTICA */
                color: {EditorConfig.TEXT_COLOR} !important;
                -webkit-text-fill-color: {EditorConfig.TEXT_COLOR} !important;
                opacity: 1 !important;
                caret-color: white !important;

                /* FUENTE Y ALINEACIÓN */
                font-family: 'Courier New', Courier, monospace !important;
                font-size: 18px !important;
                line-height: {EditorConfig.LINE_HEIGHT}px !important;
                padding: 0px !important;
                
                /* SCROLL LATERAL */
                width: {EditorConfig.ANCHO_VIRTUAL} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;

                /* FONDO RAYADO SINCRONIZADO */
                background-image: linear-gradient(
                    {EditorConfig.BG_NOTAS} 50%, 
                    {EditorConfig.BG_LETRA} 50%
                ) !important;
                background-size: {EditorConfig.ANCHO_VIRTUAL} {EditorConfig.LINE_HEIGHT * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                background-repeat: repeat-y !important;
            }}

            /* Ocultar etiquetas sobrantes del uploader */
            [data-testid="stFileUploader"] section {{ padding: 0; }}
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicApp:
    def __init__(self):
        if "texto" not in st.session_state:
            st.session_state.texto = "DO     RE     MI\nEsto es una linea de prueba"
        StyleManager.aplicar()

    def run(self):
        st.title("🎸 Editor Pro POO")
        
        # Cargador compacto
        archivo = st.file_uploader("Upload", type=["txt"], key="u_txt", label_visibility="collapsed")
        if archivo:
            st.session_state.texto = archivo.read().decode("utf-8")

        # Editor con altura dinámica
        lineas = st.session_state.texto.split("\n")
        altura = (len(lineas) * EditorConfig.LINE_HEIGHT) + 20

        # Captura de entrada con clave única
        st.session_state.texto = st.text_area(
            "Editor",
            value=st.session_state.texto,
            height=altura,
            key="input_editor",
            label_visibility="collapsed"
        )

        if st.button("🗑️ Limpiar"):
            st.session_state.texto = ""
            st.rerun()

# Ejecución blindada
if __name__ == "__main__":
    app = MusicApp()
    app.run()
