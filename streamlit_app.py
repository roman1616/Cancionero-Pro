import streamlit as st
import re

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        # --- NUEVO FILTRO DE SEGURIDAD ---
        # Si la línea tiene más de 3 palabras que NO son acordes, asumimos que es LETRA.
        # Esto evita que "La Repandilla" o "A luz" se procesen.
        palabras = linea.split()
        es_linea_de_acordes = True
        
        if len(palabras) > 0:
            no_acordes = 0
            for p in palabras:
                # Si la palabra no encaja con la estructura de un acorde, sumamos
                if not re.fullmatch(patron_universal, p, re.IGNORECASE):
                    no_acordes += 1
            
            # Si hay más de 2 palabras normales, es una frase de la canción.
            if no_acordes > 2:
                es_linea_de_acordes = False

        if not es_linea_de_acordes:
            resultado_final.append(linea)
            continue

        # Si pasamos el filtro, procesamos los acordes de esa línea
        def sustituir(match):
            acorde_completo = match.group(0)
            raiz_original = match.group(1).upper()
            
            # Convertimos y marcamos
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_original, raiz_original)
            resto = acorde_completo[len(match.group(1)):]
            return f"{raiz_nueva.upper()}{resto}*"

        linea_procesada = re.sub(patron_universal, sustituir, linea, flags=re.IGNORECASE)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz ---
st.set_page_config(page_title="Editor 2026", page_icon="🎸")
st.title("🎸 Procesador Anti-Errores de Frase")

archivo = st.file_uploader("Subir archivo .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    st.text_area("Resultado:", texto_final, height=350)
    st.download_button("Descargar TXT", texto_final, "cancionero.txt")
