import streamlit as st
import re

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    # Patrón para detectar la estructura de un acorde (Latino o Americano)
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        def sustituir(match):
            acorde_completo = match.group(0)
            raiz_original = match.group(1).upper()
            inicio_pos = match.start()
            
            # --- REGLA DE ESPACIO A LA IZQUIERDA ---
            # Verificamos si el acorde está al puro inicio de la línea (pos 0)
            # O si tiene un espacio justo antes.
            es_inicio_linea = (inicio_pos == 0)
            tiene_espacio_izq = False
            if inicio_pos > 0:
                tiene_espacio_izq = linea[inicio_pos-1].isspace()

            # Si es el inicio de la línea y hay texto inmediatamente después (sin muchos espacios),
            # o si NO tiene espacio a la izquierda, probablemente es parte de la letra.
            # EXCEPCIÓN: Si la línea entera es SOLO el acorde, sí lo marcamos.
            if es_inicio_linea and len(linea.strip()) > len(acorde_completo):
                # Si lo que sigue después del acorde es texto pegado o un solo espacio y texto, es letra.
                lo_que_sigue = linea[match.end():]
                if re.match(r'^[ ]?[a-zA-ZñÑáéíóú]', lo_que_sigue):
                    return acorde_completo
            
            if not es_inicio_linea and not tiene_espacio_izq:
                return acorde_completo

            # --- CONVERSIÓN Y MARCADO ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_original, raiz_original)
            resto = acorde_completo[len(match.group(1)):]
            return f"{raiz_nueva.upper()}{resto}*"

        linea_procesada = re.sub(patron_universal, sustituir, linea, flags=re.IGNORECASE)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Editor de Acordes Pro 2026", page_icon="🎹")
st.title("🎸 Procesador de Acordes con Filtro de Posición")
st.write("Solo marca acordes que tienen espacios a la izquierda o están aislados.")

archivo = st.file_uploader("Subir archivo .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    st.text_area("Resultado:", texto_final, height=350)
    st.download_button("Descargar TXT", texto_final, "cancionero_posicional.txt")

