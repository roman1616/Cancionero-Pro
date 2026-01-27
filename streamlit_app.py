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

st.set_page_config(page_title="Editor Musical 2026", layout="centered")

st.title("🎸 Transpositor de Notas")

# --- LÓGICA DE CARGA DE ARCHIVO ---
# Usamos session_state para persistir el texto entre recargas
if "texto_contenido" not in st.session_state:
    st.session_state.texto_contenido = ""

archivo_subido = st.file_uploader("1. Sube tu archivo .txt", type=["txt"])

# Si el usuario sube un archivo, actualizamos el session_state
if archivo_subido is not None:
    contenido_leido = archivo_subido.read().decode("utf-8")
    # Solo actualizamos si el contenido es diferente para evitar bucles
    if contenido_leido != st.session_state.texto_contenido:
        st.session_state.texto_contenido = contenido_leido
        st.rerun() # Forzamos recarga para que el text_area vea el cambio

# --- EDITOR INTERACTIVO ---
st.subheader("2. Editar y Previsualizar")

# El text_area toma su valor inicial de session_state.texto_contenido
texto_editado = st.text_area(
    "Modifica el texto aquí (Impar: Notas / Par: Letras):",
    value=st.session_state.texto_contenido,
    height=300,
    key="mi_editor"
)

# --- VISUALIZACIÓN ---
if texto_editado:
    lineas = texto_editado.split('\n')
    resultado_exportar = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            num_renglon = i + 1
            if num_renglon % 2 != 0: # IMPAR = NOTAS
                notas_cifradas = convertir_linea_notas(linea)
                resultado_exportar.append(notas_cifradas)
                st.markdown(f"**`:blue[{notas_cifradas}]`**")
            else: # PAR = LETRA
                resultado_exportar.append(linea)
                st.text(linea)

    # --- BOTONES DE ACCIÓN ---
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="💾 Descargar TXT",
            data="\n".join(resultado_exportar),
            file_name="cancion_cifrada.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.texto_contenido = ""
            st.rerun()
else:
    st.info("Sube un archivo o escribe directamente en el cuadro de arriba.")
