import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):
    # Regla 1: Contiene símbolos musicales explícitos o números de acorde (G7, Mim, etc.)
    if re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', linea, re.I):
        return True
    
    # Regla 2: Contiene más de 2 espacios seguidos (típico de espaciado entre acordes)
    if "  " in linea:
        return True

    # Regla 3: Si la línea consiste ÚNICAMENTE en una nota (ej: "SOL")
    notas_encontradas = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea, re.I)
    palabras_totales = re.findall(r'\w+', linea)
    if len(notas_encontradas) == 1 and len(palabras_totales) == 1:
        return True

    # Regla 4: Contiene 2 o más notas latinas diferentes
    if len(set(n.upper() for n in notas_encontradas)) >= 2:
        return True
        
    return False

def tiene_potencial_duda(linea):
    # Si contiene palabras que son notas pero están mezcladas con texto (ej: "La casa")
    notas = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea, re.I)
    return len(notas) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):
    if not texto_bruto: return ""
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
    dudosos = []
    
    for idx, linea in enumerate(lineas):
        if idx < 6: continue 
        
        if es_musica_obvia(linea):
            confirmados_auto.append(idx)
        elif tiene_potencial_duda(linea):
            dudosos.append((idx, linea))

    st.subheader("📊 Resumen de Análisis")
    st.write(f"✅ **{len(confirmados_auto)}** líneas detectadas como música automáticamente.")
    
    seleccion_manual = []
    if dudosos:
        st.warning("⚠️ **Dudas detectadas:** Las siguientes líneas contienen notas pero parecen ser parte de la letra. Marca las que sean **MÚSICA**:")
        for idx, texto in dudosos:
            if st.checkbox(f"L{idx+1}: {texto.strip()}", value=False, key=f"duda_{idx}"):
                seleccion_manual.append(idx)
    
    if st.button("🚀 Procesar Cancionero"):
        total_a_procesar = confirmados_auto + seleccion_manual
        texto_final = procesar_texto_selectivo(contenido, total_a_procesar)
        
        st.subheader("Vista Previa:")
        st.code(texto_final, language="text")

        # JS para Guardar
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 999;">
                <button id="dl" style="padding: 12px 25px; border-radius: 20px; border: none; background: #007AFF; color: white; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">💾 Descargar .txt</button>
            </div>
            <script>
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([`{texto_js}`], {{type:'text/plain'}});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                }};
            </script>
        """, height=80)
