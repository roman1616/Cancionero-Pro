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

# --- FUNCIÓN CRÍTICA PARA LA CARGA ---
def cargar_a_editor():
    if st.session_state.uploader_key is not None:
        # Leemos el archivo
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        # Actualizamos la KEY del text_area directamente
        st.session_state.mi_editor = contenido

st.set_page_config(page_title="Music Transposer 2026", layout="centered")

st.title("🎸 Transpositor de Notas")

# 1. Cargador de archivos con el callback que actualiza el editor
st.file_uploader(
    "1. Sube tu archivo .txt", 
    type=["txt"], 
    key="uploader_key", 
    on_change=cargar_a_editor
)

# 2. Editor de texto
# IMPORTANTE: Usamos 'key' para que el callback 'cargar_a_editor' pueda escribir aquí
texto_input = st.text_area(
    "2. Editor de contenido:",
    height=250,
    key="mi_editor" 
)

# 3. Procesamiento y Previsualización
if texto_input:
    st.subheader("3. Previsualización Final")
    
    lineas = texto_input.split('\n')
    resultado_final = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            if (i + 1) % 2 != 0:  # Línea Impar: NOTAS
                notas_c = convertir_linea_notas(linea)
                resultado_final.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else:  # Línea Par: LETRA
                resultado_final.append(linea)
                st.text(linea)

    # 4. Botones de acción
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="💾 Descargar TXT",
            data="\n".join(resultado_final),
            file_name="cancion_cifrada.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        if st.button("🗑️ Limpiar todo", use_container_width=True):
            st.session_state.mi_editor = ""
            st.rerun()
else:
    st.info("Sube un archivo o escribe para ver la previsualización.")
