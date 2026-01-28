import streamlit as st
import streamlit.components.v1 as components
import re

class Config:
    """Configuración maestra de estilos y mapeo de notas."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E"
    COLOR_LETRA = "#16213E"
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"
    # Diccionario de conversión Latino -> Americano
    LAT_TO_AM = {
        "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B",
        "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
        "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
    }

class StyleEngine:
    """Mantiene la visibilidad y el rayado de fondo intactos."""
    @staticmethod
    def aplicar():
        st.markdown(f"""
            <style>
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

    def procesar_cifrado(self):
        """Convierte Latino a Americano + ' en renglones impares desde el 9."""
        lineas = st.session_state.txt.split("\n")
        nuevas_lineas = []
        
        for i, linea in enumerate(lineas):
            n_renglon = i + 1
            # Solo renglones impares a partir del 9
            if n_renglon >= 9 and n_renglon % 2 != 0:
                # Procesar palabra por palabra para mantener espacios
                palabras = re.split(r'(\s+)', linea)
                resultado_linea = []
                for p in palabras:
                    p_upper = p.upper().strip()
                    if p_upper in Config.LAT_TO_AM:
                        resultado_linea.append(Config.LAT_TO_AM[p_upper] + "'")
                    elif p.strip() == "": # Mantener espacios
                        resultado_linea.append(p)
                    else: # Si ya es americano o no es nota, añadir ' si parece nota
                        resultado_linea.append(p + "'" if p.strip() else p)
                nuevas_lineas.append("".join(resultado_linea))
            else:
                nuevas_lineas.append(linea)
        
        st.session_state.txt = "\n".join(nuevas_lineas)
        st.session_state.v += 1 # Forzar actualización visual

    def render_interfaz(self):
        # Botón de proceso
        if st.button("🔄 Convertir Cifrado (L9+)"):
            self.procesar_cifrado()
            st.rerun()

        # Editor
        n = len(st.session_state.txt.split("\n"))
        h = (n * Config.LH) + 40
        st.session_state.txt = st.text_area("Ed", value=st.session_state.txt, height=h, 
                                           key=f"e_{st.session_state.v}", label_visibility="collapsed")

    def render_boton_guardado(self):
        """Lógica saveFile con doble confirmación (Compartir/Descargar)."""
        if st.session_state.txt:
            t_js = st.session_state.txt.replace("`", "\\`").replace("${", "\\${")
            nom = st.session_state.nom
            components.html(f"""
                <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 1000;">
                    <button id="saveBtn" style="width: 180px; height: 50px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; color: white; background: #007AFF; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">💾 GUARDAR</button>
                </div>
                <script>
                    async function saveFile() {{ 
                        const contenido = `{t_js}`; 
                        const currentFileName = "{nom}";
                        const blob = new Blob([contenido], {{ type: 'text/plain' }}); 
                        const file = new File([blob], currentFileName, {{ type: 'text/plain' }}); 
                        const esPC = /Windows|Macintosh|Linux/i.test(navigator.userAgent) && !/iPhone|iPad|Android/i.test(navigator.userAgent);

                        if (!esPC && navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                            if (confirm("🎵 COMPARTIR 🎵\\n\\n¿Deseas compartir este archivo?")) {{
                                try {{ await navigator.share({{ files: [file] }}); return; }} 
                                catch (e) {{ console.log("Cancelado"); }}
                            }}
                        }}
                        if (confirm("⬇️ DESCARGAR ⬇️\\n\\n¿Deseas descargar el archivo?")) {{
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url; a.download = currentFileName;
                            document.body.appendChild(a); a.click(); document.body.removeChild(a);
                            setTimeout(() => URL.revokeObjectURL(url), 150);
                        }}
                    }}
                    document.getElementById('saveBtn').onclick = saveFile;
                </script>
            """, height=80)

# --- EXEC ---
st.title("🎸 Editor Musical 2026")
app = MusicEditorApp()
app.gestionar_sync()
app.render_interfaz()
app.render_boton_guardado()
