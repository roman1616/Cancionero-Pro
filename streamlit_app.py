import streamlit as st

st.set_page_config(page_title="Editor Musical 2026", layout="wide")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS PARA ALINEACIÓN REAL ---
# Forzamos que tanto el editor como los números tengan exactamente el mismo line-height
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 1.6 !important;
        padding-top: 10px !important;
        font-family: monospace !important;
        font-size: 16px !important;
    }
    .line-numbers {
        line-height: 1.6 !important;
        font-family: monospace !important;
        font-size: 16px !important;
        color: #888;
        text-align: right;
        padding-top: 10px; /* Debe coincidir con el padding del textarea */
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
st.title("🎸 Transpositor de Notas 2026")
st.file_uploader("📂 Sube archivo .txt", type=["txt"], key="uploader", on_change=al_cargar)

# Procesar líneas
lineas_actuales = st.session_state.contenido.split("\n")
n_lineas = max(len(lineas_actuales), 1)
# Calculamos altura dinámica para evitar scroll
altura_px = max(200, n_lineas * 25.6 + 20) # 25.6 es 16px * 1.6 de line-height

col_n, col_e = st.columns([0.05, 0.95], gap="small")

with col_n:
    # Generamos la columna de números con la clase CSS 'line-numbers'
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(f'<div class="line-numbers">{numeros_html}</div>', unsafe_allow_html=True)

with col_e:
    # Editor vinculado al estado
    texto_edit = st.text_area("Editor", key="contenido", height=int(altura_px), label_visibility="collapsed")

# --- PREVISUALIZACIÓN ---
if st.session_state.contenido:
    st.divider()
    st.subheader("👁️ Previsualización Final")
    lineas_p = st.session_state.contenido.split('\n')
    resultado = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_p):
            if (i + 1) % 2 != 0: # NOTAS
                conv = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
                resultado.append(conv)
                st.markdown(f"**`:blue[{conv}]`**")
            else: # LETRA
                resultado.append(linea)
                st.text(linea)

    st.download_button("💾 Descargar TXT", data="\n".join(resultado), file_name="cancion.txt")

    with c2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.contenido_editor = ""
            st.rerun()
