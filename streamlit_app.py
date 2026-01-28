import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):
    if not linea.strip(): return False
    # Regla 1: Símbolos musicales o estructuras G7, Mim, etc.
    if re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', linea, re.I): return True
    # Regla 2: Doble espacio (alineación de acordes)
    if "  " in linea: return True
    # Regla 3: Una sola palabra que es una nota (ej: "SOL")
    palabras = re.findall(r'\w+', linea)
    notas = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea, re.I)
    if len(palabras) == 1 and len(notas) == 1: return True
    # Regla 4: Al menos 2 notas diferentes
    if len(set(n.upper() for n in notas)) >= 2: return True
    return False

def tiene_potencial_duda(linea):
    notas = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea, re.I)
    return len(notas) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()
        cualidad = match.group(2) or ""
        alteracion = match.group(3) or ""
        numero = match.group(4) or ""
        return f"{LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)}{alteracion}{cualidad}{numero}"

    resultado_final = []
    patron_final = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            nueva_linea = re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE)
            linea_lista = list(nueva_linea)
            ajuste = 0
            for m in re.finditer(patron_final, nueva_linea):
                fin = m.end() + ajuste
                if fin < len(linea_lista) and linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
                    ajuste += 1
                elif fin >= len(linea_lista):
                    linea_lista.append("'")
                    ajuste += 1
            resultado_final.append("".join(linea_lista))
        else:
            resultado_final.append(linea)
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.title("🎸 Cancionero Inteligente 2026")
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    
    confirmados_auto = []
    indices_duda = []
    es_linea_musica_anterior = False

    for idx, linea in enumerate(lineas):
        if idx < 0: continue # maneja desde que renglon empieza a escanear
        
        # APLICACIÓN DE CRITERIOS
        es_musica = es_musica_obvia(linea)
        
        # Si la anterior fue música, esta es probablemente texto (Letra) -> No es duda
        if es_linea_musica_anterior:
            es_linea_musica_anterior = False
            continue 

        if es_musica:
            confirmados_auto.append(idx)
            es_linea_musica_anterior = True
        elif tiene_potencial_duda(linea):
            indices_duda.append(idx)
            es_linea_musica_anterior = False
        else:
            es_linea_musica_anterior = False

    st.subheader("📊 Análisis Estructural")
    st.write(f"✅ **{len(confirmados_auto)}** líneas de música detectadas.")

    seleccion_manual = []
    if indices_duda:
        st.warning("⚠️ **Verificación manual:** ¿Estas líneas son música o letra?")
        for idx in indices_duda:
            if st.checkbox(f"L{idx+1}: {lineas[idx].strip()}", value=False, key=f"d_{idx}"):
                seleccion_manual.append(idx)
    
    if st.button("🚀 Procesar Cancionero"):
        total_indices = confirmados_auto + seleccion_manual
        texto_final = procesar_texto_selectivo(contenido, total_indices)
        
        st.subheader("Resultado:")
        st.code(texto_final, language="text")

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);">
                <button id="dl" style="padding: 12px 25px; border-radius: 20px; border: none; background: #007AFF; color: white; font-weight: bold; cursor: pointer;">💾 Descargar</button>
            </div>
            <script>
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([`{texto_js}`], {{type:'text/plain'}});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                }};
            </script>
        """, height=80)

