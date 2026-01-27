import streamlit as st

# Diccionario de conversión
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

def convertir_linea_notas(linea):
    palabras = linea.upper().split()
    convertidas = [CONVERSION.get(p, p) for p in palabras]
    return "   ".join(convertidas)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Editor Musical 2026", layout="wide")

# --- INICIALIZACIÓN DE ESTADO ---
if "main_editor" not in st.session_state:
    st.session_state.main_editor = ""

# --- LÓGICA DE CARGA ---
def procesar_archivo():
    if st.session_state.uploader is not None:
        contenido = st.session_state.uploader.read().decode("utf-8")
        # Actualizamos la key del editor directamente
        st.session_state.main_editor = contenido

st.title("🎸 Transpositor con Renglones Sincronizados")

# 1. Cargador de archivos
st.file_uploader(
    "Sube tu archivo .txt", 
    type=["txt"], 
    key="uploader", 
    on_change=procesar_archivo
)

st.subheader("Editor de Canción")

# 2. COLUMNAS: NÚMEROS Y EDITOR
# Calculamos las líneas basadas en el estado actual
lineas_actuales = st.session_state.main_editor.split("\n")
n_lineas = max(len(lineas_actuales), 1)

col_num, col_edit = st.columns([0.04, 0.96], gap="small")

with col_num:
    # Generamos los números con estilo CSS para alineación exacta
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(
        f"""
        <div style="
            line-height: 1.6; 
            font-family: monospace; 
            font-size: 1.2rem; 
            text-align: right; 
            color: #888; 
            padding-top: 36px;
            user-select: none;
        ">
            {numeros_html}
        </div>
        """, 
        unsafe_allow_html=True
    )

with col_edit:
    # IMPORTANTE: No usamos 'value', usamos 'key' vinculada al estado
    texto_input = st.text_area(
        "Editor",
        key="main_editor",
        height=400,
        label_visibility="collapsed"
    )

# 3. PREVISUALIZACIÓN PROCESADA
if st.session_state.main_editor:
    st.divider()
    st.subheader("👁️ Previsualización (Notas Convertidas)")
    
    lineas_proceso = st.session_state.main_editor.split('\n')
    resultado_final = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_proceso):
            if (i + 1) % 2 != 0: # IMPAR: Notas
                notas_c = convertir_linea_notas(linea)
                resultado_final.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else: # PAR: Letra
                resultado_final.append(linea)
                st.text(linea)

    # 4. BOTONES DE ACCIÓN
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="💾 Descargar TXT",
            data="\n".join(resultado_final),
            file_name="cancion_cifrada.txt",
            mime="text/plain",
            use_container_width=True
        )
    with c2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.main_editor = ""
            st.rerun()
else:
    st.info("Sube un archivo o escribe en el editor para comenzar.")
