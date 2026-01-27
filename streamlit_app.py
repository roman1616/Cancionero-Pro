import streamlit as st

# Diccionario de conversión a cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

def convertir_linea_notas(linea):
    """Convierte las notas de la línea al cifrado americano."""
    palabras = linea.upper().split()
    convertidas = [CONVERSION.get(p, p) for p in palabras]
    return "   ".join(convertidas)

def procesar_archivo():
    """Función que se ejecuta inmediatamente al subir un archivo."""
    if st.session_state.uploader is not None:
        contenido = st.session_state.uploader.read().decode("utf-8")
        st.session_state.texto_principal = contenido

# Configuración de la aplicación
st.set_page_config(page_title="Music Editor 2026", layout="centered")

st.title("🎸 Transpositor de Notas")

# 1. Inicializar el estado del texto si no existe
if "texto_principal" not in st.session_state:
    st.session_state.texto_principal = ""

# 2. Cargador de archivos con Callback (on_change)
# Esto asegura que al subir el archivo, el texto se cargue en el editor al instante
st.file_uploader(
    "1. Carga tu archivo .txt", 
    type=["txt"], 
    key="uploader", 
    on_change=procesar_archivo
)

# 3. Cuadro de Edición
# Este cuadro está vinculado al session_state
texto_editado = st.text_area(
    "2. Editor de contenido (Modifica aquí):",
    value=st.session_state.texto_principal,
    height=250,
    key="editor_manual"
)

# Actualizar el estado con lo que el usuario escribe manualmente
st.session_state.texto_principal = texto_editado

# 4. Visualización y Procesamiento
if st.session_state.texto_principal:
    st.subheader("3. Previsualización Final")
    
    lineas = st.session_state.texto_principal.split('\n')
    resultado_acumulado = []
    
    # Cuadro de visualización con estilo de partitura
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            n_renglon = i + 1
            if n_renglon % 2 != 0:  # IMPAR = NOTAS
                notas_convertidas = convertir_linea_notas(linea)
                resultado_acumulado.append(notas_convertidas)
                st.markdown(f"**`:blue[{notas_convertidas}]`**")
            else:  # PAR = LETRA
                resultado_acumulado.append(linea)
                st.text(linea)

    # 5. Opciones de Guardar
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="💾 Descargar Resultado",
            data="\n".join(resultado_acumulado),
            file_name="cancion_cifrada_2026.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        if st.button("🗑️ Borrar todo", use_container_width=True):
            st.session_state.texto_principal = ""
            st.rerun()

else:
    st.info("Sube un archivo o escribe en el editor para ver la previsualización.")
