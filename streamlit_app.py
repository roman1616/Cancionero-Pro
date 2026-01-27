import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto_bruto):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN UTF-8 ---
    texto = texto_bruto.replace('\r\n', '\n')
    
    # --- BLOQUE 2: CONVERSIÓN DE CIFRADO (Latino a Americano) ---
    # Captura Notas Latinas con sus variantes (Lam#, Sol7, etc.)
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()
        cualidad = match.group(2) if match.group(2) else ""
        alteracion = match.group(3) if match.group(3) else ""
        numero = match.group(4) if match.group(4) else ""
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    lineas = texto.split('\n')
    texto_convertido = [re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE) for linea in lineas]

    # --- BLOQUE 3: COLOCACIÓN DE APÓSTROFES (Con filtro anti-texto) ---
    resultado_final = []
    # Este patrón busca acordes americanos pero exige que sean musicales
    # Filtra letras sueltas 'A' o 'E' si parecen preposiciones
    patron_acorde_real = r'\b([A-G](?:[#b]|m|maj|min|aug|dim|sus|add|M|[0-9])(?:/[A-G][#b]?)?)\b|\b([A-G])\b'

    for linea in texto_convertido:
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_acorde_real, linea):
            # Verificamos si es una letra sola (posible preposición)
            es_letra_sola = m.group(2) is not None
            inicio, fin = m.start(), m.end()

            # LÓGICA DE FILTRO:
            # Si es letra sola, comprobamos si la línea parece de acordes (muchos espacios)
            # O si el acorde tiene símbolos musicales (m, #, 7), se procesa siempre.
            if es_letra_sola:
                # Si la letra sola está en una línea con mucho texto (poca densidad de espacios), la ignoramos
                if linea.count(' ') < len(linea) * 0.2: # Ajuste de sensibilidad
                    continue

            pos_final = fin + ajuste
            if pos_final < len(linea_lista):
                if linea_lista[pos_final] not in ["'", "*"]:
                    linea_lista.insert(pos_final, "'")
                    ajuste += 1
            else:
                linea_lista.append("'")
                ajuste += 1
                
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Cancionero Pro 2026</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

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
                .bar {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; }}
                .btn {{ padding: 12px 25px; border-radius: 20px; border: none; color: white; font-weight: bold; cursor: pointer; }}
                .dl {{ background: #007AFF; }} .sh {{ background: #34C759; }}
            </style>
            <div class="bar">
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
