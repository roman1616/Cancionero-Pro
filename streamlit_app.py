import streamlit as st

# Diccionario extendido de cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

def convertir_linea_notas(linea):
    """Procesa la línea y reemplaza notas manteniendo espacios."""
    palabras = linea.upper().split()
    convertidas = [CONVERSION.get(p, p) for p in palabras]
    return "   ".join(convertidas)

# Configuración profesional de la página
st.set_page_config(
    page_title="Music Transposer 2026",
    page_icon="🎸",
    layout="centered"
)

st.title("🎸 Transpositor a Cifrado Americano")
st.markdown("---")

# Gestión de estado para el texto
if 'contenido' not in st.session_state:
    st.session_state.contenido = ""

# --- ZONA DE CARGA ---
with st.expander("📂 Cargar archivo o pegar texto", expanded=True):
    archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])
    if archivo:
        st.session_state.contenido = archivo.read().decode("utf-8")
    
    texto_input = st.text_area(
        "Edita el contenido aquí:",
        value=st.session_state.contenido,
        height=250,
        help="Impares: Notas (Do Re Mi) | Pares: Letra de la canción",
        key="main_editor"
    )

# --- PROCESAMIENTO ---
if texto_input:
    lineas = texto_input.split('\n')
    resultado_lineas = []
    
    st.subheader("👁️ Previsualización Final")
    
    # Caja de visualización con estilo de partitura
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            idx = i + 1
            if idx % 2 != 0: # Renglón de NOTAS
                notas_cifradas = convertir_linea_notas(linea)
                resultado_lineas.append(notas_cifradas)
                st.markdown(f"**`:blue[{notas_cifradas}]`**")
            else: # Renglón de LETRA
                resultado_lineas.append(linea)
                st.text(linea)

    # --- EXPORTACIÓN ---
    st.markdown("---")
    texto_final = "\n".join(resultado_lineas)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="💾 Descargar .txt",
            data=texto_final,
            file_name="cancion_cifrada.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        # Instrucción para compartir la URL una vez desplegada
        st.info("💡 Para compartir, copia la URL de tu navegador una vez publicada.")

else:
    st.warning("⚠️ Ingresa texto o sube un archivo para generar la visualización.")

st.caption("© 2026 - Creado para músicos con Streamlit")
