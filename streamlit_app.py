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

def cargar_archivo():
    if st.session_state.uploader is not None:
        st.session_state.editor_content = st.session_state.uploader.read().decode("utf-8")

st.set_page_config(page_title="Editor Profesional 2026", layout="wide")

st.title("🎸 Transpositor con Líneas Laterales")

if "editor_content" not in st.session_state:
    st.session_state.editor_content = ""

# 1. Carga de archivo
st.file_uploader("Sube tu .txt", type=["txt"], key="uploader", on_change=cargar_archivo)

# 2. ÁREA DE EDICIÓN CON NÚMEROS LATERALES
st.subheader("Editor de Canción")

col_indices, col_texto = st.columns([0.05, 0.95])

with col_indices:
    # Generamos la columna de números según el contenido actual
    lineas_actuales = st.session_state.editor_content.split("\n")
    n_lineas = max(len(lineas_actuales), 1)
    # Creamos un bloque de texto con los números alineados
    numeros_html = "<br>".join([f"<b>{i+1}</b>" for i in range(n_lineas)])
    st.markdown(f"<div style='line-height: 2.3; text-align: right; color: gray; padding-top: 25px;'>{numeros_html}</div>", unsafe_allow_html=True)

with col_texto:
    texto_input = st.text_area(
        "Ingresa Notas (Impares) y Letra (Pares):",
        value=st.session_state.editor_content,
        height=400,
        key="main_editor",
        label_visibility="collapsed"
    )
    # Actualizar estado para que la columna de números reaccione
    st.session_state.editor_content = texto_input

# 3. PREVISUALIZACIÓN Y RESULTADO
if texto_input:
    st.divider()
    st.subheader("👁️ Previsualización (Cifrado Americano)")
    
    resultado_final = []
    lineas = texto_input.split('\n')
    
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            num = i + 1
            if num % 2 != 0: # NOTAS
                notas_c = convertir_linea_notas(linea)
                resultado_final.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else: # LETRA
                resultado_final.append(linea)
                st.markdown(f"&nbsp;{linea}")

    # 4. BOTONES DE ACCIÓN
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="💾 Descargar TXT",
            data="\n".join(resultado_final),
            file_name="cancion_cifrada.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_btn2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.editor_content = ""
            st.rerun()
