import streamlit as st
import re

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'do': 'C', 're': 'D', 'mi': 'E', 'fa': 'F', 
    'sol': 'G', 'la': 'A', 'si': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []

    for linea in lineas:
        # 1. Primero convertimos notas latinas (do -> C) sin importar mayúsculas
        for lat, am en LATINO_A_AMERICANO.items():
            # Buscamos la nota latina seguida opcionalmente de #, b, m, etc.
            # Ejemplo: "rem" -> "Dm", "Sol#" -> "G#"
            patron_lat = re.compile(rf'\b{lat}(?=[#bm\s]|$)', re.IGNORECASE)
            linea = patron_lat.sub(am, linea)

        # 2. Ahora buscamos todos los acordes americanos (A-G)
        # Incluye minúsculas (a-g) y las convierte a Mayúscula + Asterisco
        def marcar_acorde(match):
            acorde = match.group(1)
            # Aseguramos que la primera letra sea mayúscula (estilo americano estándar)
            acorde_formateado = acorde[0].upper() + acorde[1:]
            return f"{acorde_formateado}*"

        # Expresión regular robusta para acordes americanos (C, Am, G#, Bb, D/F#, etc.)
        patron_americano = r'\b([a-gA-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)\b'
        
        linea_procesada = re.sub(patron_americano, marcar_acorde, linea)
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz de la Aplicación Web ---
st.set_page_config(page_title="Music Transpiler 2026", page_icon="🎸")

st.title("🎸 Procesador de Acordes Universal")
st.info("Convierte 'do, re, mi' a 'C*, D*, E*' y procesa 'a, b, c' a 'A*, B*, C*'.")

archivo = st.file_uploader("Arrastra aquí tu archivo .txt", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Resultado del procesamiento:")
    st.text_area("Cifrado corregido:", texto_final, height=350)
    
    st.download_button(
        label="💾 Descargar TXT Procesado",
        data=texto_final,
        file_name="acordes_listos.txt",
        mime="text/plain"
    )
