import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []
    patron_universal = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            fin = match.end()
            lo_que_sigue = linea[fin:]
            if inicio := match.start():
                if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            raiz_nueva = LATINO_A_AMERICANO.get(match.group(1).upper(), match.group(1).upper())
            nuevo_acorde = f"{raiz_nueva}{match.group(2)}"
            if not (lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*")):
                nuevo_acorde += "'"

            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*"): ancho_original += 1
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if match.start() + i < len(linea_lista):
                    linea_lista[match.start() + i] = char
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)

# Cargador de archivos
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    try:
        nombre_archivo = archivo.name
        contenido = archivo.read().decode("utf-8")
        texto_final = procesar_texto(contenido)
        
        st.subheader("Vista Previa:")
        st.code(texto_final, language="text")

        # Inyectamos los botones SOLO cuando el archivo ya está cargado y procesado
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        
        components.html(f"""
            <style>
                .action-bar {{
                    position: fixed;
                    bottom: 30px;
                    left: 50%;
                    transform: translateX(-50%);
                    display: flex;
                    gap: 15px;
                    z-index: 9999;
                }}
                .btn {{
                    width: 140px;
                    height: 45px;
                    border: none;
                    border-radius: 25px;
                    font-family: sans-serif;
                    font-size: 15px;
                    font-weight: bold;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    color: white;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                }}
                .download-btn {{ background-color: #007AFF; }}
                .share-btn {{ background-color: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="btnDL" class="btn download-btn">💾 Guardar</button>
                <button id="btnSH" class="btn share-btn">📤 Compartir</button>
            </div>
            <script>
                const content = `{texto_js}`;
                document.getElementById('btnDL').onclick = () => {{
                    const blob = new Blob([content], {{ type: 'text/plain' }});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = "PRO_{nombre_archivo}";
                    a.click();
                }};
                document.getElementById('btnSH').onclick = async () => {{
                    const blob = new Blob([content], {{ type: 'text/plain' }});
                    const file = new File([blob], "{nombre_archivo}", {{ type: 'text/plain' }});
                    if (navigator.share) {{
                        try {{ await navigator.share({{ files: [file] }}); }} catch (e) {{}}
                    }}
                }};
            </script>
        """, height=100)
    except Exception as e:
        st.error(f"Error al procesar: {{e}}")

