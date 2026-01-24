import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página centrada
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
MAPA = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'}

# Inyectamos CSS para centrar y dar estilo
st.markdown("""
    <style>
    .stApp { text-align: center; }
    .main { display: flex; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🎸 Procesador de Acordes")
st.write("Sube tu archivo .txt (Compatible con Android y Dropbox)")

# --- COMPONENTE HTML/JS PARA CARGA SIN ERRORES DE RED ---
# Este bloque reemplaza al st.file_uploader que te daba error
components.html("""
    <div style="display: flex; flex-direction: column; align-items: center; gap: 20px; font-family: sans-serif;">
        <input type="file" id="fileInput" accept=".txt" style="display: none;">
        <button onclick="document.getElementById('fileInput').click()" 
            style="background-color: #FF4B4B; color: white; padding: 15px 25px; border-radius: 10px; border: none; cursor: pointer; font-weight: bold; font-size: 16px;">
            📁 Seleccionar Archivo .txt
        </button>
        <p id="fileName" style="color: #666; font-size: 14px;">Ningún archivo seleccionado</p>
    </div>

    <script>
    // Referencias
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileName');

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        fileNameDisplay.innerText = "Procesando: " + file.name;
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const contenido = e.target.result;
            // Enviamos el contenido a Streamlit usando un mensaje
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: {text: contenido, name: file.name}
            }, '*');
        };
        reader.readAsText(file);
    });
    </script>
""", height=150)

# 2. Lógica de procesamiento en Python
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
            
            nueva_raiz = MAPA.get(m.group(1).upper(), m.group(1).upper())
            acorde = f"{nueva_raiz}{m.group(2)}"
            if not (linea[fin:].startswith("'") or linea[fin:].startswith("*")): acorde += "'"
            
            ancho = len(m.group(0))
            if linea[fin:].startswith("'") or linea[fin:].startswith("*"): ancho += 1
            sustitucion = acorde.ljust(ancho)
            for i, char in enumerate(sustitucion):
                if ini + i < len(lista): lista[ini + i] = char
        res.append("".join(lista))
    return '\n'.join(res)

# Obtener los datos del componente HTML
datos_input = st.session_state.get("component_value")

if datos_input:
    texto_procesado = procesar_texto(datos_input['text'])
    nombre_archivo = datos_input['name']
    
    st.subheader("Vista Previa:")
    st.code(texto_procesado, language="text")

    # Botones flotantes corregidos
    texto_js = texto_procesado.replace("`", "\\`").replace("$", "\\$")
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
                a.download = "PRO_{nombre_archivo}";
                a.click();
            }}
            async function sh() {{
                const f = new File([new Blob([t])], "{nombre_archivo}", {{type: 'text/plain'}});
                if (navigator.share) {{ try {{ await navigator.share({{ files: [f] }}); }} catch (e) {{}} }}
            </script>
    """, height=100)




