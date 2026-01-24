import streamlit as st
import re

# 1. Configuración inicial (Debe ser la primera instrucción)
st.set_page_config(page_title="Cancionero Pro", page_icon="🎸")

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []
    # Patrón para detectar notas latinas o americanas
    patron = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron, linea, flags=re.IGNORECASE):
            inicio, fin = match.start(), match.end()
            raiz_orig = match.group(1).upper()
            resto = match.group(2)
            
            # Filtros para evitar palabras comunes
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^[a-zñáéíóú]', linea[fin:]): continue

            # Conversión y agregado de apóstrofe
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            nuevo_acorde = f"{raiz_nueva}{resto}"
            if not linea[fin:].startswith("'"):
                nuevo_acorde += "'"
            
            # Mantener alineación rellenando con espacios si es necesario
            sustitucion = nuevo_acorde.ljust(len(match.group(0)) + (1 if not linea[fin:].startswith("'") else 0))
            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.title("🎸 Cancionero Pro")
st.markdown("Sube tu archivo `.txt` para convertir los acordes automáticamente.")

archivo = st.file_uploader("Selecciona un archivo .txt", type="txt")

if archivo:
    # Leer contenido del archivo
    # Usamos .getvalue() para evitar que el buffer se vacíe al re-ejecutar
    contenido = archivo.getvalue().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Vista Previa")
    st.code(texto_final, language="text")

    # Botón de descarga NATIVO (Más fiable que el componente HTML/JS)
    st.download_button(
        label="💾 Descargar Archivo Procesado",
        data=texto_final,
        file_name=f"PRO_{archivo.name}",
        mime="text/plain"
    )
else:
    st.info("Por favor, sube un archivo para continuar.")


