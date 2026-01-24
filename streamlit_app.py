import streamlit as st
import re

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    # Patrón para detectar la estructura de un acorde
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        def sustituir(match):
            acorde_completo = match.group(0)
            raiz_original = match.group(1).upper()
            inicio_pos = match.start()
            fin_pos = match.end()
            
            # --- NUEVA LÓGICA DE DETECCIÓN POR AISLAMIENTO ---
            
            # 1. Miramos qué hay después
            lo_que_sigue = linea[fin_pos:]
            # Si lo que sigue es una letra minúscula pegada (ej: "La " + "luz"), es letra.
            # Pero si hay muchos espacios (acorde) o es el fin de línea, es ACORDE.
            if re.match(r'^[ ]{1}[a-zñáéíóú]', lo_que_sigue):
                return acorde_completo

            # 2. Miramos qué hay antes
            # Si el acorde NO está al inicio y NO tiene espacio antes, es parte de una palabra.
            if inicio_pos > 0 and not linea[inicio_pos-1].isspace():
                return acorde_completo

            # 3. Caso especial: "La" o "A" al inicio de una frase larga
            # Si está al inicio pero lo que sigue es texto normal a poca distancia, es letra.
            if inicio_pos == 0 and len(linea) > len(acorde_completo) + 2:
                if re.match(r'^[ ]?[a-zñáéíóúA-Z]', lo_que_sigue):
                    # Solo lo marcamos si después hay un espacio muy grande (típico de línea de acordes)
                    if not lo_que_sigue.startswith("  "):
                        return acorde_completo

            # --- SI PASA LOS FILTROS, CONVERTIR ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_original, raiz_original)
            resto = acorde_completo[len(match.group(1)):]
            
            # Si ya tiene un asterisco (porque el usuario lo puso), no ponemos otro
            if lo_que_sigue.startswith('*'):
                return f"{raiz_nueva.upper()}{resto}"
                
            return f"{raiz_nueva.upper()}{resto}*"

        # Ejecutamos la sustitución
        linea_procesada = re.sub(patron_universal, sustituir, linea, flags=re.IGNORECASE)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Editor de Acordes 2026", page_icon="🎸")
st.title("🎸 Procesador de Acordes Mixtos")
st.write("Detecta acordes incluso si hay letra en la misma línea, protegiendo las palabras.")

archivo = st.file_uploader("Sube tu .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    st.text_area("Resultado:", texto_final, height=400)
    st.download_button("Descargar TXT", texto_final, "cancion_corregida.txt")
