import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Bicolor 2026", layout="wide")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS PARA RENGLONES DE COLORES ---
# El truco: un linear-gradient que mide exactamente 25.6px por color (16px * 1.6 line-height)
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 1.6 !important;
        padding-top: 15px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        /* Fondo de colores alternos */
        background-image: linear-gradient(
            #fdfdfd 50%, 
            #f0f7ff 50%
        ) !important;
        background-size: 100% 51.2px !important; /* El doble de la altura de línea (25.6 * 2) */
        background-attachment: local !important;
    }
    .line-numbers {
        line-height: 1.6 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        color: #888;
        text-align: right;
        padding-top: 15px !important;
        margin-top: 24px;
        user-select: none;
    }
    </style>
    """, unsafe_allow_html=True)

if "contenido" not in st.session_state:
    st.session_state.contenido = ""

def al_cargar():
    if st.session_state.uploader:
        st.session_state.contenido = st.session_state.uploader.read().decode("utf-8")

# --- INTERFAZ ---
st.title("🎸 Editor Musical Bicolor")
st.caption("Renglones Blancos = Notas | Renglones Azules = Letra")

st.file_uploader("📂 Sube archivo .txt", type=["txt"], key="uploader", on_change=al_cargar)

# Procesar dimensiones
lineas_actuales = st.session_state.contenido.split("\n")
n_lineas = max(len(lineas_actuales), 1)
altura_px = (n_lineas * 25.6) + 50 

col_n, col_e = st.columns([0.05, 0.95], gap="small")

with col_n:
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(f'<div class="line-numbers">{numeros_html}</div>', unsafe_allow_html=True)

with col_e:
    st.text_area("Editor", key="contenido", height=int(altura_px), label_visibility="collapsed")

# --- PREVISUALIZACIÓN ---
if st.session_state.contenido:
    st.divider()
    st.subheader("👁️ Previsualización")
    lineas_p = st.session_state.contenido.split('\n')
    resultado_limpio = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_p):
            if (i + 1) % 2 != 0: # IMPAR: Notas
                conv = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
                resultado_limpio.append(conv)
                st.markdown(f"**`:blue[{conv}]`**")
            else: # PAR: Letra
                resultado_limpio.append(linea)
                st.text(linea)

    st.divider()
    c1, c2 = st.columns(2)
    c1.download_button("💾 Descargar TXT", data="\n".join(resultado_limpio), file_name="cancion.txt", use_container_width=True)
    if c2.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.contenido = ""
        st.rerun()
