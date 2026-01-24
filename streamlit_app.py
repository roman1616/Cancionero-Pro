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
    # Patrón universal: captura la nota base y opcionalmente # o b y el resto del acorde
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)\b'

    for linea in lineas:
        linea_lista = list(linea)
        # Usamos finditer para procesar cada coincidencia de forma independiente
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0) # Ejemplo: "A#" o "Dm"
            raiz_orig = match.group(1).upper()
            resto_acorde = match.group(2) # Ejemplo: "#" o "m"
            
            fin_pos = match.end()
            lo_que_sigue = linea[fin_pos:]
            
            # FILTRO ANTI-FRASES: Evita procesar si es el inicio de una palabra
            if re.match(r'^ [a-zA-ZñÑáéíóúÁÉÍÓÚ]', lo_que_sigue):
                continue
            
            # CONVERSIÓN
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            
            # CONSTRUCCIÓN: Unimos la nueva raíz con TODO el resto original y el '
            nuevo_acorde = f"{raiz_nueva}{resto_acorde}"
            
            # Solo añadir el apóstrofe si no existe ya un marcador
            if not (lo_que_sigue.startswith("'") or lo_que_sigue.startswith('*')):
                nuevo_acorde += "'"

            # MANTENER POSICIÓN EXACTA
            ancho_original = len(acorde_original)
            # Si en el original ya había un ', compensamos el ancho
            if lo_que_sigue.startswith("'") or lo_que_sigue.startswith('*'): 
                ancho_original += 1
            
            # Rellenamos con espacios a la derecha para que nada se mueva
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if match.start() + i < len(linea_lista):
                    linea_lista[match.start() + i] = char
                    
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type="txt", label_visibility="collapsed")

if archivo:
    nombre_archivo = archivo.name
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Vista Previa:")
    st.code(texto_final, language="text")

    texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

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
            }}
            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 25px;
                font-family: sans-serif;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
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
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "PRO_{nombre_archivo}";
                a.click();
            }};
            document.getElementById('btnSH').onclick = async () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const file = new File([blob], "{nombre_archivo}", {{ type: 'text/plain' }});
                if (navigator.share) {{
                    try {{ await navigator.share({{ files: [file] }}); }} catch (err) {{}}
                }}
            }};
        </script>
    """, height=100)


