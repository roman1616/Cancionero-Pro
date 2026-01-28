import streamlit as st
import re
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto_selectivo(texto_bruto, lineas_omitir):
    if not texto_bruto: return ""
    
    texto = texto_bruto.replace('\r\n', '\n')
    lineas = texto.split('\n')
    
    # Patron para detectar acordes en notación latina
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
        # Si la línea está en la lista de omitir, se queda igual
        if i in lineas_omitir:
            resultado_intermedio.append(linea)
        else:
            resultado_intermedio.append(re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE))

    # Colocación de apóstrofes en los acordes resultantes
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
st.info("Sube un archivo .txt. A partir de la línea 7 podrás confirmar cuáles son acordes.")

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    omitir_indices = []

    st.subheader("Configuración de líneas (Desde renglón 7)")
    st.write("Selecciona solo las líneas que contienen **MÚSICA/ACORDES**:")

    # Iteramos todas las líneas del archivo
    for idx, linea in enumerate(lineas):
        # A partir del renglón 7 (índice 6) mostramos el selector
        if idx >= 6:
            texto_muestra = linea.strip() if linea.strip() else "[Línea vacía]"
            # Si el checkbox NO se marca, se agrega a la lista de omitir procesamiento
            if not st.checkbox(f"Renglón {idx+1}: {texto_muestra}", value=False, key=f"linea_{idx}"):
                omitir_indices.append(idx)
        else:
            # Las primeras 6 líneas se omiten por defecto (puedes cambiar esto a True si prefieres)
            omitir_indices.append(idx)
    
    if st.button("Procesar y Generar"):
        texto_final = procesar_texto_selectivo(contenido, omitir_indices)
        
        st.subheader("Vista Previa del Resultado:")
        st.code(texto_final, language="text")

        # --- COMPONENTE JS PARA GUARDAR/COMPARTIR ---
        # Documentación de componentes en Streamlit: https://docs.streamlit.io
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 999; background: rgba(255,255,255,0.8); padding: 10px; border-radius: 25px;">
                <button id="dl" style="width: 120px; height: 40px; border: none; border-radius: 15px; font-weight: bold; cursor: pointer; color: white; background: #007AFF;">💾 Guardar</button>
                <button id="sh" style="width: 120px; height: 40px; border: none; border-radius: 15px; font-weight: bold; cursor: pointer; color: white; background: #34C759;">📤 Compartir</button>
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
                    if(navigator.share) {{
                        try {{ await navigator.share({{files:[f], title: 'Cancionero Pro'}}); }}
                        catch(e) {{ console.log('Error sharing', e); }}
                    }} else {{
                        alert("Tu navegador no soporta la función de compartir.");
                    }}
                }};
            </script>
        """, height=100)
