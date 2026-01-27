import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto_final(texto_bruto, lineas_confirmadas):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN UTF-8 ---
    texto = texto_bruto.replace('\r\n', '\n')
    lineas = texto.split('\n')
    
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    patron_final_apostr = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'
    
    resultado_final = []
    
    for i, linea in enumerate(lineas):
        # BLOQUE DE FILTRO: Si la línea NO fue confirmada por el usuario, se ignora
        if i in lineas_confirmadas['pendientes'] and i not in lineas_confirmadas['aprobadas']:
            resultado_final.append(linea)
            continue

        # --- BLOQUE 2: CONVERSIÓN DE CIFRADO ---
        def traducir(match):
            raiz_lat = match.group(1).upper()
            raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
            # Reordenar: Raíz + Alteración + Cualidad + Número (Ej: Lam# -> A#m)
            return f"{raiz_amer}{match.group(3) or ''}{match.group(2) or ''}{match.group(4) or ''}"

        nueva_linea = re.sub(patron_latino, traducir, linea, flags=re.IGNORECASE)
        
        # --- BLOQUE 3: COLOCACIÓN DE APÓSTROFES ---
        linea_lista = list(nueva_linea)
        ajuste = 0
        for m in re.finditer(patron_final_apostr, nueva_linea):
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
st.markdown("<h2 style='text-align: center;'>🎸 Cancionero Pro 2026</h2>", unsafe_allow_html=True)
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    
    lineas_dudosas = []
    # Patrón para identificar notas que podrían ser palabras
    patron_duda = r'\b(RE|MI|SOL|LA|SI)\b'

    for idx, linea in enumerate(lineas):
        # Buscamos si hay 2 o más coincidencias en el mismo renglón
        coincidencias = re.findall(patron_duda, linea, re.I)
        if len(coincidencias) >= 2:
            lineas_dudosas.append((idx, linea))

    # Gestión de confirmaciones
    dict_lineas = {'pendientes': [idx for idx, _ in lineas_dudosas], 'aprobadas': []}

    if lineas_dudosas:
        st.warning(f"⚠️ Se detectaron {len(lineas_dudosas)} renglones con 2 o más notas seguidas que podrían ser frases. Confirma cuáles son música:")
        for idx, texto_linea in lineas_dudosas:
            if st.checkbox(f"Renglón {idx+1}: {texto_linea.strip()}", value=False, key=f"L{idx}"):
                dict_lineas['aprobadas'].append(idx)

    if st.button("✅ Procesar y Descargar"):
        texto_final = procesar_texto_final(contenido, dict_lineas)
        
        st.subheader("Vista Previa:")
        st.code(texto_final, language="text")

        # JavaScript para guardar/compartir
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <style>
                .bar {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; z-index: 999; }}
                .btn {{ padding: 12px 25px; border: none; border-radius: 20px; color: white; font-weight: bold; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
                .dl {{ background: #007AFF; }} .sh {{ background: #34C759; }}
            </style>
            <div class="bar">
                <button id="dl" class="btn dl">💾 Guardar</button>
                <button id="sh" class="btn sh">📤 Compartir</button>
            </div>
            <script>
                const txt = `{texto_js}`;
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([txt], {{type:'text/plain;charset=utf-8'}});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                }};
                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([txt], {{type:'text/plain;charset=utf-8'}});
                    const f = new File([b], "{archivo.name}", {{type:'text/plain'}});
                    if(navigator.share) await navigator.share({{files:[f]}});
                }};
            </script>
        """, height=100)
