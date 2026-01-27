import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página centrada
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    resultado_final = []
    # Patrón: Nota base + resto del acorde
    patron_universal = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        matches = list(re.finditer(patron_universal, linea, flags=re.IGNORECASE))
        
        for match in matches:
            acorde_original = match.group(0)
            raiz_orig = match.group(1).upper()
            resto_acorde = match.group(2)
            inicio, fin = match.start(), match.end()
            
            # --- FILTROS ANTI-FRASES ---
            lo_que_sigue = linea[fin:]
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            # --- CONVERSIÓN ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            
            # UNIMOS TODO: Raíz + Resto + Apóstrofe al final
            nuevo_acorde = f"{raiz_nueva}{resto_acorde}"
            
            if not (lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*")):
                nuevo_acorde += "'"

            # --- MANTENER POSICIÓN ---
            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*"):
                ancho_original += 1
            
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char
                    
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src='https://raw.githubusercontent.com' alt='Icono' style='width: 45px; height: 45px;'>
        <h1>Cancionero Pro</h1>   
    </div>""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Convierte a cifrado Americano y coloca el apóstrofe al final del acorde.</p>", unsafe_allow_html=True)

# CARGADOR DE ARCHIVOS
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    try:
        nombre_archivo = archivo.name
        contenido = archivo.getvalue().decode("utf-8")
        texto_final = procesar_texto(contenido)
        
        st.subheader("Vista Previa:")
        st.code(texto_final, language="text")

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

        components.html(f"""
            <style>
                .action-bar {{
                    position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%);
                    display: flex; gap: 15px; z-index: 9999;
                }}
                .btn {{
                    width: 150px; height: 50px; border: none; border-radius: 25px;
                    font-family: -apple-system, system-ui, sans-serif;
                    font-size: 16px; font-weight: 700; cursor: pointer;
                    display: flex; align-items: center; justify-content: center;
                    gap: 8px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    transition: transform 0.1s;
                }}
                .btn:active {{ transform: scale(0.95); }}
                .download-btn {{ background-color: #007AFF; }}
                .share-btn {{ background-color: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="dl" class="btn download-btn">💾 Guardar</button>
                <button id="sh" class="btn share-btn">📤 Compartir</button>
            </div>
            <script>
                const content = `{texto_js}`;
                const fileName = "{nombre_archivo}";

                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const url = URL.createObjectURL(b);
                    const a = document.createElement('a');
                    a.href = url; a.download = "PRO_" + fileName; a.click();
                }};

                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const file = new File([b], fileName, {{ type: 'text/plain' }});
                    if (navigator.share) {{
                        try {{ await navigator.share({{ files: [file] }}); }} 
                        catch (e) {{ if (e.name !== 'AbortError') console.log("Error:", e); }}
                    }} else {{ alert("Usa 'Guardar'"); }}
                }};
            </script>
        """, height=100)
    
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
