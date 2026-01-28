import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):
    # Regla 1: Contiene símbolos que NO se usan en lenguaje normal
    if re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', linea, re.I):
        return True
    # Regla 2: Contiene 2 o más notas latinas diferentes (ej: "SOL" y "RE")
    notas = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea, re.I)
    if len(set(n.upper() for n in notas)) >= 2:
        return True
    return False

def tiene_potencial_duda(linea):
    # Si contiene una nota solitaria (como "LA" o "MI") sin otros indicadores
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
            # Procesar acordes
            nueva_linea = re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE)
            # Agregar apóstrofes
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

archivo = st.file_uploader("Sube tu .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    
    confirmados_auto = []
    dudosos = []
    
    for idx, linea in enumerate(lineas):
        if idx < 6: continue # Omitir encabezado
        
        if es_musica_obvia(linea):
            confirmados_auto.append(idx)
        elif tiene_potencial_duda(linea):
            dudosos.append((idx, linea))

    st.subheader("🔍 Verificación necesaria")
    st.write(f"Se detectaron **{len(confirmados_auto)}** líneas de música automáticamente.")
    
    seleccion_manual = []
    if dudosos:
        st.warning("Las siguientes líneas parecen texto, pero contienen palabras que podrían ser notas. Marca si son **MÚSICA**:")
        for idx, texto in dudosos:
            if st.checkbox(f"L{idx+1}: {texto.strip()}", value=False, key=idx):
                seleccion_manual.append(idx)
    else:
        st.success("No hay dudas detectadas en el resto del texto.")

    if st.button("Generar Cancionero"):
        total_a_procesar = confirmados_auto + seleccion_manual
        texto_final = procesar_texto_selectivo(contenido, total_a_procesar)
        
        st.code(texto_final, language="text")
        
        # Botones de Guardar/Compartir (JS)
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px;">
                <button id="dl" style="padding: 10px 20px; border-radius: 15px; border: none; background: #007AFF; color: white; font-weight: bold; cursor: pointer;">💾 Guardar</button>
            </div>
            <script>
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([`{texto_js}`], {{type:'text/plain'}});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                }};
            </script>
        """, height=80)
