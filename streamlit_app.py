import streamlit as st

# Diccionario de conversión a cifrado americano
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

st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

st.title("🎵 Editor de Notas y Letras")

# --- INICIALIZACIÓN DEL ESTADO ---
if 'texto_editor' not in st.session_state:
    st.session_state.texto_editor = ""

# --- SECCIÓN DE CARGA ---
with st.sidebar:
    st.header("Configuración")
    archivo_subido = st.file_uploader("Subir archivo .txt", type=["txt"])
    if archivo_subido:
        contenido = archivo_subido.read().decode("utf-8")
        st.session_state.texto_editor = contenido

# --- SECCIÓN DE EDICIÓN ---
st.subheader("1. Edita tu contenido")
# Este área de texto actualiza el estado en tiempo real
texto_actualizado = st.text_area(
    "Modifica aquí los renglones (Impares=Notas, Pares=Letra):",
    value=st.session_state.texto_editor,
    height=250,
    key="area_edicion"
)

# --- SECCIÓN DE PROCESAMIENTO Y VISUALIZACIÓN ---
if texto_actualizado:
    lineas = texto_actualizado.split('\n')
    resultado_final = []
    
    st.divider()
    st.subheader("2. Previsualización en Cifrado Americano")
    
    # Renderizado estético
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            num = i + 1
            if num % 2 != 0:
                # Notas
                notas_cifradas = convertir_linea_notas(linea)
                resultado_final.append(notas_cifradas)
                st.markdown(f"**`:blue[{notas_cifradas}]`**")
            else:
                # Letra
                resultado_final.append(linea)
                st.markdown(f"&nbsp;&nbsp;{linea}")

    # --- SECCIÓN DE EXPORTACIÓN ---
    st.divider()
    texto_exportar = "\n".join(resultado_final)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="💾 Descargar Resultado",
            data=texto_exportar,
            file_name="cancion_modificada_2026.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        # Enlace de acción para Streamlit Cloud
        st.link_button("🚀 Publicar y Compartir", "https://share.streamlit.io", use_container_width=True)
else:
    st.info("Escribe algo o sube un archivo para empezar a editar.")

