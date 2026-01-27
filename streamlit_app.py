import streamlit as st

# Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="wide")

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

# --- GESTIÓN DE CARGA ---
if "contenido" not in st.session_state:
    st.session_state.contenido = ""

def al_cargar_archivo():
    if st.session_state.uploader_key is not None:
        # Leemos el archivo y actualizamos el estado del editor
        st.session_state.contenido = st.session_state.uploader_key.read().decode("utf-8")

# --- INTERFAZ ---
st.title("🎸 Transpositor con Numeración Estática")

# 1. Cargador de archivos
st.file_uploader("Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_cargar_archivo)

st.subheader("Editor de Canción")

# 2. COLUMNAS: NUMERACIÓN Y EDITOR
# Calculamos las líneas del contenido actual
lineas_actuales = st.session_state.contenido.split("\n")
n_lineas = max(len(lineas_actuales), 1)

col_num, col_edit = st.columns([0.04, 0.96], gap="small")

with col_num:
    # Creamos la numeración estática (HTML)
    # El padding y line-height están calibrados para el diseño de Streamlit 2026
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(
        f"""
        <div style="
            line-height: 1.6; 
            font-family: monospace; 
            font-size: 1.25rem; 
            text-align: right; 
            color: #888; 
            padding-top: 38px;
            user-select: none;
        ">
            {numeros_html}
        </div>
        """, 
        unsafe_allow_html=True
    )

with col_edit:
    # El editor usa el session_state para mostrar el contenido cargado al instante
    texto_input = st.text_area(
        "Editor",
        value=st.session_state.contenido,
        height=400,
        key="main_editor",
        label_visibility="collapsed"
    )
    # Actualizamos el estado para que la numeración crezca si el usuario escribe
    st.session_state.contenido = texto_input

# 3. PREVISUALIZACIÓN Y PROCESAMIENTO
if st.session_state.contenido:
    st.divider()
    st.subheader("👁️ Previsualización Final")
    
    lineas_proceso = st.session_state.contenido.split('\n')
    resultado_final = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_proceso):
            num_renglon = i + 1
            if num_renglon % 2 != 0: # IMPAR: Notas
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
            label="💾 Descargar TXT (Limpio)",
            data="\n".join(resultado_final),
            file_name="cancion_convertida_2026.txt",
            mime="text/plain",
            use_container_width=True
        )
    with c2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.contenido = ""
            st.rerun()
