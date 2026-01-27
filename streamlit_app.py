import streamlit as st
import re
import streamlit.components.v1 as components

# Forzamos configuración de página
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto_selectivo(texto_bruto, lineas_omitir):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN UTF-8 ---
    # Convertimos a string asegurando limpieza de saltos de línea
    texto = texto_bruto.replace('\r\n', '\n')
    lineas = texto.split('\n')
    
    # --- BLOQUE 2: CONVERSIÓN DE CIFRADO ---
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()
        cualidad = match.group(2) or ""
        alteracion = match.group(3) or ""
        numero = match.group(4) or ""
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    resultado_intermedio = []
    for i, linea in enumerate(lineas):
        if i in lineas_omitir:
            resultado_intermedio.append(linea)
        else:
            resultado_intermedio.append(re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE))

    # --- BLOQUE 3: COLOCACIÓN DE APÓSTROFES ---
    resultado_final = []
    patron_final = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for i, linea in enumerate(resultado_intermedio):
        if i in lineas_omitir:
            resultado_final.append(linea)
            continue
            
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

# --- INTERFAZ ---
st.title("🎸 Cancionero Pro 2026")

# Cargador de archivos con codificación explícita
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    try:
        # Leemos forzando UTF-8 para evitar errores de decodificación
        contenido = archivo.getvalue().decode("utf-8", errors="replace")
        lineas = contenido.split('\n')
        
        # Escaneo de oraciones sospechosas
        patron_duda = r'\b(RE|MI|SOL|LA|SI)\b\s\b(RE|MI|SOL|LA|SI|[a-zñáéíóú]+)\b'
        
        lineas_sospechosas = []
        for idx, linea in enumerate(lineas):
            if re.search(patron_duda, linea, re.I):
                lineas_sospechosas.append((idx, linea))
        
        omitir_indices = []
        
        if lineas_sospechosas:
            st.warning("⚠️ Se detectaron oraciones que podrían confundirse con notas:")
            st.write("Selecciona solo las que **SÍ SON MÚSICA**:")
            
            for idx, texto in lineas_sospechosas:
                if not st.checkbox(f"Renglón {idx+1}: {texto.strip()}", value=False, key=idx):
                    omitir_indices.append(idx)
        
        if st.button("Procesar Cancionero"):
            texto_final = procesar_texto_selectivo(contenido, omitir_indices)
            
            st.subheader("Vista Previa:")
            st.code(texto_final, language="text")

            # --- JS ACCIONES (UTF-8 compatible) ---
            # Escapamos caracteres que rompen el JS
            texto_js = texto_final.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
            
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
                        if(navigator.share) await navigator.share({{files: [f]}});
                    }};
                </script>
            """, height=100)
            
    except Exception as e:
        st.error(f"Error crítico de lectura: {e}. Asegúrate de que el archivo sea un .txt válido.")
