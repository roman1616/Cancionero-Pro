import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de raíces
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto_bruto, notas_permitidas):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN UTF-8 ---
    texto = texto_bruto.replace('\r\n', '\n')
    
    # --- BLOQUE 2: CONVERSIÓN DE CIFRADO ---
    # Capturamos la raíz y sus complementos
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()
        # Si la nota no está en la lista de confirmadas, se devuelve tal cual
        if raiz_lat in ['RE', 'MI', 'SOL', 'LA', 'SI'] and raiz_lat not in notas_permitidas:
            return match.group(0)
            
        cualidad = match.group(2) if match.group(2) else ""
        alteracion = match.group(3) if match.group(3) else ""
        numero = match.group(4) if match.group(4) else ""
        
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    lineas = texto.split('\n')
    texto_convertido = []
    for linea in lineas:
        nueva_linea = re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE)
        texto_convertido.append(nueva_linea)

    # --- BLOQUE 3: COLOCACIÓN DE APÓSTROFES ---
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
st.markdown("<h1 style='text-align: center;'>🎸 Cancionero Pro 2026</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    contenido_original = archivo.getvalue().decode("utf-8")
    
    # Detectar qué notas de la lista están presentes en el texto
    notas_a_confirmar = ['RE', 'MI', 'SOL', 'LA', 'SI']
    notas_encontradas = [n for n in notas_a_confirmar if re.search(rf'\b{n}\b', contenido_original, re.I)]

    notas_seleccionadas = []
    
    if notas_encontradas:
        st.warning("Se encontraron notas que podrían ser palabras. Selecciona cuáles quieres convertir a cifrado americano:")
        cols = st.columns(len(notas_encontradas))
        for i, nota in enumerate(notas_encontradas):
            if cols[i].checkbox(f"Convertir {nota}", value=False):
                notas_seleccionadas.append(nota)
        
        # DO y FA se agregan por defecto ya que no suelen ser palabras comunes en oraciones
        notas_seleccionadas.extend(['DO', 'FA'])
    else:
        notas_seleccionadas = ['DO', 'RE', 'MI', 'FA', 'SOL', 'LA', 'SI']

    if st.button("Procesar Canción") or not notas_encontradas:
        try:
            texto_final = procesar_texto(contenido_original, notas_seleccionadas)
            
            st.subheader("Vista Previa:")
            st.code(texto_final, language="text")

            texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
            components.html(f"""
                <style>
                    .action-bar {{ position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; }}
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
                        a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                    }};
                    document.getElementById('sh').onclick = async () => {{
                        const b = new Blob([txt], {{type:'text/plain'}});
                        const f = new File([b], "{archivo.name}", {{type:'text/plain'}});
                        if(navigator.share) await navigator.share({{files:[f]}});
                    }};
                </script>
            """, height=100)
        except Exception as e:
            st.error(f"Error: {e}")
