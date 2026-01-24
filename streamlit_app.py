import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página
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
    patron_universal = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            fin = match.end()
            if match.start() > 0 and linea[match.start()-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', linea[fin:]): continue
            
            raiz_nueva = LATINO_A_AMERICANO.get(match.group(1).upper(), match.group(1).upper())
            nuevo_acorde = f"{raiz_nueva}{match.group(2)}'"
            sustitucion = nuevo_acorde.ljust(len(acorde_original) + 1)
            for i, char in enumerate(sustitucion):
                if match.start() + i < len(linea_lista):
                    linea_lista[match.start() + i] = char
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)

# PASO 1: Cargador manual (Puente de datos)
# Si el botón automático falla, el usuario puede pegar aquí.
# Pero el JS intentará llenar este campo automáticamente.
input_text = st.text_area("Carga de texto:", height=150, placeholder="El texto aparecerá aquí al seleccionar el archivo...")

# PASO 2: El botón de carga Real (HTML Nativo)
st.write("### 📁 Paso 1: Selecciona el archivo")
components.html("""
    <div style="display: flex; justify-content: center; font-family: sans-serif;">
        <input type="file" id="f" accept=".txt" style="display: none;">
        <button onclick="document.getElementById('f').click()" 
            style="background: #007AFF; color: white; padding: 15px 30px; border-radius: 50px; border: none; cursor: pointer; font-weight: bold; font-size: 16px;">
            📁 Cargar desde Dropbox / Carpeta
        </button>
    </div>
    <script>
        document.getElementById('f').onchange = e => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = event => {
                // Buscamos el área de texto de Streamlit y le pegamos el contenido
                const textArea = window.parent.document.querySelector('textarea');
                if(textArea) {
                    textArea.value = event.target.result;
                    textArea.dispatchEvent(new Event('input', { bubbles: true }));
                    alert("✅ Archivo '" + file.name + "' cargado. Ahora pulsa fuera del cuadro de texto o espera un segundo.");
                }
            };
            reader.readAsText(file);
        };
    </script>
""", height=100)

if input_text:
    texto_final = procesar_texto(input_text)
    
    st.subheader("Vista Previa:")
    st.code(texto_final, language="text")

    texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

    # BARRA DE ACCIONES
    components.html(f"""
        <style>
            .action-bar {{ position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 9999; }}
            .btn {{ width: 150px; height: 50px; border: none; border-radius: 25px; font-family: sans-serif; font-size: 16px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
            .download-btn {{ background-color: #007AFF; }}
            .share-btn {{ background-color: #34C759; }}
        </style>
        <div class="action-bar">
            <button id="dl" class="btn download-btn">💾 Guardar</button>
            <button id="sh" class="btn share-btn">📤 Compartir</button>
        </div>
        <script>
            const content = `{texto_js}`;
            document.getElementById('dl').onclick = () => {
                const b = new Blob([content], {type: 'text/plain'});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(b); a.download = "PRO_cancion.txt"; a.click();
            };
            document.getElementById('sh').onclick = async () => {
                const b = new Blob([content], {type: 'text/plain'});
                const f = new File([b], "cancion.txt", {type: 'text/plain'});
                if (navigator.share) { try { await navigator.share({ files: [f] }); } catch (e) {} }
            };
        </script>
    """, height=100)

