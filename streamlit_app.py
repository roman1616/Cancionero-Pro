import streamlit as st
import re

LATINO_A_AMERICANO = {
    'do': 'C', 're': 'D', 'mi': 'E', 'fa': 'F', 
    'sol': 'G', 'la': 'A', 'si': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    for linea in lineas:
        # 1. Convertir Latino a Americano (ej: "re" -> "D")
        for lat, am in LATINO_A_AMERICANO.items():
            # Solo convierte si es la nota sola o seguida de símbolos musicales
            patron_lat = re.compile(rf'\b{lat}(?=[#bm\s\-\(\/]|$) \b', re.IGNORECASE)
            # Nota: Usamos una búsqueda simple para la conversión inicial
            linea = re.sub(rf'\b{lat}\b', am, linea, flags=re.IGNORECASE)

        # 2. Lógica de Marcado con Filtro de Palabras
        # Buscamos patrones de acordes (A-G)
        patron_acorde = r'\b([a-gA-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)\b'
        
        def marcador(match):
            acorde = match.group(1)
            inicio_pos = match.end()
            
            # REGLA DE ORO: Miramos qué hay justo después del acorde
            # Si lo que sigue es un espacio y luego una letra minúscula, es una PALABRA.
            resto_linea = linea[inicio_pos:]
            # Si detecta espacio + letra minúscula (ej: "D esta cancion"), NO marca.
            if re.match(r'^[ ]+[a-zñáéíóú]', resto_linea):
                return acorde
            
            # Si no es una palabra, formateamos y ponemos asterisco
            acorde_formateado = acorde.upper() + acorde[1:]
            return f"{acorde_formateado}*"

        linea_procesada = re.sub(patron_acorde, marcador, linea)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz Web ---
st.set_page_config(page_title="Procesador Acordes 2026", page_icon="📝")
st.title("🤖 Bot de Cifrado Inteligente")
st.write("Diferencia entre acordes y palabras de la letra automáticamente.")

archivo = st.file_uploader("Sube tu archivo .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Resultado:")
    st.text_area("Contenido procesado:", texto_final, height=400)
    
    st.download_button("Descargar TXT", texto_final, "cancion_marcada.txt")

