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
    
    # REGLA NUEVA: Si hay notas en minúsculas, es muy probable que sea texto
    # Pero si hay símbolos como #, / o números pegados, manda la música
    tiene_simbolos = re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', linea)
    
    # Regla 1: Símbolos musicales explícitos
    if tiene_simbolos: return True
    # Regla 2: Doble espacio (alineación)
    if "  " in linea: return True
    
    # Regla 3: Notas en MAYÚSCULAS
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea) # Sin re.I (Case sensitive)
    palabras = re.findall(r'\w+', linea)
    
    # Si es una sola palabra y está en mayúsculas
    if len(palabras) == 1 and len(notas_mayus) == 1: return True
    # Si hay 2 o más notas en mayúsculas
    if len(set(notas_mayus)) >= 2: return True
    
    return False

def tiene_potencial_duda(linea):
    # Solo genera duda si la nota está en MAYÚSCULAS
    # Si dice "la" o "mi" en minúsculas, ni siquiera entra aquí
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    return len(notas_mayus) > 0

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
            # Solo traducimos si detecta el patrón
            nueva_linea = re.sub(patron_latino, traducir_acorde, linea) # Case sensitive
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
        if idx < 0: continue 
        
        # Filtro de seguridad: Si la anterior fue música, esta es texto
        if es_linea_musica_anterior:
            es_linea_musica_anterior = False
            continue

        if es_musica_obvia(linea):
            confirmados_auto.append(idx)
            es_linea_musica_anterior = True
        elif tiene_potencial_duda(linea):
            indices_duda.append(idx)
            es_linea_musica_anterior = False
        else:
            es_linea_musica_anterior = False

    st.subheader("🔍 Informe de Escaneo")
    st.success(f"Se detectaron {len(confirmados_auto)} líneas de acordes automáticamente.")

    seleccion_manual = []
    if indices_duda:
        st.warning("Se encontraron notas en MAYÚSCULAS que podrían ser texto. ¿Son música?")
        for idx in indices_duda:
            if st.checkbox(f"Renglón {idx+1}: {lineas[idx].strip()}", value=False, key=idx):
                seleccion_manual.append(idx)
    
    if st.button("✨ Procesar y Convertir"):
        total_indices = confirmados_auto + seleccion_manual
        texto_final = procesar_texto_selectivo(contenido, total_indices)
        
        st.subheader("Resultado Final:")
        st.code(texto_final, language="text")

        # JS Download
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <script>
                const b = new Blob([`{texto_js}`], {{type:'text/plain'}});
                const a = document.createElement('a');
                a.innerText = "💾 DESCARGAR ARCHIVO";
                a.href = URL.createObjectURL(b);
                a.download = "PRO_{archivo.name}";
                a.style = "display: block; width: 200px; margin: 20px auto; padding: 15px; background: #34C759; color: white; text-align: center; border-radius: 10px; font-family: sans-serif; font-weight: bold; text-decoration: none;";
                document.body.appendChild(a);
            </script>
        """, height=100)
