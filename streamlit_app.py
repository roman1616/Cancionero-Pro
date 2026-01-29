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
    # Detecta símbolos típicos de acordes (tanto latinos como americanos)
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
    # También dudamos si vemos letras sueltas A-G que podrían ser notas americanas
    notas_amer = re.findall(r'\b([A-G])\b', linea)
    return len(notas_mayus) > 0 or len(notas_amer) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar, formato_origen):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    
    # 1. TRADUCCIÓN (Solo si es Latino)
    if formato_origen == "Latino":
        # Convertimos temporalmente a upper para la búsqueda, manteniendo estructura
        lineas_temp = [l.upper() if i in lineas_a_procesar else l for i, l in enumerate(lineas)]
        patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
        
        def traducir_acorde(match):
            raiz_lat = match.group(1)
            alteracion = match.group(2) or ""
            cualidad = match.group(3) or ""
            numero = match.group(4) or ""
            raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
            if cualidad == "M" or cualidad == "MIN": cualidad = "m"
            return f"{raiz_amer}{alteracion}{cualidad}{numero}"

        resultado_intermedio = []
        for i, linea in enumerate(lineas_temp):
            if i in lineas_a_procesar:
                resultado_intermedio.append(re.sub(patron_latino, traducir_acorde, linea))
            else:
                resultado_intermedio.append(lineas[i]) # Mantener original (letras min/may)
    else:
        # Si ya es Americano, no traducimos nada
        resultado_intermedio = lineas

    # 2. COLOCACIÓN DE APÓSTROFE (Para ambos casos)
    resultado_final = []
    # El patrón reconoce acordes americanos estándar
    patron_americano = r'\b([A-G][#B]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD|M)?[0-9]*(?:/[A-G][#B]?)?)\b'

    for i, linea in enumerate(resultado_intermedio):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue
            
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_americano, linea, re.IGNORECASE if formato_origen == "Americano" else 0):
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

# Pregunta clave antes de subir
formato = st.radio("¿En qué formato está el cifrado original?", ["Latino (DO, RE, MI...)", "Americano (C, D, E...)"])

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    confirmados_auto = []
    indices_duda = []

    # Lógica de detección simplificada para evitar saltos erróneos
    for idx, linea in enumerate(lineas):
        if es_musica_obvia(linea):
            confirmados_auto.append(idx)
        elif tiene_potencial_duda(linea):
            indices_duda.append(idx)

    st.subheader("🔍 Análisis")
    st.info(f"Formato seleccionado: **{formato}**")
    
    seleccion_manual = []
    if indices_duda:
        st.warning("Confirma si estas líneas contienen música:")
        for idx in indices_duda:
            if st.checkbox(f"Fila {idx+1}: {lineas[idx].strip()}", value=False, key=idx):
                seleccion_manual.append(idx)
    
    if st.button("✨ Procesar y Finalizar"):
        total_indices = list(set(confirmados_auto + seleccion_manual))
        texto_final = procesar_texto_selectivo(contenido, total_indices, formato.split()[0])
        
        st.subheader("Resultado:")
        st.code(texto_final, language="text")

        # JS para compartir/descargar
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="text-align: center; margin-top: 20px;">
                <button id="actionBtn" style="padding: 15px 30px; background: #007AFF; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px;">💾 GUARDAR ARCHIVO</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;
                    const fileName = "PRO_{archivo.name}";
                    const blob = new Blob([contenido], {{ type: 'text/plain' }});
                    const file = new File([blob], fileName, {{ type: 'text/plain' }});
                    
                    if (navigator.share && /Android|iPhone|iPad/i.test(navigator.userAgent)) {{
                        try {{ await navigator.share({{ files: [file] }}); return; }} 
                        catch(e) {{}}
                    }}
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = fileName;
                    a.click();
                }};
            </script>
        """, height=120)

