import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# --- ESTILO UNIFICADO NARANJA ---
st.markdown("""
    <style>
    /* Color de los Radio Buttons activos */
    div[data-baseweb="radio"] div[aria-checked="true"] > div {
        background-color: #FF4B4B !important;
    }
    
    /* Botón Procesar (Streamlit) */
    div.stButton > button {
        width: 100% !important;
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        height: 45px !important;
        font-size: 14px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #E03E3E !important;
    }

    /* Ajuste de etiquetas */
    .stRadio [data-testid="stWidgetLabel"] { font-size: 0.9rem !important; font-weight: bold; }
    
    /* Eliminar márgenes del iframe del componente HTML */
    iframe { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar, modo_origen, corregir_posicion):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    
    # 1. Corrección de Posición (SOLO SI ESTÁ ACTIVADA)
    # Si eliges "Desactivada", este bloque se salta y el texto queda tal cual
    if corregir_posicion == "Activada":
        patron_pos = r'\b(DO|RE|MI|FA|SOL|LA|SI)(M|m|MAJ|MIN|maj|min|aug|dim|sus|add)?([#b])'
        for i in range(len(lineas)):
            if i in lineas_a_procesar:
                # Intercambia el orden para que el sostenido/bemol vaya antes de la cualidad
                lineas[i] = re.sub(patron_pos, r'\1\3\2', lineas[i], flags=re.IGNORECASE)

    # 2. Traducción de Latino a Americano
    resultado_intermedio = []
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

    # 3. Marcado de acordes con apóstrofe
    resultado_final = []
    # Este patrón detecta tanto el orden correcto (F#m) como el "incorrecto" (Fm#) para poner el apóstrofe
    patron_chord = r'\b([A-G][#b]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD|M)?[0-9]*(?:/[A-G][#b]?)?|[A-G](?:m|MAJ|MIN|AUG|DIM|SUS|ADD|M)?[#b][0-9]*)\b'
    
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
    <div style='display: flex; align-items: center; justify-content: center; gap: 15px;'>
        <img src='https://raw.githubusercontent.com/roman1616/Cancionero-Pro/refs/heads/main/192-192.png' alt='Icono' style='width: 50px; height: 50px;'>
        <h1>Cancionero Pro</h1>   
    </div>""", unsafe_allow_html=True)

st.markdown("### Configuración de Estilo")
opt_posicion = st.radio("Posición de Símbolos:", ["Activada (FA#M)","Desactivada"], horizontal=True)
opt_origen = st.radio("Cifrado de entrada:", ["Latino", "Americano"], horizontal=True)
opt_salida = st.radio("Formato de salida:", ["Apostrofado", "Original"], horizontal=True)

st.markdown("---")
archivo = st.file_uploader("Sube tu canción .txt", type=["txt"])



if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    confirmados = [i for i, l in enumerate(lineas) if (re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', l) or "  " in l) and l.strip()]
    
    if st.button("✨ PROCESAR"):
        texto_final = procesar_texto_selectivo(
            contenido, 
            confirmados, 
            opt_origen, 
            "Activada" if "Activada" in opt_posicion else "Desactivada"
        )
        
        st.code(texto_final, language="text")
        
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        
        # Componente HTML con la nueva lógica JS y el mismo estilo que el botón de Streamlit
                # Componente HTML corregido y unificado
        components.html(f"""
            <body style="margin: 0; padding: 0;">
                <button id="actionBtn" style="
                    width: 50%;
                    height: 45px;
                    background-color: #FF4B4B;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: normal;
                    height: 45px
                    font-size: 14px;
                    font-family: sans-serif;
                    transition: 0.3s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-sizing: border-box;
                ">💾 GUARDAR Y COMPARTIR</button>

                <script>
                    const btn = document.getElementById('actionBtn');
                    
                    // Efecto hover para igualar a Streamlit
                    btn.onmouseover = () => btn.style.backgroundColor = '#E03E3E';
                    btn.onmouseout = () => btn.style.backgroundColor = '#FF4B4B';

                    btn.onclick = async () => {{
                        const contenido = `{texto_js}`;
                        const fileName = "{archivo.name}";
                        const blob = new Blob([contenido], {{ type: 'text/plain' }});
                        const file = new File([blob], fileName, {{ type: 'text/plain' }});
                        
                        if (confirm("🎵 ¿Deseas COMPARTIR el archivo? 🎵")) {{
                            if (navigator.share) {{
                                try {{ 
                                    await navigator.share({{ files: [file] }}); 
                                    return; 
                                }} catch(e) {{
                                    alert("Error al compartir: " + e.message);
                                }}
                            }} else {{
                                alert("Tu navegador no soporta la función de compartir.");
                            }}
                        }}

                        if (confirm("💾 ¿Deseas DESCARGAR el archivo? 💾")) {{
                            const a = document.createElement('a');
                            a.href = URL.createObjectURL(blob);
                            a.download = fileName;
                            a.click();
                        }}
                    }};
                </script>
            </body>
        """, height=45)
