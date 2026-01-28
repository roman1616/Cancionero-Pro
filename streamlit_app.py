import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

# Diccionario de cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

# --- ESTILO CSS DARK CON ALINEACIÓN ---
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 32px !important; 
        font-family: 'Courier New', monospace !important;
        font-size: 18px !important;
        color: #FFFFFF !important;
        background-color: #1E1E1E !important;
        border: 1px solid #444 !important;
        padding-top: 15px !important;
    }
    /* Estilo para que los interruptores queden alineados con los renglones */
    .stToggle {
        height: 32px !important;
        margin-top: 10px !important;
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
st.title("🎸 Editor Musical (Control Manual por Línea)")
st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_subir)

st.divider()

# Procesar líneas del contenido actual
lineas_actuales = st.session_state.texto_maestro.split('\n')
n_lineas = max(len(lineas_actuales), 1)

# Estructura: Toggles a la izquierda, Editor a la derecha
col_toggles, col_editor = st.columns([0.15, 0.85])

with col_toggles:
    st.write("**¿Es Música?**")
    config_lineas = []
    # Generamos un interruptor para cada línea detectada
    for i in range(n_lineas):
        # Sugerimos 'Música' en impares por defecto, pero es manual
        sugerencia = (i + 1) % 2 != 0
        es_musica = st.toggle(f"L{i+1}", value=sugerencia, key=f"tgl_{i}")
        config_lineas.append(es_musica)

with col_editor:
    # Altura calculada para evitar scroll interno y alinear con toggles
    altura_dinamica = (n_lineas * 32) + 60
    st.session_state.texto_maestro = st.text_area(
        "Editor", height=int(altura_dinamica), key="editor_key",
        value=st.session_state.texto_maestro, label_visibility="collapsed"
    )

# --- PROCESAMIENTO FINAL ---
if st.session_state.texto_maestro:
    resultado_final = []
    lineas_proceso = st.session_state.texto_maestro.split('\n')
    
    for i, linea in enumerate(lineas_proceso):
        # Solo convertimos si el Toggle de esa línea está encendido
        if i < len(config_lineas) and config_lineas[i]:
            palabras = linea.split()
            # Validación estricta: solo cambia si la palabra es una nota real
            conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in palabras])
            resultado_final.append(conv)
        else:
            # Si el toggle está apagado, se queda como texto puro (Letra)
            resultado_final.append(linea)

    st.divider()
    c1, c2, c3 = st.columns(3)
    
    # Visualización con colores bajo demanda
    if c1.button("👁️ Previsualizar", use_container_width=True):
        st.subheader("Vista Previa:")
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if config_lineas[i]:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    st.markdown(f"<span style='color:white'>{linea}</span>", unsafe_allow_html=True)

    # Limpiar todo
    if c2.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.texto_maestro = ""
        st.session_state.editor_key = ""
        st.rerun()

    # Descarga limpia (Sin colores, solo texto y notas transpuestas)
    c3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_transpuesta.txt",
        mime="text/plain",
        use_container_width=True
    )
