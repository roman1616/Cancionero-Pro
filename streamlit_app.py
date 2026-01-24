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
    # Patrón para detectar acordes (latino o americano)
    patron_universal = r'\b(do|re|mi|fa|sol|la|si|[a-g])[#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?\b'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            fin = match.end()
            
            # FILTRO ANTI-FRASES (Ej: "La Repandilla")
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

            # Alineación: rellenar con espacios si el nuevo es más corto
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
st.title("🎸 Procesador de Acordes Inteligente")
st.write("Sube tu canción para convertir a Americano y compartir directamente.")

archivo = st.file_uploader("Sube tu archivo .txt", type="txt")

if archivo:
    nombre_archivo = archivo.name
    contenido = archivo.read().decode("utf-8")
    texto_final = procesar_texto(contenido)
    
    # Vista previa en fuente monoespaciada para verificar alineación
    st.subheader("Vista Previa:")
    st.code(texto_final, language="text")

    # Escapamos el texto para que no rompa el JavaScript
    texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

    # BOTÓN DE DESCARGA (PC)
    st.download_button("💾 Descargar en PC", texto_final, file_name=f"PRO_{nombre_archivo}")

    # BOTÓN DE COMPARTIR (ESPECÍFICO PARA IPHONE/MÓVIL)
    # Inyectamos el botón fuera del flujo normal para evitar bloqueos de Safari
    components.html(f"""
        <style>
            .btn-compartir {{
                position: fixed;
                bottom: 30px;
                right: 30px;
                background-color: #007AFF; /* Azul iOS */
                color: white;
                border: none;
                border-radius: 12px;
                padding: 16px 24px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica;
                font-size: 16px;
                font-weight: 600;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                cursor: pointer;
                z-index: 9999;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .btn-compartir:active {{
                transform: scale(0.95);
                background-color: #0051a8;
            }}
        </style>
        
        <button id="shareAction" class="btn-compartir">
            <span>📤</span> Compartir en Móvil
        </button>

        <script>
        document.getElementById('shareAction').onclick = async () => {{
            const content = `{texto_js}`;
            const blob = new Blob([content], {{ type: 'text/plain' }});
            const file = new File([blob], "{nombre_archivo}", {{ type: 'text/plain' }});
            
            if (navigator.share) {{
                try {{
                    await navigator.share({{
                        files: [file],
                        title: '{nombre_archivo}',
                        text: 'Canción procesada con Cancionero Pro'
                    }});
                }} catch (err) {{
                    if (err.name !== 'AbortError') {{
                        alert("Error al compartir: " + err.message);
                    }}
                }}
            }} else {{
                alert("Tu navegador no soporta la función de compartir archivos. Usa el botón 'Descargar en PC'.");
            }}
        }};
        </script>
    """, height=100)

    st.info("💡 En iPhone: Usa el botón azul flotante para enviar por WhatsApp o guardar en archivos.")
