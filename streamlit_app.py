import streamlit as st
import re
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de raíces musical
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto_bruto):
    if not texto_bruto: return ""
    
    # Normalización de saltos de línea
    texto = texto_bruto.replace('\r\n', '\n')
    
    # --- BLOQUE 1: CONVERSIÓN DE CIFRADO ---
    # Patrón: Busca raíces latinas. 
    # Nota: No usamos re.IGNORECASE en el sub para distinguir "la" (artículo) de "LA" (acorde)
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_orig = match.group(1) # Ejemplo: "LA" o "la"
        cualidad = match.group(2) if match.group(2) else ""
        alteracion = match.group(3) if match.group(3) else ""
        numero = match.group(4) if match.group(4) else ""
        
        # SEGURIDAD: Si la raíz está en minúsculas y no tiene complementos (#, m, 7), 
        # asumimos que es una palabra del lenguaje (artículo o conjunción) y no la tocamos.
        if raiz_orig.islower() and not (cualidad or alteracion or numero):
            return match.group(0)
        
        # Convertir a sistema americano
        raiz_lat_upper = raiz_orig.upper()
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat_upper, raiz_lat_upper)
        
        # Reordenar al formato estándar: Raíz + Alteración + Cualidad + Número
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    lineas = texto.split('\n')
    texto_convertido = []
    for linea in lineas:
        # Procesamos la línea respetando mayúsculas/minúsculas
        nueva_linea = re.sub(patron_latino, traducir_acorde, linea)
        texto_convertido.append(nueva_linea)

    # --- BLOQUE 2: COLOCACIÓN DE APÓSTROFES ---
    # Busca acordes en formato americano (A-G) para ponerles el cierre '
    resultado_final = []
    patron_final = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for linea in texto_convertido:
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_final, linea):
            fin = m.end() + ajuste
            if fin < len(linea_lista):
                if linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
                    ajuste += 1
            else:
                linea_lista.append("'")
                ajuste += 1
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- INTERFAZ STREAMLIT ---
st.markdown("""
    <style>
        .main-title { font-size: 2.5rem; font-weight: bold; color: #007AFF; text-align: center; }
    </style>
    <div class="main-title">🎸 Cancionero Pro 2026</div>
    <p style='text-align: center; color: #666;'>Convierte cifrado latino a americano automáticamente evitando errores de texto.</p>
    """, unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    try:
        nombre_archivo = archivo.name
        contenido = archivo.getvalue().decode("utf-8")
        texto_final = procesar_texto(contenido)
        
        st.subheader("Vista Previa del Resultado:")
        st.code(texto_final, language="text")

        # Preparar string para JS
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        
        components.html(f"""
            <style>
                .action-bar {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 1000; }}
                .btn {{ padding: 12px 24px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; color: white; font-family: sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }}
                .dl {{ background: #007AFF; }} .sh {{ background: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="dl" class="btn dl">💾 Guardar .txt</button>
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
                    if(navigator.share) {{
                        const b = new Blob([txt], {{type:'text/plain'}});
                        const f = new File([b], "{nombre_archivo}", {{type:'text/plain'}});
                        await navigator.share({{files:[f], title: 'Mi Canción'}});
                    }} else {{
                        alert("La función de compartir no es compatible con este navegador.");
                    }}
                }};
            </script>
        """, height=120)
        
    except Exception as e:
        st.error(f"Se produjo un error al procesar el archivo: {e}")

# Instrucciones de uso
with st.expander("ℹ️ Instrucciones"):
    st.write("""
    - El programa reconoce **DO, RE, MI, FA, SOL, LA, SI**.
    - **Protección de texto:** 'la canción' no cambiará, pero 'LA canción' o 'LAm' sí cambiarán a 'A' y 'Am'.
    - El resultado añadirá automáticamente el apóstrofe de cierre utilizado en lectores de acordes digitales.
    """)
