import streamlit as st
import re

# Diccionario de conversión de Latino a Americano
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_linea_de_letra(linea, patron_acorde):
    """
    Determina si una línea es letra de canción o una línea de acordes.
    Si contiene más de 2 palabras que no parecen acordes, es letra.
    """
    palabras = linea.split()
    if not palabras:
        return False
    
    no_acordes = 0
    for p in palabras:
        if not re.fullmatch(patron_acorde, p, re.IGNORECASE):
            no_acordes += 1
    
    # Si hay más de 2 palabras normales, es una frase de la letra
    return no_acordes > 2

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    # Patrón universal para detectar la estructura de un acorde
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        # Paso 1: Si la línea parece letra pura, la dejamos intacta
        if es_linea_de_letra(linea, patron_universal):
            resultado_final.append(linea)
            continue

        # Paso 2: Procesar acordes en líneas de música
        def sustituir(match):
            acorde_completo = match.group(0)
            raiz_original = match.group(1).upper()
            pos_final = match.end()
            
            # REGLA DE ORO: Si después del acorde hay un espacio y una letra, 
            # es el comienzo de una frase (ej: "La Repandilla"). No tocar.
            lo_que_sigue = linea[pos_final:]
            if re.match(r'^[ ]+[a-zA-ZñÑáéíóúÁÉÍÓÚ]', lo_que_sigue):
                return acorde_completo

            # Si pasó los filtros, convertimos a Americano y agregamos asterisco
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_original, raiz_original)
            resto = acorde_completo[len(match.group(1)):]
            
            # Formatear: Raíz en mayúscula + resto (m, #, 7) + *
            return f"{raiz_nueva.upper()}{resto}*"

        linea_procesada = re.sub(patron_universal, sustituir, linea, flags=re.IGNORECASE)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz de Usuario con Streamlit ---
st.set_page_config(page_title="Bot de Acordes Profesional 2026", page_icon="🎸")

st.title("🎸 Procesador de Cancioneros Inteligente")
st.markdown("""
Esta aplicación:
1. Convierte notas latinas (**Do, Re, Mi...**) a americanas (**C, D, E...**).
2. Agrega un **asterisco*** a cada acorde.
3. **No toca las frases** (evita errores como "La Repandilla" o "A luz").
""")

archivo = st.file_uploader("Sube tu archivo .txt", type="txt")

if archivo:
    # Leer archivo
    contenido = archivo.read().decode("utf-8")
    
    # Procesar lógica
    texto_final = procesar_texto(contenido)
    
    # Mostrar resultados
    st.subheader("Vista Previa del Resultado:")
    st.text_area("Texto procesado:", texto_final, height=400)
    
    # Botón de descarga
    st.download_button(
        label="💾 Descargar Archivo Corregido",
        data=texto_final,
        file_name="cancionero_limpio.txt",
        mime="text/plain"
    )
