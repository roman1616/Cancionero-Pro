import streamlit as st
import re
import streamlit.components.v1 as components

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            fin = match.end()
            if re.match(r'^ [a-zA-ZñÑáéíóúÁÉÍÓÚ]', linea[fin:]):
                continue
            
            raiz_nueva = LATINO_A_AMERICANO.get(match.group(1).upper(), match.group(1).upper())
            nuevo_acorde = f"{raiz_nueva}{acorde_original[len(match.group(1)):]}"
            if not linea[fin:].startswith('*'): nuevo_acorde += "*"
            
            sustitucion = nuevo_acorde.ljust(len(acorde_original))
            for i, char in enumerate(sustitucion):
                if match.start() + i < len(linea_lista):
                    linea_lista[match.start() + i] = char
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.set_page_config(page_title="Procesador 2026", layout="wide")
st.title("🎸 Procesador de Acordes Inteligente")

archivo = st.file_uploader("Sube tu .txt", type="txt")

if archivo:
    nombre_archivo = archivo.name
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.code(texto_final, language="text")

    # Columnas para los botones
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button("💾 Descargar", texto_final, file_name=f"PRO_{nombre_archivo}")

    with col2:
        # Lógica para Compartir (Web Share API)
        if st.button("📤 Compartir en Móvil"):
            # Escapamos el texto para que no rompa el JS
            texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
            
            # Inyectamos el JavaScript que dispara el menú del móvil
            components.html(f"""
                <script>
                async function compartir() {{
                    const texto = `{texto_js}`;
                    const blob = new Blob([texto], {{ type: 'text/plain' }});
                    const file = new File([blob], "{nombre_archivo}", {{ type: 'text/plain' }});
                    
                    if (navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                        try {{
                            await navigator.share({{
                                files: [file],
                                title: 'Canción Procesada'
                            }});
                        }} catch (err) {{
                            console.log("Error al compartir:", err);
                        }}
                    }} else {{
                        alert("Tu navegador no soporta la función de compartir archivos directamente.");
                    }}
                }}
                compartir();
                </script>
            """, height=0)

st.info("Nota: El botón 'Compartir' funciona principalmente en navegadores móviles (Chrome Android, Safari iOS) y algunos navegadores de escritorio modernos.")
