import streamlit as st
import re

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        linea_lista = list(linea)
        
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            raiz_original = match.group(1).upper()
            inicio = match.start()
            fin = match.end()
            
            lo_que_sigue = linea[fin:]
            if re.match(r'^ [a-zA-ZñÑáéíóúÁÉÍÓÚ]', lo_que_sigue):
                continue
            
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_original, raiz_original)
            resto_acorde = acorde_original[len(match.group(1)):]
            
            nuevo_acorde = f"{raiz_nueva}{resto_acorde}"
            if not lo_que_sigue.startswith('*'):
                nuevo_acorde += "*"

            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith('*'):
                ancho_original += 1
            
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char

        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- Interfaz de Streamlit ---

st.set_page_config(page_title="Editor de Acordes Pro 2026", layout="wide")

st.title("🎸 Procesador de Acordes con Posicionamiento Fijo")
st.write("Convierte a americano y añade `*` manteniendo los acordes justo encima de la letra.")

# Usamos el widget de carga de archivos de Streamlit
uploaded_file = st.file_uploader("Sube tu archivo .txt", type="txt")

if uploaded_file is not None:
    # Leer el archivo automáticamente por Streamlit
    contenido = uploaded_file.read().decode("utf-8")
    
    # Procesar lógica
    texto_final = procesar_texto(contenido)
    
    st.subheader("Vista Previa (Alineación fija):")
    # Usamos st.code para asegurar que se vea con fuente monoespaciada
    st.code(texto_final, language="text")
    
    # Botón de descarga con el nombre del archivo original
    st.download_button(
        label="💾 Descargar TXT",
        data=texto_final,
        file_name=f"{uploaded_file.name.replace('.txt', '')}.txt",
        mime="text/plain"
    )

    st.markdown("---")
    # Texto adicional que imita el comportamiento de compartir que pediste:
    if st.button("Simular Compartir (Compartir en móvil)"):
        st.success("¡Listo para compartir! En un dispositivo móvil, el navegador te daría opciones (WhatsApp, Email, etc.) tras la descarga.")
