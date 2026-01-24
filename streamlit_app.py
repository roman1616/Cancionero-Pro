import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página centrada
st.set_page_config(page_title="Cancionero Pro", layout="centered")

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
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            raiz_orig = match.group(1).upper()
            resto_acorde = match.group(2)
            inicio, fin = match.start(), match.end()
            
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            lo_que_sigue = linea[fin:]
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            nuevo_acorde = f"{raiz_nueva}{resto_acorde}"
            if not lo_que_sigue.startswith("'"): nuevo_acorde += "'"

            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith("'"): ancho_original += 1
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Usa el botón de abajo para cargar tu .txt (Compatible con Dropbox en Android).</p>", unsafe_allow_html=True)

# CARGADOR DE ARCHIVOS NATIVO (BYPASS DE RED)
# Este componente lee el archivo LOCALMENTE y lo pasa a Streamlit como texto plano.
uploader_html = """
    <div style="display: flex; flex-direction: column; align-items: center; gap: 15px; font-family: sans-serif;">
        <input type="file" id="fileInput" accept=".txt" style="display: none;">
        <button id="btnLoad" onclick="document.getElementById('fileInput').click()" 
            style="background-color: #007AFF; color: white; padding: 15px 30px; border-radius: 50px; border: none; cursor: pointer; font-weight: 700; font-size: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            📁 Cargar Archivo .txt
        </button>
        <p id="info" style="color: #666; font-size: 14px;">Ningún archivo seleccionado</p>
    </div>
    <script>
        const input = document.getElementById('fileInput');
        const info = document.getElementById('info');
        
        input.onchange = e => {
            const file = e.target.files[0];
            if (!file) return;
            info.innerText = "Procesando: " + file.name;
            const reader = new FileReader();
            reader.onload = event => {
                // Truco para 2026: Usamos setComponentValue con un pequeño delay para asegurar la recepción
                const data = {content: event.target.result, name: file.name};
                window.parent.postMessage({
                    isStreamlitMessage: true,
                    type: "streamlit:setComponentValue",
                    value: data
                }, "*");
            };
            reader.readAsText(file);
        };
    </script>
"""

# Ejecutamos el componente
raw_data = components.html(uploader_html, height=140)

# Verificamos si recibimos datos del componente
if st.session_state.get("component_value"):
    datos = st.session_state.get("component_value")
    nombre_archivo = datos['name']
    texto_final = procesar_texto(datos['content'])
    
    st.subheader("Vista Previa:")
    st.code(texto_final, language="text")

    texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

    # BARRA DE ACCIONES FLOTANTE
    components.html(f"""
        <style>
            .action-bar {{ position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 9999; }}
            .btn {{ width: 150px; height: 50px; border: none; border-radius: 25px; font-family: sans-serif; font-size: 16px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: transform 0.1s; }}
            .btn:active {{ transform: scale(0.95); }}
            .download-btn {{ background-color: #007AFF; }}
            .share-btn {{ background-color: #34C759; }}
        </style>
        <div class="action-bar">
            <button id="btnDL" class="btn download-btn">💾 Guardar</button>
            <button id="btnSH" class="btn share-btn">📤 Compartir</button>
        </div>
        <script>
            const content = `{texto_js}`;
            const fileName = "{nombre_archivo}";
            document.getElementById('btnDL').onclick = () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = "PRO_" + fileName; a.click();
            }};
            document.getElementById('btnSH').onclick = async () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const file = new File([blob], fileName, {{ type: 'text/plain' }});
                if (navigator.share) {{ try {{ await navigator.share({{ files: [file] }}); }} catch (e) {{}} }}
            }};
        </script>
    """, height=100)

