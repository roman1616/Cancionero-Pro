import streamlit as st
import re
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión base
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    if not texto: return ""
    
    # Aseguramos que el texto sea tratado como string (ya viene decodificado de bytes)
    lineas = texto.split('\n')
    resultado_final = []
    
    # Regex que busca: Nota Latina (grupo 1) + Sostenido/Bemol (grupo 2) + resto (grupo 3)
    # Ejemplo en "SOL#m7": G1=SOL, G2=#, G3=m7
    patron = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#b]?)(m|maj|min|aug|dim|sus|add|M|[0-9]*)'

    for linea in lineas:
        def reemplazar(match):
            nota_lat = match.group(1).upper()
            alteracion = match.group(2) # El # o b
            resto = match.group(3)      # El m, 7, etc.
            
            # 1. Convertir nota base
            nota_ame = LATINO_A_AMERICANO.get(nota_lat, nota_lat)
            
            # 2. Reconstruir: Nota Americana + Alteración + Modo + Apóstrofe
            # Ejemplo: LA + # + m -> A + # + m + '
            acorde_transformado = f"{nota_ame}{alteracion}{resto}'"
            return acorde_transformado

        # Reemplazo con ignorar mayúsculas para capturar "lam" o "LaM"
        nueva_linea = re.sub(patron, reemplazar, linea, flags=re.IGNORECASE)
        resultado_final.append(nueva_linea)
        
    return '\n'.join(resultado_final)

# --- INTERFAZ STREAMLIT ---
st.markdown("""
    <div style='text-align: center;'>
        <h1>🎸 Cancionero Pro 2026</h1>
        <p>Conversión exacta a Cifrado Americano con Apóstrofe</p>
    </div>""", unsafe_allow_html=True)

# Cargador de archivos con forzado de encoding
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    try:
        # LEER Y FORZAR UTF-8
        bytes_data = archivo.read()
        contenido = bytes_data.decode("utf-8", errors="ignore")
        
        texto_final = procesar_texto(contenido)
        
        st.subheader("Vista Previa (UTF-8):")
        st.code(texto_final, language="text")

        # Preparar para descarga/compartir
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        
        components.html(f"""
            <script>
                const content = `{texto_js}`;
                const blob = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                
                window.parent.document.addEventListener('keydown', e => {{}}); // dummy
                
                function descargar() {{
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url; a.download = "PRO_{archivo.name}";
                    a.click();
                }}

                async function compartir() {{
                    const file = new File([blob], "{archivo.name}", {{ type: 'text/plain' }});
                    if (navigator.share) {{
                        await navigator.share({{ files: [file], title: 'Cancionero Pro' }});
                    }} else {{ alert("Usa 'Guardar'"); }}
                }}
            </script>
            <div style="display: flex; gap: 10px; justify-content: center; padding-top: 20px;">
                <button onclick="descargar()" style="padding: 15px 30px; border-radius: 25px; background: #007AFF; color: white; border: none; font-weight: bold; cursor: pointer;">💾 Guardar .txt</button>
                <button onclick="compartir()" style="padding: 15px 30px; border-radius: 25px; background: #34C759; color: white; border: none; font-weight: bold; cursor: pointer;">📤 Compartir</button>
            </div>
        """, height=100)

    except Exception as e:
        st.error(f"Error procesando el archivo UTF-8: {e}")
