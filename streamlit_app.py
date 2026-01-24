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

    # Patron que busca notas latinas o letras A-G
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        def sustituir(match):
            acorde_completo = match.group(0)
            raiz_original = match.group(1).upper()
            pos_final = match.end()
            
            # --- VALIDACIÓN DE CONTEXTO ---
            # Miramos qué hay después del supuesto acorde
            lo_que_sigue = linea[pos_final:]
            
            # Si después hay un espacio y una letra minúscula (ej: "A luz", "D esta")
            # NO lo marcamos como acorde porque es parte de la letra.
            if re.match(r'^[ ]+[a-zñáéíóú]', lo_que_sigue):
                return acorde_completo

            # --- PROCESO DE CONVERSIÓN ---
            # Si pasó la validación, traducimos de latino a americano si hace falta
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_original, raiz_original)
            
            # Reconstruimos el acorde (ej: rem -> Dm)
            resto = acorde_completo[len(match.group(1)):]
            return f"{raiz_nueva.upper()}{resto}*"

        linea_procesada = re.sub(patron_universal, sustituir, linea, flags=re.IGNORECASE)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Editor de Acordes 2026", page_icon="🎸")
st.title("🎸 Procesador de Acordes Inteligente")

archivo = st.file_uploader("Subir archivo .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    st.subheader("Resultado:")
    st.text_area("Contenido:", texto_final, height=300)
    st.download_button("Descargar TXT", texto_final, "cancionero_limpio.txt")
