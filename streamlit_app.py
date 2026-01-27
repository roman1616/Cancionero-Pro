import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de raíces
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto_bruto):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN UTF-8 ---
    texto = texto_bruto.replace('\r\n', '\n')
    
    # --- BLOQUE 2: CONVERSIÓN DE CIFRADO ---
    # Captura notas latinas con sus posibles sufijos
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()
        cualidad = match.group(2) or ""
        alteracion = match.group(3) or ""
        numero = match.group(4) or ""
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    lineas = texto.split('\n')
    texto_convertido = [re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE) for linea in lineas]

    # --- BLOQUE 3: COLOCACIÓN DE APÓSTROFES CON FILTRO DE TEXTO ---
    resultado_final = []
    # Busca acordes americanos (A-G). 
    # El grupo 1 captura acordes con extras (Am, C#, G7)
    # El grupo 2 captura letras solas (A, B, E...)
    patron_final = r'\b([A-G](?:[#b]|m|maj|min|aug|dim|sus|add|M|[0-9])(?:/[A-G][#b]?)?)\b|\b([A-G])\b'

    for linea in texto_convertido:
        # Si la línea tiene muchas letras juntas y pocos espacios, es probable que sea una oración
        # Las líneas de acordes suelen tener más de un 30% de espacios
        es_linea_de_texto = (linea.count(' ') < len(linea) * 0.25) if len(linea) > 10 else False
        
        linea_lista = list(linea)
        ajuste = 0
        
        for m in re.finditer(patron_final, linea):
            es_acorde_completo = m.group(1) is not None
            es_letra_sola = m.group(2) is not None
            fin = m.end() + ajuste

            # FILTRO: No poner apóstrofe si es una letra sola en una oración
            if es_letra_sola and es_linea_de_texto:
                continue
            
            # Evitar duplicar apóstrofe si ya existe
            if fin < len(linea_lista):
                if linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
                    ajuste += 1
            else:
                linea_lista.append("'")
                ajuste += 1
                
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src='https://raw.githubusercontent.com' style='width: 45px; height: 45px;'>
        <h1>Cancionero Pro</h1>   
    </div>""", unsafe_allow_html=True)

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
                .action-bar {{ position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 100; }}
                .btn {{ width: 140px; height: 45px; border: none; border-radius: 20px; font-weight: bold; cursor: pointer; color: white; }}
                .dl {{ background: #007AFF; }} .sh {{ background: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="dl" class="btn dl">💾 Guardar</button>
                <button id="sh" class="btn sh">📤 Compartir</button>
            </div>
            <script>
                const txt = `{texto_js}`;
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([txt], {{type:'text/plain'}});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b); a.download = "PRO_{nombre_archivo}"; a.click();
                }};
                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([txt], {{type:'text/plain'}});
                    const f = new File([b], "{nombre_archivo}", {{type:'text/plain'}});
                    if(navigator.share) await navigator.share({{files:[f]}});
                }};
            </script>
        """, height=100)
    except Exception as e:
        st.error(f"Error: {e}")
