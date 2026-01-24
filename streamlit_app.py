import streamlit as st
import re

# Diccionario para usar SOLO cuando confirmemos que es un acorde
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    # Buscamos patrones que parecen acordes (latino o americano)
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        def sustituir(match):
            acorde_candidato = match.group(0)
            raiz_original = match.group(1).upper()
            inicio_pos = match.start()
            
            # --- VALIDACIÓN DE POSICIÓN (¿Es realmente un acorde?) ---
            # Un acorde debe tener al menos un espacio a la izquierda 
            # O ser la única palabra en la línea.
            tiene_espacio_izq = inicio_pos > 0 and linea[inicio_pos-1].isspace()
            es_unico_en_linea = linea.strip() == acorde_candidato
            
            # Si NO tiene espacio a la izquierda y NO es lo único en la línea:
            # Es una palabra (como "La casa" o "prende A luz"). NO TOCAR.
            if not tiene_espacio_izq and not es_unico_en_linea:
                return acorde_candidato

            # --- SI PASÓ LA VALIDACIÓN: CONVERTIR Y MARCAR ---
            # Ahora que sabemos que es un acorde, lo pasamos a Americano
            raiz_americana = LATINO_A_AMERICANO.get(raiz_original, raiz_original)
            
            # Mantener alteraciones (m, #, 7, etc.)
            resto = acorde_candidato[len(match.group(1)):]
            
            return f"{raiz_americana.upper()}{resto}*"

        linea_procesada = re.sub(patron_universal, sustituir, linea, flags=re.IGNORECASE)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Conversor Inteligente 2026")
st.title("🎸 Procesador de Acordes Latino a Americano")
st.write("Solo traduce y marca si detecta que es un acorde por su posición.")

archivo = st.file_uploader("Subir .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    st.text_area("Resultado:", texto_final, height=400)
    st.download_button("Descargar", texto_final, "cancionero_americano.txt")
