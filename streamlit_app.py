import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

# Diccionario de cifrado americano
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
    /* Alineación de los checkboxes con los renglones */
    .stCheckbox {
        margin-bottom: 8px !important;
        height: 32px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

def al_subir():
    if st.session_state.uploader_key:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.texto_maestro = contenido
        st.session_state.editor_key = contenido

# --- INTERFAZ ---
st.title("🎸 Editor de Canciones (Selección Manual)")
st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_subir)

st.divider()

# Procesar líneas actuales
lineas_actuales = st.session_state.texto_maestro.split('\n')
n_lineas = max(len(lineas_actuales), 1)

# Creamos la cuadrícula: Checkboxes a la izquierda, Editor a la derecha
col_checks, col_editor = st.columns([0.15, 0.85])

with col_checks:
    st.write("**¿Es Nota?**")
    es_nota_map = []
    # Generamos un checkbox para cada línea
    for i in range(n_lineas):
        # Sugerencia automática: impar es nota, pero el usuario manda
        sugerencia = (i + 1) % 2 != 0
        es_nota = st.checkbox(f"L{i+1}", value=sugerencia, key=f"check_linea_{i}")
        es_nota_map.append(es_nota)

with col_editor:
    # Altura calculada para que coincida con los checkboxes
    altura_dinamica = (n_lineas * 32) + 40
    st.session_state.texto_maestro = st.text_area(
        "Editor", height=altura_dinamica, key="editor_key",
        value=st.session_state.texto_maestro, label_visibility="collapsed"
    )

# --- PROCESAMIENTO FINAL ---
if st.session_state.texto_maestro:
    resultado_final = []
    lineas_proceso = st.session_state.texto_maestro.split('\n')
    
    for i, linea in enumerate(lineas_proceso):
        # Solo procesamos si el checkbox correspondiente está marcado
        if i < len(es_nota_map) and es_nota_map[i]:
            palabras = linea.split()
            # Validación estricta: si no está en el diccionario, se queda como texto
            conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in palabras])
            resultado_final.append(conv)
        else:
            resultado_final.append(linea)

    st.divider()
    c1, c2, c3 = st.columns(3)
    
    # Visualización
    if c1.button("👁️ Previsualizar Resultado", use_container_width=True):
        st.subheader("Vista Previa del Cifrado")
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if es_nota_map[i]:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    st.text(linea)

    # Limpiar
    if c2.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.texto_maestro = ""
        st.session_state.editor_key = ""
        st.rerun()

    # Descarga limpia
    c3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_transpuesta.txt",
        mime="text/plain",
        use_container_width=True
    )
