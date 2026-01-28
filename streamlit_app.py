import streamlit as st
import streamlit.components.v1 as components
import re

class Config:
    """Ajustes de estilo y mapeo de notas."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E"
    COLOR_LETRA = "#16213E"
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"
    MAPA = {
        "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B",
        "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#"
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

    def convertir_cifrado(self):
        """Procesa líneas impares desde la 9: Latino -> Am' o Am -> Am'"""
        lineas = st.session_state.txt.split("\n")
        nuevas = []
        for i, linea in enumerate(lineas):
            # Línea 9 en adelante (i >= 8) y líneas impares (1, 3, 5...)
            if (i + 1) >= 9 and (i + 1) % 2 != 0:
                # Separar manteniendo espacios para no romper alineación
                partes = re.split(r'(\s+)', linea)
                procesadas = []
                for p in partes:
                    p_up = p.upper().strip()
                    # 1. Si es Latino
                    if p_up in Config.MAPA:
                        procesadas.append(Config.MAPA[p_up] + "'")
                    # 2. Si ya es Americano (C, G, Am, etc.)
                    elif p.strip() and re.match(r'^[A-G][#bM1-9]*$', p.strip().upper()):
                        procesadas.append(p.strip() + "'")
                    else:
                        procesadas.append(p)
                nuevas.append("".join(procesadas))
            else:
                nuevas.append(linea)
        
        st.session_state.txt = "\n".join(nuevas)
        st.session_state.v += 1 # Forzamos nueva versión del widget para que se VEA el cambio
        st.rerun()

    def render_interfaz(self):
        st.title("🎸 Editor Musical Pro")
        if st.button("🔄 CONVERTIR NOTAS (L9+)"):
            self.convertir_cifrado()

        n = len(st.session_state.txt.split("\n"))
        # El editor se guarda en session_state cada vez que cambia
        st.session_state.txt = st.text_area(
            "Editor", value=st.session_state.txt, height=(n*Config.LH)+40, 
            key=f"ed_v{st.session_state.v}", label_visibility="collapsed"
        )

    def render_js_save(self):
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

# --- EJECUCIÓN ---
app = MusicEditor()
app.gestionar_sync()
app.render_interfaz()
app.render_js_save()
