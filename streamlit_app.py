import streamlit as st
import streamlit.components.v1 as components
import re

class Config:
    """Configuración Maestra."""
    LH = 32
    COLOR_NOTAS = "#1E1E1E"
    COLOR_LETRA = "#16213E"
    TEXTO = "#FFFFFF !important"
    ANCHO = "2500px"
    LAT_TO_AM = {
        "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B",
        "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
        "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
    }

class MusicEditorApp:
    def __init__(self):
        if "txt" not in st.session_state: st.session_state.txt = ""
        if "v" not in st.session_state: st.session_state.v = 0
        if "nom" not in st.session_state: st.session_state.nom = "cancion.txt"
        self.aplicar_estilos()

    def aplicar_estilos(self):
        st.markdown(f"""
            <style>
            [data-testid="stTextArea"] div, [data-baseweb="textarea"] > div {{ background-color: transparent !important; }}
            textarea {{
                color: {Config.TEXTO}; -webkit-text-fill-color: {Config.TEXTO};
                font-family: 'Courier New', monospace !important; font-size: 18px !important;
                line-height: {Config.LH}px !important; width: {Config.ANCHO} !important;
                white-space: pre !important; overflow-wrap: normal !important;
                background-image: linear-gradient({Config.COLOR_NOTAS} 50%, {Config.COLOR_LETRA} 50%) !important;
                background-size: {Config.ANCHO} {Config.LH * 2}px !important;
                background-attachment: local !important; background-position: 0px 0px !important;
                border: none !important; padding: 0px !important;
            }}
            </style>
        """, unsafe_allow_html=True)

    def sync_texto(self):
        # Captura cambios del editor inmediatamente
        st.session_state.txt = st.session_state.editor_k

    def convertir_logica(self):
        """Convierte renglones impares desde el 9 a cifrado Americano + '."""
        lineas = st.session_state.txt.split("\n")
        resultado = []
        for i, linea in enumerate(lineas):
            if (i + 1) >= 9 and (i + 1) % 2 != 0:
                # Mantenemos espacios y convertimos notas
                pals = re.split(r'(\s+)', linea)
                convertidas = []
                for p in pals:
                    p_up = p.upper().strip()
                    if p_up in Config.LAT_TO_AM:
                        convertidas.append(Config.LAT_TO_AM[p_up] + "'")
                    elif p.strip() and p.strip() in "CDEFGAB" or "#" in p or "b" in p:
                        convertidas.append(p.strip() + "'")
                    else:
                        convertidas.append(p)
                resultado.append("".join(convertidas))
            else:
                resultado.append(linea)
        st.session_state.txt = "\n".join(resultado)
        st.session_state.v += 1 # Reset de widget para mostrar cambios

    def render(self):
        st.title("🎸 Editor Pro 2026")
        
        # 1. Cargador
        f = st.file_uploader("Subir", type=['txt'], key="u_f", label_visibility="collapsed")
        if f:
            c = f.read().decode("utf-8")
            if st.session_state.txt != c:
                st.session_state.txt = c; st.session_state.v += 1; st.rerun()
        elif st.session_state.txt != "" and f is None:
            st.session_state.txt = ""; st.session_state.v += 1; st.rerun()

        # 2. Botón de Conversión (ahora funciona al primer clic)
        if st.button("🔄 Convertir Cifrado (L9+)"):
            self.convertir_logica()
            st.rerun()

        # 3. Editor (con on_change para no perder datos)
        n = len(st.session_state.txt.split("\n"))
        st.text_area("Ed", value=st.session_state.txt, height=(n*Config.LH)+40, 
                     key="editor_k", on_change=self.sync_texto, label_visibility="collapsed")

        # 4. Botón JS de Guardado (con tu lógica exacta de saveFile)
        if st.session_state.txt:
            t_js = st.session_state.txt.replace("`", "\\`").replace("${", "\\${")
            components.html(f"""
                <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 1000;">
                    <button id="sv" style="width: 180px; height: 50px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; color: white; background: #007AFF;">💾 GUARDAR</button>
                </div>
                <script>
                    document.getElementById('sv').onclick = async function() {{
                        const contenido = `{t_js}`;
                        const currentFileName = "{st.session_state.nom}";
                        const blob = new Blob([contenido], {{ type: 'text/plain' }});
                        const file = new File([blob], currentFileName, {{ type: 'text/plain' }});
                        const esPC = /Windows|Macintosh|Linux/i.test(navigator.userAgent) && !/iPhone|iPad|Android/i.test(navigator.userAgent);

                        if (!esPC && navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                            if (confirm("🎵 COMPARTIR 🎵\\n\\n¿Deseas compartir este archivo?")) {{
                                try {{ await navigator.share({{ files: [file] }}); return; }} catch (e) {{}}
                            }}
                        }}
                        if (confirm("⬇️ DESCARGAR ⬇️\\n\\n¿Deseas descargar el archivo?")) {{
                            const a = document.createElement('a');
                            a.href = URL.createObjectURL(blob); a.download = currentFileName; a.click();
                        }}
                    }};
                </script>
            """, height=80)

# --- GO ---
app = MusicEditorApp()
app.render()
