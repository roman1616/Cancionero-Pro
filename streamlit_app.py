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
    lineas = texto.split('\n')
    resultado_final = []
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            fin = match.end()
            lo_que_sigue = linea[fin:]
            if re.match(r'^ [a-zA-ZñÑáéíóúÁÉÍÓÚ]', lo_que_sigue):
                continue
            
            raiz_orig = match.group(1).upper()
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            resto = acorde_original[len(match.group(1)):]
            nuevo_acorde = f"{raiz_nueva}{resto}"
            if not lo_que_sigue.startswith('*'): nuevo_acorde += "*"

            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith('*'): ancho_original += 1
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if match.start() + i < len(linea_lista):
                    linea_lista[match.start() + i] = char
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ CENTRADA ---
# Título centrado usando Markdown (novedad 2026 para mejor control)
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Convierte y comparte tus canciones fácilmente.</p>", unsafe_allow_html=True)

# Contenedor para el cargador de archivos
with st.container():
    archivo = st.file_uploader("Sube tu archivo .txt", type="txt", label_visibility="collapsed")

if archivo:
    nombre_archivo = archivo.name
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Vista Previa:")
    st.code(texto_final, language="text")

    texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

    # BARRA DE ACCIONES FLOTANTE CENTRADA
    components.html(f"""
        <style>
            .action-bar {{
                position: fixed;
                bottom: 25px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 20px;
                z-index: 9999;
                background: rgba(255, 255, 255, 0.9);
                padding: 10px 20px;
                border-radius: 50px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }}
            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 25px;
                font-family: -apple-system, system-ui, sans-serif;
                font-size: 15px;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                color: white;
                transition: transform 0.2s, background 0.3s;
            }}
            .btn:active {{ transform: scale(0.92); }}
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
                a.href = url;
                a.download = "PRO_" + fileName;
                a.click();
            }};

            document.getElementById('btnSH').onclick = async () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const file = new File([blob], fileName, {{ type: 'text/plain' }});
                if (navigator.share) {{
                    try {{
                        await navigator.share({{ files: [file], title: fileName }});
                    }} catch (err) {{ console.log(err); }}
                }} else {{
                    alert("Usa el botón Guardar.");
                }}
            }};
        </script>
    """, height=100)


