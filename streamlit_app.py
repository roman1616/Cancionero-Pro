import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de la aplicación
st.set_page_config(
    page_title="Cancionero Pro 2026", 
    page_icon="🎸", 
    layout="centered"
)

# Diccionario de conversión de Latino a Americano
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    lineas = texto.split('\n')
    resultado_final = []
    
    # Patrón: Notas latinas o americanas + alteraciones y extensiones
    patron_universal = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        # Usamos offset para manejar cambios de longitud en la línea si fuera necesario
        # pero aquí sobreescribimos posiciones fijas para mantener alineación
        
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            raiz_orig = match.group(1).upper()
            resto_acorde = match.group(2)
            inicio = match.start()
            fin = match.end()
            
            # --- FILTROS DE FALSOS POSITIVOS ---
            if inicio > 0 and linea[inicio-1].isalpha():
                continue
            
            lo_que_sigue = linea[fin:]
            # Evitar capturar palabras (ej: "A la...", "Lado")
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue) or re.match(r'^[a-zñáéíóú]', lo_que_sigue):
                continue

            # --- CONVERSIÓN ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            nuevo_acorde = f"{raiz_nueva}{resto_acorde}"
            
            # Añadir apóstrofe si no existe
            if not lo_que_sigue.startswith("'"):
                nuevo_acorde += "'"

            # --- RECONSTRUCCIÓN DE LÍNEA ---
            # Intentamos mantener el espacio original o expandir si es necesario
            ancho_espacio = len(acorde_original)
            if lo_que_sigue.startswith("'"):
                ancho_espacio += 1
            
            sustitucion = nuevo_acorde.ljust(ancho_espacio)

            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char
                else:
                    linea_lista.append(char)
                    
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ DE USUARIO ---
st.markdown("""
    <div style='display: flex; align-items: center; justify-content: center; gap: 15px; padding: 20px;'>
        <img src='https://raw.githubusercontent.com' width='50'>
        <h1 style='margin:0;'>Cancionero Pro</h1>
    </div>
    <p style='text-align: center; color: #666;'>Convierte cifrado Latino a Americano y añade formato de lectura (') automáticamente.</p>
    """, unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo de texto (.txt)", type="txt", label_visibility="collapsed")

if archivo:
    nombre_archivo = archivo.name
    contenido = archivo.read().decode("utf-8")
    texto_procesado = procesar_texto(contenido)
    
    st.success("¡Archivo procesado con éxito!")
    
    with st.expander("Ver vista previa del texto", expanded=True):
        st.code(texto_procesado, language="text")

    # Preparar el texto para JavaScript (escapar comillas y saltos)
    texto_js = texto_procesado.replace("`", "\\`").replace("$", "\\$")

    # COMPONENTE DE ACCIONES (BOTONES FLOTANTES)
    components.html(f"""
        <style>
            .action-bar {{
                position: fixed;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 20px;
                z-index: 1000;
                background: rgba(255,255,255,0.8);
                padding: 10px 20px;
                border-radius: 40px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.15);
            }}
            .btn {{
                width: 140px;
                height: 45px;
                border: none;
                border-radius: 22px;
                font-family: sans-serif;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                color: white;
                transition: transform 0.2s, filter 0.2s;
            }}
            .btn:active {{ transform: scale(0.92); }}
            .btn-save {{ background-color: #007AFF; }}
            .btn-share {{ background-color: #34C759; }}
        </style>
        
        <div class="action-bar">
            <button id="dl" class="btn btn-save">💾 Guardar</button>
            <button id="sh" class="btn btn-share">📤 Compartir</button>
        </div>

        <script>
            const content = `{texto_js}`;
            const fileName = "PRO_{nombre_archivo}";

            // Lógica de Descarga
            document.getElementById('dl').onclick = () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = fileName;
                a.click();
                window.URL.revokeObjectURL(url);
            }};

            // Lógica de Compartir (Web Share API)
            document.getElementById('sh').onclick = async () => {{
                const file = new File([content], fileName, {{ type: 'text/plain' }});
                if (navigator.share) {{
                    try {{
                        await navigator.share({{
                            title: 'Cancionero Pro',
                            files: [file]
                        }});
                    }} catch (err) {{ 
                        if (err.name !== 'AbortError') alert("Error al compartir."); 
                    }}
                } else {{
                    alert("Tu navegador no soporta compartir archivos. Usa 'Guardar'.");
                }}
            }};
        </script>
    """, height=120)
else:
    st.info("Esperando archivo... Por favor, sube un .txt para comenzar.")


