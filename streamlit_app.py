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

def cargar_a_editor():
    if st.session_state.uploader_key is not None:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.mi_editor = contenido

st.set_page_config(page_title="Editor Musical 2026", layout="wide")

st.title("🎸 Transpositor con Numeración de Renglones")

# 1. Cargador de archivos
st.file_uploader(
    "Sube tu archivo .txt", 
    type=["txt"], 
    key="uploader_key", 
    on_change=cargar_a_editor
)

# 2. Área de edición
texto_input = st.text_area(
    "Editor de contenido (Renglón 1 = Notas, 2 = Letra...):",
    height=250,
    key="mi_editor",
    placeholder="Escribe aquí...\nLínea 1: Do Re Mi\nLínea 2: Letra de la canción"
)

# 3. Procesamiento y Previsualización Numerada
if texto_input:
    st.subheader("👁️ Previsualización y Guía de Renglones")
    
    lineas = texto_input.split('\n')
    resultado_final = []
    
    with st.container(border=True):
        # Usamos columnas para simular la numeración al margen
        for i, linea in enumerate(lineas):
            num_r = i + 1
            col_num, col_cont = st.columns([0.1, 0.9])
            
            with col_num:
                # Mostramos el número de renglón de forma discreta
                st.caption(f"{num_r}:")
            
            with col_cont:
                if num_r % 2 != 0:  # NOTAS
                    notas_c = convertir_linea_notas(linea)
                    resultado_final.append(notas_c)
                    st.markdown(f"**`:blue[{notas_c}]`** (Notas)")
                else:  # LETRA
                    resultado_final.append(linea)
                    st.markdown(f"{linea} *(Letra)*")

    # 4. Botones
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
    st.info("💡 Tip: Los renglones IMPARES se convertirán a cifrado americano.")
