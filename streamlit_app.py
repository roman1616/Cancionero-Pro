import streamlit as st
import streamlit.components.v1 as components
import re

class Config:
    """Configuración Maestra."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E" # Gris
    COLOR_LETRA = "#16213E" # Azul
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"
    # Diccionario completo para evitar fallos de detección
    LAT_AM = {
        "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B",
        "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
        "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
    }

class StyleEngine:
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
            [data-testid="stTextArea"] div, [data-baseweb="textarea"] > div {{ background-color: transparent !important; }}
            textarea {{
                color: {Config.TEXTO}; -webkit-text-fill-color: {Config.TEXTO};
                caret-color: white !important; font-family: 'Courier New', monospace !important;
                font-size: 18px !important; line-height: {Config.LH}px !important;
                width: {Config.ANCHO} !important; white-space: pre !important;
                overflow-wrap: normal !important; padding: 0px !important; border: none !important;
                background-image: linear-gradient({Config.COLOR_NOTAS} 50%, {Config.COLOR_LETRA} 50%) !important;
                background-size: {Config.ANCHO} {Config.LH * 2}px !important;
                background-attachment: local !important; background-position: 0px 0px !important;
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
        f = st.file_uploader("Subir", type=['txt'], key="u_f", label_visibility="collapsed")
        if f:
            st.session_state.nom = f.name
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c; st.session_state.v += 1; st.rerun()
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""; st.session_state.v += 1; st.rerun()

    def boton_convertir(self):
        if st.button("🔄 Cambiar Cifrado (L9+)"):
            lineas = st.session_state.txt.split("\n")
            resultado = []
            for i, linea in enumerate(lineas):
                # Renglones impares (1,3,5...) a partir del 9
                if (i + 1) >= 9 and (i + 1) % 2 != 0:
                    # Separamos por espacios pero manteniendo los delimitadores para no romper la alineación
                    partes = re.split(r'(\s+)', linea)
                    nueva_linea = []
                    for p in partes:
                        p_limpio = p.upper().strip()
                        # 1. ¿Es nota latina? -> Convertir a Am + '
                        if p_limpio in Config.LAT_AM:
                            nueva_linea.append(Config.LAT_AM[p_limpio] + "'")
                        # 2. ¿Es ya americana (C, D, Am, G7, etc)? -> Solo añadir '
                        elif p_limpio and re.match(r'^[A-G][#B1-9M]*$', p_limpio):
                            nueva_linea.append(p.strip() + "'")
                        else:
                            nueva_linea.append(p)
                    resultado.append("".join(nueva_linea))
                else:
                    resultado.append(linea)
            st.session_state.txt = "\n".join(resultado)
            st.session_state.v += 1
            st.rerun()

    def render_editor(self):
        n = len(st.session_state.txt.split("\n"))
        # Capturamos el cambio en el área de texto para no perder lo escrito
        txt_input = st.text_area("Ed", value=st.session_state.txt, height=(n*Config.LH)+40, 
                                 key=f"e_{st.session_state.v}", label_visibility="collapsed")
        if txt_input != st.session_state.txt:
            st.session_state.txt = txt_input

    def render_save_file(self):
        if st.session_state.txt:
            t_js = st.session_state.txt.replace("`", "\\`").replace("${", "\\${")
            nom = st.session_state.nom
            components.html(f"""
                <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 1000;">
                    <button id="sv" style="width: 180px; height: 50px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; color: white; background: #007AFF; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">💾 GUARDAR</button>
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
                            const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = "PRO_" + nom; a.click();
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
