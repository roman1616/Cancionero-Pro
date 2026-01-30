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
    tiene_simbolos = re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', linea)
    if tiene_simbolos: return True
    if "  " in linea: return True
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    palabras = re.findall(r'\w+', linea)
    if len(palabras) == 1 and len(notas_mayus) == 1: return True
    if len(set(notas_mayus)) >= 2: return True
    return False

def tiene_potencial_duda(linea):
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    notas_amer = re.findall(r'\b[A-G][#b]?\b', linea)
    return len(notas_mayus) > 0 or len(notas_amer) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar, modo, corregir_sostenido):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    resultado_intermedio = []

    # 1. CORRECCIÓN DE POSICIÓN (Ej: FAM# -> FA#M)
    if corregir_sostenido:
        # Busca Notas (DO-SI) seguidas de letras (M/m/maj...) y LUEGO el sostenido
        patron_correccion = r'\b(DO|RE|MI|FA|SOL|LA|SI)(M|m|MAJ|MIN|maj|min|aug|dim|sus|add)([#])'
        for i in range(len(lineas)):
            if i in lineas_a_procesar:
                lineas[i] = re.sub(patron_correccion, r'\1\3\2', lineas[i], flags=re.IGNORECASE)

    # 2. TRADUCCIÓN (Si es Latino)
    if modo == "Latino":
        patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
        
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
                linea_traducida = re.sub(patron_latino, traducir_acorde, linea.upper())
                resultado_intermedio.append(linea_traducida)
            else:
                resultado_intermedio.append(linea)
    else:
        resultado_intermedio = lineas

    # 3. COLOCACIÓN DE APÓSTROFE
    resultado_final = []
    patron_americano = r'\b([A-G][#b]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for i, linea in enumerate(resultado_intermedio):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue
            
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_americano, linea, re.IGNORECASE if modo == "Americano" else 0):
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
st.title("🎸 Cancionero Inteligente 2026")

# NUEVA OPCIÓN: Corregir formato de sostenido
corregir_sostenido = st.checkbox("🔄 Corregir posición de sostenido (Ej: FAM# ➔ FA#M)", value=False)

tipo_cifrado = st.radio("Elige el formato de origen:", ["Latino (DO, RE, MI...)", "Americano (C, D, E...)"])

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    confirmados_auto = []
    indices_duda = []

    for idx, linea in enumerate(lineas):
        if es_musica_obvia(linea):
            confirmados_auto.append(idx)
        elif tiene_potencial_duda(linea):
            indices_duda.append(idx)

    st.subheader("🔍 Análisis")
    st.success(f"Detección automática: {len(confirmados_auto)} líneas.")

    seleccion_manual = []
    if indices_duda:
        st.warning("Confirma si estas líneas son música:")
        for idx in indices_duda:
            if st.checkbox(f"Renglón {idx+1}: {lineas[idx].strip()}", value=False, key=idx):
                seleccion_manual.append(idx)
    
    if st.button("✨ Procesar"):
        modo_final = "Latino" if "Latino" in tipo_cifrado else "Americano"
        total_indices = confirmados_auto + seleccion_manual
        # Pasar el nuevo parámetro a la función
        texto_final = procesar_texto_selectivo(contenido, total_indices, modo_final, corregir_sostenido)
        
        st.subheader("Resultado:")
        st.code(texto_final, language="text")

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="text-align: center; margin-top: 20px;">
                <button id="actionBtn" style="padding: 15px 30px; background: #007AFF; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px;">💾 FINALIZAR</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;
                    const fileName = "PRO_{archivo.name}";
                    const blob = new Blob([contenido], {{ type: 'text/plain' }});
                    const file = new File([blob], fileName, {{ type: 'text/plain' }});
                    
                    if (confirm("🎵 ¿Deseas COMPARTIR el archivo?")) {{
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

                    if (confirm("💾 ¿Deseas DESCARGAR el archivo?")) {{
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = fileName;
                        a.click();
                    }}
                }};
            </script>
        """, height=120)
