import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    if not texto: return ""
    
    # Asegurar UTF-8 al inicio
    texto = texto.encode("utf-8").decode("utf-8")
    
    lineas = texto.split('\n')
    resultado_final = []
    
    # Patrón: Nota base + (opcional sostenido/bemol) + (resto del acorde m, 7, etc)
    # Separamos el grupo del sostenido para poder manipular su posición
    patron = r'(do|re|mi|fa|sol|la|si|[a-gA-G])(#|b)?((?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        # Trabajamos sobre la línea de derecha a izquierda para no romper los índices al insertar caracteres
        matches = list(re.finditer(patron, linea, flags=re.IGNORECASE))
        linea_lista = list(linea)
        
        for match in reversed(matches):
            inicio, fin = match.start(), match.end()
            raiz_orig = match.group(1).upper()
            alteracion = match.group(2) if match.group(2) else ""
            resto = match.group(3) if match.group(3) else ""
            
            # --- FILTROS DE SEGURIDAD (Evitar procesar palabras comunes) ---
            lo_que_sigue = linea[fin:]
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            # --- LÓGICA DE CONVERSIÓN Y REORDENAMIENTO ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            
            # Casos especiales de sostenido (Ej: Fam# -> Fm#)
            # El usuario pide que si hay sostenido (#), quede al final: Fm#' -> Fm#'
            # Pero específicamente solicitó: "Fam# lo convierte a Fm'# y tendría que quedar así Fm#'"
            # Es decir: Raiz + Resto + Apostrofe + Sostenido
            
            if alteracion == "#":
                # Construcción: Nota convertida + resto (m, 7, etc) + apóstrofe + sostenido
                nuevo_acorde = f"{raiz_nueva}{resto}'#"
            else:
                # Si no hay sostenido, solo añade el apóstrofe al final del acorde (incluyendo bemoles)
                nuevo_acorde = f"{raiz_nueva}{alteracion}{resto}'"

            # Reemplazar el bloque exacto en la lista de caracteres
            linea_lista[inicio:fin] = list(nuevo_acorde)
                    
        resultado_final.append("".join(linea_lista))
    
    return '\n'.join(resultado_final)

# --- INTERFAZ STREAMLIT ---
st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src='https://raw.githubusercontent.com' alt='Icono' style='width: 45px; height: 45px;'>
        <h1>Cancionero Pro</h1>   
    </div>""", unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    try:
        nombre_archivo = archivo.name
        # Decodificación explícita UTF-8
        contenido = archivo.read().decode("utf-8")
        texto_final = procesar_texto(contenido)
        
        st.subheader("Vista Previa (Formato 2026):")
        st.code(texto_final, language="text")

        # Preparar para JS
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

        components.html(f"""
            <style>
                .action-bar {{
                    position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%);
                    display: flex; gap: 15px; z-index: 9999;
                }}
                .btn {{
                    width: 140px; height: 45px; border: none; border-radius: 20px;
                    font-family: sans-serif; font-size: 14px; font-weight: bold;
                    cursor: pointer; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                }}
                .dl {{ background-color: #007AFF; }}
                .sh {{ background-color: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="dl" class="btn dl">💾 GUARDAR</button>
                <button id="sh" class="btn sh">📤 COMPARTIR</button>
            </div>
            <script>
                const content = `{texto_js}`;
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b);
                    a.download = "PRO_{nombre_archivo}";
                    a.click();
                }};
                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const f = new File([b], "{nombre_archivo}", {{ type: 'text/plain' }});
                    if (navigator.share) await navigator.share({{ files: [f] }});
                }};
            </script>
        """, height=100)
    
    except Exception as e:
        st.error(f"Error crítico de procesamiento: {e}")


