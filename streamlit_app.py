import streamlit as st
import streamlit.components.v1 as components

class EditorConfig:
    """Configuración Maestra Blindada."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E" # Gris
    COLOR_LETRA = "#16213E" # Azul
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleEngine:
    """Anula capas de Streamlit y fuerza visibilidad de fondo y texto."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            [data-testid="stTextArea"] div, 
            [data-testid="stTextArea"] textarea,
            div[data-baseweb="textarea"],
            div[data-baseweb="textarea"] > div {{
                background-color: transparent !important;
                background-image: none !important;
            }}
            div[data-baseweb="textarea"] {{
                background-color: {EditorConfig.COLOR_NOTAS} !important;
                background-image: linear-gradient(
                    {EditorConfig.COLOR_NOTAS} 50%, 
                    {EditorConfig.COLOR_LETRA} 50%
                ) !important;
                background-size: {EditorConfig.ANCHO} {EditorConfig.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
                border: 1px solid #444 !important;
            }}
            textarea {{
                color: {EditorConfig.TEXTO};
                -webkit-text-fill-color: {EditorConfig.TEXTO};
                caret-color: white !important;
                font-family: 'Courier New', monospace !important;
                font-size: 18px !important;
                line-height: {EditorConfig.LH}px !important;
                width: {EditorConfig.ANCHO} !important;
                white-space: pre !important;
                overflow-wrap: normal !important;
                padding: 0px !important;
                border: none !important;
            }}
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        if "txt" not in st.session_state: st.session_state.txt = ""
        if "v" not in st.session_state: st.session_state.v = 0
        if "archivo_nombre" not in st.session_state: st.session_state.archivo_nombre = "cancion.txt"
        StyleEngine.aplicar()

    def gestionar_datos(self):
        f = st.file_uploader("Cargar", type=['txt'], key="u_file", label_visibility="collapsed")
        if f:
            st.session_state.archivo_nombre = f.name
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c
                st.session_state.v += 1
                st.rerun()
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""
            st.session_state.v += 1
            st.rerun()

    def render(self):
        n = len(st.session_state.txt.split("\n"))
        h = (n * EditorConfig.LH) + 40
        st.session_state.txt = st.text_area(
            "Editor", value=st.session_state.txt, height=h,
            key=f"ed_{st.session_state.v}", label_visibility="collapsed"
        )

    def render_botones_flotantes(self):
        """Inyecta los botones flotantes de Guardar y Compartir."""
        if st.session_state.txt:
            # Escapamos el texto para JS
            texto_js = st.session_state.txt.replace("`", "\\`").replace("${", "\\${")
            nombre = st.session_state.archivo_nombre
            
            components.html(f"""
                <div style="position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 999;">
                    <button id="dl" style="width: 140px; height: 45px; border: none; border-radius: 20px; font-weight: bold; cursor: pointer; color: white; background: #007AFF;">💾 Guardar</button>
                    <button id="sh" style="width: 140px; height: 45px; border: none; border-radius: 20px; font-weight: bold; cursor: pointer; color: white; background: #34C759;">📤 Compartir</button>
                </div>
                <script>
                    const txt = `{texto_js}`;
                    document.getElementById('dl').onclick = () => {{
                        const b = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), txt], {{type:'text/plain;charset=utf-8'}});
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(b); a.download = "PRO_{nombre}"; a.click();
                    }};
                    document.getElementById('sh').onclick = async () => {{
                        const b = new Blob([txt], {{type:'text/plain;charset=utf-8'}});
                        const f = new File([b], "{nombre}", {{type:'text/plain;charset=utf-8'}});
                        if(navigator.share) await navigator.share({{files:[f]}});
                    }};
                </script>
            """, height=100)

# --- INICIO ---
st.title("🎸 Editor Sincronizado 2026")
app = MusicEditorApp()
app.gestionar_datos()
app.render()
app.render_botones_flotantes()
