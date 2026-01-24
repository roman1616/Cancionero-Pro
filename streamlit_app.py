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
        # 1. Convertir Latino a Americano primero
        for lat, am in LATINO_A_AMERICANO.items():
            patron_lat = re.compile(rf'\b{lat}(?=[#bm\s\-]|$)', re.IGNORECASE)
            linea = patron_lat.sub(am, linea)

        # 2. Lógica de detección de acordes con "Aislamiento"
        # Esta Regex busca el acorde solo si:
        # - Está rodeado de al menos 2 espacios: (?:\s{2,})
        # - O está al inicio/final de línea: (^|$)
        # - O está junto a caracteres especiales de música: ([\(\)\-\/])
        
        patron_acorde = r'([a-gA-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'
        
        # El acorde debe tener aire (espacios o símbolos) para ser procesado
        espaciado = r'(?:^|\s{2,}|\(|\-|/)'
        final_acorde = r'(?:\s{2,}|$|\)|\-|/)'
        
        def marcador(match):
            # match.group(0) incluye los espacios, match.group(2) es el acorde puro
            acorde_puro = match.group(2)
            # Formatear: Primera letra Mayúscula
            acorde_formateado = acorde_puro.upper() + acorde_puro[1:]
            # Reconstruimos la cadena con el asterisco y los espacios originales
            return f"{match.group(1)}{acorde_formateado}*{match.group(3)}"

        # Unimos todo: (prefijo)(ACORDE)(sufijo)
        regex_completa = rf'({espaciado}){patron_acorde}({final_acorde})'
        
        # Aplicamos la lógica (se hace dos veces para casos de acordes muy juntos)
        linea_procesada = re.sub(regex_completa, marcador, linea)
        linea_procesada = re.sub(regex_completa, marcador, linea_procesada)
        
        resultado_final.append(linea_procesada)

    return '\n'.join(resultado_final)

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Procesador Profesional 2026", page_icon="🎹")
st.title("🎸 Bot de Acordes Inteligente")
st.markdown("""
Esta versión solo marca notas que:
* Tienen **2 o más espacios** alrededor.
* Están en **paréntesis, guiones o barras**.
* Están al **principio o final** de la línea.
""")

archivo = st.file_uploader("Sube tu TXT", type="txt")

if archivo:
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Resultado:")
    st.text_area("Cifrado:", texto_final, height=400)
    
    st.download_button("Descargar Archivo", texto_final, "cancionero.txt")

