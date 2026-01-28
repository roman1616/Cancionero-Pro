import streamlit as st
import streamlit.components.v1 as components

class Config:
    """Valores críticos para sincronización y visibilidad."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E"
    COLOR_LETRA = "#16213E"
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"

class StyleEngine:
    """Anula el 'modo oscuro' de Streamlit que oculta el texto."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* VISIBILIDAD: Forzamos transparencia en capas intermedias */
            [data-testid="stTextArea"] div, [data-baseweb="textarea"] > div {{
                background-color: transparent !important;
            }}
            /* TEXTO: Blanco puro sobre fondo rayado */
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
                background-image: linear-gradient({Config.COLOR_NOTAS} 50%, {Config.COLOR_LETRA} 50%) !important;
                background-size: {Config.ANCHO} {Config.LH * 2}px !important;
                background-attachment: local !important;
                background-position: 0px 0px !important;
                border: none !important;
                padding: 0px !important;
            }}
            [data-testid="stFileUploader"] label {{ display: none; }}
            </style>
        """, unsafe_allow_html=True)

class MusicEditorApp:
    def __init__(self):
        if "txt" not in st.session_state: st.session_state.txt = ""
        if "v" not in st.session_state: st.session_state.v = 0
        if "nom" not in st.session_state: st.session_state.nom = "cancion.txt"
        StyleEngine.aplicar()

    def gestionar_sync(self):
        f = st.file_uploader("Cargar", type=['txt'], key="u_f", label_visibility="collapsed")
        if f:
            st.session_state.nom = f.name
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c; st.session_state.v += 1; st.rerun()
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""; st.session_state.v += 1; st.rerun()

    def render_editor(self):
        n = len(st.session_state.txt.split("\n"))
        h = (n * Config.LH) + 40
        st.session_state.txt = st.text_area("Ed", value=st.session_state.txt, height=h, 
                                           key=f"e_{st.session_state.v}", label_visibility="collapsed")

    def boton_save_file(self):
        """Inyecta la lógica JS corregida con pregunta de descarga en PC."""
        if st.session_state.txt:
            t_js = st.session_state.txt.replace("`", "\\`").replace("${", "\\${")
            nom = st.session_state.nom
            
            components.html(f"""
                <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 1000;">
                    <button id="sv" style="width: 180px; height: 50px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; color: white; background: #007AFF; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">💾 GUARDAR</button>
                </div>
                <script>
                    document.getElementById('sv').onclick = async function() {{
                        const contenido = `{t_js}`;
                        const currentFileName = "{nom}";
                        const blob = new Blob([contenido], {{ type: 'text/plain' }});
                        const file = new File([blob], currentFileName, {{ type: 'text/plain' }});
                        
                        const esPC = /Windows|Macintosh|Linux/i.test(navigator.userAgent) && !/iPhone|iPad|Android/i.test(navigator.userAgent);

                        // LÓGICA DE COMPARTIR (Móvil)
                        if (!esPC && navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                            if (confirm("🎵 COMPARTIR 🎵\\n\\n¿Deseas compartir este archivo?")) {{
                                try {{
                                    await navigator.share({{ files: [file] }});
                                    return;
                                }} catch (e) {{ console.log("Cancelado"); }}
                            }}
                        }}
                        
                        // LÓGICA DE DESCARGA (PC o Cancelado en móvil)
                        let procederDescarga = true;
                        if (esPC) {{
                            procederDescarga = confirm("💾 DESCARGAR 💾\\n\\n¿Deseas guardar el archivo localmente en tu PC?");
                        }}

                        if (procederDescarga) {{
                            const a = document.createElement('a');
                            a.href = URL.createObjectURL(blob); 
                            a.download = "PRO_" + currentFileName; 
                            a.click();
                        }}
                    }};
                </script>
            """, height=80)

# --- GO ---
st.title("🎸 Editor Blindado 2026")
app = MusicEditorApp()
app.gestionar_sync()
app.render_editor()
app.boton_save_file()
