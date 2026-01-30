import streamlit as st
import re
import streamlit.components.v1 as components

# Configuración de página con tema oscuro/limpio
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
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea, re.IGNORECASE)
    palabras = re.findall(r'\w+', linea)
    if len(palabras) == 1 and len(notas_mayus) == 1: return True
    if len(set(notas_mayus)) >= 2: return True
    return False

def tiene_potencial_duda(linea):
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea, re.IGNORECASE)
    notas_amer = re.findall(r'\b[A-G][#b]?\b', linea)
    return len(notas_mayus) > 0 or len(notas_amer) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar, modo, corregir_posicion):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    resultado_intermedio = []

    # 1. CORRECCIÓN DE POSICIÓN (Soporta FAM#, fam#, REMb, remb, etc.)
    if corregir_posicion:
        # Regex captura: Nota + (M/m/etc opcional) + (# o b)
        # La nota y el símbolo se mueven, la cualidad queda al final
        patron_pos = r'\b(DO|RE|MI|FA|SOL|LA|SI)(M|m|MAJ|MIN|maj|min|aug|dim|sus|add)?([#b])'
        for i in range(len(lineas)):
            if i in lineas_a_procesar:
                lineas[i] = re.sub(patron_pos, r'\1\3\2', lineas[i], flags=re.IGNORECASE)

    # 2. TRADUCCIÓN (Si es Latino)
    if modo == "Latino":
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
                linea_traducida = re.sub(patron_latino, traducir_acorde, linea, flags=re.IGNORECASE)
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
        for m in re.finditer(patron_americano, linea, re.IGNORECASE):
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

# Contenedor de configuración para coherencia visual
with st.expander("⚙️ Configuración de Formato", expanded=True):
    # Checkbox y Radio con estilo coherente
    corregir_pos = st.checkbox("Corregir posición de símbolos (Ej: FAM# ➔ FA#M)", value=True)
    tipo_cifrado = st.radio("Formato de origen:", 
                            ["Latino (DO, RE...)", "Americano (C, D...)"],
                            horizontal=True)

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

    st.subheader("🔍 Análisis de Líneas")
    col1, col2 = st.columns(2)
    col1.metric("Automáticas", len(confirmados_auto))
    col2.metric("En duda", len(indices_duda))

    seleccion_manual = []
    if indices_duda:
        with st.container():
            st.info("Por favor, confirma las líneas dudosas:")
            for idx in indices_duda:
                if st.checkbox(f"L{idx+1}: {lineas[idx].strip()[:50]}", key=f"check_{idx}"):
                    seleccion_manual.append(idx)
    
    if st.button("✨ PROCESAR CANCIONERO", use_container_width=True):
        modo_final = "Latino" if "Latino" in tipo_cifrado else "Americano"
        total_indices = confirmados_auto + seleccion_manual
        texto_final = procesar_texto_selectivo(contenido, total_indices, modo_final, corregir_pos)
        
        st.subheader("📝 Vista Previa:")
        st.code(texto_final, language="text")

        # Botón de Guardado/Compartir con JS
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="text-align: center; margin-top: 10px;">
                <button id="actionBtn" style="width: 100%; padding: 15px; background: #007AFF; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; font-family: sans-serif;">💾 FINALIZAR Y GUARDAR</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;
                    const fileName = "PRO_{archivo.name}";
                    const blob = new Blob([contenido], {{ type: 'text/plain' }});
                    const file = new File([blob], fileName, {{ type: 'text/plain' }});
                    
                    if (confirm("🎵 ¿Deseas COMPARTIR el archivo?")) {{
                        if (navigator.share) {{
                            try {{ await navigator.share({{ files: [file] }}); return; }} 
                            catch(e) {{ alert("Error al compartir: " + e.message); }}
                        }}
                    }}
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = fileName;
                    a.click();
                }};
            </script>
        """, height=100)
