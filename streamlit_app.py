import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración y Diccionario
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
            
            # FILTRO ANTI-FRASES
            lo_que_sigue = linea[fin:]
            if re.match(r'^ [a-zA-ZñÑáéíóúÁÉÍÓÚ]', lo_que_sigue):
                continue
            
            # CONVERSIÓN Y MANTENER POSICIÓN
            raiz_orig = match.group(1).upper()
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            resto = acorde_original[len(match.group(1)):]
            
            nuevo_acorde = f"{raiz_nueva}{resto}"
            if not lo_que_sigue.startswith('*'):
                nuevo_acorde += "*"

            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith('*'): ancho_original += 1
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if match.start() + i < len(linea_lista):
                    linea_lista[match.start() + i] = char

        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Cancionero Pro 2026", layout="wide")
st.title("🎸 Procesador de Acordes Profesional")

archivo = st.file_uploader("Sube tu archivo .txt", type="txt")

if archivo:
    nombre_archivo = archivo.name
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    st.subheader("Vista Previa:")
    st.code(texto_final, language="text")

    # Escapamos el texto para JavaScript
    texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

    # BARRA DE ACCIONES FLOTANTE (HTML + JS)
    # Colocamos ambos botones fuera del flujo de Streamlit para máxima compatibilidad
    components.html(f"""
        <style>
            .action-bar {{
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 15px;
                z-index: 9999;
                width: max-content;
            }}
            .btn {{
                padding: 14px 22px;
                border: none;
                border-radius: 12px;
                font-family: sans-serif;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                gap: 8px;
                color: white;
                transition: transform 0.2s;
            }}
            .btn:active {{ transform: scale(0.95); }}
            .download-btn {{ background-color: #4A90E2; }}
            .share-btn {{ background-color: #25D366; }}
        </style>
        
        <div class="action-bar">
            <button id="btnDL" class="btn download-btn">💾 Guardar</button>
            <button id="btnSH" class="btn share-btn">📤 Compartir</button>
        </div>

        <script>
            const content = `{texto_js}`;
            const fileName = "{nombre_archivo}";

            // Lógica Descargar
            document.getElementById('btnDL').onclick = () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = "PRO_" + fileName;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            }};

            // Lógica Compartir (Móvil)
            document.getElementById('btnSH').onclick = async () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const file = new File([blob], fileName, {{ type: 'text/plain' }});
                
                if (navigator.share) {{
                    try {{
                        await navigator.share({{
                            files: [file],
                            title: fileName,
                            text: 'Canción procesada'
                        }});
                    }} catch (err) {{
                        if (err.name !== 'AbortError') alert("Error: " + err.message);
                    }}
                }} else {{
                    alert("Tu navegador no soporta 'Compartir'. Usa el botón 'Guardar'.");
                }}
            }};
        </script>
    """, height=100)

    st.info("💡 Usa los botones de abajo para Guardar o Compartir directamente por WhatsApp.")

