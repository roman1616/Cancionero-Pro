import streamlit as st
import re
import streamlit.components.v1 as components
import unicodedata

# 1. Configuración de página centrada
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def quitar_acentos(texto):
    """Reemplaza caracteres acentuados por sus versiones sin acento (á -> a)."""
    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def procesar_texto(texto):
    if not texto: return ""
    
    # 1. Normalización: UTF-8 y quitar acentos (Evita símbolos raros)
    texto = quitar_acentos(texto)
    
    lineas_sucias = texto.split('\n')
    lineas_limpias = []
    for l in lineas_sucias:
        l = l.strip()
        if len(l) > 0:
            # Formato: Primera letra mayúscula, resto minúscula
            nueva_linea = l[0].upper() + l[1:].lower()
            lineas_limpias.append(nueva_linea)
        else:
            lineas_limpias.append("")
            
    resultado_final = []
    # Patrón: Nota base + resto del acorde
    patron_universal = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas_limpias:
        linea_lista = list(linea)
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            raiz_orig = match.group(1).upper()
            resto_acorde = match.group(2)
            inicio, fin = match.start(), match.end()
            
            # --- FILTROS ANTI-FRASES MEJORADOS ---
            lo_que_sigue = linea[fin:]
            
            # 1. Si la nota es una sola letra (A, E, D, etc) y lo que sigue es una letra minúscula, es una palabra, NO un acorde.
            # Ejemplo: "A esa" -> 'A' es nota, pero le sigue ' ' y luego 'e'. Se descarta.
            if len(acorde_original) == 1 and re.match(r'^[a-z]', lo_que_sigue.strip()):
                continue

            # 2. Evitar que detecte letras dentro de palabras (Ej: "pArtA")
            if inicio > 0 and linea[inicio-1].isalpha(): 
                continue
            
            # 3. Si lo que sigue es texto normal (letras minúsculas pegadas o con espacio)
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue

            # --- CONVERSIÓN ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
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

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    try:
        raw_bytes = archivo.getvalue()
        try:
            contenido = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            contenido = raw_bytes.decode("latin-1")
            
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
                const fileName = "{archivo.name}";

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
        st.error(f"Error: {e}")
