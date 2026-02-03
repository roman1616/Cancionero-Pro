import streamlit as st
import re
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# --- ESTILO UNIFICADO ---
st.markdown("""
    <style>
    div[data-baseweb="radio"] div[aria-checked="true"] > div { background-color: #FF4B4B !important; }
    div.stButton > button {
        width: 100% !important; background-color: #FF4B4B !important;
        color: white !important; border-radius: 8px !important;
        border: none !important; font-weight: bold !important;
        height: 45px !important; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #E03E3E !important; }
    iframe { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

LATINO_A_AMERICANO = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'}

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar, modo_origen, corregir_posicion, formato_salida):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    
    # 1. Corrección de Posición
    if corregir_posicion == "Activada":
        patron_pos = r'\b(DO|RE|MI|FA|SOL|LA|SI)(M|m|MAJ|MIN|maj|min|aug|dim|sus|add)?([#b])'
        for i in range(len(lineas)):
            if i in lineas_a_procesar:
                lineas[i] = re.sub(patron_pos, r'\1\3\2', lineas[i], flags=re.IGNORECASE)

    # 2. Traducción
    resultado_intermedio = []
    if "Latino" in modo_origen:
        patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#b])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
        def traducir_acorde(match):
            raiz_lat = match.group(1).upper()
            alteracion = match.group(2) or ""
            cualidad = match.group(3) or ""
            numero = match.group(4) or ""
            raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
            if cualidad.upper() == "MIN": cualidad = "m"
            elif cualidad.upper() == "M": cualidad = "" 
            return f"{raiz_amer}{alteracion}{cualidad}{numero}"
        
        for i, linea in enumerate(lineas):
            if i in lineas_a_procesar:
                resultado_intermedio.append(re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE))
            else:
                resultado_intermedio.append(linea)
    else:
        resultado_intermedio = lineas

    # 3. Apostrofado (Corregido para D# y paréntesis)
    if formato_salida == "Original":
        return '\n'.join(resultado_intermedio)

    resultado_final = []
    patron_chord = r'\b[A-G](?:[#b]|m|MAJ|MIN|AUG|DIM|SUS|ADD|M|[0-9]|/)*'
    
    for i, linea in enumerate(resultado_intermedio):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue
            
        linea_lista = list(linea)
        coincidencias = list(re.finditer(patron_chord, linea, re.IGNORECASE))
        
        for m in reversed(coincidencias):
            fin = m.end()
            # Mover apóstrofe fuera del paréntesis si existe
            if fin < len(linea_lista) and linea_lista[fin] == ")":
                fin += 1
            
            if fin < len(linea_lista):
                if linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
            else:
                linea_lista.append("'")
        resultado_final.append("".join(linea_lista))
        
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown(f"""<div style='display:flex;align-items:center;justify-content:center;gap:15px;'>
<img src='https://raw.githubusercontent.com/roman1616/Cancionero-Pro/refs/heads/main/40.png' style='width:50px;'><h1>Cancionero Pro</h1></div>""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1: opt_posicion = st.radio("Posición Símbolos:", ["Activada (FA#M)","Desactivada"])
with col2: opt_origen = st.radio("Cifrado Entrada:", ["Latino", "Americano"])
with col3: opt_salida = st.radio("Formato Salida:", ["Apostrofado", "Original"])

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    confirmados = [i for i, l in enumerate(lineas) if (re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', l, re.I) or "  " in l) and l.strip()]
    
    if st.button("✨ PROCESAR"):
        texto_final = procesar_texto_selectivo(
            contenido, confirmados, opt_origen, 
            "Activada" if "Activada" in opt_posicion else "Desactivada", 
            opt_salida
        )
        
        st.code(texto_final, language="text")
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        
        components.html(f"""
            <button id="actionBtn" style="width:30%; height:45px; background-color:#FF4B4B; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; font-family:sans-serif;">💾 GUARDAR Y COMPARTIR</button>
            <script>
                const btn = document.getElementById('actionBtn');
                btn.onclick = async () => {{
                    const blob = new Blob([`{texto_js}`], {{ type: 'text/plain' }});
                    const file = new File([blob], "{archivo.name}", {{ type: 'text/plain' }});
                    if (confirm("🎵 ¿Compartir archivo?")) {{
                        if (navigator.share) {{
                            try {{ await navigator.share({{ files: [file] }}); return; }} catch(e) {{}}
                        }} else {{ alert("Compartir no disponible."); }}
                    }}
                    if (confirm("💾 ¿Descargar archivo? 💾")) {{
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = "{archivo.name}";
                        a.click();
                    }}
                }};
            </script>
        """, height=55)
