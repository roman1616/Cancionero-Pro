import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

# Diccionario de cifrado
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

# --- ESTILO CSS DARK ---
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 32px !important; 
        font-family: 'Courier New', monospace !important;
        font-size: 18px !important;
        color: #FFFFFF !important;
        background-color: #1E1E1E !important;
        border: 1px solid #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

def al_subir():
    if st.session_state.uploader_key:
        st.session_state.texto_maestro = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.editor_key = st.session_state.texto_maestro

# --- INTERFAZ ---
st.title("🎸 Editor con Selección de Notas")

col_editor, col_opciones = st.columns([0.7, 0.3])

with col_editor:
    st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_subir)
    
    lineas = st.session_state.texto_maestro.split('\n')
    n_lineas = max(len(lineas), 1)
    
    texto_input = st.text_area(
        "Editor:", height=(n_lineas * 32) + 40, key="editor_key",
        value=st.session_state.texto_maestro, label_visibility="collapsed"
    )
    st.session_state.texto_maestro = texto_input

with col_opciones:
    st.subheader("⚙️ Configuración")
    st.write("Marca los renglones que son **NOTAS**:")
    
    # Creamos un checkbox por cada renglón detectado
    seleccion_notas = []
    for i in range(n_lineas):
        # Por defecto, marcamos los impares como notas para ahorrar tiempo
        es_impar = (i + 1) % 2 != 0
        if st.checkbox(f"Renglón {i+1}", value=es_impar, key=f"check_{i}"):
            seleccion_notas.append(True)
        else:
            seleccion_notas.append(False)

# --- PROCESAMIENTO ---
if st.session_state.texto_maestro:
    lineas_finales = st.session_state.texto_maestro.split('\n')
    resultado_final = []

    for i, linea in enumerate(lineas_finales):
        # Si el checkbox de este renglón está marcado, procesamos como notas
        if i < len(seleccion_notas) and seleccion_notas[i]:
            palabras = linea.split()
            conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in palabras])
            resultado_final.append(conv)
        else:
            resultado_final.append(linea)

    st.divider()
    c1, c2, c3 = st.columns(3)
    
    # Previsualización
    if c1.button("👁️ Ver Resultado", use_container_width=True):
        st.subheader("Vista Final:")
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if seleccion_notas[i]:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    st.text(linea)

    # Limpiar
    if c2.button("🗑️ Limpiar", use_container_width=True):
        st.session_state.texto_maestro = ""
        st.session_state.editor_key = ""
        st.rerun()

    # Descargar
    c3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_personalizada.txt",
        use_container_width=True
    )
