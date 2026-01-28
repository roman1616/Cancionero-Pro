import streamlit as st

class Config:
    """Configuración Maestra: Si cambias un valor aquí, se ajusta toda la app."""
    LINE_HEIGHT = 32
    BG_NOTAS = "#1E1E1E"
    BG_LETRA = "#252A34"
    TEXT_COLOR = "#FFFFFF"
    ANCHO_VIRTUAL = "2500px"

class StyleEngine:
    """Motor de Estilos: Blinda la visibilidad del texto y la alineación."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* 1. CONTENEDOR RAIZ: Forzamos el scroll lateral */
            div[data-baseweb="textarea"] {{
                background-color: {Config.BG_NOTAS} !important;
                overflow-x: auto !important;
                padding: 0 !important;
            }}

            /* 2. TEXTAREA: Forzamos visibilidad, fuente y fondo rayado */
            div[data-baseweb="textarea"] textarea {{
                /* Texto Blanco Real */
                color: {Config.TEXT_COLOR} !important;
                -webkit-text-fill-color: {Config.TEXT_COLOR} !important;
                
                /* Tipografía y Medidas */
                font-family: 'Courier New', Courier, monospace !important;
                font-size: 18px !important;
                line-height: {Config.LINE_HEIGHT}px !important;
                
                /* Estructura No-Wrap para que funcione el scroll */
                width: {Config.ANCHO_VIRTUAL} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;
                
                /* Fondo sincronizado: Notas (Gris) / Letra (Azul) */
                background-image: linear-gradient(
                    {Config.BG_NOTAS} 50%, 
                    {Config.BG_LETRA} 50%
                ) !important;
                background-size: {Config.ANCHO_VIRTUAL} {Config.LINE_HEIGHT * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                background-repeat: repeat-y !important;

                /* Reset de bordes y paddings internos */
                padding: 0px !important;
                border: none !important;
                outline: none !important;
            }}

            /* 3. SCROLLBAR: Estética para que no estorbe */
            div[data-baseweb="textarea"]::-webkit-scrollbar {{
                height: 8px;
            }}
            div[data-baseweb="textarea"]::-webkit-scrollbar-thumb {{
                background: #444;
                border-radius: 4px;
            }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        # Inicialización de estado
        if "texto" not in st.session_state:
            st.session_state.texto = "DO     RE     MI\nEsta es una linea de prueba"
        StyleEngine.aplicar()

    def render(self):
        st.title("🎸 Editor POO Sincronizado")
        
        # Cargador de archivos
        archivo = st.file_uploader("Cargar", type=["txt"], key="u_txt", label_visibility="collapsed")
        if archivo:
            st.session_state.texto = archivo.read().decode("utf-8")

        # Cálculo de altura basado en líneas
        num_lineas = len(st.session_state.texto.split("\n"))
        altura = (num_lineas * Config.LINE_HEIGHT) + 20

        # Editor Principal
        # Vinculamos directamente el valor al session_state
        nuevo_texto = st.text_area(
            "Editor",
            value=st.session_state.texto,
            height=altura,
            key="area_editor",
            label_visibility="collapsed"
        )
        
        # Actualización de estado
        if nuevo_texto != st.session_state.texto:
            st.session_state.texto = nuevo_texto

        # Botón Limpiar
        if st.button("🗑️ Limpiar Todo"):
            st.session_state.texto = ""
            st.rerun()

# --- EJECUCIÓN ---
if __name__ == "__main__":
    app = MusicEditorApp()
    app.render()
