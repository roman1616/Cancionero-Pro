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
    texto = texto_bruto.replace('\r\n', '\n')
    lineas = texto.split('\n')
    
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()
        # Reordenar: Lam# -> A#m
        return f"{LATINO_A_AMERICANO[raiz_lat]}{match.group(3) or ''}{match.group(2) or ''}{match.group(4) or ''}"

    resultado_intermedio = []
    for i, linea in enumerate(lineas):
        if i in lineas_omitir:
            resultado_intermedio.append(linea)
        else:
            resultado_intermedio.append(re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE))

    # --- BLOQUE 3: APÓSTROFES ---
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
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    
    lineas_sospechosas = []
    # Lista de notas para excluir de la duda
    notas_reg = r'(DO|RE|MI|FA|SOL|LA|SI)'
    
    for idx, linea in enumerate(lineas):
        # 1. Si tiene símbolos musicales (#, m, -, 7), NO es duda, es MÚSICA
        if re.search(r'[#m7\-]', linea, re.I) and re.search(notas_reg, linea, re.I):
            continue
            
        # 2. Es SOSPECHOSO solo si una nota está pegada a una palabra que NO es nota
        # Ejemplo: "la casa" -> duda | "la re" -> música
        palabras = re.findall(r'\b\w+\b', linea)
        es_duda = False
        for i in range(len(palabras)):
            p = palabras[i].upper()
            if p in LATINO_A_AMERICANO:
                # Si hay una palabra siguiente y esa palabra NO es una nota...
                if i + 1 < len(palabras):
                    sig = palabras[i+1].upper()
                    if sig not in LATINO_A_AMERICANO:
                        es_duda = True
                        break
        
        if es_duda:
            lineas_sospechosas.append((idx, linea))
    
    omitir_indices = []
    if lineas_sospechosas:
        st.warning("⚠️ Posibles oraciones detectadas:")
        for idx, texto in lineas_sospechosas:
            if not st.checkbox(f"Línea {idx+1}: {texto.strip()}", value=False, key=idx):
                omitir_indices.append(idx)
    
    if st.button("Procesar"):
        texto_final = procesar_texto_selectivo(contenido, omitir_indices)
        st.code(texto_final, language="text")
        
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px;">
                <button id="dl" style="padding:12px 25px; border-radius:20px; border:none; background:#007AFF; color:white; font-weight:bold; cursor:pointer;">💾 Guardar</button>
                <button id="sh" style="padding:12px 25px; border-radius:20px; border:none; background:#34C759; color:white; font-weight:bold; cursor:pointer;">📤 Compartir</button>
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
