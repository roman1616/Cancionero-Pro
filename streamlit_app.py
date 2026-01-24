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
            inicio = match.start()
            fin = match.end()
            
            # --- VALIDACIÓN PARA EVITAR PALABRAS (Ej: "A la gloria") ---
            # 1. Si antes hay una letra, es parte de una palabra
            if inicio > 0 and linea[inicio-1].isalpha():
                continue
            
            # 2. REGLA CRÍTICA: Si el acorde es una sola letra (como 'A') y lo 
            # que sigue es un espacio y una letra MINÚSCULA, es texto, no música.
            lo_que_sigue = linea[fin:]
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue):
                continue
            
            # 3. Si lo que sigue es una letra minúscula pegada (ej: "Lado")
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue):
                continue

            # --- CONVERSIÓN ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            nuevo_acorde = f"{raiz_nueva}{resto_acorde}"
            
            # Añadir apóstrofe si no existe
            if not lo_que_sigue.startswith("'"):
                nuevo_acorde += "'"

            # --- MANTENER POSICIÓN ---
            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith("'"):
                ancho_original += 1
            
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char
                    
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Convierte de cifrado Latino a Americano y coloca el apóstrofe al final del acorde.</p>", unsafe_allow_html=True)
archivo = st.file_uploader("Sube tu archivo .txt", type="txt", label_visibility="collapsed")

if archivo:
    nombre_archivo = archivo.name
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Vista Previa:")
    st.code(texto_final, language="text")

    texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

        # BARRA DE ACCIONES FLOTANTE (BOTONES IGUALES)
    components.html(f"""
        <style>
            .action-bar {{
                position: fixed;
                bottom: 25px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 15px; /* Espacio entre botones */
                z-index: 9999;
            }}
            .btn {{
                width: 150px; /* Ancho fijo para que sean iguales */
                height: 50px; /* Altura fija */
                border: none;
                border-radius: 25px;
                font-family: -apple-system, system-ui, sans-serif;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center; /* Centra el texto e icono dentro del botón */
                gap: 8px;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transition: transform 0.1s;
            }}
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
                a.href = url;
                a.download = "PRO_" + fileName;
                a.click();
            }};

            document.getElementById('btnSH').onclick = async () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const file = new File([blob], fileName, {{ type: 'text/plain' }});
                if (navigator.share) {{
                    try {{
                        await navigator.share({{ files: [file] }});
                    }} catch (err) {{ if (err.name !== 'AbortError') console.log(err); }}
                }} else {{
                    alert("Usa 'Guardar'.");
                }}
            }};
        </script>
    """, height=100)   en android no funciona
