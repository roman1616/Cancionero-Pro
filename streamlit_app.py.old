import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto_selectivo(texto_bruto, lineas_omitir):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN UTF-8 ---
    texto = texto_bruto.replace('\r\n', '\n')
    lineas = texto.split('\n')
    
    # --- BLOQUE 2: CONVERSIÓN DE CIFRADO ---
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    # Almacenaremos qué líneas y qué posiciones fueron modificadas
    lineas_procesadas = []
    posiciones_cambiadas = [] # Lista de sets para cada línea

    for i, linea in enumerate(lineas):
        cambios_en_esta_linea = set()
        
        if i in lineas_omitir:
            lineas_procesadas.append(linea)
            posiciones_cambiadas.append(cambios_en_esta_linea)
            continue

        # Función de reemplazo que registra la posición
        def traducir_acorde(match):
            raiz_lat = match.group(1).upper()
            cualidad = match.group(2) or ""
            alteracion = match.group(3) or ""
            numero = match.group(4) or ""
            raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
            
            # Marcamos esta posición como "procedente de latino"
            inicio_match = match.start()
            cambios_en_esta_linea.add(inicio_match)
            
            return f"{raiz_amer}{alteracion}{cualidad}{numero}"

        nueva_linea = re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE)
        lineas_procesadas.append(nueva_linea)
        posiciones_cambiadas.append(cambios_en_esta_linea)

    # --- BLOQUE 3: COLOCACIÓN DE APÓSTROFES (Solo en notas cambiadas) ---
    resultado_final = []
    # Patrón para identificar notas americanas
    patron_final = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for i, linea in enumerate(lineas_procesadas):
        if i in lineas_omitir:
            resultado_final.append(linea)
            continue
            
        linea_lista = list(linea)
        ajuste = 0
        set_cambios = posiciones_cambiadas[i]

        for m in re.finditer(patron_final, linea):
            inicio_nota = m.start()
            fin_nota = m.end() + ajuste
            
            # CONDICIÓN CLAVE: Solo poner apóstrofe si la nota empezó en una posición 
            # que registramos como "cambiada desde latino" en el Bloque 2
            if inicio_nota in set_cambios:
                if fin_nota < len(linea_lista):
                    if linea_lista[fin_nota] not in ["'", "*"]:
                        linea_lista.insert(fin_nota, "'")
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
    try:
        # Intento de decodificación robusta para 2026 (UTF-8 con fallback a Latin-1)
        raw_bytes = archivo.getvalue()
        try:
            contenido = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            contenido = raw_bytes.decode("latin-1")
            
        lineas = contenido.split('\n')
        
        # Escaneo de oraciones sospechosas
        patron_duda = r'\b(RE|MI|SOL|LA|SI)\b\s\b(RE|MI|SOL|LA|SI|[a-zñáéíóú]+)\b'
        
        lineas_sospechosas = []
        for idx, linea in enumerate(lineas):
            if re.search(patron_duda, linea, re.I):
                lineas_sospechosas.append((idx, linea))
        
        omitir_indices = []
        
        if lineas_sospechosas:
            st.warning("⚠️ Se detectaron posibles oraciones:")
            for idx, texto in lineas_sospechosas:
                if not st.checkbox(f"Renglón {idx+1}: {texto.strip()}", value=False, key=idx):
                    omitir_indices.append(idx)
        
        if st.button("Procesar Cancionero"):
            texto_final = procesar_texto_selectivo(contenido, omitir_indices)
            
            st.subheader("Vista Previa:")
            st.code(texto_final, language="text")

            texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
            components.html(f"""
                <div style="position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 999;">
                    <button id="dl" style="width: 140px; height: 45px; border: none; border-radius: 20px; font-weight: bold; cursor: pointer; color: white; background: #007AFF;">💾 Guardar</button>
                    <button id="sh" style="width: 140px; height: 45px; border: none; border-radius: 20px; font-weight: bold; cursor: pointer; color: white; background: #34C759;">📤 Compartir</button>
                </div>
                <script>
                    const txt = `{texto_js}`;
                    document.getElementById('dl').onclick = () => {{
                        const b = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), txt], {{type:'text/plain;charset=utf-8'}});
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                    }};
                    document.getElementById('sh').onclick = async () => {{
                        const b = new Blob([txt], {{type:'text/plain;charset=utf-8'}});
                        const f = new File([b], "{archivo.name}", {{type:'text/plain;charset=utf-8'}});
                        if(navigator.share) await navigator.share({{files:[f]}});
                    }};
                </script>
            """, height=100)
    except Exception as e:
        st.error(f"Error: {e}")

