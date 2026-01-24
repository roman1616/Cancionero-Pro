import streamlit as st
import re

# Mapa de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    # Regex que busca notas latinas (do, re...) O americanas (a, b, c...)
    # Ignorando mayúsculas/minúsculas y permitiendo alteraciones (#, b, m, etc.)
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        def sustituir(match):
            acorde_original = match.group(0)
            
            # 1. Extraer la raíz (ej: de "rem" extrae "re")
            raiz = match.group(1).upper()
            resto = acorde_original[len(match.group(1)):]

            # 2. Si la raíz es latina, traducirla a americana
            if raiz in LATINO_A_AMERICANO:
                raiz = LATINO_A_AMERICANO[raiz]
            
            # 3. Formatear (Mayúscula la raíz + resto + asterisco)
            return f"{raiz.upper()}{resto}*"

        # Aplicamos la sustitución solo en los casos que encajen con el patrón
        linea_procesada = re.sub(patron_universal, sustituir, linea, flags=re.IGNORECASE)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Editor de Acordes 2026", page_icon="🎸")
st.title("🎸 Procesador de Acordes")

archivo = st.file_uploader("Subir archivo .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    st.text_area("Resultado:", texto_final, height=300)
    st.download_button("Descargar TXT", texto_final, "cancion_procesada.txt")
