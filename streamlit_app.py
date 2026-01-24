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
    # Patrón para detectar la estructura de un acorde (Latino o Americano)
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        linea_lista = list(linea)
        # Buscamos todos los acordes en la línea original
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            fin = match.end()
            
            # FILTRO ANTI-FRASES (Ej: "La Repandilla")
            lo_que_sigue = linea[fin:]
            # Si hay un espacio y luego una letra, es parte de la letra de la canción
            if re.match(r'^ [a-zA-ZñÑáéíóúÁÉÍÓÚ]', lo_que_sigue):
                continue
            
            # CONVERSIÓN A AMERICANO Y MARCADO CON APÓSTROFE (')
            raiz_orig = match.group(1).upper()
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            resto = acorde_original[len(match.group(1)):]
            
            # Formamos el nuevo acorde. Si ya tiene ', no lo duplicamos.
            nuevo_acorde = f"{raiz_nueva}{resto}"
            if not lo_que_sigue.startswith("'"):
                nuevo_acorde += "'"

            # MANTENER EL LUGAR (Alineación)
            # Rellenamos con espacios si el nuevo acorde es más corto que el original
            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith("'"): ancho_original += 1
            
            sustitucion = nuevo_acorde.ljust(ancho_original)

            # Escribimos la sustitución en la posición exacta
            for i, char in enumerate(sustitucion):
                if match.start() + i < len(linea_lista):
                    linea_lista[match.start() + i] = char

        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- INTERFAZ CENTRADA ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Cambia de cifrado Latino a Americano y agrega un apóstrofe (') para detectar las notas.</p>", unsafe_allow_html=True)

# Cargador de archivos
archivo = st.file_uploader("Sube tu archivo .txt", type="txt", label_visibility="collapsed")

if archivo:
    nombre_archivo = archivo.name
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Vista Previa:")
    # Usamos st.code para asegurar fuente monoespaciada (alineación correcta)
    st.code(texto_final, language="text")

    # Escapamos el texto para JavaScript
    texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

    # BARRA DE ACCIONES FLOTANTE (SIN FONDO, BOTONES INDEPENDIENTES)
    components.html(f"""
        <style>
            .action-bar {{
                position: fixed;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 20px;
                z-index: 9999;
                /* Sin fondo ni contenedor visible */
            }}
            .btn {{
                padding: 14px 24px;
                border: none;
                border-radius: 50px;
                font-family: -apple-system, system-ui, sans-serif;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
                color: white;
                transition: transform 0.1s;
                box-shadow: 0 4px 15px rgba(0,0,0,0.4);
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

            // FUNCIÓN GUARDAR (PC/Android)
            document.getElementById('btnDL').onclick = () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "PRO_" + fileName;
                a.click();
                window.URL.revokeObjectURL(url);
            }};

            // FUNCIÓN COMPARTIR (Corregida para iPhone: solo envía files)
            document.getElementById('btnSH').onclick = async () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const file = new File([blob], fileName, {{ type: 'text/plain' }});
                
                if (navigator.share) {{
                    try {{
                        // Al enviar SOLO 'files', evitamos que iOS genere el archivo extra con fecha/hora
                        await navigator.share({{
                            files: [file]
                        }});
                    }} catch (err) {{
                        if (err.name !== 'AbortError') console.log("Error al compartir:", err);
                    }}
                }} else {{
                    alert("Tu navegador no soporta compartir. Usa el botón 'Guardar'.");
                }}
            }};
        </script>
    """, height=120)
