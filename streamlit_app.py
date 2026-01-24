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

    # Patrón para detectar acordes (latino o americano)
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        def sustituir(match):
            acorde_completo = match.group(0)
            raiz_original = match.group(1).upper()
            pos_final = match.end()
            
            # --- REGLA DE ORO PARA 2026: DISTANCIA DE PALABRA ---
            lo_que_sigue = linea[pos_final:]
            
            # 1. Si después del "La" hay un solo espacio y luego letras, es LETRA (ej: "La Repandilla")
            # Los acordes reales suelen tener 2 o más espacios después o ser el final de la línea.
            if re.match(r'^ [a-zA-ZñÑáéíóú]', lo_que_sigue):
                return acorde_completo

            # 2. Si el acorde ya tiene un asterisco, no hacemos nada más
            if lo_que_sigue.startswith('*'):
                return acorde_completo

            # --- CONVERSIÓN ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_original, raiz_original)
            resto = acorde_completo[len(match.group(1)):]
            
            return f"{raiz_nueva.upper()}{resto}*"

        # Aplicar la lógica
        linea_procesada = re.sub(patron_universal, sustituir, linea, flags=re.IGNORECASE)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Editor de Acordes Pro 2026", page_icon="🎸")
st.title("🎸 Procesador de Acordes Inteligente")
st.write("Corrige automáticamente 'La Repandilla' para que no se marque como acorde.")

archivo = st.file_uploader("Sube tu archivo .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Resultado:")
    st.text_area("Contenido procesado:", texto_final, height=400)
    
    st.download_button("Descargar TXT", texto_final, "cancionero_limpio.txt")
