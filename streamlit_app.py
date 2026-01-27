import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="wide")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS PARA ALINEACIÓN REAL ---
# Forzamos line-height exacto y eliminamos variaciones de padding
st.markdown("""
    <style>
    /* Estilo para el área de texto del editor */
    .stTextArea textarea {
        line-height: 1.6 !important;
        padding-top: 15px !important; /* Ajuste crítico para el primer renglón */
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
    }
    /* Estilo para la columna de números */
    .line-numbers {
        line-height: 1.6 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        color: #888;
        text-align: right;
        padding-top: 15px !important; /* Debe ser IGUAL al padding del textarea */
        user-select: none;
        margin-top: 24px; /* Ajuste para compensar el espacio del label oculto */
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "contenido" not in st.session_state:
    st.session_state.contenido = ""

def al_cargar():
    if st.session_state.uploader:
        st.session_state.contenido = st.session_state.uploader.read().decode("utf-8")

# --- INTERFAZ ---
st.title("🎸 Transpositor de Notas 2026")
st.file_uploader("📂 Sube archivo .txt", type=["txt"], key="uploader", on_change=al_cargar)

# Procesar dimensiones
lineas_actuales = st.session_state.contenido.split("\n")
n_lineas = max(len(lineas_actuales), 1)
# Altura calculada: (n_lineas * altura_linea) + padding + margen de seguridad
altura_px = (n_lineas * 25.6) + 40 

st.subheader("📝 Editor")
col_n, col_e = st.columns([0.05, 0.95], gap="small")

with col_n:
    # Generamos los números con el estilo CSS 'line-numbers'
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(f'<div class="line-numbers">{numeros_html}</div>', unsafe_allow_html=True)

with col_e:
    # Editor vinculado al estado. La altura dinámica evita el scroll interno.
    st.text_area("Editor Principal", key="contenido", height=int(altura_px), label_visibility="collapsed")

# --- PREVISUALIZACIÓN ---
if st.session_state.contenido:
    st.divider()
    st.subheader("👁️ Previsualización Final")
    lineas_p = st.session_state.contenido.split('\n')
    resultado_limpio = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_p):
            if (i + 1) % 2 != 0: # NOTAS
                conv = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
                resultado_limpio.append(conv)
                st.markdown(f"**`:blue[{conv}]`**")
            else: # LETRA
                resultado_limpio.append(linea)
                st.text(linea)

    st.divider()
    c1, c2 = st.columns(2)
    c1.download_button("💾 Descargar TXT", data="\n".join(resultado_limpio), file_name="cancion.txt", use_container_width=True)
    if c2.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.contenido = ""
        st.rerun()
