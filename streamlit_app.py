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
    
    # --- BLOQUE 1: NORMALIZACIÓN ---
    texto = texto_bruto.replace('\r\n', '\n')
    lineas = texto.split('\n')
    
    # --- BLOQUE 2 Y 3 COMBINADOS CON FILTRO DE LÍNEA ---
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    patron_final_apostr = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'
    
    resultado_final = []
    
    for i, linea in enumerate(lineas):
        # Si la línea contiene una nota dudosa pero NO fue confirmada, se deja intacta
        # Notas dudosas: RE, MI, SOL, LA, SI (DO y FA suelen ser seguras)
        contiene_dudosa = re.search(r'\b(RE|MI|SOL|LA|SI)\b', linea, re.I)
        
        if contiene_dudosa and i not in lineas_confirmadas:
            # Si el usuario no confirmó esta línea específica, no tocamos nada
            resultado_final.append(linea)
            continue

        # --- CONVERSIÓN DE CIFRADO ---
        def traducir(match):
            raiz_lat = match.group(1).upper()
            raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
            return f"{raiz_amer}{match.group(3) or ''}{match.group(2) or ''}{match.group(4) or ''}"

        nueva_linea = re.sub(patron_latino, traducir, linea, flags=re.IGNORECASE)
        
        # --- COLOCACIÓN DE APÓSTROFES ---
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

# --- INTERFAZ ---
st.title("🎸 Cancionero Pro 2026")
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    
    lineas_con_duda = []
    for idx, linea in enumerate(lineas):
        # Buscamos notas que parecen palabras (RE, MI, SOL, LA, SI)
        if re.search(r'\b(RE|MI|SOL|LA|SI)\b', linea, re.I):
            lineas_con_duda.append((idx, linea))

    st.subheader("🔍 Confirmación de contexto")
    st.info("He encontrado notas en estos renglones. Selecciona solo los que sean **música**:")

    confirmados = []
    for idx, texto_linea in lineas_con_duda:
        # Mostramos el renglón completo para que el usuario decida
        if st.checkbox(f"Línea {idx+1}: {texto_linea.strip()}", value=False, key=f"L{idx}"):
            confirmados.append(idx)

    if st.button("🚀 Generar Cancionero Pro"):
        texto_final = procesar_texto_final(contenido, confirmados)
        
        st.subheader("Vista Previa:")
        st.code(texto_final, language="text")

        # --- JS PARA GUARDAR/COMPARTIR ---
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <style>
                .bar {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; }}
                .btn {{ padding: 12px 20px; border: none; border-radius: 20px; color: white; font-weight: bold; cursor: pointer; }}
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
                    a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                }};
                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([txt], {{type:'text/plain'}});
                    const f = new File([b], "{archivo.name}", {{type:'text/plain'}});
                    if(navigator.share) await navigator.share({{files:[f]}});
                }};
            </script>
        """, height=100)

