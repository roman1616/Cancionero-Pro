import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="wide")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Alineación y Bicolor) ---
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 1.6 !important;
        padding-top: 15px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        background-image: linear-gradient(#ffffff 50%, #f0f7ff 50%) !important;
        background-size: 100% 51.2px !important;
        background-attachment: local !important;
    }
    .line-numbers {
        line-height: 1.6 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        color: #888;
        text-align: right;
        padding-top: 15px !important;
        margin-top: 25px;
        user-select: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO CRÍTICA ---
if "main_editor" not in st.session_state:
    st.session_state.main_editor = ""

def al_cargar_archivo():
    if st.session_state.uploader_key is not None:
        # Leemos e inyectamos directamente en la KEY del editor
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.main_editor = contenido

# --- INTERFAZ ---
st.title("🎸 Transpositor de Notas 2026")

# Cargador con callback para visualización inmediata
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_cargar_archivo)

# Calculamos dimensiones basadas en el estado actual
lineas_actuales = st.session_state.main_editor.split("\n")
n_lineas = max(len(lineas_actuales), 1)
altura_px = (n_lineas * 25.6) + 50 

st.subheader("📝 Editor (Blanco: Notas | Azul: Letra)")
col_n, col_e = st.columns([0.05, 0.95], gap="small")

with col_n:
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(f'<div class="line-numbers">{numeros_html}</div>', unsafe_allow_html=True)

with col_e:
    # Usamos SOLO la key vinculada al estado para asegurar que el contenido se vea
    st.text_area("Editor", key="main_editor", height=int(altura_px), label_visibility="collapsed")

# --- PREVISUALIZACIÓN ---
if st.session_state.main_editor:
    st.divider()
    st.subheader("👁️ Previsualización Final")
    
    lineas_p = st.session_state.main_editor.split('\n')
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
    c1.download_button("💾 Descargar TXT Limpio", data="\n".join(resultado_limpio), 
                       file_name="cancion_cifrada.txt", use_container_width=True)
    
    if c2.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.main_editor = ""
        st.rerun()
