import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

# --- LÓGICA DE PROCESAMIENTO ---
def procesar_texto_selectivo(texto_bruto, lineas_a_procesar, modo_origen, corregir_posicion):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    resultado_intermedio = []

    # 1. CORRECCIÓN DE POSICIÓN (Ej: FAM# -> FA#M)
    if corregir_posicion == "Activada":
        patron_pos = r'\b(DO|RE|MI|FA|SOL|LA|SI)(M|m|MAJ|MIN|maj|min|aug|dim|sus|add)?([#b])'
        for i in range(len(lineas)):
            if i in lineas_a_procesar:
                lineas[i] = re.sub(patron_pos, r'\1\3\2', lineas[i], flags=re.IGNORECASE)

    # 2. TRADUCCIÓN A AMERICANO
    if "Latino" in modo_origen:
        patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#b])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
        def traducir_acorde(match):
            raiz_lat = match.group(1).upper()
            alteracion = match.group(2) or ""
            cualidad = match.group(3) or ""
            numero = match.group(4) or ""
            raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
            if cualidad.upper() in ["M", "MIN"]: cualidad = "m"
            return f"{raiz_amer}{alteracion}{cualidad}{numero}"

        for i, linea in enumerate(lineas):
            if i in lineas_a_procesar:
                resultado_intermedio.append(re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE))
            else:
                resultado_intermedio.append(linea)
    else:
        resultado_intermedio = lineas

    # 3. COLOCACIÓN DE APÓSTROFE
    resultado_final = []
    patron_chord = r'\b([A-G][#b]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD|M)?[0-9]*(?:/[A-G][#b]?)?)\b'
    for i, linea in enumerate(resultado_intermedio):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_chord, linea, re.IGNORECASE):
            fin = m.end() + ajuste
            if fin < len(linea_lista) and linea_lista[fin] not in ["'", "*"]:
                linea_lista.insert(fin, "'")
                ajuste += 1
            elif fin >= len(linea_lista):
                linea_lista.append("'")
                ajuste += 1
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src='https://raw.githubusercontent.com/roman1616/Cancionero-Pro/refs/heads/main/192-192.png' alt='Icono' style='width: 45px; height: 45px;'>
        <h1>Cancionero Pro</h1>   
    </div>""", unsafe_allow_html=True)

st.markdown("### 1. Configuración de Estilo")
# Tres selecciones circulares (Radio) para coherencia total
opt_posicion = st.radio("Posición de Sostenidos/Bemoles:", ["Activada (FA#M)", "Sin cambios (FAM#)"], horizontal=True)
opt_origen = st.radio("Cifrado de entrada:", ["Latino (DO, RE...)", "Americano (C, D...)"], horizontal=True)
opt_salida = st.radio("Formato de salida:", ["Apostrofado (C' D')", "Original"], horizontal=True)

st.markdown("---")
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    
    # Análisis rápido (Funciones internas simplificadas para brevedad)
    confirmados = [i for i, l in enumerate(lineas) if (re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', l) or "  " in l) and l.strip()]
    
    if st.button("✨ PROCESAR ARCHIVO", use_container_width=True):
        texto_final = procesar_texto_selectivo(
            contenido, 
            confirmados, 
            opt_origen, 
            "Activada" if "Activada" in opt_posicion else "Desactivada"
        )
        
        st.code(texto_final, language="text")
        
        # Script de guardado (Streamlit Components)
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <button id="btn" style="width:100%; padding:15px; background:#007AFF; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">💾 FINALIZAR Y DESCARGAR</button>
            <script>
                document.getElementById('btn').onclick = () => {{
                    const blob = new Blob([`{texto_js}`], {{type:'text/plain'}});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = "PRO_{archivo.name}";
                    a.click();
                }};
            </script>
        """, height=100)
