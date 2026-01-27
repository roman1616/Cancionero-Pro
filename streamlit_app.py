import streamlit as st

# Diccionario de conversión a cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

def convertir_linea_notas(linea):
    """Convierte palabras que coincidan con notas a cifrado americano."""
    palabras = linea.upper().split()
    convertidas = [CONVERSION.get(p, p) for p in palabras]
    return "   ".join(convertidas)

# Configuración de página
st.set_page_config(page_title="Editor de Canciones 2026", layout="centered")

st.title("🎵 Conversor de Notas a Cifrado Americano")

# --- SECCIÓN 1: CARGA DE ARCHIVO O ENTRADA MANUAL ---
st.subheader("1. Carga tu contenido")
archivo_subido = st.file_uploader("Sube un archivo de texto (.txt)", type=["txt"])
texto_manual = st.text_area("O pega el texto aquí (Impar: Notas / Par: Letra):", height=200)

# Prioridad: Si hay archivo, usarlo; si no, usar el texto manual
contenido = ""
if archivo_subido is not None:
    contenido = archivo_subido.read().decode("utf-8")
elif texto_manual:
    contenido = texto_manual

# --- SECCIÓN 2: PROCESAMIENTO Y VISUALIZACIÓN ---
if contenido:
    lineas = contenido.split('\n')
    resultado_final = []
    
    st.divider()
    st.subheader("2. Visualización del Cifrado")
    
    # Contenedor con estilo para la canción
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            numero_renglon = i + 1
            
            if numero_renglon % 2 != 0:
                # Renglón IMPAR: Notas
                notas_convertidas = convertir_linea_notas(linea)
                resultado_final.append(notas_convertidas)
                # Visualización con color azul para notas
                st.markdown(f"**`:blue[{notas_convertidas}]`**") 
            else:
                # Renglón PAR: Letra
                resultado_final.append(linea)
                st.markdown(f"&nbsp;&nbsp;&nbsp;{linea}") # Sangría para la letra

    # --- SECCIÓN 3: GUARDAR Y COMPARTIR ---
    st.divider()
    st.subheader("3. Exportar")
    
    texto_para_exportar = "\n".join(resultado_final)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="💾 Descargar TXT",
            data=texto_para_exportar,
            file_name="cancion_cifrada_2026.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with col2:
        # En 2026, la opción de compartir se facilita mediante el despliegue en la nube
        if st.button("🔗 Obtener enlace para compartir", use_container_width=True):
            st.success("Para compartir, publica esta app en [Streamlit Community Cloud](https://streamlit.io).")

else:
    st.info("Sube un archivo .txt o escribe en el cuadro superior para comenzar.")
