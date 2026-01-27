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

st.set_page_config(page_title="Conversor de Cifrado Americano 2026", layout="wide")

st.title("🎵 Modificador de Notas a Cifrado Americano")
st.markdown("""
**Instrucciones:** Ingresa el contenido línea por línea. 
- Los **renglones impares (1, 3, 5...)** se tratarán como **notas** (ej: Do Re Mi).
- Los **renglones pares (2, 4, 6...)** se tratarán como **letra** de la canción.
""")

# Entrada de texto
texto_input = st.text_area("Pega aquí tu canción (alternando notas y letra):", height=300, 
                          placeholder="Ejemplo:\nDo Re Mi\nEsta es la letra\nFa Sol La\nSegunda línea de letra")

if texto_input:
    lineas = texto_input.split('\n')
    resultado_final = []
    
    st.subheader("Visualización del Resultado")
    
    # Contenedor para la visualización con estilo de acordes
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            numero_renglon = i + 1
            if numero_renglon % 2 != 0:
                # Línea impar: Notas -> Convertir
                notas_convertidas = convertir_linea_notas(linea)
                resultado_final.append(notas_convertidas)
                st.markdown(f"**`{notas_convertidas}`**") # Estilo resaltado para notas
            else:
                # Línea par: Letra -> Mantener
                resultado_final.append(linea)
                st.write(linea)
    
    texto_para_guardar = "\n".join(resultado_final)
    
    # Opciones de Guardar y Compartir
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="💾 Descargar como .txt",
            data=texto_para_guardar,
            file_name="cancion_cifrada_2026.txt",
            mime="text/plain"
        )
        
    with col2:
        if st.button("🔗 Generar enlace para compartir (Simulado)"):
            st.info("En 2026, puedes desplegar esta app en [Streamlit Community Cloud](https://streamlit.io) para obtener un enlace permanente.")

else:
    st.info("Esperando entrada de texto...")
