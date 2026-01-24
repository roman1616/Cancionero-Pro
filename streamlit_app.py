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
        # Usamos una lista de caracteres para poder modificar la línea por posición
        linea_lista = list(linea)
        offset = 0 # Para controlar el desplazamiento si fuera necesario

        # Buscamos todos los acordes en la línea
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            inicio = match.start()
            fin = match.end()
            raiz_orig = match.group(1).upper()
            
            # --- REGLA DE EXCLUSIÓN PARA FRASES (Ej: La Repandilla) ---
            lo_que_sigue = linea[fin:]
            # Si hay un solo espacio y luego una letra, es una palabra, no un acorde
            if re.match(r'^ [a-zA-ZñÑáéíóú]', lo_que_sigue):
                continue
            
            # --- CONVERSIÓN ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            resto = acorde_original[len(match.group(1)):]
            
            # Si ya tiene asterisco, no lo duplicamos
            nuevo_acorde = f"{raiz_nueva.upper()}{resto}"
            if not lo_que_sigue.startswith('*'):
                nuevo_acorde += "*"

            # --- COMPENSACIÓN DE ESPACIOS (MANTENER POSICIÓN) ---
            # Calculamos la diferencia de longitud entre el original y el nuevo
            len_orig = len(acorde_original)
            # Si el nuevo es más largo, lo ponemos tal cual (moverá un poco)
            # Si el nuevo es más corto, rellenamos con espacios para que lo siguiente no se mueva
            espacios_relleno = ""
            if len(nuevo_acorde) < len_orig:
                espacios_relleno = " " * (len_orig - len(nuevo_acorde))
            
            # Reemplazamos en la línea respetando el ancho original si es posible
            sustitucion = nuevo_acorde + espacios_relleno
            
            # Como modificar una lista mientras iteramos es complejo, 
            # guardamos los cambios para aplicarlos al final de la línea
            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char

        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Editor de Acordes Pro 2026", layout="wide")
st.title("🎸 Procesador de Acordes con Posicionamiento Fijo")
st.write("Convierte a americano y añade `*` manteniendo los acordes justo encima de la letra.")

archivo = st.file_uploader("Sube tu archivo .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Resultado (Usa fuente Monoespaciada):")
    # Usamos st.code para que se vea con fuente de ancho fijo (Courier)
    st.code(texto_final, language="text")
    
    st.download_button("Descargar TXT", texto_final, "cancionero_alineado.txt")
