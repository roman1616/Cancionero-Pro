import streamlit as st
import re

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'do': 'C', 're': 'D', 'mi': 'E', 'fa': 'F', 
    'sol': 'G', 'la': 'A', 'si': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    for linea in lineas:
        # 1. Convertimos notas latinas (do -> C) 
        # Usamos 'in' (corregido) y Regex para evitar cambiar palabras comunes
        for lat, am in LATINO_A_AMERICANO.items():
            # Esta regex busca la nota latina ignorando mayúsculas/minúsculas
            patron_lat = re.compile(rf'\b{lat}(?=[#bm\s\-]|$)', re.IGNORECASE)
            linea = patron_lat.sub(am, linea)

        # 2. Buscamos acordes americanos y añadimos el asterisco
        def marcar_acorde(match):
            acorde = match.group(1)
            # Pasamos la primera letra a mayúscula y el resto queda igual (ej: am -> Am)
            acorde_formateado = acorde[0].upper() + acorde[1:]
            return f"{acorde_formateado}*"

        # Expresión regular para detectar acordes americanos:
        # Detecta A-G, a-g, seguidos de sostenidos, bemoles, menores, séptimas, etc.
        patron_americano = r'\b([a-gA-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)\b'
        
        linea_procesada = re.sub(patron_americano, marcar_acorde, linea)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Editor de Acordes 2026", page_icon="🎸")

st.title("🎸 Procesador de Acordes")
st.write("Sube tu archivo para convertir a cifrado americano y marcar con `*`.")

archivo = st.file_uploader("Subir archivo .txt", type="txt")

if archivo:
    # Leer el archivo correctamente
    contenido = archivo.read().decode("utf-8")
    
    # Procesar
    texto_final = procesar_texto(contenido)
    
    st.subheader("Vista Previa")
    st.text_area("Resultado:", texto_final, height=300)
    
    st.download_button(
        label="Descargar TXT",
        data=texto_final,
        file_name="cancion_procesada.txt",
        mime="text/plain"
    )
