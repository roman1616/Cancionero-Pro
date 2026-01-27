import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página centrada
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión (Latino a Americano)
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    resultado_final = []
    
    # Patrón mejorado: Captura la nota base (do-si) y el resto del acorde
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#b]?[a-zA-Z0-9\/\+\-\(]*)'

    for linea in lineas:
        # Usamos re.sub con una función de reemplazo para mayor control
        def reemplazar(match):
            nota_latina = match.group(1).upper()
            resto = match.group(2)
            
            # Convertir nota base
            nota_americana = LATINO_A_AMERICANO.get(nota_latina, nota_latina)
            acorde_completo = f"{nota_americana}{resto}"
            
            # Si ya tiene apóstrofe o asterisco, no lo duplicamos
            # Si no, lo agregamos al final
            if not (acorde_completo.endswith("'") or acorde_completo.endswith("*")):
                return f"{acorde_completo}'"
            return acorde_completo

        # Aplicamos la conversión ignorando mayúsculas/minúsculas en la búsqueda
        nueva_linea = re.sub(patron_latino, reemplazar, linea, flags=re.IGNORECASE)
        resultado_final.append(nueva_linea)
        
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src='https://raw.githubusercontent.com/roman1616/Cancionero-Pro/refs/heads/main/192-192.png' alt='Icono' style='width: 45px; height: 45px;'>
        <h1>Cancionero Pro</h1>   
    </div>""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Convierte a cifrado Americano y coloca el apóstrofe al final del acorde.</p>", unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    try:
        nombre_archivo = archivo.name
        contenido = archivo.getvalue().decode("utf-8")
        texto_final = procesar_texto(contenido)
        
        st.subheader("Vista Previa:")
        st.code(texto_final, language="text")

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

        components.html(f"""
            <style>
                .action-bar {{
                    position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%);
                    display: flex; gap: 15px; z-index: 9999;
                }}
                .btn {{
                    width: 150px; height: 50px; border: none; border-radius: 25px;
                    font-family: -apple-system, system-ui, sans-serif;
                    font-size: 16px; font-weight: 700; cursor: pointer;
                    display: flex; align-items: center; justify-content: center;
                    gap: 8px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    transition: transform 0.1s;
                }}
                .btn:active {{ transform: scale(0.95); }}
                .download-btn {{ background-color: #007AFF; }}
                .share-btn {{ background-color: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="dl" class="btn download-btn">💾 Guardar</button>
                <button id="sh" class="btn share-btn">📤 Compartir</button>
            </div>
            <script>
                const content = `{texto_js}`;
                const fileName = "{nombre_archivo}";

                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const url = URL.createObjectURL(b);
                    const a = document.createElement('a');
                    a.href = url; a.download = "PRO_" + fileName; a.click();
                }};

                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const file = new File([b], fileName, {{ type: 'text/plain' }});
                    if (navigator.share) {{
                        try {{ await navigator.share({{ files: [file] }}); }} 
                        catch (e) {{ if (e.name !== 'AbortError') console.log("Error:", e); }}
                    }} else {{ alert("Navegador no compatible con compartir"); }}
                }};
            </script>
        """, height=100)
    
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
