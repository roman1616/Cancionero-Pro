import streamlit as st
import streamlit.components.v1 as components
import re

class Config:
    """Configuración maestra para sincronización y mapeo."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E"
    COLOR_LETRA = "#16213E"
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"
    # Mapeo Latino -> Americano
    MAPA = {
        "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B",
        "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
        "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
    }

class StyleEngine:
    """Mantiene la visibilidad blindada."""
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

class MusicEditorApp:
    def __init__(self):
        if "txt" not in st.session_state: st.session_state.txt = ""
        if "nom" not in st.session_state: st.session_state.nom = "cancion.txt"
        StyleEngine.aplicar()

    def procesar_automatico(self, texto):
        """Aplica cifrado americano + ' automáticamente en impares L9+."""
        lineas = texto.split("\n")
        nuevas = []
        for i, linea in enumerate(lineas):
            num_l = i + 1
            # Solo líneas impares desde la 9
            if num_l >= 9 and num_l % 2 != 0:
                # Separar por espacios para procesar notas individuales
                palabras = re.split(r'(\s+)', linea)
                procesadas = []
                for p in palabras:
                    limpia = p.upper().strip().replace("'", "")
                    if limpia in Config.MAPA:
                        procesadas.append(Config.MAPA[limpia] + "'")
                    elif p.strip() and re.match(r'^[A-G][#B1-9M]*$', limpia):
                        procesadas.append(p.strip() + "'")
                    else:
                        procesadas.append(p)
                nuevas.append("".join(procesadas))
            else:
                # Si es par o menor a 9, se queda como está (se restaura)
                nuevas.append(linea)
        return "\n".join(nuevas)

    def gestionar_sync(self):
        f = st.file_uploader("Cargar", type=['txt'], key="u_f", label_visibility="collapsed")
        if f:
            st.session_state.nom = f.name
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = self.procesar_automatico(c)
                st.rerun()
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""; st.rerun()

    def render(self):
        st.title("🎸 Editor Automático 2026")
        n = len(st.session_state.txt.split("\n"))
        
        # El procesamiento ocurre en el on_change para ser automático
        nuevo_val = st.text_area(
            "Editor", value=st.session_state.txt, height=(n*Config.LH)+40, 
            key="main_ed", label_visibility="collapsed"
        )
        
        if nuevo_val != st.session_state.txt:
            st.session_state.txt = self.procesar_automatico(nuevo_val)
            st.rerun()

    def render_save(self):
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

# --- GO ---
app = MusicEditorApp()
app.gestionar_sync()
app.render()
app.render_save()
