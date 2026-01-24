import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

MAPA = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'}

def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    res = []
    patron = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'
    for linea in lineas:
        lista = list(linea)
        for m in re.finditer(patron, linea, flags=re.IGNORECASE):
            ini, fin = m.start(), m.end()
            if ini > 0 and linea[ini-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', linea[fin:]): continue
            raiz_nueva = MAPA.get(m.group(1).upper(), m.group(1).upper())
            acorde = f"{raiz_nueva}{m.group(2)}'"
            sustitucion = acorde.ljust(len(m.group(0)) + 1)
            for i, char in enumerate(sustitucion):
                if ini + i < len(lista): lista[ini + i] = char
        res.append("".join(lista))
    return '\n'.join(res)

st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)

# --- CARGADOR NATIVO (SOLUCIÓN PARA ANDROID) ---
# Este componente lee el archivo directamente en el móvil y se lo pasa a Python
st.write("### 📁 Paso 1: Carga tu archivo")
html_uploader = """
    <div style="border: 2px dashed #ccc; padding: 20px; text-align: center; border-radius: 10px; font-family: sans-serif;">
        <input type="file" id="fileInput" accept=".txt" style="display: none;">
        <button onclick="document.getElementById('fileInput').click()" style="padding: 10px 20px; background: #007AFF; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
            Seleccionar archivo .txt
        </button>
        <p id="status" style="margin-top: 10px; color: #666;">Compatible con Dropbox y Drive</p>
    </div>
    <script>
        const input = document.getElementById('fileInput');
        input.onchange = e => {
            const file = e.target.files[0];
            const reader = new FileReader();
            document.getElementById('status').innerText = "Procesando: " + file.name;
            reader.onload = event => {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: event.target.result
                }, '*');
            };
            reader.readAsText(file);
        };
    </script>
"""
# Capturamos el contenido del archivo desde el componente HTML
contenido_archivo = components.html(html_uploader, height=150)

# Streamlit captura el valor enviado por postMessage automáticamente en session_state
if "manual_content" not in st.session_state:
    st.session_state.manual_content = ""

# --- PROCESAMIENTO Y VISTA PREVIA ---
# Si el componente HTML envió datos, los procesamos
if st.session_state.get("component_value"):
    contenido_final = st.session_state.get("component_value")
    texto_pro = procesar_texto(contenido_final)
    
    st.subheader("Vista Previa:")
    st.code(texto_pro, language="text")

    # Botones flotantes corregidos
    texto_js = texto_pro.replace("`", "\\`").replace("$", "\\$")
    components.html(f"""
        <style>
            .bar {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 9999; }}
            .btn {{ width: 140px; height: 50px; border: none; border-radius: 25px; font-family: sans-serif; font-size: 16px; font-weight: bold; cursor: pointer; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; gap: 8px; }}
            .dl {{ background-color: #007AFF; }} .sh {{ background-color: #34C759; }}
        </style>
        <div class="bar">
            <button onclick="dl()" class="btn dl">💾 Guardar</button>
            <button onclick="sh()" class="btn sh">📤 Compartir</button>
        </div>
        <script>
            const t = `{texto_js}`;
            function dl() {{
                const b = new Blob([t], {{type: 'text/plain'}});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(b);
                a.download = "PRO_cancion.txt";
                a.click();
            }}
            async function sh() {{
                const f = new File([new Blob([t])], "cancion.txt", {{type: 'text/plain'}});
                if (navigator.share) {{ try {{ await navigator.share({{ files: [f] }}); }} catch (e) {{}} }}
            </script>
    """, height=100)
