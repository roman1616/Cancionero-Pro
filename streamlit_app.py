import streamlit as st

# 1. Configuración de página (debe ser lo primero)
st.set_page_config(page_title="Editor Musical 2026", layout="wide")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS PARA ALINEACIÓN EXACTA ---
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
        padding-top: 10px;
        user-select: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "contenido" not in st.session_state:
    st.session_state.contenido = ""

def al_cargar():
    if st.session_state.uploader:
        texto = st.session_state.uploader.read().decode("utf-8")
        st.session_state.contenido = texto

# --- INTERFAZ ---
st.title("🎸 Transpositor de Notas 2026")
st.file_uploader("📂 Sube archivo .txt", type=["txt"], key="uploader", on_change=al_cargar)

# Procesar dimensiones
lineas_actuales = st.session_state.contenido.split("\n")
n_lineas = max(len(lineas_actuales), 1)
altura_px = max(250, n_lineas * 25.6 + 40)

st.subheader("📝 Editor")
col_n, col_e = st.columns([0.05, 0.95], gap="small")

with col_n:
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(f'<div class="line-numbers">{numeros_html}</div>', unsafe_allow_html=True)

with col_e:
    # Vinculamos directamente al session_state mediante la key
    st.text_area("Editor", key="contenido", height=int(altura_px), label_visibility="collapsed")

# --- RESULTADOS Y BOTONES ---
if st.session_state.contenido:
    st.divider()
    st.subheader("👁️ Previsualización Final")
    
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
    # Para evitar el error del 'with c2', definimos las columnas y los botones de forma directa
    btn_col1, btn_col2 = st.columns(2)
    
    btn_col1.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_limpio),
        file_name="cancion_cifrada.txt",
        mime="text/plain",
        use_container_width=True
    )
    
    # El botón limpiar ahora usa un callback para evitar el error de ejecución
    if btn_col2.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.contenido = ""
        st.rerun()
