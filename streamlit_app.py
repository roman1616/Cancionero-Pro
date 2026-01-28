import streamlit as st
import streamlit.components.v1 as components
import re

class Config:
    """Configuración Maestra de Sincronización."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E" # Gris
    COLOR_LETRA = "#16213E" # Azul
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"
    # Mapeo para conversión
    LAT_AM = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B"}

class StyleEngine:
    """Anula capas de Streamlit y fuerza visibilidad de fondo y texto."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            /* VISIBILIDAD TOTAL */
            [data-testid="stTextArea"] div, [data-baseweb="textarea"] > div {{
                background-color: transparent !important;
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

class MusicEditor:
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

    def boton_convertir(self):
        """Lógica de conversión: Líneas impares desde la 9."""
        if st.button("🔄 Cambiar Cifrado (L9+)"):
            lineas = st.session_state.txt.split("\n")
            resultado = []
            for i, linea in enumerate(lineas):
                if (i + 1) >= 9 and (i + 1) % 2 != 0:
                    # Reemplazo de notas + apóstrofe
                    palabras = re.split(r'(\s+)', linea)
                    nueva_l = []
                    for p in palabras:
                        p_up = p.upper().strip()
                        # Si es latino, convertir. Si ya es americano o nota, añadir '
                        if p_up in Config.LAT_AM:
                            nueva_l.append(Config.LAT_AM[p_up] + "'")
                        elif p.strip() and any(n in p_up for n in "CDEFGAB"):
                            nueva_l.append(p.strip() + "'")
                        else:
                            nueva_l.append(p)
                    resultado.append("".join(nueva_l))
                else:
                    resultado.append(linea)
            st.session_state.txt = "\n".join(resultado)
            st.session_state.v += 1
            st.rerun()

    def render_editor(self):
        n = len(st.session_state.txt.split("\n"))
        st.session_state.txt = st.text_area("Ed", value=st.session_state.txt, height=(n*Config.LH)+40, 
                                           key=f"e_{st.session_state.v}", label_visibility="collapsed")

    def render_save_file(self):
        """Función saveFile con doble confirmación."""
        if st.session_state.txt:
            t_js = st.session_state.txt.replace("`", "\\`").replace("${", "\\${")
            nom = st.session_state.nom
            components.html(f"""
                <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 1000;">
                    <button id="sv" style="width: 180px; height: 50px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; color: white; background: #007AFF;">💾 GUARDAR</button>
                </div>
                <script>
                    document.getElementById('sv').onclick = async function() {{
                        const txt = `{t_js}`; const nom = "{nom}";
                        const b = new Blob([txt], {{type:'text/plain'}});
                        const f = new File([b], nom, {{type:'text/plain'}});
                        const esPC = !/iPhone|iPad|Android/i.test(navigator.userAgent);
                        if (!esPC && navigator.canShare && navigator.canShare({{files:[f]}})) {{
                            if (confirm("🎵 ¿COMPARTIR?")) {{ await navigator.share({{files:[f]}}); return; }}
                        }}
                        if (confirm("⬇️ ¿DESCARGAR?")) {{
                            const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = nom; a.click();
                        }}
                    }};
                </script>
            """, height=80)

# --- START ---
st.title("🎸 Editor Musical Pro")
app = MusicEditor()
app.gestionar_sync()
app.boton_convertir()
app.render_editor()
app.render_save_file()
