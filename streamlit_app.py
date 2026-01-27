import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="wide")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Alineación Perfecta y Bicolor) ---
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 1.6 !important;
        padding-top: 15px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        /* Fondo bicolor: blanco para impares, azul claro para pares */
        background-image: linear-gradient(#ffffff 50%, #f0f7ff 50%) !important;
        background-size: 100% 51.2px !important;
        background-attachment: local !important;
        border: 1px solid #ddd !important;
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

# --- GESTIÓN DE ESTADO ---
if "contenido" not in st.session_state:
    st.session_state.contenido = ""
if "editor_id" not in st.session_state:
    st.session_state.editor_id = 0

def al_cargar_archivo():
    if st.session_state.uploader_key:
        # Leemos el archivo
        contenido_archivo = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.contenido = contenido_archivo
        # Cambiamos el ID del editor para forzar el refresco visual total
        st.session_state.editor_id += 1

# --- INTERFAZ ---
st.title("🎸 Transpositor Musical 2026")

# Cargador con callback
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_cargar_archivo)

# Procesar dimensiones
lineas_actuales = st.session_state.contenido.split("\n")
n_lineas = max(len(lineas_actuales), 1)
# Altura dinámica: cada línea mide exactamente 25.6px (16px * 1.6)
altura_px = (n_lineas * 25.6) + 45 

st.subheader("📝 Editor (Línea Blanca: Notas | Línea Azul: Letra)")
col_n, col_e = st.columns([0.05, 0.95], gap="small")

with col_n:
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(f'<div class="line-numbers">{numeros_html}</div>', unsafe_allow_html=True)

with col_e:
    # Usamos una KEY dinámica (editor_id) para obligar a mostrar el nuevo contenido
    # No usamos 'value' para evitar errores de duplicidad en session_state
    st.session_state.contenido = st.text_area(
        "Editor", 
        value=st.session_state.contenido,
        height=int(altura_px), 
        key=f"editor_id_{st.session_state.editor_id}",
        label_visibility="collapsed"
    )

# --- PREVISUALIZACIÓN ---
if st.session_state.contenido:
    st.divider()
    st.subheader("👁️ Previsualización Final")
    
    lineas_p = st.session_state.contenido.split('\n')
    resultado_limpio = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_p):
            if (i + 1) % 2 != 0: # NOTAS (Renglón Impar)
                # Convertimos palabras individuales a cifrado
                conv = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
                resultado_limpio.append(conv)
                st.markdown(f"**`:blue[{conv}]`**")
            else: # LETRA (Renglón Par)
                resultado_limpio.append(linea)
                st.text(linea)

    st.divider()
    c1, c2 = st.columns(2)
    c1.download_button("💾 Descargar TXT", data="\n".join(resultado_limpio), 
                       file_name="cancion_convertida.txt", use_container_width=True)
    
    if c2.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.contenido = ""
        st.session_state.editor_id += 1
        st.rerun()
