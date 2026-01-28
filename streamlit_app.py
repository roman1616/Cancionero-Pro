import streamlit as st
import streamlit.components.v1 as components

class Config:
    """Configuración Maestra."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E" # Gris
    COLOR_LETRA = "#16213E" # Azul
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"
    # Diccionario de conversión directa
    MAPA = {
        "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B",
        "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
        "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb",
        "C": "C", "D": "D", "E": "E", "F": "F", "G": "G", "A": "A", "B": "B"
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
        f = st.file_uploader("Cargar", type=['txt'], key="u_f", label_visibility="collapsed")
        if f:
            st.session_state.nom = f.name
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c; st.session_state.v += 1; st.rerun()
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""; st.session_state.v += 1; st.rerun()

    def procesar_notas(self):
        """Lógica bruta: reemplaza notas latinas por americanas + apostrofe."""
        lineas = st.session_state.txt.split("\n")
        nuevas = []
        for i, linea in enumerate(lineas):
            # Línea 9 en adelante e impares
            if (i + 1) >= 9 and (i + 1) % 2 != 0:
                palabras = linea.split(" ")
                linea_procesada = []
                for p in palabras:
                    limpia = p.upper().replace("'", "").strip()
                    if limpia in Config.MAPA:
                        # Reemplaza por la americana y pone el apostrofe
                        linea_procesada.append(Config.MAPA[limpia] + "'")
                    else:
                        linea_procesada.append(p)
                nuevas.append(" ".join(linea_procesada))
            else:
                nuevas.append(linea)
        
        st.session_state.txt = "\n".join(nuevas)
        st.session_state.v += 1 # Cambia key para que Streamlit refresque el texto
        st.rerun()

    def render(self):
        st.title("🎸 Editor Pro 2026")
        if st.button("🔄 CONVERTIR CIFRADO (L9+)"):
            self.procesar_notas()

        n = len(st.session_state.txt.split("\n"))
        # Captura lo que escribes para no perderlo antes de darle al botón
        val = st.text_area("Ed", value=st.session_state.txt, height=(n*Config.LH)+40, 
                          key=f"e_v{st.session_state.v}", label_visibility="collapsed")
        if val != st.session_state.txt:
            st.session_state.txt = val

    def render_save(self):
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
                            const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = "PRO_" + nom; a.click();
                        }}
                    }};
                </script>
            """, height=80)

# --- GO ---
app = MusicEditor()
app.gestionar_sync()
app.render()
app.render_save()
