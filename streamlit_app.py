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

def procesar_texto(texto_bruto):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN UTF-8 ---
    # Aseguramos que el contenido sea tratado como string de Python (UTF-8 por defecto)
    # y limpiamos caracteres de retorno de carro de Windows
    texto = texto_bruto.replace('\r\n', '\n')
    
    # --- BLOQUE 2: CONVERSIÓN LATINO A AMERICANO ---
    # Patrón para detectar notas latinas (ignora mayúsculas/minúsculas)
    patron_notas = r'\b(DO|RE|MI|FA|SOL|LA|SI)\b'
    
    def reemplazar_nota(match):
        nota = match.group(1).upper()
        return LATINO_A_AMERICANO.get(nota, nota)

    # Aplicamos la conversión nota por nota preservando el resto (m, 7, maj7, etc)
    # Usamos un patrón que detecte la nota al inicio de una palabra
    lineas = texto.split('\n')
    texto_americano = []
    
    patron_acorde = r'([Dd][Oo]|[Rr][Ee]|[Mm][Ii]|[Ff][Aa]|[Ss][Oo][Ll]|[Ll][Aa]|[Ss][Ii])'
    
    for linea in lineas:
        # Convertimos solo las raíces de los acordes
        nueva_linea = re.sub(patron_acorde, reemplazar_nota, linea)
        texto_americano.append(nueva_linea)

    # --- BLOQUE 3: COLOCACIÓN DE APÓSTROFES ---
    # Una vez que todo es Americano (C, D, E, F, G, A, B), ponemos el apóstrofe
    resultado_final = []
    # Busca Notas A-G seguidas opcionalmente de sostenidos, bemoles y tipos de acorde
    patron_final = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for linea in texto_americano:
        linea_con_apostrofes = list(linea)
        offset = 0
        
        for match in re.finditer(patron_final, linea):
            acorde = match.group(0)
            fin = match.end() + offset
            
            # Verificamos si ya tiene apóstrofe o asterisco para no duplicar
            if fin < len(linea_con_apostrofes):
                siguiente_char = linea_con_apostrofes[fin]
                if siguiente_char not in ["'", "*"]:
                    linea_con_apostrofes.insert(fin, "'")
                    offset += 1
            else:
                # Si es el final de la línea, lo añadimos
                linea_con_apostrofes.append("'")
                offset += 1
                
        resultado_final.append("".join(linea_con_apostrofes))

    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src='https://raw.githubusercontent.com/roman1616/Cancionero-Pro/refs/heads/main/192-192.png' alt='Icono' style='width: 45px; height: 45px;'>
        <h1>Cancionero Pro</h1>   
    </div>""", unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    try:
        nombre_archivo = archivo.name
        # El bloque de decodificación asegura la integridad del UTF-8
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
                }}
                .download-btn {{ background-color: #007AFF; }}
                .share-btn {{ background-color: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="dl" class="btn download-btn">💾 Guardar</button>
                <button id="sh" class="btn share-btn">📤 Compartir</button>
            </div>
            <script>
                const content = `{texto_js}`;
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const url = URL.createObjectURL(b);
                    const a = document.createElement('a');
                    a.href = url; a.download = "PRO_{nombre_archivo}"; a.click();
                }};
                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const file = new File([b], "{nombre_archivo}", {{ type: 'text/plain' }});
                    if (navigator.share) {{
                        try {{ await navigator.share({{ files: [file] }}); }} catch (e) {{}}
                    }} else {{ alert("Usa 'Guardar'"); }}
                }};
            </script>
        """, height=100)
    
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
