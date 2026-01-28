import streamlit as st
import streamlit.components.v1 as components

class Config:
    """Configuración Maestra."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E"
    COLOR_LETRA = "#16213E"
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleEngine:
    """Anula capas de Streamlit y fuerza visibilidad de fondo y texto."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            [data-testid="stTextArea"] div, [data-testid="stTextArea"] textarea,
            div[data-baseweb="textarea"], div[data-baseweb="textarea"] > div {{
                background-color: transparent !important;
                background-image: none !important;
            }}
            div[data-baseweb="textarea"] {{
                background-color: {Config.COLOR_NOTAS} !important;
                background-image: linear-gradient({Config.COLOR_NOTAS} 50%, {Config.COLOR_LETRA} 50%) !important;
                background-size: {Config.ANCHO} {Config.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                overflow-x: auto !important;
                border: 1px solid #444 !important;
            }}
            textarea {{
                color: {Config.TEXTO};
                -webkit-text-fill-color: {Config.TEXTO};
                caret-color: white !important;
                font-family: 'Courier New', monospace !important;
                font-size: 18px !important;
                line-height: {Config.LH}px !important;
                width: {Config.ANCHO} !important;
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
        f = st.file_uploader("Subir", type=['txt'], key="u_file", label_visibility="collapsed")
        if f:
            st.session_state.archivo_nombre = f.name
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c; st.session_state.v += 1; st.rerun()
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""; st.session_state.v += 1; st.rerun()

    def render_editor(self):
        n = len(st.session_state.txt.split("\n"))
        h = (n * Config.LH) + 40
        st.session_state.txt = st.text_area("Editor", value=st.session_state.txt, height=h, key=f"ed_{st.session_state.v}", label_visibility="collapsed")

    def inyectar_save_file(self):
        """Implementa la lógica saveFile solicitada con detección de PC/Móvil."""
        if st.session_state.txt:
            texto_js = st.session_state.txt.replace("`", "\\`").replace("${", "\\${")
            nombre = st.session_state.archivo_nombre
            
            components.html(f"""
                <div style="position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); z-index: 999;">
                    <button id="btnSave" style="width: 160px; height: 50px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; color: white; background: #007AFF; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">💾 Guardar / Compartir</button>
                </div>
                <script>
                    document.getElementById('btnSave').onclick = async function() {{
                        const contenido = `{texto_js}`;
                        const currentFileName = "{nombre}";
                        const blob = new Blob([contenido], {{ type: 'text/plain' }});
                        const file = new File([blob], currentFileName, {{ type: 'text/plain' }});
                        
                        const esPC = /Windows|Macintosh|Linux/i.test(navigator.userAgent) && !/iPhone|iPad|Android/i.test(navigator.userAgent);

                        // 1. LÓGICA DE COMPARTIR (Móvil)
                        if (!esPC && navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                            const deseaCompartir = confirm("    🎵 COMPARTIR 🎵\\n\\n¿Deseas compartir este archivo por (WhatsApp, Email, Dropbox, iCloud, etc.)?");
                            if (deseaCompartir) {{
                                try {{
                                    await navigator.share({{ files: [file] }});
                                    return; 
                                } catch (e) {{ console.log("Compartir cancelado"); }}
                            }}
                        }}

                        // 2. LÓGICA DE DESCARGA (PC o Cancelado en móvil)
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = "PRO_" + currentFileName;
                        a.click();
                    }};
                </script>
            """, height=100)

# --- EXEC ---
st.title("🎸 Editor Inteligente 2026")
app = MusicEditorApp()
app.gestionar_datos()
app.render_editor()
app.inyectar_save_file()
